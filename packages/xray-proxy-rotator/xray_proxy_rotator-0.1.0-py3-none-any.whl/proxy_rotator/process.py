"""
Xray process management for proxy-rotator.

This module handles the lifecycle of Xray-core processes, including
starting, monitoring, and graceful shutdown.
"""

import asyncio
import logging
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Self

from .errors import PortAllocationError, ProcessError
from .models import XrayConfig


class XrayProcess:
    """
    Manages a single Xray-core process instance.

    Handles process lifecycle including startup, monitoring, and graceful shutdown.
    Automatically cleans up resources on exit.
    """

    def __init__(
        self,
        config: XrayConfig,
        port: int,
        config_path: Path,
        binary_path: str = "xray",
        init_wait_seconds: float = 2.0,
        shutdown_timeout: float = 5.0,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize Xray process manager.

        Args:
            config: Xray configuration to use
            port: Local port the proxy will listen on
            config_path: Path where config file will be written
            binary_path: Path to xray binary
            init_wait_seconds: Time to wait for process initialization
            shutdown_timeout: Timeout for graceful shutdown before force kill
            logger: Optional logger instance
        """
        self._config = config
        self._port = port
        self._config_path = config_path
        self._binary_path = binary_path
        self._init_wait_seconds = init_wait_seconds
        self._shutdown_timeout = shutdown_timeout
        self._logger = logger or logging.getLogger(__name__)

        self._process: Popen | None = None

    @property
    def port(self) -> int:
        """Local port the proxy is listening on."""
        return self._port

    @property
    def is_running(self) -> bool:
        """Check if the Xray process is currently running."""
        if self._process is None:
            return False
        return self._process.poll() is None

    async def start(self) -> None:
        """
        Start the Xray process and wait for initialization.

        Raises:
            ProcessError: If process fails to start or exits immediately
            PortAllocationError: If the port is already in use
        """
        if self._process is not None:
            raise ProcessError("Xray process is already running")

        # Write config file
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._config_path.write_text(
                self._config.model_dump_json(indent=2, exclude_none=True),
                encoding="utf-8",
            )
            self._logger.debug(f"Wrote Xray config to {self._config_path}")
        except Exception as e:
            raise ProcessError(f"Failed to write Xray config: {e}") from e

        # Start process
        try:
            self._logger.debug(
                f"Starting Xray process: {self._binary_path} on port {self._port}"
            )
            self._process = Popen(
                [self._binary_path, "run", "-config", str(self._config_path)],
                stdout=PIPE,
                stderr=PIPE,
                text=True,
            )
        except FileNotFoundError:
            raise ProcessError(
                f"Xray binary not found: {self._binary_path}. "
                "Make sure xray-core is installed and in PATH."
            ) from None
        except Exception as e:
            raise ProcessError(f"Failed to start Xray process: {e}") from e

        # Wait for initialization
        self._logger.debug(f"Waiting {self._init_wait_seconds}s for Xray to initialize")
        await asyncio.sleep(self._init_wait_seconds)

        # Check if process is still running
        if not self.is_running:
            stdout, stderr = self._process.communicate()

            # Check for specific error conditions
            if (
                "failed to listen" in stdout.lower()
                or "address already in use" in stderr.lower()
            ):
                raise PortAllocationError(f"Port {self._port} is already in use")

            raise ProcessError(
                f"Xray process exited immediately. "
                f"STDOUT: {stdout[:200]}, STDERR: {stderr[:200]}"
            )

        self._logger.info(f"Xray process started successfully on port {self._port}")

    def stop(self) -> None:
        """
        Stop the Xray process gracefully.

        Attempts graceful termination first, then force kills if necessary.
        Cleans up config file after stopping.
        """
        if self._process is None:
            self._logger.debug("No Xray process to stop")
            return

        if not self.is_running:
            self._logger.debug("Xray process already stopped")
            self._process = None
            self._cleanup_config()
            return

        try:
            self._logger.debug("Terminating Xray process gracefully")
            self._process.terminate()

            # Wait for graceful shutdown
            try:
                self._process.wait(timeout=self._shutdown_timeout)
                self._logger.debug("Xray process terminated gracefully")
            except TimeoutExpired:
                self._logger.warning(
                    f"Xray process did not terminate after {self._shutdown_timeout}s, force killing"
                )
                self._process.kill()
                self._process.wait()
                self._logger.debug("Xray process force killed")

        except ProcessLookupError:
            self._logger.debug("Xray process already terminated")
        except Exception as e:
            self._logger.error(f"Error stopping Xray process: {e}", exc_info=True)
        finally:
            self._process = None
            self._cleanup_config()

    def _cleanup_config(self) -> None:
        """Remove the Xray config file."""
        try:
            if self._config_path.exists():
                self._config_path.unlink()
                self._logger.debug(f"Cleaned up config file: {self._config_path}")
        except Exception as e:
            self._logger.warning(f"Failed to cleanup config file: {e}")

    async def __aenter__(self) -> Self:
        """Context manager entry - start the process."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - stop the process."""
        self.stop()
