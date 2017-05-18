#! /usr/bin/python3.5

import socket
from select import select
from logging import getLogger
from collections import defaultdict

RECV_BUFF = 2048
PORT = 5000
logger = getLogger(__name__)

def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.setblocking(False)
    listener.bind(('', PORT))
    listener.listen(50)

    to_send = defaultdict(list)
    to_read, to_write, to_exc = [listener], [], []
    while True:
        readable, writable, _ = select(to_read, to_write, to_exc)

        for sock in readable:
            if sock is listener:
                sock, addr = listener.accept()
                logger.error('succeeded in accepting %s from %s', sock.fileno(), addr)
                to_read.append(sock)
            else:
                rv = sock.recv(RECV_BUFF)
                if not rv:
                    to_send[sock] = b''.join(to_send[sock])
                    to_write.append(sock)
                    to_read.remove(sock)
                else:
                    logger.error('succeeded in receiving %s bytes from %s', len(rv), sock.fileno())
                    to_send[sock].append(rv)

        for sock in writable:
            content = to_send[sock]
            sent = sock.send(content)
            if sent < len(content):
                to_send[sock] = content[:-sent]
                logger.error('succeeded in sending %s bytes to %s, remaining', sent, sock.filenoe())
            else:
                del to_send[sock]
                to_write.remove(sock)
                logger.error('succeeded in send %s bytes to %s, preparing to close', sent, sock.fileno())


if __name__ == '__main__':
    main()
