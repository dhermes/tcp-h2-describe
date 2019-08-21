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

import tcp_h2_describe._buffer
import tcp_h2_describe._describe
import tcp_h2_describe._display


def redirect_socket(recv_socket, send_socket, description, expect_preface):
    """Redirect a TCP stream from one socket to another.

    This only redirects in **one** direction, i.e. it RECVs from
    ``recv_socket`` and SENDs to ``send_socket``.

    Args:
        recv_socket (socket.socket): The socket that will be RECV-ed from.
        send_socket (socket.socket): The socket that will be SENT to.
        description (str): A description of the RECV->SEND relationship for
            this socket pair.
        expect_preface (bool): Indicates if the ``h2_frames`` should begin
            with the client connection preface. This should only be
            :data:`True` on the **first** TCP frame for the client socket.
    """
    tcp_chunk = tcp_h2_describe._buffer.recv(recv_socket)
    while tcp_chunk != b"":
        # Describe the chunk that was just encountered
        message = tcp_h2_describe._describe.describe(
            tcp_chunk, description, expect_preface
        )
        tcp_h2_describe._display.display(message)
        # After the first usage, make sure ``expect_preface`` is not set.
        expect_preface = False

        tcp_h2_describe._buffer.send(send_socket, tcp_chunk)
        # Read the next chunk from the socket.
        tcp_chunk = tcp_h2_describe._buffer.recv(recv_socket)

    tcp_h2_describe._display.display(
        f"Done redirecting socket for {description}"
    )


def connect_socket_pair(client_socket, client_addr, server_host, server_port):
    """Connect two socket pairs for bidirectional RECV<->SEND.

    Since calls to RECV (both on the client and the server sockets) can block,
    this will spawn two threads that simultaneously read (via RECV) from one
    socket and write (via SEND) into the other socket.

    Args:
        client_socket (socket.socket): An already open socket from a client
            that has made a request directly to a running ``tcp-h2-describe``
            proxy.
        client_addr (str): The address of the client socket; used for printing
            information about the connection. Note that
            ``client_socket.getsockname()`` could be used directly to recover
            this information.
        server_host (str): The host name where the "server" process is running
            (i.e. the server that is being proxied).
        server_port (int): A port number for a running "server" process.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((server_host, server_port))

    server_addr = f"{server_host}:{server_port}"
    read_description = f"client({client_addr})->proxy->server({server_addr})"
    t_read = threading.Thread(
        target=redirect_socket,
        args=(client_socket, server_socket, read_description, True),
    )
    write_description = f"server({server_addr})->proxy->client({client_addr})"
    t_write = threading.Thread(
        target=redirect_socket,
        args=(server_socket, client_socket, write_description, False),
    )

    t_read.start()
    t_write.start()

    t_read.join()
    t_write.join()

    client_socket.close()
    server_socket.close()
