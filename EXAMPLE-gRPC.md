# Example With gRPC

If we run the basic gRPC users service stored in the `_grpc` subdirectory:

```
$ python3 -m virtualenv grpc-example
$ grpc-example/bin/python -m pip install \
>   grpcio==1.23.0 protobuf==3.9.1 six==1.12.0
$ grpc-example/bin/python -m pip install .
$ PYTHONPATH=_grpc/ GRPC_PORT=38895 grpc-example/bin/python \
>   _bin/grpc_server.py > /dev/null 2>&1 &
[1] 4035
$
$ PYTHONPATH=_grpc/ GRPC_PORT=38895 grpc-example/bin/python \
>   _bin/grpc_proxy.py
Starting tcp-h2-describe proxy server on port 24909
  Proxying server located at localhost:38895
...
```

Rather than using `python -m tcp_h2_describe` directly, we use a custom
`grpc_proxy.py` that first calls

```python
tcp_h2_describe.register_payload_handler("DATA", handle_data_payload)
```

to register a custom handler that has access to the the protobuf definitions
in our application.

If we hit the proxy directly by using the **proxy's** `GRPC_PORT` with
`call_grpc.py`:

```
$ PYTHONPATH=_grpc/ GRPC_PORT=24909 grpc-example/bin/python \
>   _bin/call_grpc.py
Inserted user:
   user_id: 3079877744918980318

Inserted user:
   user_id: 7444709551642703711

Retrieving users:
   User:
      first_name: "Bob"
      last_name: "Green"
      id: 3079877744918980318

   User:
      first_name: "Alice"
      last_name: "Redmond"
      id: 7444709551642703711

```

we'll see all the frames:

