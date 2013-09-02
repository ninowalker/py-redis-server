# py-redis-server

With this module, you can stand up a python TCP server that speaks the Redis Protocol. 
The [Redis Protocol](http://redis.io/topics/protocol) is light-weight wire protocol with
clients in every mature language. These clients are designed for robust and persistent connections
suitable for low latency LAN network traffic, making them ideal for IPC.

This module includes two parts: the [protocol codecs](/ninowalker/py-redis-server/blob/rediserver/protocol.py),
and a [server](/ninowalker/py-redis-server/blob/rediserver/net.py). The server uses the 
[Asyncore module](http://www.python.org/doc//current/library/asyncore.html),
a non-blocking framework bundled with Python since (at least) 2.4.

# Benchmarks

Run on a Macbook Pro, 2.7GHz i7, 8GB RAM.

Locally, redis is blazing fast:

```
$ redis-benchmark -p 6379 incr foo 1
====== incr foo 1 ======
  10000 requests completed in 0.17 seconds
  50 parallel clients
  3 bytes payload
  keep alive: 1
...
60606.06 requests per second
```

Locally, the python server is pretty good, and certainly good for a  

```
$ redis-benchmark -p 33333 incr foo 1
====== incr foo 1 ======
  10000 requests completed in 0.73 seconds
  50 parallel clients
  3 bytes payload
  keep alive: 1
...
13888.89 requests per second
```

# Prerequisites

`redis >= 2.4.1`

# An echo server

```python

from rediserver.net import AsyncoreServer
import asyncore

def echo(cmd, response, request):
    """Echo back input from the client.
    `cmd`: an array of strings that constitute the command, e.g. ['incr', 'foo', '1']
    `response`: a handle for sending data. Supports:
       .encode(list|tuple|bool|int|long|string)
       .status(msg="OK")
       .error(msg)
    `request`: the connection handler, generally unused.
    """
    response.encode(cmd)


port = 12345
s = AsyncoreServer('', port, callback=echo)
asyncore.loop() # start the event loop.
```

# License (MIT)

```
Copyright (c) 2013 Nino Walker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
