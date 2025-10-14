from datetime import timedelta
from pathlib import Path
from typing import Self

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RotationConfig(BaseModel):
    """
    Configuration for proxy rotation behavior.

    Either provide a list of proxy URLs directly, or a subscription URL to fetch them.
    If both are provided, an error will be raised.
    """

    proxies: list[str] | None = Field(
        default=None,
        description="Direct list of proxy URLs (vmess://...). Mutually exclusive with subscription_url.",
    )
    subscription_url: HttpUrl | None = Field(
        default=None,
        description="URL to fetch proxy subscription. Mutually exclusive with proxies.",
    )
    subscription_update_interval: timedelta = Field(
        default=timedelta(hours=24),
        description="How often to refresh subscription data.",
    )
    enable_shuffling: bool = Field(
        default=True,
        description="Whether to shuffle available proxies before each complete rotation.",
    )

    @model_validator(mode="after")
    def validate_proxy_source(self) -> Self:
        """Ensure exactly one proxy source is provided."""
        if self.proxies is not None and self.subscription_url is not None:
            raise ValueError(
                "Cannot specify both 'proxies' and 'subscription_url'. Choose one."
            )
        if self.proxies is None and self.subscription_url is None:
            raise ValueError("Must specify either 'proxies' or 'subscription_url'.")
        return self

    @field_validator("proxies", mode="after")
    @classmethod
    def validate_proxies_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """Ensure proxies list is not empty if provided."""
        if v is not None and len(v) == 0:
            raise ValueError("Proxies list cannot be empty.")
        return v


class ConnectionTestConfig(BaseModel):
    """
    Configuration for testing proxy connectivity and performance.
    """

    url: HttpUrl = Field(
        default=HttpUrl("https://httpbin.org/"),
        description="URL to test proxy connectivity against.",
    )
    timeout: float = Field(
        default=10.0,
        gt=0,
        description="Timeout in seconds for connection tests.",
    )
    interval: timedelta | None = Field(
        default=timedelta(hours=1),
        description="How often to re-test proxies. None disables periodic testing.",
    )
    max_parallel_connections: int = Field(
        default=10,
        ge=1,
        description="Maximum total parallel connections for test client.",
    )
    retries: int = Field(
        default=2,
        ge=0,
        description="Number of retry attempts for failed connections.",
    )


class HeadersConfig(BaseModel):
    """
    Configuration for HTTP headers and User-Agent rotation.
    """

    rotate_user_agent: bool = Field(
        default=True,
        description="Whether to rotate User-Agent headers with each proxy.",
    )
    user_agents_url: HttpUrl | None = Field(
        default=HttpUrl(
            "https://cdn.jsdelivr.net/gh/microlinkhq/top-user-agents@master/src/desktop.json"
        ),
        description="URL to fetch User-Agent list. Mutually exclusive with user_agents_list.",
    )
    user_agents_list: list[str] | None = Field(
        default=None,
        description="Fixed list of User-Agents. Mutually exclusive with user_agents_url.",
    )
    default_values: dict[str, str] = Field(
        default_factory=lambda: {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
        },
        description="Default headers to include with requests.",
    )

    @model_validator(mode="after")
    def validate_user_agent_source(self) -> Self:
        """Ensure user agent configuration is valid."""
        if not self.rotate_user_agent:
            return self

        if self.user_agents_url is not None and self.user_agents_list is not None:
            raise ValueError(
                "Cannot specify both 'user_agents_url' and 'user_agents_list'. Choose one."
            )
        if self.user_agents_url is None and self.user_agents_list is None:
            raise ValueError(
                "Must specify either 'user_agents_url' or 'user_agents_list' when rotate_user_agent is enabled."
            )
        return self

    @field_validator("user_agents_list")
    @classmethod
    def validate_user_agents_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """Ensure user agents list is not empty if provided."""
        if v is not None and len(v) == 0:
            raise ValueError("User agents list cannot be empty.")
        return v


