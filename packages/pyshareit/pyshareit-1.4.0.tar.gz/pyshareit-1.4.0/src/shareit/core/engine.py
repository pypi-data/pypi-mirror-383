# File: src/shareit/core/engine.py

import asyncio

from .protocol import run_server, send_file_client
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
        # 1. Ensure keys exist before starting network services
        generate_self_signed_cert_if_needed()

        # 2. Start the QUIC server to listen for files
        self._server_task = asyncio.create_task(
            run_server(CONFIG.listen_host, CONFIG.listen_port)
        )

        # 3. Start broadcasting this device's presence
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

    async def transfer_file(self, target_ip: str, file_path: str):
        """Initiates a file transfer to a target device."""
        try:
            await send_file_client(
                host=target_ip,
                port=CONFIG.listen_port,
                file_path=file_path
            )
            return True, f"Successfully sent {file_path}"
        except Exception as e:
            return False, f"Transfer failed: {e}"