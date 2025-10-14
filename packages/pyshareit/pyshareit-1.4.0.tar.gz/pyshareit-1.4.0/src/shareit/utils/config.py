# File: src/shareit/utils/config.py

import socket
from pathlib import Path
from pydantic import BaseModel, Field, computed_field


# Define a dedicated, cross-platform configuration directory
APP_DIR = Path.home() / ".shareit"
CERT_PATH = APP_DIR / "cert.pem"
KEY_PATH = APP_DIR / "key.pem"

def get_local_ip():
    """Finds the local IP address of the machine."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('1.1.1.1', 1))
            return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'

class AppConfig(BaseModel):
    """Application Configuration"""
    device_name: str = Field(default_factory=socket.gethostname)
    listen_port: int = 47808
    listen_host: str = Field(default_factory=get_local_ip)
    service_type: str = "_shareit._udp.local."

    @computed_field
    @property
    def server_name(self) -> str:
        """Creates a network-safe server name from the device name."""
        return self.device_name.lower().replace(" ", "-")

    def ensure_config_dir_exists(self):
        """Creates the ~/.shareit directory if it doesn't exist."""
        APP_DIR.mkdir(exist_ok=True)

CONFIG = AppConfig()