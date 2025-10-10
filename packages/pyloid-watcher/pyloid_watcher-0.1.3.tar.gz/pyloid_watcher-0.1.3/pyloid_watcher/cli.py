import argparse
import sys
from pathlib import Path
from typing import NoReturn

from .watcher import Colors, PyloidWatcher


def main() -> NoReturn:
    """Main entry point for the Pyloid file watcher."""
    parser = argparse.ArgumentParser(
        description="Cross-platform Pyloid backend file watcher with auto-restart",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyloid-watcher                    # Watch current directory
  pyloid-watcher --path ./src      # Watch specific path
  pyloid-watcher --pattern "*.py"  # Specify file pattern
        """
    )

    parser.add_argument(
        "--path", "-p",
        type=str,
        default="src-pyloid",
        help="Directory path to watch (default: src-pyloid)"
    )

    parser.add_argument(
        "--pattern", "-t",
        type=str,
        default="*.py",
        help="File pattern to watch (default: *.py)"
    )

    parser.add_argument(
        "--command", "-c",
        type=str,
        default="uv run -p .venv ./src-pyloid/main.py",
        help="Command to restart on file changes"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    try:
        watcher = PyloidWatcher(
            watch_path=args.path,
            file_pattern=args.pattern,
            command=args.command,
            verbose=args.verbose
        )
        watcher.start()
    except KeyboardInterrupt:
        print(Colors.colorize("\n[STOP] Watcher stopped", Colors.GREEN))
        sys.exit(0)
    except Exception as e:
        print(Colors.colorize(f"[ERROR] {e}", Colors.RED))
        sys.exit(1)

if __name__ == "__main__":
    main()