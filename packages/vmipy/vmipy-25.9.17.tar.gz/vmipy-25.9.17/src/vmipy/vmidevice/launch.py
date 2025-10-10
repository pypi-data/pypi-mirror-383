from ._abstract import DeviceListener
from ._wsdevice import WSDevice

__all__ = [
    "create_ws_device"
]

def create_ws_device(
    device_type: str,
    device_id: str,
    server_ip: str,
    device_listener : DeviceListener | None = None):
    return WSDevice(server_ip, device_type, device_id, device_listener)
