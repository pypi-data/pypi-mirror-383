"""
Proxy Rotator - Async VMESS proxy rotation manager

A Python library for managing VMESS proxy rotation with automatic subscription
updates, connection testing, and user-agent rotation.
"""

from .config import (
    ConnectionTestConfig,
    DelayConfig,
    HeadersConfig,
    ProxyRotatorConfig,
    RotationConfig,
    XrayConfig,
)
from .errors import (
    NetworkError,
    PortAllocationError,
    ProcessError,
    ProtocolError,
    ProxyRotatorError,
    SubscriptionError,
    ValidationError,
)
from .models import VmessProxy
from .models import XrayConfig as XrayConfigModel
from .rotator import ProxyRotator

__version__ = "0.1.0"
__author__ = "Keyhan Kamyar"
__email__ = "keyhankamyar@gmail.com"

__all__ = [
    # Main class
    "ProxyRotator",
    # Configuration
    "ProxyRotatorConfig",
    "RotationConfig",
    "ConnectionTestConfig",
    "HeadersConfig",
    "XrayConfig",
    "DelayConfig",
    # Models
    "VmessProxy",
    "XrayConfigModel",
    # Errors
    "ProxyRotatorError",
    "NetworkError",
    "ProcessError",
    "PortAllocationError",
    "ValidationError",
    "SubscriptionError",
    "ProtocolError",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
]
