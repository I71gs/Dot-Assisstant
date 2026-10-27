"""
main.py — DOT Assistant entry point

Usage:
    python main.py
"""

from __future__ import annotations

import sys


def main() -> None:
    from core.assistant import Assistant

    assistant = Assistant()
    assistant.initialize()
    assistant.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
