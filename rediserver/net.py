from logging import getLogger
from rediserver.protocol import InputParser, Response
import asynchat
import asyncore
import cStringIO
import socket

LOG = getLogger(__name__)


class RedisProtocolHandler(asynchat.async_chat):
    """
    Handler responsible for decoding wire payloads and dispatching
    to the server's callback.
    """

    LINE_FEED = '\r\n'

    def __init__(self, conn, addr, server):
        asynchat.async_chat.__init__(self, conn)
        self.client_address = addr
        self.connection = conn
        self.server = server
        self.data = []
        self.wfile = cStringIO.StringIO() #SocketStream(self.connection)

        self.set_terminator(self.LINE_FEED)
        self.found_terminator = self._parse_header
        self.can_read = True

    def readable(self):
        # we should not read before sending our last paylaod
        return self.can_read

    def close_when_done(self):
        # unblock for reading after a payload is sent.
        self.can_read = True

    def collect_incoming_data(self, data):
        """Collect the data arriving on the connection."""
        self.data.append(data)

    def handle_expt(self):
        # called when there's an exception
        self.close()

    def handle_close(self):
        # called when the write buffer is empty.
        self.can_read = True

    def _parse_header(self):
        """Determine how many lines to read."""
        self.numlines = int(self.data[0][1:])
        # the next line is a length line
        self.found_terminator = self._parse_length

    def _parse_length(self):
        """Read a *<len> line."""
        length = int(self.data[-1][1:])
        self.set_terminator(length)
        self.found_terminator = self._parse_line

    def _parse_feed(self):
        """_parse a feed after raw data."""
        if self.numlines <= 0:
            self.found_terminator = self._parse_header
        else:
            self.found_terminator = self._parse_length

    def _parse_line(self):
        # parse a line payload
        self.numlines -= 1
        self.set_terminator(self.LINE_FEED)
        self.found_terminator = self._parse_feed
        if self.numlines > 0:
            return
        self.can_read = False
        self._process_data()

    def _process_data(self):
        response = Response(self.wfile.write)
        try:
            cmd = InputParser(self.data).read_response()
            self.server._callback(cmd, response, self)
            if not response.dirty:
                raise Exception("no response")
        except Exception, e:
            response.error(u"ERR: %s" % e)
            raise
        finally:
            resp = self.wfile.getvalue()
            self.wfile = cStringIO.StringIO()
            self.data = []

            # write the data out async; close_when_done actually
            # causes handle_close to be called, and we unblock and
            # enable reads again.
            self.push(resp)
            self.close_when_done()


class AsyncoreServer(asyncore.dispatcher):
    protocol_handler = RedisProtocolHandler
    allow_address_reuse = True
    backlog = 1024

    def __init__(self, ip, port, callback, ):
        self.ip = ip
        self.port = port
        self._callback = callback
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.allow_address_reuse:
            self.set_reuse_addr()
        self.bind((ip, port))
        self.listen(self.backlog)

    def serve_forever(self):
        """Starts the asyncore IO loop."""
        asyncore.loop()

    def handle_accept(self):
        try:
            conn, addr = self.accept()
        except socket.error:
            LOG.warning('socket.error thrown by accept()')
        except TypeError:
            LOG.warning('EWOULDBLOCK thrown by accept()')
        else:
            self.protocol_handler(conn, addr, self)
