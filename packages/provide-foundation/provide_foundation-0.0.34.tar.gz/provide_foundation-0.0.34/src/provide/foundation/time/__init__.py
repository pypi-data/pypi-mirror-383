from __future__ import annotations

from provide.foundation.time.core import (
    provide_now,
    provide_sleep,
    provide_time,
)

"""Production time utilities for Foundation.

Provides consistent time handling with Foundation integration,
better testability, and timezone awareness.
"""

__all__ = [
    "provide_now",
    "provide_sleep",
    "provide_time",
]
