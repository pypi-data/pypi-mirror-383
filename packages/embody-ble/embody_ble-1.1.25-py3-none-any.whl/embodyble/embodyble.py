"""Communicator module to communicate with an EmBody device over BLE (Bluetooth).

Allows for both sending messages synchronously and asynchronously,
receiving response messages and subscribing for incoming messages from the device.
"""

import asyncio
import logging
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from bleak import BleakClient
from bleak import BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from embodycodec import codec
from embodycodec.exceptions import CrcError
from embodyserial import embodyserial
from embodyserial.helpers import EmbodySendHelper
from packaging import version

from .exceptions import EmbodyBleError
from .listeners import BleMessageListener
from .listeners import ConnectionListener
from .listeners import MessageListener
from .listeners import ResponseMessageListener

logger = logging.getLogger(__name__)

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


class EmbodyBle(embodyserial.EmbodySender):
    """Main class for setting up BLE communication with an EmBody device.

    If serial_port is not set, the first port identified with proper manufacturer name is used.

    Handles both custom EmBody messages being sent on NUS_RX_UUID and received on NUS_TX_UUID,
    as well as standard BLE messages sending/receiving. Different callback interfaces
    (listeners) are used to be notified of incoming EmBody messages (MessageListener) and
    incoming BLE messages (BleMessageListener).

    Separate connect method, since it supports reconnecting to a device as well.

    Note that a new thread is created for each instance of this class, to run an asyncio
    event loop. Invoke the shutdown method to stop the thread.
    """

    def __init__(
        self,
        msg_listener: MessageListener | None = None,
        ble_msg_listener: BleMessageListener | None = None,
        connection_listener: ConnectionListener | None = None,
        response_msg_listener: ResponseMessageListener | None = None,
    ) -> None:
        super().__init__()
        self.__client: BleakClient | None = None
        self.__reader: _MessageReader | None = None
        self.__sender: _MessageSender | None = None
        self.__message_listeners: set[MessageListener] = set()
        self.__response_msg_listeners: set[ResponseMessageListener] = set()
        self.__ble_message_listeners: set[BleMessageListener] = set()
        self.__connection_listeners: set[ConnectionListener] = set()
        if msg_listener:
            self.__message_listeners.add(msg_listener)
        if response_msg_listener:
            self.__response_msg_listeners.add(response_msg_listener)
        if ble_msg_listener:
            self.__ble_message_listeners.add(ble_msg_listener)
        if connection_listener:
            self.__connection_listeners.add(connection_listener)
        self.__connection_listener_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="conn-worker")
        self.__loop = asyncio.new_event_loop()
        t = Thread(target=self.__start_background_loop, args=(self.__loop,), daemon=True)
        t.start()

    def __start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Runs an asyncio event loop in a background thread."""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def connect(self, device_name: str | None = None) -> None:
        asyncio.run_coroutine_threadsafe(self.__async_connect(device_name), self.__loop).result()

    async def __async_connect(self, device_name: str | None = None) -> None:
        """Connect to specified device (or use device name from serial port as default)."""
        if self.__client:
            await self.__client.disconnect()
        if self.__reader:
            self.__reader.stop()
        if device_name:
            self.__device_name = device_name
        else:
            self.__device_name = self.__find_name_from_serial_port()
        logger.info(f"Using EmBody device name: {self.__device_name}")
        scanner = BleakScanner()

        device = await scanner.find_device_by_filter(
            lambda d, ad: bool(ad.local_name and ad.local_name.lower() == self.__device_name.lower())
            or bool(d and d.name and d.name.lower() == self.__device_name.lower())
        )  # type: ignore[call-arg]
        if not device:
            raise EmbodyBleError(f"Could not find device with name {self.__device_name}")
        self.__client = BleakClient(device, self._on_disconnected)
        # self.__client._backend._mtu_size = 1497
        await self.__client.connect()

        logger.info(f"Connected: {self.__client}, mtu size: {self.__client.mtu_size}")
        self.__reader = _MessageReader(
            self.__client,
            self.__message_listeners,
            self.__ble_message_listeners,
            self.__response_msg_listeners,
        )
        self.__sender = _MessageSender(self.__client)
        self.__reader.add_response_message_listener(self.__sender)
        await self.__client.start_notify(UART_TX_CHAR_UUID, self.__reader.on_uart_tx_data)
        self.__notify_connection_listeners(True)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Async connect completed: {self.__client}")

    def disconnect(self) -> None:
        asyncio.run_coroutine_threadsafe(self.__async_disconnect(), self.__loop).result()

    async def __async_disconnect(self) -> None:
        """Disconnect from device if connected."""
        if self.__client:
            try:
                await self.__client.stop_notify(UART_TX_CHAR_UUID)
            except Exception as e:
                logger.debug(f"Failed to stop notify UART_TX:: {e}")
            await self.__client.disconnect()
            logger.info(f"Disconnected: {self.__client}")
            if self.__reader:
                self.__reader.stop()
                self.__reader = None
            self.__client = None

    def shutdown(self) -> None:
        """Shutdown after use."""
        self.disconnect()
        self.__sender = None
        if self.__reader:
            self.__reader.stop()
            self.__reader = None
        self.__loop.stop()
        self.__connection_listener_executor.shutdown(wait=False, cancel_futures=False)

    def send_async(self, msg: codec.Message) -> None:
        if not self.__sender:
            raise EmbodyBleError("Sender not initialized")
        asyncio.run_coroutine_threadsafe(self.__sender.send_async(msg, False), self.__loop).result()

    def send(self, msg: codec.Message, timeout: int | None = 5) -> codec.Message | None:
        if not self.__sender:
            raise EmbodyBleError("Sender not initialized")
        return asyncio.run_coroutine_threadsafe(self.__sender.send_async(msg, True, timeout), self.__loop).result()

    def write_ble_attribute(self, uuid: str, data: bytes) -> None:
        if not self.__client:
            raise EmbodyBleError("BLE client not initialized")
        return asyncio.run_coroutine_threadsafe(self.__client.write_gatt_char(uuid, data), self.__loop).result()

    def request_ble_attribute(self, uuid: str) -> bytearray:
        if not self.__client:
            raise EmbodyBleError("BLE client not initialized")
        return asyncio.run_coroutine_threadsafe(self.__client.read_gatt_char(uuid), self.__loop).result()

    def start_ble_notify(self, uuid: str) -> None:
        if not self.__reader:
            raise EmbodyBleError("Reader not initialized")
        asyncio.run_coroutine_threadsafe(self.__reader.start_ble_notify(uuid), self.__loop).result()

    def stop_ble_notify(self, uuid: str) -> None:
        if not self.__reader:
            raise EmbodyBleError("Reader not initialized")
        asyncio.run_coroutine_threadsafe(self.__reader.stop_ble_notify(uuid), self.__loop).result()

    def _on_disconnected(self, client: BleakClient) -> None:
        """Invoked by bleak when disconnected."""
        logger.info(f"Disconnected: {client}")
        self.__notify_connection_listeners(False)
        if self.__reader:
            self.__reader.stop()

    @staticmethod
    def __find_name_from_serial_port() -> str:
        """Request serial no from EmBody device."""
        comm = embodyserial.EmbodySerial()
        send_helper = EmbodySendHelper(comm)
        serial_no = send_helper.get_serial_no()
        firmware_version = version.parse(send_helper.get_firmware_version())
        prefix = "G3_" if firmware_version < version.parse("5.4.0") else "EmBody_"
        device_name = prefix + serial_no[-4:].upper()
        comm.shutdown()
        return device_name

    def list_available_devices(self, timeout=3) -> list[str]:
        """List available devices filtered by NUS service."""
        return asyncio.run_coroutine_threadsafe(self.__list_available_devices(timeout), self.__loop).result()

    async def __list_available_devices(self, timeout=3) -> list[str]:
        """List available devices filtered by NUS service."""
        scanner = BleakScanner()
        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()
        devices = scanner.discovered_devices
        return [d.name for d in devices if d.name and EmbodyBle.is_embody_ble_device(d.name)]

    @staticmethod
    def is_embody_ble_device(device_name: str | None) -> bool:
        """Check if the device name is an EmBody device."""
        return device_name is not None and device_name.lower().startswith(("g3", "embody"))

    def add_message_listener(self, listener: MessageListener) -> None:
        self.__message_listeners.add(listener)
        if self.__reader:
            self.__reader.add_message_listener(listener)

    def discard_message_listener(self, listener: MessageListener) -> None:
        self.__message_listeners.discard(listener)
        if self.__reader:
            self.__reader.discard_message_listener(listener)

    def add_response_message_listener(self, listener: ResponseMessageListener) -> None:
        self.__response_msg_listeners.add(listener)
        if self.__reader:
            self.__reader.add_response_message_listener(listener)

    def discard_response_message_listener(self, listener: ResponseMessageListener) -> None:
        self.__response_msg_listeners.discard(listener)
        if self.__reader:
            self.__reader.discard_response_message_listener(listener)

    def add_ble_message_listener(self, listener: BleMessageListener) -> None:
        self.__ble_message_listeners.add(listener)
        if self.__reader:
            self.__reader.add_ble_message_listener(listener)

    def discard_ble_message_listener(self, listener: BleMessageListener) -> None:
        self.__ble_message_listeners.discard(listener)
        if self.__reader:
            self.__reader.discard_ble_message_listener(listener)

    def add_connection_listener(self, listener: ConnectionListener) -> None:
        self.__connection_listeners.add(listener)

    def discard_connection_listener(self, listener: ConnectionListener) -> None:
        self.__connection_listeners.discard(listener)

    def __notify_connection_listeners(self, connected: bool) -> None:
        if len(self.__connection_listeners) == 0:
            return
        for listener in self.__connection_listeners:
            self.__connection_listener_executor.submit(EmbodyBle.__notify_connection_listener, listener, connected)

    @staticmethod
    def __notify_connection_listener(listener: ConnectionListener, connected: bool) -> None:
        try:
            listener.on_connected(connected)
        except Exception as e:
            logger.warning(f"Error notifying connection listener: {e!s}", exc_info=True)


class _MessageSender(ResponseMessageListener):
    """All send functionality is handled by this class.

    This includes thread safety, async handling and windowing
    """

    def __init__(self, client: BleakClient) -> None:
        self.__client = client
        self.__send_lock = asyncio.Lock()
        self.__response_event = asyncio.Event()
        self.__current_response_message: codec.Message | None = None

    def response_message_received(self, msg: codec.Message) -> None:
        """Invoked when response message is received by Message reader.

        Sets the local response message and notifies the waiting sender thread
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Response message received: {msg}")
        self.__current_response_message = msg
        self.__response_event.set()

    async def send_async(
        self,
        msg: codec.Message,
        wait_for_response: bool = True,
        timeout: int | None = 5,
    ) -> codec.Message | None:
        async with self.__send_lock:
            data = msg.encode()
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Sending message: {msg}, encoded: {data.hex()}")
            try:
                self.__response_event.clear()
                self.__current_response_message = None
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Sending message over BLE: {msg}")
                await self.__client.write_gatt_char(UART_RX_CHAR_UUID, data)
            except Exception as e:
                logger.warning(f"Error sending message: {e!s}", exc_info=False)
                return None
            if wait_for_response:
                try:
                    await asyncio.wait_for(self.__response_event.wait(), timeout)
                except TimeoutError as e:
                    logger.warning(f"Timeout waiting for response message: {e!s}", exc_info=False)
                    return None
            return self.__current_response_message


