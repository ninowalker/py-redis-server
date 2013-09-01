import sys
import os
import glob

__parent = os.path.join(os.path.dirname(__file__), "../")

sys.path.append(__parent)
sys.path.extend(glob.glob(os.path.join(__parent, "*.egg")))

from rediserver.net import AsyncoreServer


def echo(cmd, response, _handler):
    """Echo back input from the client."""
    response.encode(cmd)

if __name__ == "__main__":
    port = int(sys.argv[1])
    s = AsyncoreServer('', port, callback=echo)
    print "Echo RediServer running on port %s" % port
    s.start()