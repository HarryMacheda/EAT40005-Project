from abstracts.AAdapter import AAdapter
from abstracts.ASocket import ASocket
import socket

#To do import these depending on adapter
START_CODE:bytes = b'\xFF\xFF\xFF\xFF'
END_CODE:bytes = b'\x00\x00\x00\x00'
MESSAGE_LENGTH = 1024
#Socket implimentation with adapter
class AdaptedSocket(ASocket):
    def __init__(self, ip: str, port: int, adapter: AAdapter):
        self.adapter = adapter
        super().__init__(ip, port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._isBound = False

    def SendMessage(self, object: object):
        if (self._isBound == False):
            self._socket.bind((self.ip, self.port))
            self._socket.listen()
            self._isBound = True
            connection, address = self._socket.accept()
            self.connection = connection
        data = self.adapter.Encode(object)
        #assume data is byte array
        if (self.connection):
            length = len(data)
            sent = 0
            while sent < length:  
                end = min(sent + MESSAGE_LENGTH, length) # either chunk of send whole thing  
                chunk = data[sent:end]  
                self.connection.send(chunk)
                sent += MESSAGE_LENGTH

    def RunListener(self):
        self._socket.connect((self.ip, self.port))
        buffer = bytearray()
        reading = False

        while True:
            data = self._socket.recv(MESSAGE_LENGTH)
            buffer.extend(data)

            if not reading and START_CODE in buffer:
                reading = True
                start_index = buffer.index(START_CODE)
                buffer = buffer[start_index:]

            if reading and END_CODE in buffer:
                self._handler(self.adapter.Decode(buffer))
                reading = False
                buffer = bytearray()