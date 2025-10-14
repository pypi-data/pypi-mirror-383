"""Listener interfaces that can be subscribed to by clients."""

from abc import ABC
from abc import abstractmethod

from embodycodec import codec


class MessageListener(ABC):
    """Listener interface for being notified of incoming messages."""

    @abstractmethod
    def message_received(self, msg: codec.Message) -> None:
        """Process received message"""


class BleMessageListener(ABC):
    """Listener interface for being notified of incoming BLE messages."""

    @abstractmethod
    def ble_message_received(self, uuid: str, data: bytes) -> None:
        """Process received message"""


class ResponseMessageListener(ABC):
    """Listener interface for being notified of incoming response messages."""

    @abstractmethod
    def response_message_received(self, msg: codec.Message) -> None:
        """Process received response message"""


class ConnectionListener(ABC):
    """Listener interface for being notified of connection changes."""

    @abstractmethod
    def on_connected(self, connected: bool) -> None:
        """Process connection status."""
        pass
