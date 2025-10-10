import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"

    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Apply color to text if terminal supports it."""
        if not sys.stdout.isatty():
            return text  # No colors for non-interactive terminals
        return f"{color}{text}{Colors.RESET}"


class PyloidWatcher(FileSystemEventHandler):
    """Cross-platform file watcher with auto-restart functionality for Pyloid applications."""

    def __init__(
        self,
        watch_path: str = "src-pyloid",
        file_pattern: str = "*.py",
        command: Optional[str] = None,
        verbose: bool = False
    ) -> None:
        self.watch_path = Path(watch_path)
        self.file_pattern = file_pattern
        self.command = command or "uv run -p .venv ./src-pyloid/main.py"
        self.verbose = verbose
        self.process: Optional[subprocess.Popen[str]] = None
        self.observer: Optional[Observer] = None

        if not self.watch_path.exists():
            raise ValueError(f"Watch path does not exist: {self.watch_path}")

        # Start initial process
        self.restart()

    def log(self, message: str, level: str = "info") -> None:
        """Log message with color coding and optional verbose prefix."""
        # Define color mapping for different log levels
        colors = {
            "info": Colors.BLUE,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error": Colors.RED,
            "process": Colors.CYAN,
            "file": Colors.MAGENTA,
        }

        color = colors.get(level, Colors.WHITE)
        prefix = Colors.colorize("[WATCHER]", Colors.BOLD + Colors.CYAN)

        if self.verbose:
            colored_message = Colors.colorize(message, color)
            print(f"{prefix} {colored_message}")
        else:
            print(Colors.colorize(message, color))

    def should_restart(self, event: FileSystemEvent) -> bool:
        """Determine if process should restart based on file event."""
        # Check if file matches pattern
        if not event.src_path.endswith(self.file_pattern.lstrip("*")):
            return False

        # Check if file is within watch directory
        try:
            Path(event.src_path).relative_to(self.watch_path)
            return True
        except ValueError:
            return False

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if self.should_restart(event):
            self.log(f"📁 File change detected: {event.src_path}", "file")
            self.restart()

    def restart(self) -> None:
        """Restart the watched process."""
        # Terminate existing process
        if self.process and self.process.poll() is None:
            self.log("🔄 Terminating existing process...", "process")
            self._terminate_process(self.process)

        # Start new process
        self.log("🚀 Starting Pyloid application...", "process")
        try:
            self.process = subprocess.Popen(
                self.command.split(),
                cwd=os.getcwd()
            )
        except Exception as e:
            self.log(f"❌ Failed to start process: {e}", "error")

    def _terminate_process(self, process: subprocess.Popen[str]) -> None:
        """Cross-platform process termination."""
        if platform.system() == "Windows":
            self._terminate_windows_process(process)
        else:
            self._terminate_unix_process(process)

    def _terminate_windows_process(self, process: subprocess.Popen[str]) -> None:
        """Terminate process on Windows."""
        try:
            self.log(f"🔪 Force terminating PID {process.pid}...", "warning")
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                timeout=3,
                capture_output=True,
                check=True
            )
            self.log("✅ Process terminated successfully", "success")
        except subprocess.CalledProcessError:
            self.log("⚠️  taskkill failed, trying process.kill()...", "warning")
            self._force_kill_process(process)
        except subprocess.TimeoutExpired:
            self.log("⏰ taskkill timeout, trying process.kill()...", "warning")
            self._force_kill_process(process)

    def _terminate_unix_process(self, process: subprocess.Popen[str]) -> None:
        """Terminate process on Unix-like systems."""
        self.log(f"🔪 Terminating Unix process PID {process.pid}...", "warning")
        process.terminate()
        try:
            process.wait(timeout=3)
            self.log("✅ Process terminated successfully", "success")
        except subprocess.TimeoutExpired:
            self.log("⚠️  SIGTERM failed, using SIGKILL...", "warning")
            process.kill()
            process.wait(timeout=2)
            self.log("💀 Process force killed with SIGKILL", "error")

    def _force_kill_process(self, process: subprocess.Popen[str]) -> None:
        """Force kill a process as last resort."""
        try:
            process.kill()
            process.wait(timeout=2)
            self.log("✅ Process killed successfully", "success")
        except Exception as e:
            self.log(f"❌ Failed to kill process: {e}", "error")

    def start(self) -> None:
        """Start the file watcher."""
        self.observer = Observer()
        self.observer.schedule(self, path=str(self.watch_path), recursive=True)
        self.observer.start()

        def cleanup(signum: int, frame) -> None:
            """Cleanup function for graceful shutdown."""
            self.log(f"🛑 Received signal: {signum}", "warning")
            if self.observer:
                self.observer.stop()
            if self.process and self.process.poll() is None:
                self._terminate_process(self.process)
            if self.observer:
                self.observer.join()
            self.log("👋 Pyloid watcher stopped", "info")
            sys.exit(0)

        # Register signal handlers
        if platform.system() == "Windows":
            signal.signal(signal.SIGINT, cleanup)
            signal.signal(signal.SIGBREAK, cleanup)  # type: ignore
        else:
            signal.signal(signal.SIGTERM, cleanup)
            signal.signal(signal.SIGINT, cleanup)

        self.log(f"🎯 Pyloid watcher started (path: {self.watch_path}, pattern: {self.file_pattern})", "success")
        self.log("💡 Press Ctrl+C to stop", "info")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            cleanup(signal.SIGINT, None)