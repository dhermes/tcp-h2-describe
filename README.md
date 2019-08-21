# `tcp-h2-describe`

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
   --- decoded as raw bytes ---
   b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'
----------------------------------------
Frame Length = 36 (00 00 24)
Frame Type = SETTINGS (04)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Settings =
   SETTINGS_HEADER_TABLE_SIZE: 4096 (00 01 00 00 10 00)
   SETTINGS_ENABLE_PUSH: 1 (00 02 00 00 00 01)
   SETTINGS_INITIAL_WINDOW_SIZE: 65535 (00 04 00 00 ff ff)
   SETTINGS_MAX_FRAME_SIZE: 16384 (00 05 00 00 40 00)
   SETTINGS_MAX_CONCURRENT_STREAMS: 100 (00 03 00 00 00 64)
   SETTINGS_MAX_HEADER_LIST_SIZE: 65536 (00 06 00 01 00 00)
----------------------------------------
Frame Length = 6 (00 00 06)
Frame Type = SETTINGS (04)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Settings =
   SETTINGS_ENABLE_PUSH: 0 (00 02 00 00 00 00)
----------------------------------------
============================================================
server(localhost:8080)->proxy->client(127.0.0.1:59600)

Frame Length = 36 (00 00 24)
Frame Type = SETTINGS (04)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Settings =
   SETTINGS_HEADER_TABLE_SIZE: 4096 (00 01 00 00 10 00)
   SETTINGS_ENABLE_PUSH: 0 (00 02 00 00 00 00)
   SETTINGS_INITIAL_WINDOW_SIZE: 65535 (00 04 00 00 ff ff)
   SETTINGS_MAX_FRAME_SIZE: 16384 (00 05 00 00 40 00)
   SETTINGS_MAX_CONCURRENT_STREAMS: 100 (00 03 00 00 00 64)
   SETTINGS_MAX_HEADER_LIST_SIZE: 65536 (00 06 00 01 00 00)
----------------------------------------
============================================================
server(localhost:8080)->proxy->client(127.0.0.1:59600)

Frame Length = 0 (00 00 00)
Frame Type = SETTINGS (04)
Flags = ACK:0x1 (01)
Stream Identifier = 0 (00 00 00 00)
----------------------------------------
Frame Length = 0 (00 00 00)
Frame Type = SETTINGS (04)
Flags = ACK:0x1 (01)
Stream Identifier = 0 (00 00 00 00)
----------------------------------------
============================================================
client(127.0.0.1:59600)->proxy->server(localhost:8080)

Frame Length = 0 (00 00 00)
Frame Type = SETTINGS (04)
Flags = ACK:0x1 (01)
Stream Identifier = 0 (00 00 00 00)
----------------------------------------
============================================================
client(127.0.0.1:59600)->proxy->server(localhost:8080)

Frame Length = 11 (00 00 0b)
Frame Type = HEADERS (01)
Flags = END_STREAM:0x1 | END_HEADERS:0x4 (05)
Stream Identifier = 1 (00 00 00 01)
Headers =
   ':method' -> 'GET'
   ':scheme' -> 'http'
   ':authority' -> 'localhost'
   ':path' -> '/'
Hexdump =
   82 86 41 86 a0 e4 1d 13 9d 09 84
----------------------------------------
============================================================
server(localhost:8080)->proxy->client(127.0.0.1:59600)

Frame Length = 34 (00 00 22)
Frame Type = HEADERS (01)
Flags = END_HEADERS:0x4 (04)
Stream Identifier = 1 (00 00 00 01)
Headers =
   ':status' -> '200'
   'server' -> 'basic-h2-server/1.0'
   'content-length' -> '78'
   'content-type' -> 'application/json'
Hexdump =
   88 76 8e 8c 68 31 16 9c 4b 20 b6 77 2d 8c 05 70
   7f 5c 82 75 ef 5f 8b 1d 75 d0 62 0d 26 3d 4c 74
   41 ea
----------------------------------------
Frame Length = 78 (00 00 4e)
Frame Type = DATA (00)
Flags = END_STREAM:0x1 (01)
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
