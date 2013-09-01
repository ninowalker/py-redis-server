import sys
import os
import glob

__parent = os.path.join(os.path.dirname(__file__), "../")

sys.path.append(__parent)
sys.path.extend(glob.glob(os.path.join(__parent, "*.egg")))

from rediserver.net import AsyncoreServer


class EchoServer(AsyncoreServer):
    def process_cmd(self, cmd, encoder, _handler):
        encoder.encode(cmd)

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1])
    s = EchoServer('', port)
    print "Echo RediServer running on port %s" % port
    s.start()