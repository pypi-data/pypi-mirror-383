# File: src/shareit/core/protocol.py

import asyncio
import os
import ssl
from typing import Optional, Dict, BinaryIO, cast

from aioquic.asyncio import QuicConnectionProtocol, connect, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived, QuicEvent, ConnectionTerminated

from ..utils.config import CERT_PATH, KEY_PATH

class ShareItProtocol(QuicConnectionProtocol):
    """A QUIC protocol that handles both sending and receiving files."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handlers: Dict[int, 'FileStreamHandler'] = {}

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, StreamDataReceived):
            handler = self._handlers.get(event.stream_id)
            if handler is None:
                # This is a new incoming stream, create a handler for it
                handler = FileStreamHandler(self.transmit)
                self._handlers[event.stream_id] = handler
            
            # Pass the data to the correct stream handler
            handler.handle_data(event.data, event.end_stream)
        
        elif isinstance(event, ConnectionTerminated):
            # Clean up handlers on disconnect
            for handler in self._handlers.values():
                handler.close()
            self._handlers.clear()

class FileStreamHandler:
    """Manages the state of a single incoming file transfer stream."""
    def __init__(self, transmit_callback):
        self.buffer = b""
        self.file_handle: Optional[BinaryIO] = None
        self.filename: Optional[str] = None
        self.transmit = transmit_callback

    def handle_data(self, data: bytes, end_stream: bool):
        if self.filename is None:
            # Buffer until we get the metadata (filename)
            self.buffer += data
            if b"\n" in self.buffer:
                metadata_raw, self.buffer = self.buffer.split(b"\n", 1)
                self.filename = metadata_raw.decode().split(":", 1)[1]
                
                # Sanitize filename to prevent directory traversal attacks
                self.filename = os.path.basename(self.filename)
                
                print(f"Receiving file: {self.filename}")
                self.file_handle = open(self.filename, "wb")
                
                # Write any remaining buffered data
                if self.buffer:
                    self.file_handle.write(self.buffer)
                    self.buffer = b""
        else:
            # Already have filename, just write data
            if self.file_handle:
                self.file_handle.write(data)

        if end_stream:
            self.close()

    def close(self):
        if self.file_handle:
            print(f"Finished receiving {self.filename}")
            self.file_handle.close()
            self.file_handle = None

async def run_server(host, port):
    """Starts the QUIC server to listen for incoming files."""
    configuration = QuicConfiguration(
        is_client=False,
        alpn_protocols=["shareit/1.0"],
    )
    configuration.load_cert_chain(CERT_PATH, KEY_PATH)
    await serve(host, port, configuration=configuration, create_protocol=ShareItProtocol)

async def send_file_client(host: str, port: int, file_path: str):
    """Connects to a peer and sends a file."""
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=["shareit/1.0"],
        verify_mode=ssl.CERT_NONE  # WARNING: Insecure, for local networks only
    )
    
    async with connect(
        host, port, configuration=configuration, create_protocol=ShareItProtocol
    ) as protocol:
        protocol = cast(ShareItProtocol, protocol)
        stream_id = protocol._quic.get_next_available_stream_id()
        
        # Send metadata first: "filename:my_document.pdf\n"
        filename = os.path.basename(file_path)
        metadata = f"filename:{filename}\n".encode()
        protocol._quic.send_stream_data(stream_id, metadata)
        
        # Stream the file content
        with open(file_path, "rb") as f:
            while data := f.read(4096):
                protocol._quic.send_stream_data(stream_id, data)
                protocol.transmit()
                await asyncio.sleep(0) # Allow other tasks to run

        # End the stream
        protocol._quic.send_stream_data(stream_id, b"", end_stream=True)
        protocol.transmit()
        print(f"Finished sending {filename}")