import socket
from contextlib import suppress
from select import POLLIN, POLLOUT

from tear.libs.logging import logger
from tear.libs.base import YieldPoint, run_till_yieldpoint
from tear.libs.singletons import poll_object



class TCPSocket:
    def __init__(self):
        self.sock = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)

    def connect(self, addr):
        return _ConnectSocket(self.sock, addr)

    def send(self, bytes):
        return _SendSocket(self.sock, bytes)

    def recv(self, bufsize):
        return _RecvSocket(self.sock, bufsize)

    def close(self):
        return _CloseSocket(self.sock)


class _ConnectSocket(YieldPoint):
    def __init__(self, sock, addr):
        self.addr = addr
        super().__init__(sock)

    def handle_block(self):
        poll_object.register_or_modify(self, POLLOUT)

    def handle_proceed(self):
        with suppress(OSError):
            self.sock.connect(self.addr)
        logger.debug('succeeded in connecting %s', self.addr)


class _SendSocket(YieldPoint):

    def __init__(self, sock, bytes):
        self.bytes = bytes
        super().__init__(sock)

    def handle_block(self):
        poll_object.register_or_modify(self, POLLOUT)

    def handle_proceed(self):
        to_send = self.bytes
        self.sock.send(to_send)
        logger.debug('succeeded in sending "%s"', to_send)


class _RecvSocket(YieldPoint):
    def __init__(self, sock, bufsize):
        self.bufsize = bufsize
        super().__init__(sock)

    def handle_block(self):
        poll_object.register_or_modify(self, POLLIN)

    def handle_proceed(self):
        recv =  self.sock.recv(self.bufsize)
        logger.debug('succeeded in receiving "%s"', recv)
        self.result = recv


class _CloseSocket(YieldPoint):
    def handle_block(self):
        poll_object.register_or_modify(self.POLLOUT)

    def handle_proceed(self):
        self.sock.close()
        logger.debug('succeeded in closing fd %s', self.fileno())
