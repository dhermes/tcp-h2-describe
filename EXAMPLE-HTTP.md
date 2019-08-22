# Example With HTTP (over HTTP/2)

Using an `h2` [example][1] that echoes back HTTP/2 headers:

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

Client Connection Preface = b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'
Hexdump (Client Connection Preface) =
   50 52 49 20 2a 20 48 54 54 50 2f 32 2e 30 0d 0a
   0d 0a 53 4d 0d 0a 0d 0a
----------------------------------------
Frame Length = 36 (00 00 24)
Frame Type = SETTINGS (04)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Settings =
   SETTINGS_HEADER_TABLE_SIZE:0x1 -> 4096 (00 01 | 00 00 10 00)
   SETTINGS_ENABLE_PUSH:0x2 -> 1 (00 02 | 00 00 00 01)
   SETTINGS_INITIAL_WINDOW_SIZE:0x4 -> 65535 (00 04 | 00 00 ff ff)
   SETTINGS_MAX_FRAME_SIZE:0x5 -> 16384 (00 05 | 00 00 40 00)
   SETTINGS_MAX_CONCURRENT_STREAMS:0x3 -> 100 (00 03 | 00 00 00 64)
   SETTINGS_MAX_HEADER_LIST_SIZE:0x6 -> 65536 (00 06 | 00 01 00 00)
----------------------------------------
Frame Length = 6 (00 00 06)
Frame Type = SETTINGS (04)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Settings =
   SETTINGS_ENABLE_PUSH:0x2 -> 0 (00 02 | 00 00 00 00)
----------------------------------------
============================================================
server(localhost:8080)->proxy->client(127.0.0.1:59600)

Frame Length = 36 (00 00 24)
Frame Type = SETTINGS (04)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Settings =
   SETTINGS_HEADER_TABLE_SIZE:0x1 -> 4096 (00 01 | 00 00 10 00)
   SETTINGS_ENABLE_PUSH:0x2 -> 0 (00 02 | 00 00 00 00)
   SETTINGS_INITIAL_WINDOW_SIZE:0x4 -> 65535 (00 04 | 00 00 ff ff)
   SETTINGS_MAX_FRAME_SIZE:0x5 -> 16384 (00 05 | 00 00 40 00)
   SETTINGS_MAX_CONCURRENT_STREAMS:0x3 -> 100 (00 03 | 00 00 00 64)
   SETTINGS_MAX_HEADER_LIST_SIZE:0x6 -> 65536 (00 06 | 00 01 00 00)
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
Hexdump (Compressed Headers) =
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
Hexdump (Compressed Headers) =
   88 76 8e 8c 68 31 16 9c 4b 20 b6 77 2d 8c 05 70
   7f 5c 82 75 ef 5f 8b 1d 75 d0 62 0d 26 3d 4c 74
   41 ea
----------------------------------------
Frame Length = 78 (00 00 4e)
Frame Type = DATA (00)
Flags = END_STREAM:0x1 (01)
Stream Identifier = 1 (00 00 00 01)
Frame Payload =
   b'{":method": "GET", ":scheme": "http", ":authority": "localhost", ":path": "/"}'
Hexdump (Frame Payload) =
   7b 22 3a 6d 65 74 68 6f 64 22 3a 20 22 47 45 54
   22 2c 20 22 3a 73 63 68 65 6d 65 22 3a 20 22 68
   74 74 70 22 2c 20 22 3a 61 75 74 68 6f 72 69 74
   79 22 3a 20 22 6c 6f 63 61 6c 68 6f 73 74 22 2c
   20 22 3a 70 61 74 68 22 3a 20 22 2f 22 7d
----------------------------------------
Done redirecting socket for client(127.0.0.1:59600)->proxy->server(localhost:8080)
Done redirecting socket for server(localhost:8080)->proxy->client(127.0.0.1:59600)
```

[1]: https://python-hyper.org/projects/h2/en/stable/basic-usage.html
