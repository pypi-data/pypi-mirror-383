"""
Exception hierarchy for proxy-rotator.

All exceptions inherit from ProxyRotatorError to allow catching all
library-specific errors with a single except clause.
"""


class ProxyRotatorError(Exception):
    """Base exception for all proxy-rotator errors."""

    pass


class NetworkError(ProxyRotatorError):
    """Raised when network operations fail."""

    pass


class ProcessError(ProxyRotatorError):
    """Raised when proxy process management fails."""

    pass


class PortAllocationError(ProcessError):
    """Raised when unable to allocate a free port for proxy."""

    pass


class ValidationError(ProxyRotatorError):
    """Raised when proxy data validation fails."""

    pass


class SubscriptionError(ProxyRotatorError):
    """Raised when fetching or parsing subscription data fails."""

    pass


class ProtocolError(ProxyRotatorError):
    """Raised when proxy protocol parsing or handling fails."""

    pass
