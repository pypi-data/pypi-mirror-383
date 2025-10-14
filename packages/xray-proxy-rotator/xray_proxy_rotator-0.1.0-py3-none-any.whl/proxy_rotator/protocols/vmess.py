"""
VMESS protocol parser and Xray configuration generator.

This module handles parsing of vmess:// URLs and generation of Xray-core
configuration files for VMESS proxies.
"""

import base64
import json
from typing import Any

from proxy_rotator.errors import ProtocolError, ValidationError
from proxy_rotator.models import VmessProxy, XrayConfig


def _fix_base64_padding(s: str) -> str:
    """
    Add padding to base64 string if needed.

    Base64 strings must be multiples of 4 characters. This function
    adds the necessary '=' padding characters.

    Args:
        s: Base64 string that may be missing padding

    Returns:
        Properly padded base64 string
    """
    missing_padding = len(s) % 4
    if missing_padding:
        s += "=" * (4 - missing_padding)
    return s


def parse_vmess_link(link: str) -> VmessProxy:
    """
    Parse a vmess:// URL into a validated proxy configuration.

    VMESS links follow the format: vmess://<base64-encoded-json>

    Args:
        link: VMESS URL string (vmess://...)

    Returns:
        Validated VmessProxy instance

    Raises:
        ProtocolError: If link format is invalid
        ValidationError: If required fields are missing or invalid
    """
    if not link or not isinstance(link, str):
        raise ProtocolError("VMESS link must be a non-empty string")

    if not link.startswith("vmess://"):
        raise ProtocolError("Invalid VMESS link format: must start with 'vmess://'")

    # Extract base64 payload
    try:
        payload = link.split("://", 1)[1]
    except IndexError:
        raise ProtocolError("VMESS link is missing payload after 'vmess://'") from None

    # Decode base64
    try:
        payload = _fix_base64_padding(payload)
        decoded_bytes = base64.b64decode(payload)
        decoded_str = decoded_bytes.decode("utf-8")
    except Exception as e:
        raise ProtocolError(f"Failed to decode VMESS link: {e}") from e

    # Parse JSON
    try:
        data = json.loads(decoded_str)
    except json.JSONDecodeError as e:
        raise ProtocolError(f"Invalid JSON in VMESS link: {e}") from e

    # Validate with Pydantic
    try:
        return VmessProxy(**data)
    except Exception as e:
        raise ValidationError(f"Invalid VMESS configuration: {e}") from e


def create_xray_config(proxy: VmessProxy, local_port: int) -> XrayConfig:
    """
    Generate Xray-core configuration for a VMESS proxy.

    Creates a complete Xray configuration that sets up a local HTTP proxy
    on the specified port, routing traffic through the VMESS proxy.

    Args:
        proxy: Validated VMESS proxy configuration
        local_port: Local port to bind the HTTP proxy to

    Returns:
        Complete Xray configuration ready for use

    Raises:
        ValidationError: If configuration generation fails
    """
    # Build stream settings
    stream_settings: dict[str, Any] = {
        "network": proxy.net,
        "security": proxy.tls,
    }

    # Add network-specific settings
    if proxy.net == "tcp" and proxy.type == "http":
        stream_settings["tcpSettings"] = {
            "header": {
                "type": "http",
                "request": {
                    "path": [proxy.path],
                    "headers": {"Host": [proxy.host]},
                },
            }
        }
    elif proxy.net == "ws":
        stream_settings["wsSettings"] = {
            "path": proxy.path,
            "headers": {"Host": proxy.host},
        }

    # Build outbound
    vmess_outbound = {
        "protocol": "vmess",
        "settings": {
            "vnext": [
                {
                    "address": proxy.add,
                    "port": proxy.port,
                    "users": [
                        {
                            "id": proxy.id,
                            "alterId": proxy.aid,
                            "security": proxy.scy,
                        }
                    ],
                }
            ]
        },
        "streamSettings": stream_settings,
    }

    direct_outbound = {
        "protocol": "freedom",
        "tag": "direct",
        "settings": {},
    }

    # Build inbound
    http_inbound = {
        "port": local_port,
        "protocol": "http",
        "settings": {"allowTransparent": False},
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
    }
    # socks_inbound = {
    #     "port": local_port,
    #     "protocol": "socks",
    #     "settings": {"auth": "noauth", "udp": True, "ip": "127.0.0.1"},
    #     "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
    # }

    # Complete configuration
    try:
        config = XrayConfig(
            log={"loglevel": "warning"},
            inbounds=[http_inbound],
            outbounds=[vmess_outbound, direct_outbound],
            routing={
                "domainStrategy": "IPIfNonMatch",
                "rules": [
                    {"type": "field", "ip": ["geoip:private"], "outboundTag": "direct"}
                ],
            },
        )
        return config
    except Exception as e:
        raise ValidationError(f"Failed to create Xray configuration: {e}") from e
