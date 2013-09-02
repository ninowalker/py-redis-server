import sys
import os
import glob
import asyncore
from collections import defaultdict

# make demos easy.
__parent = os.path.join(os.path.dirname(__file__), "../")
sys.path.append(__parent)
sys.path.extend(glob.glob(os.path.join(__parent, "*.egg")))

from rediserver.net import AsyncoreServer

_counter = iter(xrange(1000000000)) # used by the count module
_incr = defaultdict(int)


def echo(cmd, response, request):
    """Echo back input from the client.
    `cmd`: an array of strings that constitute the command, e.g. ['incr', 'foo', '1']
    `response`: a handle for responding. Supports:
       .encode(list|tuple|bool|int|long|string)
       .status(msg="OK")
       .error(msg)
    `request`: the connection handler, generally unused.
    """
    response.encode(cmd)


def count(_cmd, response, _handler):
    """Report the count of requests."""
    value = _counter.next()
    response.encode(value)


def summer(cmd, response, _handler):
    """Return the sum of all the numbers sent in the command."""
    response.encode(sum(map(int, cmd)))


def incr(cmd, response, request):
    v = _incr[cmd[1]]
    _incr[cmd[1]] += int(cmd[2])
    response.encode(v)

MODE = {'echo': echo, 'count': count, 'sum': summer, 'incr': incr}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: python %s <port> [<echo|count|sum|incr>]"
        sys.exit(1)
    port, mode = sys.argv[1:]
    mode = MODE.get(sys.argv[2], 'echo')
    if not mode:
        print "usage: python %s <port> <echo|count|sum|incr>"
        sys.exit(1)

    s = AsyncoreServer('', int(port), callback=mode)
    print "%s server running on port %s" % (sys.argv[2], port)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print "Crtl+C pressed. Shutting down."
