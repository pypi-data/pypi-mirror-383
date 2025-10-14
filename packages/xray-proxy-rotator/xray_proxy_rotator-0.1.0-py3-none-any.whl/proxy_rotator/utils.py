"""
Utility functions for proxy-rotator.

This module provides helper functions for port allocation, file I/O,
and other common operations.
"""

import json
import random
import socket
from pathlib import Path
from typing import Any

from .errors import PortAllocationError


def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if a specific port is available for binding.

    Args:
        port: Port number to check
        host: Host address to check (default: localhost)

    Returns:
        True if port is free, False if in use
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_free_port(
    start: int = 1024,
    end: int = 65535,
    max_attempts: int = 100,
) -> int:
    """
    Find a free port on localhost within the specified range.

    Args:
        start: Starting port number (inclusive)
        end: Ending port number (inclusive)
        max_attempts: Maximum number of ports to try

    Returns:
        A free port number

    Raises:
        PortAllocationError: If no free port found after max_attempts
        ValueError: If port range is invalid
    """
    if start < 1 or end > 65535:
        raise ValueError(f"Port range must be between 1-65535, got {start}-{end}")

    if start >= end:
        raise ValueError(f"start ({start}) must be less than end ({end})")

    for _ in range(max_attempts):
        port = random.randint(start, end)
        if is_port_free(port):
            return port

    raise PortAllocationError(
        f"Could not find free port in range {start}-{end} after {max_attempts} attempts"
    )


def read_json_file(path: Path) -> Any:
    """
    Read and parse a JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, data: Any, indent: int = 2) -> None:
    """
    Write data to a JSON file with pretty formatting.

    Creates parent directories if they don't exist.

    Args:
        path: Path to write JSON file
        data: Data to serialize to JSON
        indent: Indentation level for pretty printing
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=indent, ensure_ascii=False), encoding="utf-8"
    )


def calculate_delay(
    base_delay: float,
    jitter: float = 0.0,
    min_delay: float = 0.0,
    max_delay: float | None = None,
) -> float:
    """
    Calculate delay with jitter for rate limiting.

    Applies proportional jitter to the base delay, then clamps to min/max bounds.

    Args:
        base_delay: Base delay in seconds
        jitter: Proportional jitter [0-1]. 0.1 means ±10% of base_delay
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds (None for no maximum)

    Returns:
        Calculated delay in seconds
    """
    if jitter < 0 or jitter > 1:
        raise ValueError(f"jitter must be between 0 and 1, got {jitter}")

    if base_delay < 0:
        raise ValueError(f"base_delay must be non-negative, got {base_delay}")

    # Calculate jittered delay
    jitter_amount = base_delay * jitter
    lower_bound = base_delay - jitter_amount
    upper_bound = base_delay + jitter_amount

    delay = random.uniform(lower_bound, upper_bound)

    # Apply min/max bounds
    delay = max(delay, min_delay)
    if max_delay is not None:
        delay = min(delay, max_delay)

    return delay
