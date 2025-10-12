"""Protocol definitions for file operation detectors."""

from __future__ import annotations

from typing import Protocol

from provide.foundation.file.operations.types import FileEvent, FileOperation


class DetectorFunc(Protocol):
    """Protocol for file operation detector functions.

    A detector function analyzes a list of file events and attempts to
    identify a specific file operation pattern (atomic save, batch update, etc.).

    Returns None if the pattern is not detected, or a FileOperation with
    confidence score if the pattern matches.
    """

    def __call__(self, events: list[FileEvent]) -> FileOperation | None:
        """Detect file operation pattern from events.

        Args:
            events: List of file events to analyze

        Returns:
            FileOperation if pattern detected, None otherwise
        """
        ...


__all__ = ["DetectorFunc"]
