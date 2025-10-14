"""
Data models for proxy-rotator.
This module contains Pydantic models for proxy configurations.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class VmessProxy(BaseModel):
    """
    Validated VMESS proxy configuration.

    Represents a parsed and validated VMESS proxy with all necessary
    fields for connecting through Xray-core.
    """

    protocol: Literal["vmess"] = "vmess"
    add: str = Field(..., description="Server address (IP or domain)")
    port: int = Field(..., ge=1, le=65535, description="Server port")
    id: str = Field(..., description="User UUID")
    aid: int = Field(default=0, ge=0, description="Alter ID")
    scy: str = Field(default="auto", description="Security method")
    net: str = Field(default="tcp", description="Network type (tcp, ws, etc.)")
    type: str = Field(default="none", description="Header type")
    host: str = Field(default="", description="Host header")
    path: str = Field(default="/", description="Path (for WebSocket)")
    tls: str = Field(default="none", description="TLS setting")
    ps: str = Field(default="", description="Proxy name/description")
    v: str = Field(default="2", description="VMESS version")

    @field_validator("add")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """
        Validate that a proxy address is usable.
        Filters out invalid, empty, or known problematic addresses.
        """
        error = ValueError(f"Invalid or unusable proxy address: {v}")
        if not v:
            raise error

        v = v.strip()

        if not v:
            raise error

        # Filter out Cloudflare DNS (often used as placeholder)
        if "1.1.1.1" in v:
            raise error

        # Addresses shouldn't contain spaces
        if " " in v:
            raise error

        return v.strip()

    @property
    def name(self) -> str:
        """Return a human-readable name for this proxy."""
        return self.ps or f"{self.add}:{self.port}"


class XrayConfig(BaseModel):
    """
    Complete Xray-core configuration.

    This model represents a full Xray configuration ready to be
    serialized to JSON and used with xray-core.
    """

    log: dict[str, Any]
    inbounds: list[dict[str, Any]]
    outbounds: list[dict[str, Any]]
    routing: dict[str, Any]
