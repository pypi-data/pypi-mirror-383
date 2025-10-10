from enum import Enum
import time
from abc import ABC, abstractmethod
import serial
import threading
import struct

class SerialPortocolState(Enum):
    WAIT_ON_HEADER_0 = 1
    WAIT_ON_HEADER_1 = 2 
    WAIT_ON_ADDRESSED_NODE_ID = 3
    WAIT_ON_OWN_NODE_ID = 4
    WAIT_ON_COMMAND_ID = 5
    WAIT_ON_BYTECOUNT = 6
    WAIT_ON_DATA = 7
    WAIT_ON_LRC = 8

class OHandProtocol(Enum):
    Serial = 1
    Modbus = 2

class ProtocolParse(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def parse(self, byteData):
        pass

class _SerialChannel:
    createdChannel = {}
    lock = threading.Lock()
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=3) -> None:
        self._baudrate = baudrate
        self._port = port
        self._timeout = timeout
        self._serial = None
        self._lock = threading.Lock()
            
    def _read(self, readLength):
        try:
            value = self._serial.read(readLength)
            return value
        except:
            return None

    def SendAndWaitResponse(self, command, protocolParser, timeout):
        with self._lock:
            if self._serial is None or self._serial.is_open is False:
                try:
                    self._serial = serial.Serial(self._port, self._baudrate, timeout=self._timeout)
                except serial.SerialException:
                    #print("[Error]: error in open serial channel")
                    return None
            try:
                hasAttr = getattr(self._serial, 'flushInput', None)
                if hasAttr is not None:
                    self._serial.flushInput()
                else:
                    self._serial.reset_input_buffer()
                self._serial.write(command)
            except serial.SerialTimeoutException:
                #print("error about serial timeout")
                raise
            endTime = int(time.time() * 1000) + timeout
            protocolParser.reset()
            while int(time.time() * 1000) < endTime:
                value = self._serial.read(size=1)
                for _v in value:
                    ret = protocolParser.parse(_v)
                    if ret is not None:
                        return ret
            return None
        
def _createSerialChannel(port, baudrate, timeout):
    with _SerialChannel.lock:
        if port in _SerialChannel.createdChannel:
            return _SerialChannel.createdChannel[port]
        else:
            _SerialChannel.createdChannel[port] = _SerialChannel(port=port, baudrate=baudrate, timeout=timeout)
            return _SerialChannel.createdChannel[port]
        
class SerialProtocolParser(ProtocolParse):
    def __init__(self):
        self._state = SerialPortocolState.WAIT_ON_HEADER_0
        self._data= []
        self._DataLengthIndex = 5
        self._byteCount = 0

    def calcCrc(self):
        length = self._data[self._DataLengthIndex] + 4
        lrc = 0
        for idx in range(length):
            lrc ^= self._data[idx + 2]
        return lrc
    
    def reset(self):
        pass

    def parse(self, data):
        if self._state == SerialPortocolState.WAIT_ON_HEADER_0:
            if data == 0x55:
                self._data = []
                self._data.append(data)
                self._state = SerialPortocolState.WAIT_ON_HEADER_1
        elif self._state == SerialPortocolState.WAIT_ON_HEADER_1:
            if data == 0xaa:
                self._data.append(data)
                self._state = SerialPortocolState.WAIT_ON_ADDRESSED_NODE_ID
            else:
                self._state = SerialPortocolState.WAIT_ON_HEADER_0
        elif self._state == SerialPortocolState.WAIT_ON_ADDRESSED_NODE_ID:
            self._data.append(data)
            self._state = SerialPortocolState.WAIT_ON_OWN_NODE_ID
        elif self._state == SerialPortocolState.WAIT_ON_OWN_NODE_ID:
            self._data.append(data)
            self._state = SerialPortocolState.WAIT_ON_COMMAND_ID
        elif self._state == SerialPortocolState.WAIT_ON_COMMAND_ID:
            self._data.append(data)
            self._state = SerialPortocolState.WAIT_ON_BYTECOUNT
        elif self._state == SerialPortocolState.WAIT_ON_BYTECOUNT:
            self._data.append(data)
            self._byteCount = data
            if data > 0:
                self._state = SerialPortocolState.WAIT_ON_DATA
            else:
                self._state = SerialPortocolState.WAIT_ON_LRC
        elif self._state == SerialPortocolState.WAIT_ON_DATA:
            self._data.append(data)
            self._byteCount = self._byteCount - 1
            if self._byteCount == 0:
                self._state = SerialPortocolState.WAIT_ON_LRC
        elif self._state == SerialPortocolState.WAIT_ON_LRC:
            self._data.append(data)
            lrcData = self.calcCrc()
            if lrcData == data:
                return True
        return None
                
class SerialProtocolGenerator:
    def __init__(self, masterId, handId):
        self._masterId = masterId
        self._handId = handId
    
    def generate(self, sourceData):
        _data = []
        _data.append(self._handId)
        _data.append(self._masterId)
        _data += sourceData
        dataLength = len(_data)
        lrc = 0
        for i in range(dataLength):
            lrc ^= _data[i]
        retData = [0x55, 0xaa]
        retData += _data
        retData.append(lrc)
        return retData


class SerialProtocolCMD:
    HAND_CMD_SET_FINGER_PID = 0x45
    HAND_CMD_SET_FINGER_POS = 0x4c

class OHand:
    def __init__(self, port, baudrate, timeout, protocol = OHandProtocol.Serial):
        self._protocol = protocol
        self._masterId = 0x01
        self._handId = 0x02
        self._dataChannel = _createSerialChannel(port=port, baudrate=baudrate, timeout=timeout)

    @property
    def masterId(self):
        return self._masterId

    @masterId.setter
    def masterId(self, value):
        self._masterId = value

    @property
    def handId(self):
        return self._handId
    
    @handId.setter
    def handId(self, value):
        self._handId = value

    def _sendCmd(self, cmdData):
        generator = SerialProtocolGenerator(masterId=self._masterId, handId=self._handId)
        outdata = generator.generate(cmdData)
        ret = self._dataChannel.SendAndWaitResponse(outdata, SerialProtocolParser(), 2000)
        if ret is None:
            pass
            #print("[Error]: Failed to get response")

    def SetFingerPID(self,finger_id, p, i, d, j):
        payload = [finger_id]
        bap = bytearray(struct.pack("f", p))
        bai = bytearray(struct.pack("f", i))
        bad = bytearray(struct.pack("f", d))
        baj = bytearray(struct.pack("f", j))
        payload += list(bap)
        payload += list(bai)
        payload += list(bad)
        payload += list(baj)
        data = [SerialProtocolCMD.HAND_CMD_SET_FINGER_PID, len(payload)]
        data += payload
        self._sendCmd(data)
    
    def SetFingerPos(self, finger_id, pos, speed):
        payload= [finger_id]
        payload += list(struct.pack("H", pos))
        payload.append(speed)
        data = [SerialProtocolCMD.HAND_CMD_SET_FINGER_POS, len(payload)]
        data += payload
        self._sendCmd(data)


def main():
    hand = OHand(port="COM12", baudrate=115200, timeout=3)
    hand.masterId= 0x01
    hand.handId=0x02
    hand.SetFingerPos(1, 0, 250)
    time.sleep(2)
    hand.SetFingerPos(1, 60000, 250)
    time.sleep(2)
    

if __name__ == "__main__":
    main()