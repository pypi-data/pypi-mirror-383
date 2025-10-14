"""
User-Agent management for proxy-rotator.

This module handles fetching, storing, and providing User-Agent strings
for HTTP requests through proxies.
"""

import logging
from pathlib import Path

import httpx

from .errors import SubscriptionError
from .utils import read_json_file, write_json_file


class UserAgentManager:
    """
    Manages User-Agent strings for proxy rotation.

    Handles fetching from remote sources or using a provided list,
    storing locally, and providing user agents for each proxy.
    """

    def __init__(
        self,
        storage_path: Path,
        fetch_url: str | None = None,
        user_agents_list: list[str] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize User-Agent manager.

        Args:
            storage_path: Path to store user agents JSON file
            fetch_url: Optional URL to fetch user agents from
            user_agents_list: Optional direct list of user agents
            logger: Optional logger instance
        """
        self._storage_path = storage_path
        self._fetch_url = fetch_url
        self._user_agents_list = user_agents_list
        self._logger = logger or logging.getLogger(__name__)

        if fetch_url is None and user_agents_list is None:
            raise ValueError("Must provide either fetch_url or user_agents_list")

    async def fetch_and_store(self) -> list[str]:
        """
        Fetch user agents from URL or use provided list, then store locally.

        Returns:
            List of user agent strings

        Raises:
            SubscriptionError: If fetching from URL fails
        """
        if self._fetch_url:
            self._logger.debug(f"Fetching user agents from {self._fetch_url}")

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(self._fetch_url)
                    response.raise_for_status()

                    user_agents = response.json()
                    if not isinstance(user_agents, list):
                        raise SubscriptionError("User agents response is not a list")

                    self._logger.debug(f"Fetched {len(user_agents)} user agents")

            except httpx.HTTPError as e:
                raise SubscriptionError(f"Failed to fetch user agents: {e}") from e
            except Exception as e:
                raise SubscriptionError(f"Unexpected error fetching user agents: {e}") from e
        else:
            if self._user_agents_list is None:
                raise ValueError("No user agents list provided")
            user_agents = self._user_agents_list
            self._logger.debug(f"Using provided list of {len(user_agents)} user agents")

        # Store locally
        write_json_file(self._storage_path, user_agents)
        return user_agents

    def load(self) -> list[str]:
        """
        Load user agents from local storage.

        Returns:
            List of user agent strings

        Raises:
            FileNotFoundError: If storage file doesn't exist
        """
        if not self._storage_path.exists():
            raise FileNotFoundError(
                f"User agents file not found: {self._storage_path}. "
                "Run fetch_and_store() first."
            )

        return read_json_file(self._storage_path)

    def get_for_proxy(self, proxy_index: int, total_proxies: int) -> str:
        """
        Get appropriate user agent for a proxy at given index.

        If there are fewer user agents than proxies, cycles through them.

        Args:
            proxy_index: Index of the proxy (0-based)
            total_proxies: Total number of proxies

        Returns:
            User agent string for this proxy
        """
        user_agents = self.load()

        if len(user_agents) < total_proxies:
            self._logger.debug(
                f"Only {len(user_agents)} user agents for {total_proxies} proxies, "
                "cycling through them"
            )

        # Cycle through user agents if needed
        ua_index = proxy_index % len(user_agents)
        return user_agents[ua_index]
