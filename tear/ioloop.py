#! /usr/bin/python3.5

from contextlib import suppress
from select import POLLHUP, POLLERR, POLLNVAL

from tear.libs.logging import logger
from tear.libs.base import run_till_yieldpoint
from tear.libs.singletons import yieldpoint_gen_mapping, fd_sock_mapping, poll_object


ioloop = None


class IOLoop:
    def __new__(cls, *args, **kws):
        global ioloop
        if ioloop:
            return ioloop
        ioloop = super().__new__(cls, *args, **kws)
        return ioloop

    def __init__(self):
        self.tasks = []

    def add_task(self, tasks):
        self.tasks.extend(tasks)

    def poll_forever(self, poll_object):
        while True:
            for fd, event in poll_object.poll():
                yield fd, event

    def run(self):
        for task in self.tasks:
            with suppress(StopIteration):
                run_till_yieldpoint(task)

        for fd, event in self.poll_forever(poll_object):
            sock = fd_sock_mapping[fd]

            if event & (POLLHUP | POLLERR | POLLNVAL):
                logger.info('preparing to close fd %s', fd)
                poll_object.unregister(fd)
                del yieldpoint_gen_mapping[sock]
                del fd_sock_mapping[fd]

            else:
                logger.debug('succeeded in getting event %s for fd %s', event, fd)
                generator = yieldpoint_gen_mapping[sock]
                sock.handle_resume()
                with suppress(StopIteration):
                    run_till_yieldpoint(generator, sock.result)
