from abc import ABC, abstractmethod
from dataclasses import dataclass

__all__ = [
    "DevicePingData",
    "TopicConfig",
    "DeviceListener",
    "Device"
]

@dataclass
class DevicePingData:
    interval: int
    ssh: str
    jupyter: str
    cpu: float
    memory: float
    disk: float
    macAddress: str
    ip: str
    running: int

@dataclass
class TopicConfig:
    device_id: str
    device_type: str
    topic: str

class DeviceListener(ABC):
    @abstractmethod
    def on_connect(self):
        pass

    @abstractmethod
    def on_disconnect(self):
        pass

    @abstractmethod
    def on_error(self, error_msg:str):
        pass

    @abstractmethod
    def on_data(self):
        pass

class Device(ABC):
    """
    Abstract base class representing a device interface.
    This class defines the required interface for device implementations,
    including methods for sending messages, subscribing to topics, and resource cleanup.
        listener (DeviceListener): The listener object that handles device events.
    Methods:
        send_d2c_message(payload):
            Sends a device-to-cloud message with the given payload.
        send_ping_message(ping_msg: DevicePingData):
            Sends a ping message containing device ping data.
        subscribe(topic: TopicConfig):
            Subscribes the device to a specified topic.
        destory():
            Cleans up resources and destroys the device instance.
    """
    def __init__(self, listener: DeviceListener):
        self._listener : DeviceListener = listener

    @abstractmethod
    def send_d2c_message(self, payload):
        pass

    @abstractmethod
    def send_ping_message(self, ping_msg: DevicePingData):
        pass

    @abstractmethod
    def subscribe(self, topic: TopicConfig):
        pass

    @abstractmethod
    def destory(self):
        pass
