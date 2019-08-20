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

import socket
import threading

import tcp_h2_describe._connect
import tcp_h2_describe._display


PROXY_HOST = "0.0.0.0"
DEFAULT_SERVER_HOST = "localhost"
BACKLOG = 5


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
    proxy_socket.bind((PROXY_HOST, proxy_port))
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.listen(BACKLOG)
    tcp_h2_describe._display.display(
        f"Starting tcp-h2-describe proxy server on port {proxy_port}\n"
        f"  Proxying server located at {server_host}:{server_port}"
    )

    while True:
        client_socket, (ip_addr, port) = proxy_socket.accept()
        client_addr = f"{ip_addr}:{port}"
        tcp_h2_describe._display.display(
            f"Accepted connection from {client_addr}"
        )
        # NOTE: Nothing actually `.join()`-s this thread.
        t_handle = threading.Thread(
            target=tcp_h2_describe._connect.connect_socket_pair,
            args=(client_socket, client_addr, server_host, server_port),
        )
        t_handle.start()
