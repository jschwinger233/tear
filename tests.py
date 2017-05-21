#! /usr/bin/python3.5

import urllib.parse

from tear.ioloop import IOLoop
from tear.libs.aiosocket import TCPSocket

HTTP_MSG = 'GET {path} HTTP/1.1\nHost: {netloc}\nAccept: */*\nUser-Agent: python-tear/0.1\n\n'


def requests_get(url):
    sock = TCPSocket()
    scheme, netloc, path, params, query, fragment = urllib.parse.urlparse(url)
    yield sock.connect((netloc, 80))
    http_msg = HTTP_MSG.format(**locals()).encode()
    yield sock.send(http_msg)
    page = yield sock.recv(4086)
    yield sock.close()
    return page


def request_len(url):
    page = yield from requests_get(url)
    print('got {} bytes from url {}'.format(len(page), url))


def request(url):
    yield from request_len(url)


if __name__ == '__main__':
    task1 = request('http://www.google.com/')
    task2 = request('http://www.baidu.com/')
    ioloop = IOLoop()
    ioloop.add_task([task1, task2])
    ioloop.run()

