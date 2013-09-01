import asynchat
import cStringIO
import select
from rediserver.protocol import InputParser, ResponseEncoder
import asyncore
import socket


class SocketStream(object):
    def __init__(self, sock):
        """Initiate a socket (non-blocking) and a buffer"""
        self.sock = sock
        self.buffer = cStringIO.StringIO()
        self.closed = 1   # compatibility with SocketServer

    def write(self, data):
        """Buffer the input, then send as many bytes as possible"""
        self.buffer.write(data)
        if self.writable():
            buff = self.buffer.getvalue()
            # next try/except clause suggested by Robert Brown
            try:
                sent = self.sock.send(buff)
            except:
                # Catch socket exceptions and abort
                # writing the buffer
                sent = len(data)

            # reset the buffer to the data that has not yet be sent
            self.buffer = cStringIO.StringIO()
            self.buffer.write(buff[sent:])

    def finish(self):
        """When all data has been received, send what remains
        in the buffer"""
        data = self.buffer.getvalue()
        # send data
        while len(data):
            while not self.writable():
                pass
            sent = self.sock.send(data)
            data = data[sent:]

    def writable(self):
        """Used as a flag to know if something can be sent to the socket"""
        return select.select([], [self.sock], [])[1]


class RedisProtocolHandler(asynchat.async_chat):
    def __init__(self, conn, addr, server):
        asynchat.async_chat.__init__(self, conn)
        self.client_address = addr
        self.connection = conn
        self.server = server
        self.set_terminator('\r\n')
        self.rfile = []
        self.found_terminator = self.handle_header
        self.wfile = SocketStream(self.connection)

    def collect_incoming_data(self, data):
        """Collect the data arriving on the connection."""
        self.rfile.append(data)

    def handle_header(self):
        """Determine how many lines to read."""
        self.numlines = int(self.rfile[0][1:]) * 2
        self.found_terminator = self.handle_line

    def handle_line(self):
        self.numlines -= 1
        if self.numlines != 0:
            return
        cmd = InputParser(self.rfile).read_response()
        encoder = ResponseEncoder(self.wfile)

        self.server.process_cmd(cmd, encoder, self)

        self.wfile.finish()
        self.found_terminator = self.handle_header


class Server(asyncore.dispatcher):
    _io_loop_started = False

    def process_cmd(self, cmd, encoder, handler):
        abstract #@UndefinedVariable

    def __init__(self, ip, port, handler=RedisProtocolHandler, backlog=1024):
        self.ip = ip
        self.port = port
        self.handler = handler
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        self.set_reuse_addr()
        self.bind((ip, port))

        self.listen(backlog)

    def handle_accept(self):
        try:
            conn, addr = self.accept()
        except socket.error:
            self.log_info('warning: server accept() threw an exception', 'warning')
            return
        except TypeError:
            self.log_info('warning: server accept() threw EWOULDBLOCK', 'warning')
            return
        # creates an instance of the handler class to handle the request/response
        # on the incoming connexion
        self.handler(conn, addr, self)

    def start(self, start_io_loop=True, **loop_kwargs):
        if self.__class__._io_loop_started or not start_io_loop:
            return
        self.__class__._io_loop_started = True
        try:
            asyncore.loop(**loop_kwargs)
        except KeyboardInterrupt:
            print "Crtl+C pressed. Shutting down."