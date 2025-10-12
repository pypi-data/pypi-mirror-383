import asyncio
import logging
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Optional

from .lifespan import Lifespan, LifespanContext

# ANSI escape codes for colors
PURPLE = "\033[95m"
RESET = "\033[0m"

logger = logging.getLogger(__name__)


# Define the ASGI application type
ASGIApp = Callable[[Dict[str, Any], Callable[[], Awaitable[Dict[str, Any]]], Callable[[Dict[str, Any]], Awaitable[None]]], Awaitable[None]]


class LifespanMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        context: Optional[LifespanContext] = LifespanContext(service_type="app"),
    ):
        self.app = app
        self.startup_task = None
        self.shutdown_task = None
        self.lifespan = Lifespan.get_instance()
        self.context = context

    async def __call__(self, scope: Dict[str, Any], receive: Callable[[], Awaitable[Dict[str, Any]]], send: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        if scope["type"] != "lifespan":
            await self.app(scope, receive, send)
            return

        async for message in self.lifespan_handler(receive, send):
            if message["type"] == "lifespan.shutdown":
                break

    async def lifespan_handler(self, receive, send) -> AsyncGenerator[Dict[str, Any], None]:
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await self.handle_startup(send)
            elif message["type"] == "lifespan.shutdown":
                await self.handle_shutdown(send)
            yield message

    async def handle_startup(self, send):
        if self.startup_task is None:
            logger.info("Starting App ...")
            context = LifespanContext(service_type="app")
            self.startup_task = asyncio.create_task(self.lifespan.startup(context=context))

        try:
            await self.startup_task
            logger.info("App startup completed successfully")
        except Exception as e:
            logger.error(f"Error during app startup: {str(e)}")

        await send({"type": "lifespan.startup.complete"})

    async def handle_shutdown(self, send):
        if self.shutdown_task is None:
            logger.info("Shutting down App ...")
            context = LifespanContext(service_type="app")
            self.shutdown_task = asyncio.create_task(self.lifespan.shutdown(context=context))

        try:
            await self.shutdown_task
            logger.info("App shutdown completed successfully")
        except Exception as e:
            logger.error(f"Error during app shutdown: {str(e)}")

        await send({"type": "lifespan.shutdown.complete"})