```
...
  Proxying server located at localhost:38895
Accepted connection from 127.0.0.1:51600
============================================================
client(127.0.0.1:51600)->proxy->server(localhost:38895)

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
   SETTINGS_ENABLE_PUSH:0x2 -> 0 (00 02 | 00 00 00 00)
   SETTINGS_MAX_CONCURRENT_STREAMS:0x3 -> 0 (00 03 | 00 00 00 00)
   SETTINGS_INITIAL_WINDOW_SIZE:0x4 -> 4194304 (00 04 | 00 40 00 00)
   SETTINGS_MAX_FRAME_SIZE:0x5 -> 4194304 (00 05 | 00 40 00 00)
   SETTINGS_MAX_HEADER_LIST_SIZE:0x6 -> 8192 (00 06 | 00 00 20 00)
   GRPC_ALLOW_TRUE_BINARY_METADATA:0xfe03 -> 1 (fe 03 | 00 00 00 01)
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 4128769 (00 3f 00 01)
----------------------------------------
Frame Length = 8 (00 00 08)
Frame Type = PING (06)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Opaque Data = 00 00 00 00 00 00 00 00
----------------------------------------
Frame Length = 247 (00 00 f7)
Frame Type = HEADERS (01)
Flags = END_HEADERS:0x4 (04)
Stream Identifier = 1 (00 00 00 01)
Headers =
   ':scheme' -> 'http'
   ':method' -> 'POST'
   ':authority' -> 'localhost:24909'
   ':path' -> '/users.v1.Users/AddUser'
   'te' -> 'trailers'
   'content-type' -> 'application/grpc'
   'user-agent' -> 'grpc-python/1.23.0 grpc-c/7.0.0 (osx; chttp2; gangnam)'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> 'identity,gzip'
Hexdump (Compressed Headers) =
   86 83 40 0a 3a 61 75 74 68 6f 72 69 74 79 0f 6c
   6f 63 61 6c 68 6f 73 74 3a 32 34 39 30 39 40 05
   3a 70 61 74 68 17 2f 75 73 65 72 73 2e 76 31 2e
   55 73 65 72 73 2f 41 64 64 55 73 65 72 40 02 74
   65 08 74 72 61 69 6c 65 72 73 40 0c 63 6f 6e 74
   65 6e 74 2d 74 79 70 65 10 61 70 70 6c 69 63 61
   74 69 6f 6e 2f 67 72 70 63 40 0a 75 73 65 72 2d
   61 67 65 6e 74 36 67 72 70 63 2d 70 79 74 68 6f
   6e 2f 31 2e 32 33 2e 30 20 67 72 70 63 2d 63 2f
   37 2e 30 2e 30 20 28 6f 73 78 3b 20 63 68 74 74
   70 32 3b 20 67 61 6e 67 6e 61 6d 29 40 14 67 72
   70 63 2d 61 63 63 65 70 74 2d 65 6e 63 6f 64 69
   6e 67 15 69 64 65 6e 74 69 74 79 2c 64 65 66 6c
   61 74 65 2c 67 7a 69 70 40 0f 61 63 63 65 70 74
   2d 65 6e 63 6f 64 69 6e 67 0d 69 64 65 6e 74 69
   74 79 2c 67 7a 69 70
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 1 (00 00 00 01)
Reserved Bit = 0, Window Size Increment = 5 (00 00 00 05)
----------------------------------------
Frame Length = 17 (00 00 11)
Frame Type = DATA (00)
Flags = END_STREAM:0x1 (01)
Stream Identifier = 1 (00 00 00 01)
gRPC Tag = 0 (00)
Protobuf Length = 12 (00 00 00 0c)
Protobuf Message (users.v1.User) =
   first_name: "Bob"
   last_name: "Green"
Hexdump (Protobuf Message) =
   0a 03 42 6f 62 12 05 47 72 65 65 6e
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 5 (00 00 00 05)
----------------------------------------
============================================================
server(localhost:38895)->proxy->client(127.0.0.1:51600)

Frame Length = 24 (00 00 18)
Frame Type = SETTINGS (04)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Settings =
   SETTINGS_INITIAL_WINDOW_SIZE:0x4 -> 4194304 (00 04 | 00 40 00 00)
   SETTINGS_MAX_FRAME_SIZE:0x5 -> 4194304 (00 05 | 00 40 00 00)
   SETTINGS_MAX_HEADER_LIST_SIZE:0x6 -> 8192 (00 06 | 00 00 20 00)
   GRPC_ALLOW_TRUE_BINARY_METADATA:0xfe03 -> 1 (fe 03 | 00 00 00 01)
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 4128769 (00 3f 00 01)
----------------------------------------
Frame Length = 8 (00 00 08)
Frame Type = PING (06)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Opaque Data = 00 00 00 00 00 00 00 00
----------------------------------------
============================================================
server(localhost:38895)->proxy->client(127.0.0.1:51600)

Frame Length = 8 (00 00 08)
Frame Type = PING (06)
Flags = ACK:0x1 (01)
Stream Identifier = 0 (00 00 00 00)
Opaque Data = 00 00 00 00 00 00 00 00
----------------------------------------
Frame Length = 0 (00 00 00)
Frame Type = SETTINGS (04)
Flags = ACK:0x1 (01)
Stream Identifier = 0 (00 00 00 00)
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 17 (00 00 00 11)
----------------------------------------
============================================================
client(127.0.0.1:51600)->proxy->server(localhost:38895)

Frame Length = 8 (00 00 08)
Frame Type = PING (06)
Flags = ACK:0x1 (01)
Stream Identifier = 0 (00 00 00 00)
Opaque Data = 00 00 00 00 00 00 00 00
----------------------------------------
Frame Length = 0 (00 00 00)
Frame Type = SETTINGS (04)
Flags = ACK:0x1 (01)
Stream Identifier = 0 (00 00 00 00)
----------------------------------------
============================================================
server(localhost:38895)->proxy->client(127.0.0.1:51600)

Frame Length = 107 (00 00 6b)
Frame Type = HEADERS (01)
Flags = END_HEADERS:0x4 (04)
Stream Identifier = 1 (00 00 00 01)
Headers =
   ':status' -> '200'
   'content-type' -> 'application/grpc'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> 'identity,gzip'
Hexdump (Compressed Headers) =
   88 40 0c 63 6f 6e 74 65 6e 74 2d 74 79 70 65 10
   61 70 70 6c 69 63 61 74 69 6f 6e 2f 67 72 70 63
   40 14 67 72 70 63 2d 61 63 63 65 70 74 2d 65 6e
   63 6f 64 69 6e 67 15 69 64 65 6e 74 69 74 79 2c
   64 65 66 6c 61 74 65 2c 67 7a 69 70 40 0f 61 63
   63 65 70 74 2d 65 6e 63 6f 64 69 6e 67 0d 69 64
   65 6e 74 69 74 79 2c 67 7a 69 70
----------------------------------------
Frame Length = 15 (00 00 0f)
Frame Type = DATA (00)
Flags = UNSET (00)
Stream Identifier = 1 (00 00 00 01)
gRPC Tag = 0 (00)
Protobuf Length = 10 (00 00 00 0a)
Protobuf Message (users.v1.AddUserResponse) =
   user_id: 3079877744918980318
Hexdump (Protobuf Message) =
   08 de cd 9b cc db 8f fb de 2a
----------------------------------------
Frame Length = 30 (00 00 1e)
Frame Type = HEADERS (01)
Flags = END_STREAM:0x1 | END_HEADERS:0x4 (05)
Stream Identifier = 1 (00 00 00 01)
Headers =
   'grpc-status' -> '0'
   'grpc-message' -> ''
Hexdump (Compressed Headers) =
   40 0b 67 72 70 63 2d 73 74 61 74 75 73 01 30 40
   0c 67 72 70 63 2d 6d 65 73 73 61 67 65 00
----------------------------------------
============================================================
client(127.0.0.1:51600)->proxy->server(localhost:38895)

Frame Length = 34 (00 00 22)
Frame Type = HEADERS (01)
Flags = END_HEADERS:0x4 (04)
Stream Identifier = 3 (00 00 00 03)
Headers =
   ':scheme' -> 'http'
   ':method' -> 'POST'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> '/users.v1.Users/AddUser'
   'content-type' -> 'application/grpc'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> 'identity,gzip'
   'grpc-status' -> '0'
   'grpc-message' -> ''
Hexdump (Compressed Headers) =
   86 83 c4 0f 34 17 2f 75 73 65 72 73 2e 76 31 2e
   55 73 65 72 73 2f 41 64 64 55 73 65 72 c2 c1 c0
   bf be
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 3 (00 00 00 03)
Reserved Bit = 0, Window Size Increment = 5 (00 00 00 05)
----------------------------------------
Frame Length = 21 (00 00 15)
Frame Type = DATA (00)
Flags = END_STREAM:0x1 (01)
Stream Identifier = 3 (00 00 00 03)
gRPC Tag = 0 (00)
Protobuf Length = 16 (00 00 00 10)
Protobuf Message (users.v1.User) =
   first_name: "Alice"
   last_name: "Redmond"
Hexdump (Protobuf Message) =
   0a 05 41 6c 69 63 65 12 07 52 65 64 6d 6f 6e 64
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 15 (00 00 00 0f)
----------------------------------------
============================================================
server(localhost:38895)->proxy->client(127.0.0.1:51600)

Frame Length = 4 (00 00 04)
Frame Type = HEADERS (01)
Flags = END_HEADERS:0x4 (04)
Stream Identifier = 3 (00 00 00 03)
Headers =
   ':status' -> '200'
   'content-type' -> 'application/grpc'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> 'identity,gzip'
Hexdump (Compressed Headers) =
   88 c2 c1 c0
----------------------------------------
Frame Length = 15 (00 00 0f)
Frame Type = DATA (00)
Flags = UNSET (00)
Stream Identifier = 3 (00 00 00 03)
gRPC Tag = 0 (00)
Protobuf Length = 10 (00 00 00 0a)
Protobuf Message (users.v1.AddUserResponse) =
   user_id: 7444709551642703711
Hexdump (Protobuf Message) =
   08 df ee fb cc cb fc ba a8 67
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = HEADERS (01)
Flags = END_STREAM:0x1 | END_HEADERS:0x4 (05)
Stream Identifier = 3 (00 00 00 03)
Headers =
   'grpc-status' -> '0'
   'grpc-message' -> ''
Hexdump (Compressed Headers) =
   bf 0f 2f 00
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 21 (00 00 00 15)
----------------------------------------
============================================================
client(127.0.0.1:51600)->proxy->server(localhost:38895)

Frame Length = 35 (00 00 23)
Frame Type = HEADERS (01)
Flags = END_HEADERS:0x4 (04)
Stream Identifier = 5 (00 00 00 05)
Headers =
   ':scheme' -> 'http'
   ':method' -> 'POST'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> '/users.v1.Users/GetUsers'
   'content-type' -> 'application/grpc'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> 'identity,gzip'
   'grpc-status' -> '0'
   'grpc-message' -> ''
Hexdump (Compressed Headers) =
   86 83 c4 0f 34 18 2f 75 73 65 72 73 2e 76 31 2e
   55 73 65 72 73 2f 47 65 74 55 73 65 72 73 c2 c1
   c0 bf be
----------------------------------------
Frame Length = 5 (00 00 05)
Frame Type = DATA (00)
Flags = END_STREAM:0x1 (01)
Stream Identifier = 5 (00 00 00 05)
gRPC Tag = 0 (00)
Protobuf Length = 0 (00 00 00 00)
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 10 (00 00 00 0a)
----------------------------------------
============================================================
server(localhost:38895)->proxy->client(127.0.0.1:51600)

Frame Length = 4 (00 00 04)
Frame Type = HEADERS (01)
Flags = END_HEADERS:0x4 (04)
Stream Identifier = 5 (00 00 00 05)
Headers =
   ':status' -> '200'
   'content-type' -> 'application/grpc'
   'grpc-accept-encoding' -> 'identity,deflate,gzip'
   'accept-encoding' -> 'identity,gzip'
Hexdump (Compressed Headers) =
   88 c2 c1 c0
----------------------------------------
Frame Length = 27 (00 00 1b)
Frame Type = DATA (00)
Flags = UNSET (00)
Stream Identifier = 5 (00 00 00 05)
gRPC Tag = 0 (00)
Protobuf Length = 22 (00 00 00 16)
Protobuf Message (users.v1.User) =
   first_name: "Bob"
   last_name: "Green"
   id: 3079877744918980318
Hexdump (Protobuf Message) =
   0a 03 42 6f 62 12 05 47 72 65 65 6e 18 de cd 9b
   cc db 8f fb de 2a
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = WINDOW_UPDATE (08)
Flags = UNSET (00)
Stream Identifier = 0 (00 00 00 00)
Reserved Bit = 0, Window Size Increment = 5 (00 00 00 05)
----------------------------------------
============================================================
server(localhost:38895)->proxy->client(127.0.0.1:51600)

Frame Length = 31 (00 00 1f)
Frame Type = DATA (00)
Flags = UNSET (00)
Stream Identifier = 5 (00 00 00 05)
gRPC Tag = 0 (00)
Protobuf Length = 26 (00 00 00 1a)
Protobuf Message (users.v1.User) =
   first_name: "Alice"
   last_name: "Redmond"
   id: 7444709551642703711
Hexdump (Protobuf Message) =
   0a 05 41 6c 69 63 65 12 07 52 65 64 6d 6f 6e 64
   18 df ee fb cc cb fc ba a8 67
----------------------------------------
Frame Length = 4 (00 00 04)
Frame Type = HEADERS (01)
Flags = END_STREAM:0x1 | END_HEADERS:0x4 (05)
Stream Identifier = 5 (00 00 00 05)
Headers =
   'grpc-status' -> '0'
   'grpc-message' -> ''
Hexdump (Compressed Headers) =
   bf 0f 2f 00
----------------------------------------
Done redirecting socket for client(127.0.0.1:51600)->proxy->server(localhost:38895)
```
