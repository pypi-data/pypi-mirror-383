"""Base classes and utilities for Kubernetes resource watchers."""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from kubernetes import watch
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


class BaseResourceWatcher(ABC):
    """Base class for Kubernetes resource watchers."""

    def __init__(self, name: str):
        """Initialize watcher.

        Args:
            name: Name of the watcher for logging
        """
        self.name = name
        self.running = False
        self.watch = watch.Watch()

    @abstractmethod
    async def watch_resource(self) -> None:
        """Watch the specific resource type. Must be implemented by subclasses."""
        pass

    @abstractmethod
    async def handle_event(self, event: Dict[str, Any]) -> None:
        """Handle a resource event. Must be implemented by subclasses.

        Args:
            event: Kubernetes event dictionary with 'type' and 'object' keys
        """
        pass

    async def start(self) -> None:
        """Start watching the resource."""
        logger.info(f"Starting {self.name} watcher...")
        self.running = True

        while self.running:
            try:
                await self.watch_resource()
            except ApiException as e:
                logger.error(f"Kubernetes API error in {self.name} watcher: {e}")
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info(f"{self.name} watcher cancelled")
                self.running = False
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {self.name} watcher: {e}", exc_info=True)
                await asyncio.sleep(5)

    def stop(self) -> None:
        """Stop watching the resource."""
        logger.info(f"Stopping {self.name} watcher...")
        self.running = False
        self.watch.stop()


async def watch_with_timeout(
    watch_stream: Callable,
    timeout_seconds: int = 60,
    **kwargs
) -> None:
    """Watch a Kubernetes resource with timeout.

    Args:
        watch_stream: Watch stream callable
        timeout_seconds: Timeout for watch stream
        **kwargs: Additional arguments to pass to watch_stream
    """
    w = watch.Watch()
    try:
        async for event in w.stream(watch_stream, timeout_seconds=timeout_seconds, **kwargs):
            yield event
    finally:
        w.stop()
