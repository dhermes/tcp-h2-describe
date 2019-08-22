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

See example output when proxying an [HTTP server][3] and a [gRPC server][4].

## Development

To work on adding a feature or to run the tests, see the [DEVELOPMENT doc][1]
for more information on how to get started.

## License

`tcp-h2-describe` is made available under the Apache 2.0 License. For more
details, see the [LICENSE][2].

[1]: https://github.com/dhermes/tcp-h2-describe/blob/0.0.3/README.md
[2]: https://github.com/dhermes/tcp-h2-describe/blob/0.0.3/LICENSE
[3]: https://github.com/dhermes/tcp-h2-describe/blob/0.0.3/EXAMPLE-HTTP.md
[4]: https://github.com/dhermes/tcp-h2-describe/blob/0.0.3/EXAMPLE-gRPC.md
