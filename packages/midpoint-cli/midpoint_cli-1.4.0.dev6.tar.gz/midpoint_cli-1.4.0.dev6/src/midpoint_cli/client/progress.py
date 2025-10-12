from abc import ABC, abstractmethod


class ProgressMonitor(ABC):
    """Abstract base class for task progress monitors."""

    @abstractmethod
    def update(self, progress: int) -> None:
        """Update the progress display with the current progress value."""
        pass

    @abstractmethod
    def __enter__(self):
        """Enter context manager."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass


class NopProgressMonitor(ProgressMonitor):
    """No-op implementation."""

    def update(self, progress: int) -> None:
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
