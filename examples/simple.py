import sys
import os
import glob
import asyncore

# make demos easy.
__parent = os.path.join(os.path.dirname(__file__), "../")
sys.path.append(__parent)
sys.path.extend(glob.glob(os.path.join(__parent, "*.egg")))

from rediserver.net import AsyncoreServer

_counter = iter(xrange(1000000000))


def echo(cmd, response, _handler):
    """Echo back input from the client."""
    response.encode(cmd)


def count(_cmd, response, _handler):
    """Report the count of requests."""
    value = _counter.next()
    response.encode(value)


def summer(cmd, response, _handler):
    """Return the sum of all the numbers sent in the command."""
    response.encode(sum(map(int, cmd)))


MODE = {'echo': echo, 'count': count, 'sum': summer}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: python %s <port> <echo|count|sum>"
        sys.exit(1)
    port, mode = sys.argv[1:]
    mode = MODE.get(sys.argv[2])
    if not mode:
        print "usage: python %s <port> <echo|count|sum>"
        sys.exit(1)

    s = AsyncoreServer('', int(port), callback=mode)
    print "%s server running on port %s" % (sys.argv[2], port)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print "Crtl+C pressed. Shutting down."
