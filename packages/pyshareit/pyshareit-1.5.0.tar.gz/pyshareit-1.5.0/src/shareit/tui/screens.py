# File: src/shareit/tui/screens.py

from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Static, Button, DataTable, DirectoryTree, Input, Log
from rich.panel import Panel

class MainDashboard(Screen):
    """The main landing screen."""
    def compose(self) -> ComposeResult:
        yield Static(Panel("Welcome to ShareIt! Your device is now broadcasting.",
                           title="🚀 Dashboard"), id="welcome")
        yield Button("Start Broadcasting", id="start-broadcast", variant="primary")
        yield Log(id="app-log", max_lines=100)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-broadcast":
            self.app.engine.start()
            self.query_one("#app-log").write_line("📡 Device broadcasting started...")
            event.button.disabled = True

class DeviceDiscovery(Screen):
    """Screen for discovering other devices."""
    def compose(self) -> ComposeResult:
        yield Static("Discovered Devices on the Network", classes="title")
        yield DataTable(id="device-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Device Name", "IP Address", "Port")
        self.set_interval(2, self.update_device_list)

    def update_device_list(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        devices = self.app.engine.nexus_finder.get_discovered_devices()
        for name, info in devices.items():
            table.add_row(info['name'], info['ip'], info['port'])

class FileTransfer(Screen):
    """Screen for selecting and sending files."""
    def compose(self) -> ComposeResult:
        with Vertical(id="transfer-layout"):
            yield Static("Select a File to Transfer", classes="title")
            yield DirectoryTree(str(Path.home()), id="file-tree")
            yield Input(placeholder="Target IP Address...", id="target-ip")
            yield Button("Send File", id="send-file", variant="success", disabled=True)
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.query_one(Input).value = "" # Clear IP on new file selection
        self.query_one(Button).disabled = False
        self.app.selected_file_path = str(event.path)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-file":
            target_ip = self.query_one(Input).value
            file_path = self.app.selected_file_path
            if target_ip and file_path:
                self.app.notify(f"Initiating transfer to {target_ip}...")
                success, message = await self.app.engine.transfer_file(target_ip, file_path)
                self.app.notify(message, severity="information" if success else "error")
            else:
                self.app.notify("Please select a file and enter a target IP.", severity="error")