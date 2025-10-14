# File: src/shareit/core/engine.py

import asyncio
from typing import Optional, Callable

from .protocol import run_server, send_file_client, ProgressCallback
from .security import generate_self_signed_cert_if_needed
from ..discovery.finder import NexusFinder
from ..utils.config import CONFIG

class ShareItEngine:
    """The main backend engine for ShareIt."""

    def __init__(self):
        self.nexus_finder = NexusFinder()
        self._server_task: asyncio.Task = None

    def start(self):
        """Prepares and starts all background services."""
        generate_self_signed_cert_if_needed()
        self._server_task = asyncio.create_task(
            run_server(CONFIG.listen_host, CONFIG.listen_port)
        )
        self.nexus_finder.start_broadcasting()

    async def stop(self):
        """Gracefully stops all services."""
        print("Shutting down...")
        self.nexus_finder.stop()
        if self._server_task:
            self._server_task.cancel()
            try:
                await self._server_task
            except asyncio.CancelledError:
                pass
        print("Shutdown complete.")

    async def transfer_file(
        self, target_ip: str, file_path: str, progress_callback: Optional[ProgressCallback] = None
    ):
        """Initiates a file transfer to a target device."""
        try:
            await send_file_client(
                host=target_ip,
                port=CONFIG.listen_port,
                file_path=file_path,
                progress_callback=progress_callback
            )
            return True, f"Successfully sent {file_path}"
        except Exception as e:
            return False, f"Transfer failed: {e}"