class XrayConfig(BaseModel):
    """
    Configuration for Xray proxy process management.
    """

    binary_path: str = Field(
        default="xray",
        description="Path to Xray binary executable.",
    )
    max_port_attempts: int = Field(
        default=100,
        gt=0,
        description="Maximum attempts to find a free local port.",
    )
    port_range_start: int = Field(
        default=1024,
        ge=1024,
        lt=65535,
        description="Starting port number for allocation.",
    )
    port_range_end: int = Field(
        default=65535,
        ge=1024,
        le=65535,
        description="Ending port number for allocation.",
    )
    init_wait_seconds: float = Field(
        default=2.0,
        gt=0,
        description="Seconds to wait for Xray process initialization.",
    )
    shutdown_timeout: float = Field(
        default=5.0,
        gt=0,
        description="Timeout in seconds for graceful Xray shutdown.",
    )

    @model_validator(mode="after")
    def validate_port_range(self) -> Self:
        """Ensure port range is valid."""
        if self.port_range_start >= self.port_range_end:
            raise ValueError(
                f"port_range_start ({self.port_range_start}) must be less than "
                f"port_range_end ({self.port_range_end})."
            )
        return self


class DelayConfig(BaseModel):
    """
    Configuration for request delays with jitter to avoid rate limiting.
    """

    enabled: bool = Field(
        default=False,
        description="Whether to add delays between rotations.",
    )
    base_delay: float = Field(
        default=1.0,
        ge=0,
        description="Base delay in seconds between rotations.",
    )
    jitter: float = Field(
        default=0.1,
        ge=0,
        le=1,
        description=(
            "Proportional jitter [0-1]. Delay will be random between base*(1-jitter)"
            " and base*(1+jitter). Pass 0.0 for no jitter, and 1 for ±100% of base delay"
        ),
    )
    max_delay: float | None = Field(
        default=None,
        gt=0,
        description="Maximum delay in seconds. None means no maximum.",
    )
    min_delay: float = Field(
        default=0.0,
        ge=0,
        description="Minimum delay in seconds.",
    )

    @model_validator(mode="after")
    def validate_delay_bounds(self) -> Self:
        """Ensure delay bounds are valid."""
        if self.max_delay is not None and self.min_delay >= self.max_delay:
            raise ValueError(
                f"min_delay ({self.min_delay}) must be less than max_delay ({self.max_delay})."
            )

        # Ensure base delay is within bounds if specified
        if self.enabled:
            lower_bound = self.base_delay * (1 - self.jitter)
            upper_bound = self.base_delay * (1 + self.jitter)

            if upper_bound < self.min_delay:
                raise ValueError(
                    f"base_delay with jitter (max {upper_bound:.2f}s) cannot satisfy "
                    f"min_delay ({self.min_delay}s)."
                )
            if self.max_delay is not None and lower_bound > self.max_delay:
                raise ValueError(
                    f"base_delay with jitter (min {lower_bound:.2f}s) cannot satisfy "
                    f"max_delay ({self.max_delay}s)."
                )

        return self


class ProxyRotatorConfig(BaseSettings):
    """
    Main configuration class that can be loaded from environment variables,
    configuration files, or direct instantiation.

    For nested models, it's recommended to use direct instantiation or .env files
    rather than environment variables.

    Simple fields can use environment variables:
      PROXY_ROTATOR__DATA_DIR=/custom/path
      PROXY_ROTATOR__XRAY__BINARY_PATH=/usr/local/bin/xray
    """

    model_config = SettingsConfigDict(
        env_prefix="PROXY_ROTATOR_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    data_dir: Path = Field(
        default=Path.cwd() / ".proxy_rotator",
        description="Directory to store proxy data, configs, and test results.",
    )
    rotation_config: RotationConfig
    connection_test: ConnectionTestConfig = Field(default_factory=ConnectionTestConfig)
    headers: HeadersConfig = Field(default_factory=HeadersConfig)
    xray: XrayConfig = Field(default_factory=XrayConfig)
    delay: DelayConfig = Field(default_factory=DelayConfig)

    @model_validator(mode="after")
    def ensure_data_dir_exists(self) -> Self:
        """Create data directory if it doesn't exist."""
        if self.data_dir.is_file():
            raise ValueError(f"Data dir must be a directory. Got {self.data_dir}")

        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self
