# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import select
import socket
import threading

import tcp_h2_describe._connect
import tcp_h2_describe._display
import tcp_h2_describe._keepalive


PROXY_HOST = "0.0.0.0"
DEFAULT_SERVER_HOST = "localhost"
BACKLOG = 5
KEEP_ALIVE_INTERVAL = 180  # 3 minutes, in seconds


def accept(non_blocking_socket):
    """Accept a connection on a non-blocking socket.

    Since the socket is non-blocking, a **blocking** call to
    ``select.select()`` is used to wait until the socket is ready.

    Args:
        non_blocking_socket (socket.socket): A socket that will block to accept
            a connection.

    Returns:
       Tuple[socket.socket, str]: A pair of:
       * The socket of the client connection that was accepted
       * The address (IP and port) of the client socket

    Raises:
        ValueError: If ``non_blocking_socket`` is not readable after
            ``select.select()`` returns.
    """
    readable, _, _ = select.select([non_blocking_socket], [], [])
    if readable != [non_blocking_socket]:
        raise ValueError("Socket not ready to accept connections")

    client_socket, (ip_addr, port) = non_blocking_socket.accept()
    # See: https://docs.python.org/3/library/socket.html#timeouts-and-the-accept-method
    client_socket.setblocking(0)
    # Turn on KEEPALIVE for the connection.
    tcp_h2_describe._keepalive.set_keepalive(
        client_socket, KEEP_ALIVE_INTERVAL
    )

    client_addr = f"{ip_addr}:{port}"
    return client_socket, client_addr


def serve_proxy(proxy_port, server_port, server_host=DEFAULT_SERVER_HOST):
    """Serve the proxy.

    This should run as a top-level server and CLI invocations of
    ``tcp-h2-describe`` will directly invoke it.

    Args:
        proxy_port (int): A legal port number that the caller has permissions
            to bind to.
        server_port (int): A port number for a running "server" process.
        server_host (Optional[str]): The host name where the server process is
            running (i.e. the server that is being proxied). Defaults to
            ``localhost``.
    """
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setblocking(0)
    proxy_socket.bind((PROXY_HOST, proxy_port))
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.listen(BACKLOG)
    tcp_h2_describe._display.display(
        f"Starting tcp-h2-describe proxy server on port {proxy_port}\n"
        f"  Proxying server located at {server_host}:{server_port}"
    )

    while True:
        client_socket, client_addr = accept(proxy_socket)
        tcp_h2_describe._display.display(
            f"Accepted connection from {client_addr}"
        )
        # NOTE: Nothing actually `.join()`-s this thread.
        t_handle = threading.Thread(
            target=tcp_h2_describe._connect.connect_socket_pair,
            args=(client_socket, client_addr, server_host, server_port),
        )
        t_handle.start()
