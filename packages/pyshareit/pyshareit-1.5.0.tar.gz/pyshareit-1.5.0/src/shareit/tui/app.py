# File: src/shareit/tui/app.py

import asyncio
from pathlib import Path
from typing import Callable  # <-- ADD THIS LINE
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, DataTable, Log, ProgressBar, RichLog
from textual.containers import Vertical
from textual.message import Message

from ..core.engine import ShareItEngine
from ..utils.config import CONFIG

class ShareItApp(App[None]):
    """A simple TUI for pyshareit with progress feedback."""

    TITLE = "pyshareit - Drop a file on a peer to send"
    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.engine = ShareItEngine()
        self.transfer_count = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="peers", cursor_type="row")
        
        # A dedicated container for dropping files
        with Vertical(id="drop_zone"):
            yield RichLog(id="transfer_log", markup=True, wrap=True)

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        peers_table = self.query_one(DataTable)
        peers_table.add_columns("Device Name", "IP Address")

        transfer_log = self.query_one(RichLog)
        transfer_log.write(f"[bold cyan]pyshareit is running. Your IP: {CONFIG.listen_host}[/]")
        transfer_log.write("[bold yellow]Select a peer from the table, then drop a file below to start a transfer.[/]")

        self.engine.start()
        self.set_interval(3, self.update_peers)

    async def on_quit(self) -> None:
        await self.engine.stop()

    def update_peers(self) -> None:
        """Refreshes the peers DataTable."""
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
        self.query_one(RichLog).write(f"[green]Selected peer: {event.row_key.value}.[/]")

    async def on_drop(self, event: "Drop") -> None:
        """Handles a file being dropped onto the terminal."""
        peers_table = self.query_one(DataTable)
        target_ip = peers_table.get_row_key(peers_table.cursor_row) if peers_table.row_count > 0 else None
        
        if not target_ip:
            self.query_one(RichLog).write("[bold red]Please select a peer from the table first![/]")
            return
            
        file_path = event.path
        if file_path:
            self.transfer_count += 1
            transfer_id = f"transfer-{self.transfer_count}"

            # Create a new progress bar for this transfer
            progress_bar = ProgressBar(total=100, id=transfer_id)
            self.query_one("#drop_zone").mount(progress_bar)

            self.query_one(RichLog).write(f"Starting transfer of '{file_path.name}'...")

            # Define the callback that will update the UI
            def progress_callback(sent: int, total: int, speed: float):
                percentage = (sent / total) * 100 if total > 0 else 0
                progress_bar.update(progress=percentage)
                self.query_one(RichLog).write(
                    f"[#888888]  ↳ {Path(file_path).name} | "
                    f"{sent/1024/1024:.2f}MB / {total/1024/1024:.2f}MB | "
                    f"[bold yellow]{speed:.2f} MB/s[/]"
                )

            asyncio.create_task(self.run_transfer(target_ip, str(file_path), progress_callback, progress_bar))

    async def run_transfer(
        self, target_ip: str, file_path: str, callback: Callable, progress_bar: ProgressBar
    ):
        """Worker task for performing a file transfer."""
        success, message = await self.engine.transfer_file(target_ip, file_path, callback)
        log_message = f"[bold green]✅ {message}" if success else f"[bold red]❌ {message}"
        self.query_one(RichLog).write(log_message)
        # Remove the progress bar after a short delay
        await asyncio.sleep(5)
        progress_bar.remove()

def main():
    app = ShareItApp()
    app.run()