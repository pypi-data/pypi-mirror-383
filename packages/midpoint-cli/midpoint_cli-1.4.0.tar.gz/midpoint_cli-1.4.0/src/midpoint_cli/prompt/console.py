import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme

from midpoint_cli.client import MidpointCommunicationObserver
from midpoint_cli.client.progress import ProgressMonitor


def is_tty() -> bool:
    """Check if stdout is connected to a TTY (terminal)."""
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


# Rich Console singleton
_console_instance: Optional[RichConsole] = None


def get_console() -> RichConsole:
    """Get or create the global Rich Console instance."""
    global _console_instance
    if _console_instance is None:
        custom_theme = Theme(
            {
                'info': 'cyan',
                'warning': 'yellow',
                'error': 'bold red',
                'success': 'bold green',
                'oid': 'blue',
                'name': 'bright_cyan',
                'status_running': 'yellow',
                'status_success': 'green',
                'status_error': 'red',
            }
        )
        _console_instance = RichConsole(theme=custom_theme, highlight=False)
    return _console_instance


def print_error(message: str) -> None:
    """Print an error message with rich formatting."""
    console = get_console()
    console.print(f'[error]Error:[/error] {message}')


def print_success(message: str) -> None:
    """Print a success message with rich formatting."""
    console = get_console()
    console.print(f'[success]✓[/success] {message}')


def print_info(message: str) -> None:
    """Print an info message with rich formatting."""
    console = get_console()
    console.print(f'[info]ℹ[/info] {message}')


def print_warning(message: str) -> None:
    """Print a warning message with rich formatting."""
    console = get_console()
    console.print(f'[warning]⚠[/warning] {message}')


def print_xml(xml_text: str, line_numbers: bool = False) -> None:
    """Print XML with syntax highlighting."""
    console = get_console()
    if is_tty():
        syntax = Syntax(xml_text, 'xml', theme='monokai', line_numbers=line_numbers)
        console.print(syntax)
    else:
        console.print(xml_text)


def create_table(title: Optional[str] = None, show_header: bool = True) -> Table:
    """Create a Rich table with consistent styling."""
    table = Table(title=title, show_header=show_header, header_style='bold cyan', border_style='blue')
    return table


def print_table_from_dicts(data: list[dict[str, Any]], title: Optional[str] = None) -> None:
    """Print a table from a list of dictionaries."""
    if not data:
        print_info('No data to display')
        return

    console = get_console()
    table = create_table(title=title)

    # Add columns from first dict
    headers = list(data[0].keys())
    for header in headers:
        table.add_column(header, style='white')

    # Add rows
    for row in data:
        table.add_row(*[str(row.get(h, '')) for h in headers])

    console.print(table)


def print_panel(content: str, title: Optional[str] = None, style: str = 'cyan') -> None:
    """Print content in a rich panel."""
    console = get_console()
    panel = Panel(content, title=title, border_style=style)
    console.print(panel)


class Spinner:
    """Reusable animated spinner using Rich for TTY/console output."""

    def __init__(self):
        self._console = get_console()
        self._status = None
        self._message = ''

    def start(self, message_callback: Callable[[str], str]):
        """
        Start spinner animation using Rich status.

        Args:
            message_callback: Function that receives spinner frame and returns full message to display
        """
        # Rich handles the spinner frame internally, so we just need the base message
        self._message = message_callback('')
        if is_tty():
            self._status = self._console.status(self._message, spinner='dots')
            self._status.__enter__()
        else:
            # For non-TTY, just print the message
            print(self._message, end='', flush=True)

    def stop(self, clear_length: int = 80):
        """
        Stop the spinner and clear the line.

        Args:
            clear_length: Number of characters to clear (default 80)
        """
        if self._status:
            self._status.__exit__(None, None, None)
            self._status = None
        elif not is_tty():
            # Clear the non-TTY message
            print('\r' + ' ' * clear_length + '\r', end='', flush=True)


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
    """Animated progress monitor using Rich Progress for TTY/console output."""

    def __init__(self):
        self._progress_value = 0
        self._progress = None
        self._task = None
        self._console = get_console()

    def update(self, progress: int) -> None:
        self._progress_value = progress
        if self._progress and self._task is not None:
            self._progress.update(self._task, completed=progress)

    def __enter__(self):
        if is_tty():
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn('[progress.description]{task.description}'),
                BarColumn(),
                TextColumn('[progress.percentage]{task.completed}'),
                TimeElapsedColumn(),
                console=self._console,
            )
            self._progress.__enter__()
            self._task = self._progress.add_task('Processing...', total=None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._progress:
            self._progress.__exit__(exc_type, exc_val, exc_tb)
        self._console.print(f'Total progress: {self._progress_value}')


# Backwards compatibility alias
AsciiProgressMonitor = DottedProgressMonitor
