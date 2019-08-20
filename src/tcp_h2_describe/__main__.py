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

import argparse

from tcp_h2_describe._serve import serve_proxy


DESCRIPTION = """\
Run `tcp-h2-describe` reverse proxy server.

This will forward traffic to a proxy port along to an already running
HTTP/2 server. For each HTTP/2 frame forwarded (either client->server or
server->client) a description will be printed to the console explaining what
each byte in the frame means.
"""


def get_args():
    """Get the command line arguments for ``tcp-h2-describe``.

    Returns:
       Tuple[int, int, Optional[str]]: A triple of
       * The port for the "describe" proxy
       * The port for the server that is being proxied
       * The hostname for the server that is being proxied (or :data:`None` if
         not provided)
    """
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="tcp-h2-describe",
    )
    parser.add_argument(
        "--proxy-port",
        dest="proxy_port",
        type=int,
        default=24909,
        help='The port that will be used for running the "describe" proxy.',
    )
    parser.add_argument(
        "--server-host",
        dest="server_host",
        help="The hostname for the server that is being proxied.",
    )
    parser.add_argument(
        "--server-port",
        dest="server_port",
        type=int,
        default=80,
        help="The port for the server that is being proxied.",
    )

    args = parser.parse_args()
    return args.proxy_port, args.server_port, args.server_host


def main():
    proxy_port, server_port, server_host = get_args()
    kwargs = {}
    if server_host is not None:
        kwargs["server_host"] = server_host

    serve_proxy(proxy_port, server_port, **kwargs)


if __name__ == "__main__":
    main()
