import sys
import threading
import time
from abc import ABC, abstractmethod
from typing import Callable

from midpoint_cli.client import MidpointCommunicationObserver
from midpoint_cli.client.progress import ProgressMonitor


def is_tty() -> bool:
    """Check if stdout is connected to a TTY (terminal)."""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


class Spinner:
    """Reusable animated spinner for TTY/console output."""

    def __init__(self):
        self._spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self._frame_index = 0
        self._spinner_thread = None
        self._stop_event = threading.Event()
        self._message_callback = None

    def start(self, message_callback: Callable[[str], str]):
        """
        Start spinner animation.

        Args:
            message_callback: Function that receives spinner frame and returns full message to display
        """
        self._message_callback = message_callback
        # Print initial message
        print(message_callback(self._spinner_frames[self._frame_index]), end='', flush=True)
        self._stop_event.clear()
        self._spinner_thread = threading.Thread(target=self._animate, daemon=True)
        self._spinner_thread.start()

    def _animate(self):
        """Background thread that continuously animates the spinner."""
        assert self._message_callback is not None
        while not self._stop_event.is_set():
            self._frame_index = (self._frame_index + 1) % len(self._spinner_frames)
            message = self._message_callback(self._spinner_frames[self._frame_index])
            print(f'\r{message}', end='', flush=True)
            time.sleep(0.1)

    def stop(self, clear_length: int = 80):
        """
        Stop the spinner and clear the line.

        Args:
            clear_length: Number of characters to clear (default 80)
        """
        self._stop_event.set()
        if self._spinner_thread:
            self._spinner_thread.join(timeout=1.0)
        print('\r' + ' ' * clear_length + '\r', end='', flush=True)
        self._frame_index = 0


class WaitingIndicator(ABC):
    """Abstract base class for waiting indicators."""

    @abstractmethod
    def start(self):
        """Start displaying the waiting indicator."""
        pass

    @abstractmethod
    def update(self):
        """Update the waiting indicator (called on each retry)."""
        pass

    @abstractmethod
    def stop(self):
        """Stop displaying the waiting indicator."""
        pass


class SpinnerWaitingIndicator(WaitingIndicator):
    """Animated spinner indicator for TTY/console output."""

    def __init__(self):
        self._spinner = Spinner()

    def start(self):
        """Start the animated spinner."""
        self._spinner.start(lambda frame: f'Waiting for http service {frame}')

    def update(self):
        """No-op: thread handles updates automatically."""
        pass

    def stop(self):
        """Stop the animated spinner and clear the line."""
        self._spinner.stop(clear_length=40)


class DottedWaitingIndicator(WaitingIndicator):
    """Classic dotted indicator for file redirection/non-TTY output."""

    def start(self):
        """Print initial waiting message."""
        print('Waiting for http service...', end='', flush=True)

    def update(self):
        """Print a dot on each update."""
        print('.', end='', flush=True)

    def stop(self):
        """Print newline to finish the line."""
        print('', flush=True)


class ConsoleDisplay(MidpointCommunicationObserver):
    def __init__(self):
        self._waiting = False
        # Detect if output is a TTY (console) or file redirection
        self._indicator = SpinnerWaitingIndicator() if is_tty() else DottedWaitingIndicator()

    def on_http_error(self):
        if not self._waiting:
            self._indicator.start()
            self._waiting = True
        else:
            self._indicator.update()

    def on_http_success(self):
        if self._waiting:
            self._indicator.stop()
            self._waiting = False

    def on_http_call(self):
        pass


# Progress Monitors


class DottedProgressMonitor(ProgressMonitor):
    """Dotted progress monitor for file redirection/non-TTY output."""

    def __init__(self, width=80, icon='.'):
        self._progress = 0
        self._width = width
        self._icon = icon

    def update(self, progress: int) -> None:
        while self._progress < progress:
            self.advance()

    def advance(self):
        if self._progress % self._width == 0:
            if self._progress > 0:
                print(f' {self._progress:7d}')

            print('Progress: ', end='', flush=True)

        print(self._icon, end='', flush=True)
        self._progress += 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print()
        print('Total progress:', self._progress)


class AnimatedProgressMonitor(ProgressMonitor):
    """Animated progress monitor with spinner for TTY/console output."""

    def __init__(self):
        self._progress = 0
        self._spinner = Spinner()
        self._started = False

    def update(self, progress: int) -> None:
        self._progress = progress
        if not self._started:
            self._spinner.start(lambda frame: f'Progress: {frame} {self._progress}')
            self._started = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._started:
            self._spinner.stop(clear_length=60)
        print(f'Total progress: {self._progress}')


# Backwards compatibility alias
AsciiProgressMonitor = DottedProgressMonitor
