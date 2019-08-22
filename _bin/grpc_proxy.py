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

import os
import struct
import textwrap

import tcp_h2_describe
import tcp_h2_describe._describe


simple_hexdump = tcp_h2_describe._describe.simple_hexdump
FLAG_PADDED = tcp_h2_describe._describe.FLAG_PADDED
STRUCT_L = struct.Struct(">L")


def handle_data_payload(frame_payload, flags):
    """Handle a DATA HTTP/2 frame payload.

    This assumes **every** DATA frame is a serialized protobuf sent over
    gRPC with a length prefix.

    .. DATA spec: https://http2.github.io/http2-spec/#DATA

    See `DATA spec`_.

    Args:
        frame_payload (bytes): The frame payload to be parsed.
        flags (int): The flags for the frame payload.

    Returns:
        str: The deserialized protobuf from ``frame_payload``.

    Raises:
        NotImplementedError: If ``flags`` has ``PADDED`` set.
        NotImplementedError: If the first bytes is not ``\x00``.
        ValueError: If the length of ``frame_payload`` does not match the
            length prefix.
    """
    if flags & FLAG_PADDED == FLAG_PADDED:
        raise NotImplementedError(
            "PADDED flag not currently supported for data"
        )

    if frame_payload[:1] != b"\x00":
        raise NotImplementedError(
            "Serialized protobuf over gRPC only supported with tag 0",
            frame_payload,
        )

    # NOTE: This will fail if ``frame_payload`` has fewer than 5 bytes.
    length, = STRUCT_L.unpack(frame_payload[1:5])
    if len(frame_payload) != 5 + length:
        raise ValueError(
            "Frame payload has unexpected length", frame_payload, 5 + length
        )
    length_bytes = simple_hexdump(frame_payload[1:5])

    pb_bytes = frame_payload[5:]
    parts = [
        "gRPC Tag = 0 (00)",
        f"Protobuf Length = {length} ({length_bytes})",
    ]
    if length > 0:
        parts.extend(
            [
                "Protobuf Message =",
                f"   {pb_bytes}",
                "Hexdump (Protobuf Message) =",
                textwrap.indent(simple_hexdump(pb_bytes), "   "),
            ]
        )

    return "\n".join(parts)


def main():
    tcp_h2_describe.register_payload_handler("DATA", handle_data_payload)
    proxy_port = 24909
    server_port = int(os.environ.get("GRPC_PORT", 50051))
    tcp_h2_describe.serve_proxy(proxy_port, server_port)


if __name__ == "__main__":
    main()
