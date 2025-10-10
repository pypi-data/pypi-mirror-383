import websocket
import threading
import json
import time

class WebSocketChannel:
    def __init__(self, url):
        self._url = url
        self._onConnectCB = None
        self._onDisconnectCB = None
        self._onMessageCB = None
        self._onErrorCB = None
        self._client = None
        self._connectedClient = None


    def _onConnect(self, ws):
        self._connectedClient = ws
        if self._onConnectCB is not None:
            self._onConnectCB(ws)
    
    def _onDisconnect(self, ws, close_status_code, close_msg):
        self._connectedClient = None
        if self._onDisconnectCB is not None:
            self._onDisconnectCB(ws, close_status_code, close_msg)

    def _onMessage(self,client, message):
        if self._onMessageCB is not None:
            self._onMessageCB(client, message)

    def _onError(self, ws, error):
        if self._onErrorCB is not None:
            self._onErrorCB(ws, error)

    @property
    def on_connect(self):
        return self._onConnectCB

    @on_connect.setter
    def on_connect(self, cb):
        self._onConnectCB = cb

    @property
    def on_disconnect(self):
        return self._onDisconnectCB

    @property
    def on_error(self):
        return self._onErrorCB
    
    @on_error.setter
    def on_error(self, cb):
        self._onErrorCB = cb
        
    @on_disconnect.setter
    def on_disconnect(self, cb):
        self._onDisconnectCB = cb

    @property
    def on_message(self):
        return self._onMessageCB
    
    @on_message.setter
    def on_message(self,cb):
        self._onMessageCB = cb
    
    def Send(self, payload):
        if self._connectedClient is not None:
            self._connectedClient.send(payload)
            return True
        return False

    def Run(self):
        #websocket.enableTrace(True)
        self._client = websocket.WebSocketApp(
            self._url,
            on_open=self._onConnect,
            on_message = self._onMessage,
            on_close = self._onDisconnect,
            on_error = self._onError
        )
        self._client.run_forever()
        #rel.signal(2, rel.abort)
        #rel.dispatch()

    def GetChannelType(self):
        return "websocket"
    
if __name__ =="__main__":
    class Device:
        def __init__(self):
            self._deviceType = "wstype"
            self._deviceId = "001"
            self._channel = WebSocketChannel(url="ws://localhost:8081/ws/edge/iot?devicetype={deviceType}&deviceid={deviceId}".format(deviceType = self._deviceType, deviceId = self._deviceId))
            self._connectEvent = threading.Event()
            self._connectEvent.clear()
            self._channel.on_connect = self._onConnect
            self._channel.on_disconnect = self._onDisConnected
            self._pingThread = None
            self._propertyThread = None

        def _onConnect(self,ws):
            self._connectEvent.set()
            print("ws channel connected")

        def _onDisConnected(self,ws, close_status_code, close_msg):
            self._connectEvent.clear()
            print("channel disconnected")

        def _sendPing(self):
            while True:
                if self._connectEvent.is_set() is False:
                    time.sleep(3)
                    continue
                ping = {
                        "jsonrpc":"2.0",
                        "method": "internal.call",
                        "params": {
                            "topic": "d2cping/wstype/001",
                            "payload": {
                                "interval": 20,  
                                "ssh": "127.0.0.1:22",
                                "jupyter": "127.0.0.1:8890",
                                "cpu": 0.3,
                                "memory": 40,
                                "disk": 3.45,
                                "macAddress": "33.44.55.66",
                                "ip": "127.0.0.1",
                                "running": 123456
                            }
                        }
                }
                print("send ping---->")
                self._channel.Send(json.dumps(ping))
                time.sleep(20)

        def _sendProperty(self):
            prop1 = 1
            prop2 = 1
            while True:
                if self._connectEvent.is_set() is False:
                    time.sleep(3)
                prop = {
                    "jsonrpc": "2.0",
                    "method": "internal.call",
                    "params": {
                        "topic": "d2c/wstype/001/property",
                        "payload": {
                            "prop1": str(prop1),
                            "prop2": str(prop2)
                        }
                    }
                }
                prop1 = prop1 + 1
                prop2 = prop2 + 1
                print("send property++++>")
                self._channel.Send(json.dumps(prop))
                time.sleep(5)
                
        def startPingService(self):
            self._pingThread = threading.Thread(target=self._sendPing, args=())
            self._pingThread.isDaemon = True
            self._pingThread.start()

        def startPropService(self):
            self._propertyThread = threading.Thread(target=self._sendProperty, args=())
            self._propertyThread.isDaemon = True
            self._propertyThread.start()

        def Run(self):
            self.startPingService()
            self.startPropService()
            self._channel.Run()
            print("start run application")
    dev = Device()
    dev.Run()



