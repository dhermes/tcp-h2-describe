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

import google.protobuf.message
import tcp_h2_describe
import tcp_h2_describe._describe

import users_pb2


simple_hexdump = tcp_h2_describe._describe.simple_hexdump
FLAG_PADDED = tcp_h2_describe._describe.FLAG_PADDED
STRUCT_L = struct.Struct(">L")
PB_TYPES = (users_pb2.User, users_pb2.AddUserResponse)


def _maybe_parse(pb_bytes, pb_class):
    """Attempt to parse a protobuf to a given message class.

    Args:
        pb_bytes (str): A raw protobuf serialized as a bytestring.
        pb_class (type): A protobuf message type.

    Returns:
        object: An instance of ``pb_class`` if parsing succeeded, otherwise
        :data:`None`.
    """
    pb = pb_class()
    # NOTE: If ``ParseFromString()`` fails, the underlying Python binary
    #       extension may print a message to STDERR. See
    #         https://stackoverflow.com/a/17954769/1068170
    #       for an idea on how to capture STDERR during ``ParseFromString()``.
    try:
        pb.ParseFromString(pb_bytes)
    except google.protobuf.message.DecodeError:
        return None

    pb.DiscardUnknownFields()
    if pb.SerializeToString() == pb_bytes:
        return pb

    return None


def parse_pb(pb_bytes):
    """Parse a serialized protobuf and display with message name.

    Args:
        pb_bytes (str): A raw protobuf serialized as a bytestring.

    Returns:
        Tuple[str, str]: Pair of the full name of the matched message type and
        a string representation of the protobuf (with field names, etc.).

    Raises:
        ValueError: If ``pb_bytes`` could not be matched to a message type.
    """
    matches = []
    for pb_class in PB_TYPES:
        pb = _maybe_parse(pb_bytes, pb_class)
        if pb is not None:
            matches.append(pb)

    if len(matches) != 1:
        raise ValueError(
            "Serialized protobuf could not be matched to a message type",
            pb_bytes,
            matches,
        )

    pb = matches[0]
    return pb.DESCRIPTOR.full_name, str(pb).rstrip()


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
    if length == 0:
        return "\n".join(parts)

    pb_name, pb_str = parse_pb(pb_bytes)
    parts.extend(
        [
            f"Protobuf Message ({pb_name}) =",
            textwrap.indent(pb_str, "   "),
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
