from vmipy.vmichannel import WebSocketChannel
import threading
import queue
import time
import json
from ._abstract import Device, DevicePingData, DeviceListener, TopicConfig
from dataclasses import asdict
from typing import List

class DevicePingMessage:
    def __init__(self,
                 interval=30,
                 ssh="",
                 jupyter="",
                 cpu=0,
                 memory=0,
                 disk=0,
                 macAddress="",
                 ip="",
                 running=0) -> None:
        self.interval = interval
        self.ssh = ssh
        self.jupyter = jupyter
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.macAddress = macAddress
        self.ip = ip
        self.running = running
    
    def toJson(self):
        return {
            "interval": self.interval,
            "ssh": self.ssh,
            "jupyter": self.jupyter,
            "cpu": self.cpu,
            "memory": self.memory,
            "disk": self.disk,
            "macAddress": self.macAddress,
            "ip": self.ip,
            "running": self.running
        }


class WSDeviceProtocolGen:
    @classmethod
    def GenD2CMessage(cls, deviceType, deviceId, payload):
        topic = "d2c/{0}/{1}/property".format(deviceType, deviceId)
        return {
            "jsonrpc": "2.0",
            "method": "internal.call",
            "params": {
                "topic": topic,
                "payload": payload
            }
        }
    @classmethod
    def GenD2CPingMessage(cls, deviceType, deviceId, pingMsg):
        topic = "d2cping/{0}/{1}".format(deviceType, deviceId)
        return {
            "jsonrpc": "2.0",
            "method": "internal.call",
            "params": {
                "topic": topic,
                "payload": pingMsg
            }
        }
    
class WSDevice(Device):
    def __init__(self,serverIp, deviceType, deviceId, listener: DeviceListener | None):
        super().__init__(listener)
        self._deviceType = deviceType
        self._deviceId = deviceId
        self._serverIp = serverIp
        self._wsUrl = f"ws://{self._serverIp}/ws/edge/iot?devicetype={self._deviceType}&deviceid={self._deviceId}"
        self._wsChannel = WebSocketChannel(url=self._wsUrl)
        self._wsChannel.on_connect = self._onConnect
        self._wsChannel.on_disconnect = self._onDisconnected
        self._wsChannel.on_error = self._onError
        self._connectEvent = threading.Event()
        self._connectEvent.clear()
        self._queue = queue.Queue()
        self._is_running = True
        self._d2cThread = threading.Thread(target=self._send_msg, args=(), daemon=True)
        self._d2cThread.start()

        self._channelThread = threading.Thread(target=self._wsChannel.Run, args=(), daemon=True)
        self._channelThread.start()


    def _onConnect(self, ws):
        self._connectEvent.set()
        if self._listener is not None:
            self._listener.on_connect()

    def _onDisconnected(self, ws, close_code, close_msg):
        self._connectEvent.clear()
        if self._listener is not None:
            self._listener.on_disconnect()

    def _onError(self, ws, error):
        if self._listener is not None:
            self._listener.on_error(error)

    def _send_msg(self):
        while self._is_running:
            _ret = self._queue.get()
            if _ret is None:
                continue
            if self._connectEvent.is_set() is False:
                continue
            self._wsChannel.Send(json.dumps(_ret))

    def send_d2c_message(self, payload):
        msg = WSDeviceProtocolGen.GenD2CMessage(
            self._deviceType,
            self._deviceId,
            payload=payload
        )
        self._queue.put(msg)

    def send_ping_message(self, ping_msg: DevicePingData):
        msg = WSDeviceProtocolGen.GenD2CPingMessage(
            self._deviceType,
            self._deviceId,
            asdict(ping_msg)
        )
        self._queue.put(msg)

    def subscribe(self, topic:TopicConfig):
        raise NotImplementedError("subscribe method not supported yet")
        
    def destory(self):
        self._is_running = False
        self._queue.put(None)
        if self._d2cThread is not None and self._d2cThread.is_alive():
            self._d2cThread.join(timeout=2)
        