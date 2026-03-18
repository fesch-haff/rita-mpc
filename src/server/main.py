import os
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from client import Client
from logging_config import setup_logging, LOGGING

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


class HomeAssistantServer:
    """
    Class-based FastAPI server managing the Home Assistant client lifecycle.
    """

    def __init__(self):
        self.running = None
        self.client = Client(os.getenv("HOME_ASSISTANT_WS_URL"), os.getenv("ACCESS_TOKEN"))
        self.app = FastAPI(lifespan=self.lifespan)

    async def websocket_startup(self):
        logger.info("Starting Home Assistant client...")
        await self.client.connect()
        await self.client.fetch_states()
        await self.client.subscribe_to_events()
        logger.info("Home Assistant client started successfully.")

    async def websocket_shutdown(self):
        logger.info("Disconnecting Home Assistant client...")
        await self.client.disconnect()
        logger.info("Home Assistant client disconnected.")


    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """
        Async context manager for managing the client lifecycle.
        """
        await self.websocket_startup()

        try:
            yield
        finally:
            await self.websocket_shutdown()


    def run(self, host="0.0.0.0", port=8000, reload=False):
        """
        Run the FastAPI app with Uvicorn.
        """
        uvicorn.run(self.app, host=host, port=port, reload=reload, log_config=LOGGING)


if __name__ == "__main__":
    server = HomeAssistantServer()
    server.run()