from select import poll

from tear.libs.logging import logger


fd_sock_mapping = {}
yieldpoint_gen_mapping = {}

class Poll:
    def __init__(self):
        self._poll = poll()

    def __getattr__(self, attr):
        return getattr(self._poll, attr)

    def register_or_modify(self, fd, eventmask):
        try:
            self._poll.modify(fd, eventmask)
            logger.debug('succeeded in modifying fd %s with event %s', fd, eventmask)
        except FileNotFoundError:
            self._poll.register(fd, eventmask)
            logger.debug('succeeded in register fd %s with event %s', fd, eventmask)


poll_object = Poll()
