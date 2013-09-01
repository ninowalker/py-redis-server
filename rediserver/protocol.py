"""
Provides the codecs for parsing/sending messages.

See http://redis.io/topics/protocol for more info.
"""

import redis.connection


class InputParser(redis.connection.PythonParser):
    """Subclasses the client PythonParser to spoof the internals of reading off a socket."""
    def __init__(self, lines, encoding=None):
        super(InputParser, self).__init__()
        self.data = lines
        self.pos = 0
        self.encoding = encoding

    def read(self, _length=None):
        """Override; read from memory instead of a socket."""
        self.pos += 1
        data = self.data[self.pos - 1]
        if self.encoding:
            data.decode(self.encoding)
        return data


class ResponseEncoder(object):
    """Writes data to a file descriptor as dicated by the Redis Protocol."""
    def __init__(self, sock):
        self._fp = sock

    def bulk(self, value):
        data = ["$", str(len(value)), "\r\n", unicode(value), "\r\n"]
        self._fp.write("".join(data))

    def error(self, msg):
        data = ['-', unicode(msg), "\r\n"]
        self._fp.write("".join(data))

    def encode(self, value):
        if isinstance(value, (list, tuple)):
            self._fp.write('*%d\r\n' % len(value))
            for v in value:
                self.bulk(v)
        elif isinstance(value, (int, long)):
            self._fp.write(':%d\r\n' % value)
        elif isinstance(value, bool):
            self._fp.write(':%d\r\n' % (1 if value else 0))
        else:
            self.bulk(v)

    def status(self, msg="OK"):
        self._fp.write("+%s\r\n" % msg)
