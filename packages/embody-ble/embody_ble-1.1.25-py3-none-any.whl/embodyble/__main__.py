"""Default execution entry point if running the package via python -m."""

import sys

from . import cli


def main():
    """Run cli from script entry point."""
    cli.main()


if __name__ == "__main__":
    sys.exit(main())
