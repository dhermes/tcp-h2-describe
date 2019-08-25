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

import tcp_h2_describe._buffer
import tcp_h2_describe._display


PROXY_PREFIX = b"PROXY"


def verify_inet_protocol(inet_protocol):
    """Verify the ``INET_PROTOCOL`` from a proxy protocol line.

    Args:
        inet_protocol (bytes): The segment from the proxy protocol line.

    Returns:
        socket.AddressFamily: The address family enum associated with the
        protocol.

    Raises:
        ValueError: If ``inet_protocol`` does not match ``TPC{4,6}``.
    """
    if inet_protocol == b"TCP4":
        return socket.AF_INET
    if inet_protocol == b"TCP6":
        return socket.AF_INET6

    raise ValueError(f"Unhandled protocol type: {inet_protocol}")


def verify_ip(ip_, address_family):
    """Verify that a string is an IP in a given family (IPv4 or IPv6).

    Args:
        ip_ (bytes): The IP address as a bytestring.
        address_family (socket.AddressFamily): The expected address family of
           the IP address,

    Returns:
        str: The parsed IP address as a string.

    Raises:
        ValueError: If ``ip_`` is not valid for  ``address_family``.
    """
    try:
        ip_ascii = ip_.decode("ascii")
    except:
        ip_ascii = ""

    try:
        socket.inet_pton(address_family, ip_ascii)
    except OSError:
        raise ValueError(
            f"Invalid IP {ip_} for address family {address_family}"
        )

    return ip_ascii


def verify_port(port_str):
    """Verify that a bytestring is a valid port.

    Args:
        port_str (bytes): The port as a bytestring.

    Returns:
        int: The parsed port.

    Raises:
        ValueError: If ``port_str`` is not a valid port.
    """
    try:
        port = int(port_str.decode("ascii"))
    except:
        port = -1

    if not 0 < port < 0x10000:
        raise ValueError(f"Invalid port: {port_str}")

    return port


def read_next_byte(recv_socket, send_socket):
    """Read the next byte (via RECV) from an open socket.

    This assumes ``recv_socket`` is non-blocking, so first waits until the
    socket is ready via ``select.select()``.

    Args:
        recv_socket (socket.socket): A socket to RECV from.
        send_socket (socket.socket): A socket connected (on the "other end") to
            ``recv_socket``.

    Returns:
        bytes: The byte that was RECV-ed.

    Raises:
        RuntimeError: If ``wait_readable`` returns :data:`None`; this
            indicates that the ``send_socket`` is closed.
        RuntimeError: If the RECV returns an empty bytestring, indicating the
            TCP stream has no more data.
    """
    recv_socket = tcp_h2_describe._buffer.wait_readable(
        recv_socket, send_socket
    )
    if recv_socket is None:
        raise RuntimeError("Trying to read next byte on a closed connection.")

    next_byte = recv_socket.recv(1)
    if len(next_byte) != 1:
        raise RuntimeError(
            "Trying to read next byte on stream with no more data."
        )

    return next_byte


def consume_proxy_line(recv_socket, send_socket):
    """(Maybe) consume the proxy protocol (first) line of a TCP frame.

    .. proxy protocol: https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-proxy-protocol.html

    This assumes ``recv_socket`` is non-blocking. Uses ``MSG_PEEK`` to check
    if the first five bytes are ``PROXY`` and exits early if not. After
    confirming the first line **is** a `proxy protocol`_ line, this reads until
    a newline byte is reached, then verifies each of the (six) parts in the
    header line.

    Args:
        recv_socket (socket.socket): A socket to RECV from.
        send_socket (socket.socket): A socket connected (on the "other end") to
            ``recv_socket``.

    Returns:
        Optional[bytes]: The proxy protocol line (including the CRLF) if the
        first line of the TCP frame begins with ``PROXY ...``, otherwise
        :data:`None`.

    Raises:
        RuntimeError: If ``wait_readable`` returns :data:`None`; this
            indicates that the ``send_socket`` is closed.
        ValueError: If the character immediately preceding the newline is not
            a carriage return (TCP lines are CRLF delimited).
        ValueError: If the proxy protocol line does not have 6
            (space-delimited) parts.
    """
    recv_socket = tcp_h2_describe._buffer.wait_readable(
        recv_socket, send_socket
    )
    if recv_socket is None:
        raise RuntimeError("Socket not readable when checking for proxy line")

    prefix = recv_socket.recv(len(PROXY_PREFIX), socket.MSG_PEEK)
    if prefix != PROXY_PREFIX:
        return None

    read_bytes = []
    next_byte = read_next_byte(recv_socket, send_socket)
    while next_byte != b"\n":
        read_bytes.append(next_byte)
        next_byte = read_next_byte(recv_socket, send_socket)

    if read_bytes[-1] != b"\r":
        raise ValueError("Expected first line to end in CRLF")

    proxy_protocol_line = b"".join(read_bytes[:-1])
    proxy_parts = proxy_protocol_line.split(b" ")

    if len(proxy_parts) != 6:
        raise ValueError(
            f"Invalid header line {proxy_protocol_line}; "
            f"has {len(proxy_parts)} parts"
        )

    _, inet_protocol, client_ip, proxy_ip, client_port, proxy_port = (
        proxy_parts
    )
    address_family = verify_inet_protocol(inet_protocol)
    client_ip = verify_ip(client_ip, address_family)
    proxy_ip = verify_ip(proxy_ip, address_family)
    client_port = verify_port(client_port)
    proxy_port = verify_port(proxy_port)

    return proxy_protocol_line + b"\r\n"
