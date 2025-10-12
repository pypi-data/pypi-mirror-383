from __future__ import annotations

from provide.foundation.errors import FoundationError

"""Custom exceptions for OpenObserve integration."""


class OpenObserveError(FoundationError):
    """Base exception for OpenObserve-related errors."""


class OpenObserveConnectionError(OpenObserveError):
    """Error connecting to OpenObserve API."""


class OpenObserveAuthenticationError(OpenObserveError):
    """Authentication failed with OpenObserve."""


class OpenObserveQueryError(OpenObserveError):
    """Error executing query in OpenObserve."""


class OpenObserveStreamingError(OpenObserveError):
    """Error during streaming operations."""


class OpenObserveConfigError(OpenObserveError):
    """Configuration error for OpenObserve."""
