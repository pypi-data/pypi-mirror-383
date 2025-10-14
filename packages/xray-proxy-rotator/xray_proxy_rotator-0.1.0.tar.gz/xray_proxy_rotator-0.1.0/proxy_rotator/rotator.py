"""
Main proxy rotation manager for proxy-rotator.

This module provides the ProxyRotator class which manages a pool of VMESS proxies,
handles rotation, subscription updates, and connection testing.
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Self

import httpx

from .config import ProxyRotatorConfig
from .errors import NetworkError, PortAllocationError, SubscriptionError
from .models import VmessProxy
from .process import XrayProcess
from .protocols import create_xray_config
from .subscription import fetch_and_parse_subscription, parse_proxy_list
from .user_agents import UserAgentManager
from .utils import calculate_delay, find_free_port, read_json_file, write_json_file


class ProxyRotator:
    """
    VMESS proxy rotation manager.

    Manages a pool of VMESS proxies with automatic rotation, subscription updates,
    and connection testing. Can be used as a context manager or with explicit
    start/stop calls.

    Example:
        ```python
        config = ProxyRotatorConfig(
            rotation_config=RotationConfig(subscription_url="https://..."),
        )
        rotator = ProxyRotator(config)

        async with rotator:
            async with httpx.AsyncClient(
                proxy=rotator.proxy_url,
                headers=rotator.headers
            ) as client:
                response = await client.get("https://example.com")
        ```
    """

    # Global lock to prevent multiple simultaneous proxy sessions
    _GLOBAL_LOCK = asyncio.Lock()

    def __init__(
        self,
        config: ProxyRotatorConfig,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize the proxy rotator.

        Args:
            config: Configuration for proxy rotation behavior
            logger: Optional logger instance
        """
        self._config = config
        self._logger = logger or logging.getLogger(__name__)

        # Setup directory structure
        self._data_dir = config.data_dir
        self._proxies_file = self._data_dir / "proxies.json"
        self._metadata_file = self._data_dir / "metadata.json"
        self._test_results_file = self._data_dir / "test_results.json"
        self._xray_config_file = self._data_dir / "xray_config.json"

        # Initialize user agent manager if rotation enabled
        if self._config.headers.rotate_user_agent:
            self._user_agent_manager = UserAgentManager(
                storage_path=self._data_dir / "user_agents.json",
                fetch_url=str(self._config.headers.user_agents_url)
                if self._config.headers.user_agents_url
                else None,
                user_agents_list=self._config.headers.user_agents_list,
                logger=self._logger,
            )
        else:
            self._user_agent_manager = None

        # Runtime state
        self._process: XrayProcess | None = None
        self._current_proxy: VmessProxy | None = None
        self._current_user_agent: str | None = None
        self._rotation_queue: list[int] = []  # Indices of valid proxies

        self._lock = ProxyRotator._GLOBAL_LOCK

        self._logger.info("ProxyRotator initialized")

    @property
    def proxy_url(self) -> str | None:
        """Current proxy URL for use with HTTP clients."""
        if self._process and self._process.is_running:
            return f"http://127.0.0.1:{self._process.port}"
        return None

    @property
    def headers(self) -> dict[str, str] | None:
        """HTTP headers with current User-Agent if rotation is enabled."""
        if not self._config.headers.rotate_user_agent:
            return self._config.headers.default_values.copy()

        if self._current_user_agent:
            headers = self._config.headers.default_values.copy()
            headers["User-Agent"] = self._current_user_agent
            return headers

        return None

    # ==================== Subscription Management ====================

    async def _update_subscription(self) -> None:
        """Update subscription data and user agents from remote sources or config."""
        self._logger.info("Updating subscription data")

        # Fetch or use configured proxies
        if self._config.rotation_config.subscription_url:
            proxies = await fetch_and_parse_subscription(
                str(self._config.rotation_config.subscription_url), self._logger
            )
        else:
            # Use direct proxy list from config
            if self._config.rotation_config.proxies is None:
                raise SubscriptionError("No proxies configured")
            proxies = parse_proxy_list(
                self._config.rotation_config.proxies, self._logger
            )

        if not proxies:
            raise SubscriptionError("No valid proxies found in subscription")

        self._logger.info(f"Parsed {len(proxies)} valid proxies from subscription")

        # Fetch user agents if rotation enabled
        if self._user_agent_manager:
            await self._user_agent_manager.fetch_and_store()

        # Store proxies
        proxy_dicts = [proxy.model_dump() for proxy in proxies]
        write_json_file(self._proxies_file, proxy_dicts)

        # Update metadata
        metadata = {
            "updated_at": datetime.now().isoformat(),
            "proxy_count": len(proxies),
        }
        write_json_file(self._metadata_file, metadata)

        # Clear test results
        if self._test_results_file.exists():
            self._test_results_file.unlink()

        self._logger.info("Subscription update completed")

    # ==================== Connection Testing ====================

    async def _test_proxy(
        self, proxy: VmessProxy, index: int
    ) -> tuple[int, float | None]:
        """
        Test a single proxy's connectivity and measure latency.

        Args:
            proxy: Proxy to test
            index: Index of proxy in the list

        Returns:
            Tuple of (index, latency_in_seconds or None if failed)
        """
        self._logger.debug(f"Testing proxy {index}: {proxy.name}")

        # Start temporary Xray process for this proxy
        port = find_free_port(
            self._config.xray.port_range_start,
            self._config.xray.port_range_end,
            self._config.xray.max_port_attempts,
        )

        xray_config = create_xray_config(proxy, port)
        temp_config_path = self._data_dir / f"test_config_{index}.json"

        process = XrayProcess(
            config=xray_config,
            port=port,
            config_path=temp_config_path,
            binary_path=self._config.xray.binary_path,
            init_wait_seconds=self._config.xray.init_wait_seconds,
            shutdown_timeout=self._config.xray.shutdown_timeout,
            logger=self._logger,
        )

        try:
            await process.start()

            # Test connection
            start_time = asyncio.get_event_loop().time()

            async with httpx.AsyncClient(
                proxy=f"http://127.0.0.1:{port}",
                timeout=self._config.connection_test.timeout,
                limits=httpx.Limits(
                    max_connections=self._config.connection_test.max_parallel_connections,
                ),
                transport=httpx.AsyncHTTPTransport(
                    retries=self._config.connection_test.retries
                ),
            ) as client:
                try:
                    response = await client.get(
                        str(self._config.connection_test.url),
                        timeout=self._config.connection_test.timeout,
                    )

                    if response.status_code == 200:
                        latency = asyncio.get_event_loop().time() - start_time
                        self._logger.debug(
                            f"Proxy {index} test successful - latency: {latency:.3f}s"
                        )
                        return (index, latency)
                    else:
                        self._logger.debug(
                            f"Proxy {index} test failed - status: {response.status_code}"
                        )
                        return (index, None)

                except (httpx.TimeoutException, httpx.ConnectError) as e:
                    self._logger.debug(f"Proxy {index} test failed: {type(e).__name__}")
                    return (index, None)

        except Exception as e:
            self._logger.debug(f"Proxy {index} test error: {e}")
            return (index, None)
        finally:
            process.stop()

    async def _test_all_proxies(self) -> None:
        """
        Test all proxies for connectivity and store results.

        Tests proxies sequentially to avoid overwhelming the system.
        """
        self._logger.info("Testing all proxies for connectivity")

        # Load proxies
        if not self._proxies_file.exists():
            raise NetworkError("No proxies available. Run update_subscription first.")

        proxy_dicts = read_json_file(self._proxies_file)
        proxies = [VmessProxy(**p) for p in proxy_dicts]

        # Test each proxy
        test_results = {}
        valid_count = 0

        for index, proxy in enumerate(proxies):
            _, latency = await self._test_proxy(proxy, index)
            test_results[index] = latency

            if latency is not None:
                valid_count += 1

        self._logger.info(
            f"Testing complete: {valid_count}/{len(proxies)} proxies are valid"
        )

        if valid_count == 0:
            raise NetworkError("No valid proxies found. All connection tests failed.")

        # Store results
        write_json_file(self._test_results_file, test_results)

        # Update metadata
        metadata = read_json_file(self._metadata_file)
        metadata["tested_at"] = datetime.now().isoformat()
        metadata["valid_proxy_count"] = valid_count
        write_json_file(self._metadata_file, metadata)

    # ==================== Data Management ====================

    async def _ensure_data_ready(self) -> None:
        """
        Ensure subscription data and test results are available and current.

        Updates subscription if needed and runs tests if they're stale.
        """
        needs_update = False
        needs_test = False

        # Check if we have basic data
        if not (
            self._proxies_file.exists()
            and self._metadata_file.exists()
            and self._test_results_file.exists()
        ):
            self._logger.info("Initial data missing, performing first-time setup")
            needs_update = True
            needs_test = True
        else:
            # Check if data is stale
            metadata = read_json_file(self._metadata_file)

            updated_at = datetime.fromisoformat(
                metadata.get("updated_at", "2000-01-01")
            )
            if (
                datetime.now() - updated_at
                > self._config.rotation_config.subscription_update_interval
            ):
                self._logger.info("Subscription data is stale, updating")
                needs_update = True
                needs_test = True
            elif self._config.connection_test.interval:
                tested_at = datetime.fromisoformat(
                    metadata.get("tested_at", "2000-01-01")
                )
                if datetime.now() - tested_at > self._config.connection_test.interval:
                    self._logger.info("Test data is stale, re-testing")
                    needs_test = True

        # Perform updates as needed
        if needs_update:
            await self._update_subscription()

        if needs_test:
            await self._test_all_proxies()

    def _load_rotation_queue(self) -> None:
        """
        Load valid proxy indices into rotation queue.

        Filters for working proxies and optionally shuffles them.
        """
        if not self._test_results_file.exists():
            raise NetworkError("No test results available")

        test_results = read_json_file(self._test_results_file)

        # Get indices of valid proxies (non-None latency)
        valid_indices = [
            int(idx) for idx, latency in test_results.items() if latency is not None
        ]

        if not valid_indices:
            raise NetworkError("No valid proxies available")

        # Optionally shuffle
        if self._config.rotation_config.enable_shuffling:
            random.shuffle(valid_indices)

        self._rotation_queue = valid_indices
        self._logger.debug(
            f"Loaded {len(self._rotation_queue)} proxies into rotation queue"
        )

    # ==================== Proxy Rotation ====================

    async def _start_proxy(self) -> None:
        """
        Start a proxy from the rotation queue.

        Selects next proxy from queue, starts Xray process, and sets up headers.
        """
        # Ensure we have proxies to rotate
        if not self._rotation_queue:
            self._load_rotation_queue()

        # Get next proxy
        proxy_index = self._rotation_queue.pop(0)

        # Load proxy data
        proxy_dicts = read_json_file(self._proxies_file)
        proxy = VmessProxy(**proxy_dicts[proxy_index])

        self._logger.debug(f"Starting proxy {proxy_index}: {proxy.name}")

        # Get user agent if rotation enabled
        if self._user_agent_manager:
            proxy_dicts = read_json_file(self._proxies_file)
            total_proxies = len(proxy_dicts)
            self._current_user_agent = self._user_agent_manager.get_for_proxy(
                proxy_index, total_proxies
            )

        # Find free port and create Xray config

        port = find_free_port(
            self._config.xray.port_range_start,
            self._config.xray.port_range_end,
            self._config.xray.max_port_attempts,
        )

        xray_config = create_xray_config(proxy, port)

        # Start Xray process
        self._process = XrayProcess(
            config=xray_config,
            port=port,
            config_path=self._xray_config_file,
            binary_path=self._config.xray.binary_path,
            init_wait_seconds=self._config.xray.init_wait_seconds,
            shutdown_timeout=self._config.xray.shutdown_timeout,
            logger=self._logger,
        )

        await self._process.start()
        self._current_proxy = proxy

        self._logger.info(f"Proxy started: {proxy.name} on port {port}")

    def _stop_proxy(self) -> None:
        """Stop current proxy process and clean up."""
        if self._process:
            self._logger.debug("Stopping current proxy")
            self._process.stop()
            self._process = None

        self._current_proxy = None
        self._current_user_agent = None

    # ==================== Public API ====================

    async def start(self) -> None:
        """
        Start the proxy rotator and activate first proxy.

        Acquires global lock, ensures data is ready, and starts a proxy.
        Must be paired with stop() or use as context manager.
        """
        self._logger.debug("Starting proxy rotator")
        await self._lock.acquire()

        try:
            await self._ensure_data_ready()
            await self._start_proxy()

            # Apply delay if configured
            if self._config.delay.enabled:
                delay = calculate_delay(
                    self._config.delay.base_delay,
                    self._config.delay.jitter,
                    self._config.delay.min_delay,
                    self._config.delay.max_delay,
                )
                self._logger.debug(f"Applying startup delay: {delay:.2f}s")
                await asyncio.sleep(delay)

        except Exception:
            self._stop_proxy()
            if self._lock.locked():
                self._lock.release()
            raise

    async def stop(self) -> None:
        """
        Stop the proxy rotator and release resources.

        Stops current proxy and releases global lock.
        """
        self._logger.debug("Stopping proxy rotator")
        try:
            self._stop_proxy()
        finally:
            if self._lock.locked():
                self._lock.release()

    async def rotate(self) -> None:
        """
        Rotate to the next proxy in the queue.

        Stops current proxy and starts the next one. If queue is empty,
        reloads the queue (optionally reshuffling).
        """
        self._logger.debug("Rotating to next proxy")
        self._stop_proxy()

        # Apply delay if configured
        if self._config.delay.enabled:
            delay = calculate_delay(
                self._config.delay.base_delay,
                self._config.delay.jitter,
                self._config.delay.min_delay,
                self._config.delay.max_delay,
            )
            self._logger.debug(f"Applying rotation delay: {delay:.2f}s")
            await asyncio.sleep(delay)

        await self._start_proxy()

    async def refresh(self) -> None:
        """
        Force refresh of subscription data and re-test all proxies.

        Useful for manually updating the proxy pool.
        """
        self._logger.info("Forcing subscription refresh")
        await self._update_subscription()
        await self._test_all_proxies()
        self._rotation_queue.clear()  # Force queue reload on next use

    # ==================== Context Manager ====================

    async def __aenter__(self) -> Self:
        """Context manager entry - start the rotator."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                await self.start()
                return self
            except PortAllocationError:
                self._logger.warning(
                    f"Port allocation failed (attempt {attempt + 1}/{max_retries})"
                )
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)  # Brief wait before retry

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - stop the rotator."""
        await self.stop()
