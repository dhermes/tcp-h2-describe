# Example With Proxy Protocol

When raw TCP traffic comes through a proxy (e.g. [Amazon's ELB][1]) a proxy
protocol line will be added to the first TCP frame. For example

```
PROXY TCP4 198.51.100.22 203.0.113.7 35646 80
```

followed by a CRLF. So when running `tcp-h2-describe` behind an AWS ELB, the
"describe" output will have an extra section before the client connection
preface:

```
Starting tcp-h2-describe proxy server on port 50052
  Proxying server located at localhost:50051
Accepted connection from 10.101.130.13:62522
============================================================
client(10.101.130.13:62522)->proxy->server(localhost:50052)

Proxy Protocol Header =
   b'PROXY TCP4 10.31.2.14 10.10.7.177 58014 10900\r\n'
Hexdump (Proxy Protocol Header) =
   50 52 4f 58 59 20 54 43 50 34 20 31 30 2e 33 31
   2e 32 2e 31 34 20 31 30 2e 31 30 2e 37 2e 31 37
   37 20 35 38 30 31 34 20 31 30 39 30 30 0d 0a
----------------------------------------
Client Connection Preface = b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'
Hexdump (Client Connection Preface) =
   50 52 49 20 2a 20 48 54 54 50 2f 32 2e 30 0d 0a
   0d 0a 53 4d 0d 0a 0d 0a
----------------------------------------
...
```

[1]: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-proxy-protocol.html
