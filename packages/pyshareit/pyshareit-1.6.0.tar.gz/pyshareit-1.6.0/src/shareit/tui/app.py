# File: src/shareit/tui/app.py

import asyncio
from pathlib import Path
from typing import Callable
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, DataTable, Log, ProgressBar, RichLog, DirectoryTree
from textual.containers import Vertical, Grid

from ..core.engine import ShareItEngine
from ..utils.config import CONFIG

class FileSelectScreen(ModalScreen):
    """A modal screen for selecting a file to send."""

    def compose(self) -> ComposeResult:
        with Grid(id="file_select_grid"):
            yield DirectoryTree(str(Path.home()), id="file_tree")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when the user clicks a file in the tree."""
        self.dismiss(str(event.path))


class ShareItApp(App[None]):
    """A simple TUI for pyshareit with progress feedback."""

    TITLE = "pyshareit - Drop a file on a peer to send"
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "select_file", "Send File..."),
    ]

    def __init__(self):
        super().__init__()
        self.engine = ShareItEngine()
        self.transfer_count = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="peers", cursor_type="row")
        with Vertical(id="drop_zone"):
            yield RichLog(id="transfer_log", markup=True, wrap=True)
        yield Footer()

    # Find the on_mount method in app.py

    def on_mount(self) -> None:
        peers_table = self.query_one(DataTable)
        peers_table.add_columns("Device Name", "IP Address")
        transfer_log = self.query_one(RichLog)
        transfer_log.write(f"[bold cyan]pyshareit is running. Your IP: {CONFIG.listen_host}[/]")
        transfer_log.write("[bold yellow]Select a peer, then [u]drop a file below[/u] or [u]press 's'[/u] to send.[/]")

    # ADD THIS BLOCK
        drop_zone = self.query_one("#drop_zone")
        drop_zone.border_title = "Drop File Here or Press s"
    # END OF BLOCK TO ADD

        self.engine.start()
        self.set_interval(3, self.update_peers)

    async def on_quit(self) -> None:
        await self.engine.stop()

    def update_peers(self) -> None:
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

    def action_select_file(self) -> None:
        """A key binding to open the file selection modal."""
        peers_table = self.query_one(DataTable)
        if peers_table.row_count == 0 or peers_table.cursor_row < 0:
            self.query_one(RichLog).write("[bold red]Please select a peer from the table first![/]")
            return

        def file_selected_callback(path: str):
            target_ip = peers_table.get_row_key(peers_table.cursor_row)
            self.start_transfer(target_ip, Path(path))

        self.push_screen(FileSelectScreen(), file_selected_callback)

    async def on_drop(self, event: "Drop") -> None:
        """Handles a file being dropped into the terminal."""
        peers_table = self.query_one(DataTable)
        target_ip = peers_table.get_row_key(peers_table.cursor_row) if peers_table.row_count > 0 else None
        
        if not target_ip:
            self.query_one(RichLog).write("[bold red]Please select a peer from the table first![/]")
            return
            
        if event.path:
            self.start_transfer(target_ip, event.path)

    def start_transfer(self, target_ip: str, file_path: Path):
        """Initiates a file transfer and sets up the UI."""
        self.transfer_count += 1
        transfer_id = f"transfer-{self.transfer_count}"

        progress_bar = ProgressBar(total=100, id=transfer_id)
        self.query_one("#drop_zone").mount(progress_bar)

        self.query_one(RichLog).write(f"Starting transfer of '{file_path.name}'...")

        def progress_callback(sent: int, total: int, speed: float):
            percentage = (sent / total) * 100 if total > 0 else 0
            progress_bar.update(progress=percentage)
            # This check prevents spamming the log with zero-speed updates
            if sent < total:
                self.query_one(RichLog).write(
                    f"[#888888]  ↳ {file_path.name} | "
                    f"{sent/1024/1024:.2f}MB / {total/1024/1024:.2f}MB | "
                    f"[bold yellow]{speed:.2f} MB/s[/]"
                )

        asyncio.create_task(self.run_transfer(target_ip, str(file_path), progress_callback, progress_bar))

    async def run_transfer(
        self, target_ip: str, file_path: str, callback: Callable, progress_bar: ProgressBar
    ):
        """Worker task for performing the file transfer."""
        success, message = await self.engine.transfer_file(target_ip, file_path, callback)
        log_message = f"[bold green]✅ Transfer complete: {Path(file_path).name}" if success else f"[bold red]❌ {message}"
        self.query_one(RichLog).write(log_message)
        
        await asyncio.sleep(5)
        progress_bar.remove()

def main():
    app = ShareItApp()
    app.run()