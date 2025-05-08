from abstracts.AAdapter import AAdapter
from abstracts.ASocket import ASocket
import socket

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
        if (self.connection):           
            self.connection.sendall(str(data).encode())

    def RunListener(self):
        self._socket.connect((self.ip, self.port))
        while True:
            data = self._socket.recv(1024 * 1000 * 1000)
            if not data:
                break
            self._handler(self.adapter.Decode(data.decode()))