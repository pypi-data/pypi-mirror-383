# File: src/shareit/discovery/finder.py

import socket
from typing import Dict
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser

from ..utils.config import CONFIG

class DeviceListener:
    """Listens for discovered ShareIt services."""

    def __init__(self):
        self.devices: Dict[str, Dict] = {}

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")
        if name in self.devices:
            del self.devices[name]
    
    def update_service(self, zeroconf, type, name):
        """Handles service updates by re-adding the service."""
        print(f"Service {name} updated")
        self.add_service(zeroconf, type, name)

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            try:
                address = socket.inet_ntoa(info.addresses[0])
                self.devices[name] = {
                    "name": info.properties.get(b"device_name", b"Unknown").decode(),
                    "ip": address,
                    "port": info.port,
                    "full_name": name
                }
                print(f"Discovered/updated device: {self.devices[name]}")
            except (IndexError, OSError):
                print(f"Could not get address for service {name}")



class NexusFinder:
    """Manages service discovery and broadcasting using Zeroconf."""

    def __init__(self):
        self._zeroconf = Zeroconf()
        self.listener = DeviceListener()
        self._browser = ServiceBrowser(self._zeroconf, CONFIG.service_type, self.listener)
        self._service_info = None

    def start_broadcasting(self):
        """Broadcasts this device's presence on the network."""
        self._service_info = ServiceInfo(
            CONFIG.service_type,
            f"{CONFIG.device_name}.{CONFIG.service_type}",
            addresses=[socket.inet_aton(CONFIG.listen_host)],
            port=CONFIG.listen_port,
            properties={"device_name": CONFIG.device_name},
            server=f"{CONFIG.server_name}.local.",
        )
        self._zeroconf.register_service(self._service_info)
        print(f"Broadcasting as '{CONFIG.device_name}' on {CONFIG.listen_host}:{CONFIG.listen_port}")

    def stop(self):
        """Stops broadcasting and closes discovery."""
        if self._service_info:
            self._zeroconf.unregister_service(self._service_info)
        self._zeroconf.close()
        print("Stopped broadcasting and discovery.")

    def get_discovered_devices(self) -> Dict[str, Dict]:
        return self.listener.devices