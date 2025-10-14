# File: src/shareit/tui/app.py

import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, DataTable, Log
from textual.message import Message
# The 'Drop' event is no longer imported from textual.events

from ..core.engine import ShareItEngine
from ..utils.config import CONFIG

class ShareItApp(App[None]):
    """A simple, single-screen TUI for pyshareit with drag-and-drop support."""

    TITLE = "pyshareit - Drop a file to send"

    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.engine = ShareItEngine()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="peers", cursor_type="row")
        yield Log(id="status", auto_scroll=True)
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        status_log = self.query_one(Log)
        status_log.write_line(f"pyshareit is running. Your IP: {CONFIG.listen_host}")
        status_log.write_line("... Waiting for you to drop a file on a peer ...")

        peers_table = self.query_one(DataTable)
        peers_table.add_columns("Device Name", "IP Address")

        self.engine.start()
        
        self.set_interval(3, self.update_peers)

    async def on_quit(self) -> None:
        """Called when the user presses 'q'."""
        await self.engine.stop()

    def update_peers(self) -> None:
        """Refreshes the peers DataTable with discovered devices."""
        peers_table = self.query_one(DataTable)
        current_selection = peers_table.cursor_row
        
        peers_table.clear()
        devices = self.engine.nexus_finder.get_discovered_devices()
        
        my_full_name = f"{CONFIG.device_name}.{CONFIG.service_type}"
        
        for name, info in devices.items():
            if my_full_name not in name:
                peers_table.add_row(info['name'], info['ip'], key=info['ip'])
        
        if peers_table.is_valid_row_index(current_selection):
            peers_table.move_cursor(row=current_selection)

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.query_one(Log).write_line(f"Selected peer: {event.row_key.value}. Drag a file onto this row to send.")

    # Use a string for the type hint for forward-compatibility
    async def on_drop(self, event: "Drop") -> None:
        """Handles a file being dropped into the terminal."""
        peers_table = self.query_one(DataTable)
        if not peers_table.has_focus:
            self.query_one(Log).write_line("[bold red]Please select a peer from the table first![/]")
            return
            
        target_ip = peers_table.get_row_key(peers_table.cursor_row)
        file_path = event.path
        
        if target_ip and file_path:
            status_log = self.query_one(Log)
            status_log.write_line(f"Starting transfer of '{file_path.name}' to {target_ip}...")
            
            asyncio.create_task(self.run_transfer(target_ip, str(file_path)))

    async def run_transfer(self, target_ip: str, file_path: str) -> None:
        """Worker task for performing a file transfer."""
        success, message = await self.engine.transfer_file(target_ip, file_path)
        log_message = f"[bold green]Transfer successful: {message}" if success else f"[bold red]Transfer failed: {message}"
        self.query_one(Log).write_line(log_message)

def main():
    app = ShareItApp()
    app.run()