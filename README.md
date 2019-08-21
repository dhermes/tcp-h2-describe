# `tcp-h2-describe`

[![PyPI package](https://img.shields.io/pypi/v/tcp-h2-describe.svg)](https://pypi.org/project/tcp-h2-describe/)

> Python library and CLI for running an HTTP/2 proxy that describes each frame

## Install

```
python3 -m pip install --upgrade tcp-h2-describe
```

## Usage

For example, on a machine where there is a local HTTP/2 server running on
port 50051:

```
$ tcp-h2-describe --server-port 50051
Starting tcp-h2-describe proxy server on port 24909
  Proxying server located at localhost:50051
...
$ # OR
$ python -m tcp_h2_describe --server-port 50051
Starting tcp-h2-describe proxy server on port 24909
  Proxying server located at localhost:50051
...
```

Options also exist to customize the port where the `tcp-h2-describe` proxy
runs as well as the remote server that is being proxied:

```
$ python -m tcp_h2_describe --help
usage: tcp-h2-describe [-h] [--proxy-port PROXY_PORT]
                       [--server-host SERVER_HOST] [--server-port SERVER_PORT]

Run `tcp-h2-describe` reverse proxy server. This will forward traffic to a
proxy port along to an already running HTTP/2 server. For each HTTP/2 frame
forwarded (either client->server or server->client) a description will be
printed to the console explaining what each byte in the frame means.

optional arguments:
  -h, --help            show this help message and exit
  --proxy-port PROXY_PORT
                        The port that will be used for running the "describe"
                        proxy. (default: 24909)
  --server-host SERVER_HOST
                        The hostname for the server that is being proxied.
                        (default: None)
  --server-port SERVER_PORT
                        The port for the server that is being proxied.
                        (default: 80)
```

To use directly from Python code

```python
import tcp_h2_describe

proxy_port = 13370
server_port = 50051
tcp_h2_describe.serve_proxy(proxy_port, server_port)

# OR: Spawn a thread to avoid blocking
import threading

server_thread = threading.Thread(
    target=tcp_h2_describe.serve_proxy,
    args=(proxy_port, server_port),
)
server_thread.start()
```

For example, using an `h2` [example][3] that echos back HTTP/2 headers:

```
$ python3 -m virtualenv h2-example
$ h2-example/bin/python -m pip install \
>   h2==2.6.2 hpack==3.0.0 hyper==0.7.0 hyperframe==3.2.0
$ h2-example/bin/python _bin/h2_server.py > /dev/null 2>&1 &
[1] 7060
$ python -m tcp_h2_describe --server-port 8080
Starting tcp-h2-describe proxy server on port 24909
  Proxying server located at localhost:8080
...
```

If we hit the proxy directly

```
$ h2-example/bin/hyper --h2 GET http://localhost:24909
{":method": "GET", ":scheme": "http", ":authority": "localhost", ":path": "/"}
```

we'll see all the frames:

```
...
  Proxying server located at localhost:8080
Accepted connection from 127.0.0.1:59600
============================================================
client(127.0.0.1:59600)->proxy->server(localhost:8080)

Client Connection Preface
50 52 49 20 2a 20 48 54 54 50 2f 32 2e 30 0d 0a
0d 0a 53 4d 0d 0a 0d 0a
   ... decoded as raw bytes ...
   b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'
----------------------------------------
Frame Length = 36 (00 00 24)
Frame Type = 4 (04)
Flags = 0 (00)
Stream Identifier = 0 (00 00 00 00)
Frame Payload = b'\x00\x01\x00\x00\x10\x00\x00\x02\x00\x00\x00\x01\x00\x04\x00\x00\xff\xff\x00\x05\x00\x00@\x00\x00\x03\x00\x00\x00d\x00\x06\x00\x01\x00\x00'
----------------------------------------
Frame Length = 6 (00 00 06)
Frame Type = 4 (04)
Flags = 0 (00)
Stream Identifier = 0 (00 00 00 00)
Frame Payload = b'\x00\x02\x00\x00\x00\x00'
----------------------------------------
============================================================
server(localhost:8080)->proxy->client(127.0.0.1:59600)

Frame Length = 36 (00 00 24)
Frame Type = 4 (04)
Flags = 0 (00)
Stream Identifier = 0 (00 00 00 00)
Frame Payload = b'\x00\x01\x00\x00\x10\x00\x00\x02\x00\x00\x00\x00\x00\x04\x00\x00\xff\xff\x00\x05\x00\x00@\x00\x00\x03\x00\x00\x00d\x00\x06\x00\x01\x00\x00'
----------------------------------------
============================================================
server(localhost:8080)->proxy->client(127.0.0.1:59600)

Frame Length = 0 (00 00 00)
Frame Type = 4 (04)
Flags = 1 (01)
Stream Identifier = 0 (00 00 00 00)
Frame Payload = b''
----------------------------------------
Frame Length = 0 (00 00 00)
Frame Type = 4 (04)
Flags = 1 (01)
Stream Identifier = 0 (00 00 00 00)
Frame Payload = b''
----------------------------------------
============================================================
client(127.0.0.1:59600)->proxy->server(localhost:8080)

Frame Length = 0 (00 00 00)
Frame Type = 4 (04)
Flags = 1 (01)
Stream Identifier = 0 (00 00 00 00)
Frame Payload = b''
----------------------------------------
============================================================
client(127.0.0.1:59600)->proxy->server(localhost:8080)

Frame Length = 11 (00 00 0b)
Frame Type = 1 (01)
Flags = 5 (05)
Stream Identifier = 1 (00 00 00 01)
Frame Payload = b'\x82\x86A\x86\xa0\xe4\x1d\x13\x9d\t\x84'
----------------------------------------
============================================================
server(localhost:8080)->proxy->client(127.0.0.1:59600)

Frame Length = 34 (00 00 22)
Frame Type = 1 (01)
Flags = 4 (04)
Stream Identifier = 1 (00 00 00 01)
Frame Payload = b'\x88v\x8e\x8ch1\x16\x9cK \xb6w-\x8c\x05p\x7f\\\x82u\xef_\x8b\x1du\xd0b\r&=LtA\xea'
----------------------------------------
Frame Length = 78 (00 00 4e)
Frame Type = 0 (00)
Flags = 1 (01)
Stream Identifier = 1 (00 00 00 01)
Frame Payload = b'{":method": "GET", ":scheme": "http", ":authority": "localhost", ":path": "/"}'
----------------------------------------
Done redirecting socket for client(127.0.0.1:59600)->proxy->server(localhost:8080)
```

## Development

To work on adding a feature or to run the tests, see the [DEVELOPMENT doc][1]
for more information on how to get started.

## License

`tcp-h2-describe` is made available under the Apache 2.0 License. For more
details, see the [LICENSE][2].

[1]: https://github.com/dhermes/tcp-h2-describe/blob/master/README.md
[2]: https://github.com/dhermes/tcp-h2-describe/blob/master/LICENSE
[3]: https://python-hyper.org/projects/h2/en/stable/basic-usage.html
