#! /usr/bin/python3.5

import socket
import logging
from select import poll, POLLIN, POLLOUT, POLLHUP, POLLERR, POLLNVAL
from collections import defaultdict

RECV_BUFF = 2048
PORT = 5000
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.setblocking(False)
    listener.bind(('', PORT))
    listener.listen(50)

    sockets = {listener.fileno(): listener}
    bytes_to_send = bytes_received = defaultdict(bytes)

    poll_object = poll()
    poll_object.register(listener, POLLIN)
    while True:
        fd, event = poll_object.poll()[0]
        sock = sockets[fd]

        if event & (POLLHUP | POLLERR | POLLNVAL):
            rb = bytes_received.pop(sock, b'')
            sb = bytes_to_send.pop(sock, b'')
            if rb:
                logger.error('received %s from client %s but aborted', rb, fd)
            elif sb:
                logger.error('prepared to send %s to client %s but aborted', sb, fd)
            else:
                logger.info('succeeded in closing %s normally', fd)
            poll_object.unregister(fd)
            del sockets[fd]

        elif sock is listener:
            sock, address = listener.accept()
            logger.info('succeeded in accepting client %s from %s', sock.fileno(), address)
            sock.setblocking(False)
            sockets[sock.fileno()] = sock
            poll_object.register(sock, POLLIN)

        elif event & POLLIN:
            data = sock.recv(RECV_BUFF)
            if not data:
                logger.debug('succeeded in receiving FIN from client %s', fd)
                sock.close()
            else:
                logger.debug('succeeded in receiving %s from client %s', data, fd)
                bytes_received[sock] += data
                if data.endswith(b'\n'):
                    poll_object.modify(sock, POLLOUT)

        elif event & POLLOUT:
            data = bytes_to_send.pop(sock, b'')
            sent = sock.send(data)
            logger.debug('succeeded in sending %s bytes to client %s', sent, fd)
            if sent < len(data):
                bytes_to_send[sock] = data[sent:]
            else:
                poll_object.modify(sock, POLLIN)


if __name__ == '__main__':
    main()
