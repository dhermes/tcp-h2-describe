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
import sys


IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform in ("linux", "linux2")
# See: https://github.com/golang/go/blob/go1.12.9/src/syscall/zerrors_darwin_amd64.go#L1017
MACOS_TCP_KEEPALIVE = 0x10


def increase_sockopt(socket_, level, option, value):
    """Increase a socket option to ``value``.

    If the currently set value for that ``option`` equals or exceeds ``value``,
    this will do nothing.

    Args:
        level (int): The protocol level where the option should be set.
        option (int): The option to set for the protocol level.
        value (int): The value to set for the socket option.

    Returns:
        bool: Indicating if the value was set.
    """
    current_value = socket_.getsockopt(level, option)
    if current_value >= value:
        return False

    socket_.setsockopt(level, option, value)
    return True


def set_keepalive(socket_, seconds):
    """Set keepalive options on a TCP socket.

    Some helpful resources:

    https://stackoverflow.com/a/14855726
    https://github.com/golang/go/blob/go1.12.9/src/net/tcpsockopt_unix.go#L19-L22
    https://github.com/golang/go/blob/go1.12.9/src/net/sockopt_posix.go#L116-L120
    https://github.com/golang/go/blob/go1.12.9/src/net/tcpsockopt_darwin.go#L19-L22

    Note that ``increase_sockopt()`` is used here rather than directly calling
    ``setsockopt``. This way the keepalive interval **exceeds** ``seconds``,
    this won't downgrade the window. For example, the ``TCP_KEEPIDLE`` (on
    Linux) / ``TCP_KEEPALIVE`` (on macOS) interval is typically 2 hours by
    default so calling ``setsockopt`` may actually decrease this interval. On
    the other hand the ``TCP_KEEPINTVL`` value (on Linux) is 75 seconds, so
    it may be worthwhile to increase this.

    Args:
        socket_ (socket.socket): The socket to have keepalive set.
        seconds (int): The number of seconds to use for keepalive.

    Raises:
        NotImplementedError: If the current platform is not macOS or Linux.
    """
    if IS_LINUX:
        socket_.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        increase_sockopt(
            socket_, socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, seconds
        )
        increase_sockopt(
            socket_, socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, seconds
        )
        return

    if IS_MACOS:
        socket_.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        increase_sockopt(
            socket_, socket.IPPROTO_TCP, MACOS_TCP_KEEPALIVE, seconds
        )
        return

    raise NotImplementedError(f"Unsupported platform {sys.platform}")
