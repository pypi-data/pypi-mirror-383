"""
Subscription management for proxy-rotator.

This module handles fetching proxy subscriptions from remote sources
and parsing them into usable proxy configurations.
"""

import base64
import logging

import httpx

from .errors import ProtocolError, SubscriptionError, ValidationError
from .models import VmessProxy
from .protocols import parse_vmess_link


async def fetch_subscription(
    subscription_url: str,
    logger: logging.Logger | None = None,
) -> str:
    """
    Fetch subscription content from a URL.

    Handles base64-encoded subscriptions (typical format) and falls back
    to plain text if decoding fails.

    Args:
        subscription_url: URL to fetch subscription from
        logger: Optional logger instance

    Returns:
        Decoded subscription content (one proxy link per line)

    Raises:
        SubscriptionError: If fetching or decoding fails
    """
    logger = logger or logging.getLogger(__name__)
    logger.debug(f"Fetching subscription from {subscription_url}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(subscription_url)
            response.raise_for_status()

            # Subscription content is typically base64 encoded
            content = response.text.strip()
            try:
                decoded = base64.b64decode(content).decode("utf-8")
                logger.debug(
                    f"Fetched and decoded subscription ({len(decoded.splitlines())} lines)"
                )
                return decoded
            except Exception:
                # Maybe it's not base64 encoded
                logger.debug("Subscription content not base64 encoded, using as-is")
                return content

    except httpx.HTTPError as e:
        raise SubscriptionError(f"Failed to fetch subscription: {e}") from e
    except Exception as e:
        raise SubscriptionError(f"Unexpected error fetching subscription: {e}") from e


def parse_subscription(
    subscription_content: str,
    logger: logging.Logger | None = None,
) -> list[VmessProxy]:
    """
    Parse subscription content into validated proxy configurations.

    Processes each line, attempts to parse as VMESS link, validates,
    and filters out invalid proxies silently.

    Args:
        subscription_content: Raw subscription content (one link per line)
        logger: Optional logger instance

    Returns:
        List of validated VMESS proxy configurations
    """
    logger = logger or logging.getLogger(__name__)
    proxies = []

    for line_num, line in enumerate(subscription_content.splitlines(), 1):
        link = line.strip()

        if not link:
            continue

        if not link.startswith("vmess://"):
            continue

        try:
            proxy = parse_vmess_link(link)
            proxies.append(proxy)
        except (ProtocolError, ValidationError) as e:
            # Skip invalid links silently
            logger.debug(f"Skipping invalid link at line {line_num}: {e}")
            continue

    logger.debug(f"Parsed {len(proxies)} valid proxies from subscription")
    return proxies


async def fetch_and_parse_subscription(
    subscription_url: str,
    logger: logging.Logger | None = None,
) -> list[VmessProxy]:
    """
    Fetch and parse a subscription in one step.

    Convenience function that combines fetching and parsing.

    Args:
        subscription_url: URL to fetch subscription from
        logger: Optional logger instance

    Returns:
        List of validated VMESS proxy configurations

    Raises:
        SubscriptionError: If fetching fails
    """
    content = await fetch_subscription(subscription_url, logger)
    return parse_subscription(content, logger)


def parse_proxy_list(
    proxy_urls: list[str],
    logger: logging.Logger | None = None,
) -> list[VmessProxy]:
    """
    Parse a direct list of proxy URLs.

    Useful when proxies are provided directly in configuration
    rather than fetched from a subscription URL.

    Args:
        proxy_urls: List of proxy URLs (vmess://...)
        logger: Optional logger instance

    Returns:
        List of validated VMESS proxy configurations
    """
    subscription_content = "\n".join(proxy_urls)
    return parse_subscription(subscription_content, logger)
