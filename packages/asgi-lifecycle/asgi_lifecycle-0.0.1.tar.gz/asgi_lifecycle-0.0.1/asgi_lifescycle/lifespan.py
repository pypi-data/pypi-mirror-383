from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from functools import wraps
import logging
import threading
from typing import Any, Awaitable, Callable, Dict, List, Literal, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

DEFAULT_SHUTDOWN_TIMEOUT = 30.0

ServiceType = Literal["app", "worker", "api", "scheduler", "test"]


@dataclass
class LifespanContext:
    """Context object for lifespan operations"""

    service_type: ServiceType
    environment: str = "development"
    config: Optional[Dict[str, Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_worker(self) -> bool:
        """Check if running in worker context"""
        return self.service_type == "worker"

    def is_api(self) -> bool:
        """Check if running in API context"""
        return self.service_type in ["app", "api"]

    def is_test(self) -> bool:
        """Check if running in test context"""
        return self.service_type == "test"

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default) if self.config else default

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)


# Type variables for better typing
F = TypeVar("F", bound=Callable[..., Any])


# Type aliases
StartupHook = Union[
    Callable[[], None],  # Sync, no context
    Callable[[], Awaitable[None]],  # Async, no context
    Callable[["LifespanContext"], None],  # Sync, with context
    Callable[["LifespanContext"], Awaitable[None]],  # Async, with context
]

ShutdownHook = Union[
    Callable[[], None],  # Sync, no context
    Callable[[], Awaitable[None]],  # Async, no context
    Callable[["LifespanContext"], None],  # Sync, with context
    Callable[["LifespanContext"], Awaitable[None]],  # Async, with context
]


class Lifespan:
    """Singleton Lifespan with context-aware operations"""

    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _startup_hooks: List[Dict[str, Any]] = []
    _shutdown_hooks: List[Dict[str, Any]] = []
    _shutdown_timeout = DEFAULT_SHUTDOWN_TIMEOUT

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Lifespan, cls).__new__(cls)
                    cls._instance._startup_hooks = []
                    cls._instance._shutdown_hooks = []
                    cls._instance._shutdown_timeout = DEFAULT_SHUTDOWN_TIMEOUT
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = False

    def on_start(self, priority: int = 0, name: Optional[str] = None, service_types: Optional[List[ServiceType]] = None):
        """Decorator for startup hooks with service type filtering"""

        def decorator(func: StartupHook) -> StartupHook:
            if self._initialized:
                raise RuntimeError("Cannot add hooks after initialization")

            # Convert sync functions to async
            if asyncio.iscoroutinefunction(func):
                async_hook = func
            else:
                async_hook = self._make_async(func)

            hook_with_meta = {
                "hook": async_hook,
                "priority": priority,
                "name": name or func.__name__,
                "service_types": service_types or ["app"],  # Default to APP
            }

            self._startup_hooks.append(hook_with_meta)
            self._startup_hooks.sort(key=lambda x: x["priority"])

            logger.debug(f"Registered startup hook: {hook_with_meta['name']} (priority: {priority}, services: {service_types})")
            return func

        return decorator

    def on_shutdown(self, priority: int = 0, name: Optional[str] = None, service_types: Optional[List[ServiceType]] = None):
        """Decorator for shutdown hooks with service type filtering"""

        def decorator(func: ShutdownHook):
            if self._initialized:
                raise RuntimeError("Cannot add hooks after initialization")

            if asyncio.iscoroutinefunction(func):
                async_hook = func
            else:
                async_hook = self._make_async(func)

            hook_with_meta = {
                "hook": async_hook,
                "priority": priority,
                "name": name or func.__name__,
                "service_types": service_types or ["app"],  # Default to APP
            }

            self._shutdown_hooks.append(hook_with_meta)
            self._shutdown_hooks.sort(key=lambda x: x["priority"], reverse=True)

            logger.debug(f"Registered shutdown hook: {hook_with_meta['name']} (priority: {priority}, services: {service_types})")
            return func

        return decorator

    async def startup(self, context: LifespanContext):
        """Initialize the application with context"""
        if self._initialized:
            logger.warning("LifespanManager already initialized")
            return

        # Filter hooks by service type
        relevant_hooks = [hook for hook in self._startup_hooks if context.service_type in hook["service_types"]]

        logger.info(f"Initializing {len(relevant_hooks)} startup hooks for {context.service_type}...")

        for hook_meta in relevant_hooks:
            try:
                logger.debug(f"Running startup hook: {hook_meta['name']}")
                hook_func = hook_meta["hook"]
                if self._hook_expects_context(hook_func):
                    await hook_func(context)
                else:
                    await hook_func()
                logger.debug(f"✓ Startup hook completed: {hook_meta['name']}")
            except Exception as e:
                logger.error(f"✗ Startup hook failed: {hook_meta['name']} - {e}")

        self._initialized = True
        logger.info("All startup hooks completed")

    async def shutdown(self, context: LifespanContext):
        """Shutdown the application with context"""
        if not self._initialized:
            logger.warning("LifespanManager not initialized")
            return

        # Filter hooks by service type
        relevant_hooks = [hook for hook in self._shutdown_hooks if context.service_type in hook["service_types"]]

        logger.info(f"Shutting down {len(relevant_hooks)} shutdown hooks for {context.service_type}...")

        for hook_meta in relevant_hooks:
            try:
                logger.debug(f"Running shutdown hook: {hook_meta['name']}")

                # Check if hook expects context and pass it accordingly
                hook_func = hook_meta["hook"]
                if self._hook_expects_context(hook_func):
                    await asyncio.wait_for(
                        hook_func(context),  # Pass context to hook
                        timeout=self._shutdown_timeout,
                    )
                else:
                    await asyncio.wait_for(
                        hook_func(),  # No context for backward compatibility
                        timeout=self._shutdown_timeout,
                    )

                logger.debug(f"✓ Shutdown hook completed: {hook_meta['name']}")
            except asyncio.TimeoutError:
                logger.error(f"✗ Shutdown hook timed out: {hook_meta['name']}")
            except Exception as e:
                logger.error(f"✗ Shutdown hook failed: {hook_meta['name']} - {e}")

        self._initialized = False
        logger.info("All shutdown hooks completed")

    def is_initialized(self) -> bool:
        """Check if the manager is initialized"""
        return self._initialized

    def _hook_expects_context(self, hook_func) -> bool:
        """Check if hook function expects context parameter"""
        import inspect

        sig = inspect.signature(hook_func)
        return len(sig.parameters) > 0

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        return cls()

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance (mainly for testing)"""
        with cls._lock:
            cls._instance = None
            cls._initialized = False

    @staticmethod
    def _make_async(sync_func):
        """Convert sync function to async"""

        @wraps(sync_func)
        async def async_wrapper():
            return sync_func()

        return async_wrapper


# Convenience function for easy access
def get_lifespan() -> Lifespan:
    """Get the singleton Lifespan instance"""
    return Lifespan.get_instance()


# Global access
lifespan = get_lifespan()