class _MessageReader:
    """Process and dispatch incoming messages to subscribers/listeners."""

    def __init__(
        self,
        client: BleakClient,
        message_listeners: set[MessageListener] | None = None,
        ble_message_listeners: set[BleMessageListener] | None = None,
        response_message_listeners: set[ResponseMessageListener] | None = None,
    ) -> None:
        """Initialize MessageReader."""
        super().__init__()
        self.__client = client
        self.__message_listener_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="rcv-worker")
        self.__ble_message_listener_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ble-msg-worker")
        if message_listeners is not None:
            self.__message_listeners = message_listeners
        else:
            self.__message_listeners = set()
        self.__message_listeners_lock = threading.Lock()
        if ble_message_listeners is not None:
            self.__ble_message_listeners = ble_message_listeners
        else:
            self.__ble_message_listeners = set()
        self.__ble_message_listeners_lock = threading.Lock()
        if response_message_listeners is not None:
            self.__response_message_listeners = response_message_listeners
        else:
            self.__response_message_listeners = set()
        self.__response_message_listeners_lock = threading.Lock()
        self.saved_data = bytearray()

    def stop(self) -> None:
        self.__message_listener_executor.shutdown(wait=False, cancel_futures=False)
        self.__ble_message_listener_executor.shutdown(wait=False, cancel_futures=False)

    async def start_ble_notify(self, uuid: str) -> None:
        """Start notification on a given characteristic."""
        try:
            await self.__client.start_notify(uuid, self.on_ble_message_received)
        except ValueError:
            return

    async def stop_ble_notify(self, uuid: str) -> None:
        """Stop notification on a given characteristic."""
        try:
            await self.__client.stop_notify(uuid)
        except ValueError:
            return

    def on_uart_tx_data(self, _: BleakGATTCharacteristic, data: bytearray) -> None:
        """Callback invoked by bleak when a new notification is received.

        New messages, both custom codec messages and BLE messages are received here.
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"New incoming data UART TX data: {bytes(data).hex()}")
        if len(self.saved_data) > 0:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Adding saved data: {bytes(self.saved_data).hex()}")
            data = self.saved_data + data
            self.saved_data = bytearray()
        pos = 0
        while pos < len(data):
            try:
                msg = codec.decode(
                    data=bytes(data[pos:]), accept_crc_error=True
                )  # Set to False when only using FW>=5.4.0
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Decoded incoming UART message: {msg}")
                self.__handle_incoming_message(msg)
                pos += msg.length
            except BufferError as e:
                # BufferError is sort of OK as we just need to aggregate the data for now?
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Saving {len(data[pos:])} bytes for later parsing due to {e!r}.")
                self.saved_data = data[pos:]
                break
            except CrcError as e:
                (msgtype, msglen) = codec.Message.get_meta(bytes(data[pos:]))
                logger.warning(
                    f"CRC error {e!r} at position {pos} for message type {hex(msgtype)} with length {msglen} in Data={data.hex()}"
                )
                pos += msglen  # Skip entire packet to resync, assuming fault is NOT in the length field!
                continue
            except Exception as e:
                (msgtype, msglen) = codec.Message.get_meta(bytes(data[pos:]))
                logger.warning(
                    f"Receive error in on_uart_tx_data(): {e!r} at position {pos} of {len(data)} in Data={data.hex()}"
                )
                logger.warning("".join(traceback.format_exception(Exception, e, e.__traceback__)))
                pos += msglen  # Skip message length to keep sync if message code was just unknown
                continue

    def on_ble_message_received(self, uuid: BleakGATTCharacteristic, data: bytes) -> None:
        """Callback invoked when a new BLE message is received.

        This is invoked by the BLE message listener.
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Received BLE message for uuid {uuid}: {data.hex()}")
        self.__handle_ble_message(uuid=uuid.uuid, data=data)

    def __handle_incoming_message(self, msg: codec.Message) -> None:
        if msg.msg_type < 0x80:
            self.__handle_message(msg)
        else:
            self.__handle_response_message(msg)

    def __handle_message(self, msg: codec.Message) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Handling new incoming message: {msg}")
        with self.__message_listeners_lock:
            for listener in self.__message_listeners:
                self.__message_listener_executor.submit(_MessageReader.__notify_message_listener, listener, msg)

    @staticmethod
    def __notify_message_listener(listener: MessageListener, msg: codec.Message) -> None:
        try:
            listener.message_received(msg)
        except Exception as e:
            logger.warning(f"Error notifying listener: {e!s}", exc_info=True)

    def add_message_listener(self, listener: MessageListener) -> None:
        with self.__message_listeners_lock:
            self.__message_listeners.add(listener)

    def discard_message_listener(self, listener: MessageListener) -> None:
        with self.__message_listeners_lock:
            self.__message_listeners.discard(listener)

    def add_response_message_listener(self, listener: ResponseMessageListener) -> None:
        with self.__response_message_listeners_lock:
            self.__response_message_listeners.add(listener)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"{listener!r} was added to response message listener set!")

    def discard_response_message_listener(self, listener: ResponseMessageListener) -> None:
        with self.__response_message_listeners_lock:
            self.__response_message_listeners.discard(listener)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"{listener!r} was removed from response message listener set!")

    def add_ble_message_listener(self, listener: BleMessageListener) -> None:
        with self.__ble_message_listeners_lock:
            self.__ble_message_listeners.add(listener)

    def discard_ble_message_listener(self, listener: BleMessageListener) -> None:
        with self.__ble_message_listeners_lock:
            self.__ble_message_listeners.discard(listener)

    def __handle_response_message(self, msg: codec.Message) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Handling new response message: {msg}")
        with self.__response_message_listeners_lock:
            for listener in self.__response_message_listeners:
                _MessageReader.__notify_rsp_message_listener(listener, msg)

    @staticmethod
    def __notify_rsp_message_listener(listener: ResponseMessageListener, msg: codec.Message) -> None:
        try:
            listener.response_message_received(msg)
        except Exception as e:
            logger.warning(f"Error notifying listener: {e!s}", exc_info=True)

    def __handle_ble_message(self, uuid: str, data: bytes) -> None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Handling new BLE message. UUID: {uuid}, data: {data.hex()}")
        with self.__ble_message_listeners_lock:
            for listener in self.__ble_message_listeners:
                self.__ble_message_listener_executor.submit(
                    _MessageReader.__notify_ble_message_listener, listener, uuid, data
                )

    @staticmethod
    def __notify_ble_message_listener(listener: BleMessageListener, uuid: str, data: bytes) -> None:
        try:
            listener.ble_message_received(uuid, data)
        except Exception as e:
            logger.warning(f"Error notifying ble listener: {e!s}", exc_info=True)
