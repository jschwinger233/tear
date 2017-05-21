from tear.libs.logging import logger
from tear.libs.singletons import fd_sock_mapping, yieldpoint_gen_mapping

BLOCK, PROCEED = 0, 1


class YieldPoint:
    def __init__(self, sock):
        self.sock = sock
        self.result = None

    def fileno(self):
        return self.sock.fileno()

    def handle_block(self):
        raise NotImplementedError

    def handle_yield(self):
        try:
            self.handle_proceed()
        except BlockingIOError:
            logger.debug('failed in proceeding, preparing to poll')
            self.handle_block()
            return BLOCK
        else:
            logger.debug('succeeded in proceeding')
            return PROCEED

    def handle_proceed(self):
        raise NotImplementedError

    def handle_resume(self):
        self.handle_proceed()


def run_till_yieldpoint(generator, result=None):
    yielded = generator.send(result)

    while not isinstance(yielded, YieldPoint):
        yielded = next(generator)
    else:
        res = yielded.handle_yield()
        if res == BLOCK:
            fd_sock_mapping[yielded.fileno()] = yielded
            yieldpoint_gen_mapping[yielded] = generator
        else:
            run_till_yieldpoint(generator, yielded.result)
