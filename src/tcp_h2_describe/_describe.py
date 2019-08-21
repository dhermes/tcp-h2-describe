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

import struct
import textwrap

import hpack


PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
PREFACE_PRETTY = r"""Client Connection Preface
50 52 49 20 2a 20 48 54 54 50 2f 32 2e 30 0d 0a
0d 0a 53 4d 0d 0a 0d 0a
   --- decoded as raw bytes ---
   b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'"""
HEADER = "=" * 60
FOOTER = "-" * 40
STRUCT_H = struct.Struct(">H")
STRUCT_L = struct.Struct(">L")
HPACK_DECODER = hpack.Decoder()
# See: https://http2.github.io/http2-spec/#iana-frames
FRAME_TYPES = {
    0x0: "DATA",
    0x1: "HEADERS",
    0x2: "PRIORITY",
    0x3: "RST_STREAM",
    0x4: "SETTINGS",
    0x5: "PUSH_PROMISE",
    0x6: "PING",
    0x7: "GOAWAY",
    0x8: "WINDOW_UPDATE",
    0x9: "CONTINUATION",
}
# The following bit flags are defined "globally" (i.e. across all types), but
# some flags apply to only certain frame types (e.g. END_STREAM only applies
# to DATA or HEADERS frames). This is why the mapping is keys first based on
# the frame type.
FLAG_ACK = 0x1
FLAG_END_STREAM = 0x1
FLAG_END_HEADERS = 0x4
FLAG_PADDED = 0x8
FLAG_PRIORITY = 0x20
FLAGS_DEFINED = {
    # See: https://http2.github.io/http2-spec/#DATA
    "DATA": {FLAG_END_STREAM: "END_STREAM", FLAG_PADDED: "PADDED"},
    # See: https://http2.github.io/http2-spec/#HEADERS
    "HEADERS": {
        FLAG_END_STREAM: "END_STREAM",
        FLAG_END_HEADERS: "END_HEADERS",
        FLAG_PADDED: "PADDED",
        FLAG_PRIORITY: "PRIORITY",
    },
    # See: https://http2.github.io/http2-spec/#PRIORITY
    "PRIORITY": {},
    # See: https://http2.github.io/http2-spec/#RST_STREAM
    "RST_STREAM": {},
    # See: https://http2.github.io/http2-spec/#SETTINGS
    "SETTINGS": {FLAG_ACK: "ACK"},
    # See: https://http2.github.io/http2-spec/#PUSH_PROMISE
    "PUSH_PROMISE": {FLAG_END_HEADERS: "END_HEADERS", FLAG_PADDED: "PADDED"},
    # See: https://http2.github.io/http2-spec/#PING
    "PING": {FLAG_ACK: "ACK"},
    # See: https://http2.github.io/http2-spec/#GOAWAY
    "GOAWAY": {},
    # See: https://http2.github.io/http2-spec/#WINDOW_UPDATE
    "WINDOW_UPDATE": {},
    # See: https://http2.github.io/http2-spec/#CONTINUATION
    "CONTINUATION": {FLAG_END_HEADERS: "END_HEADERS"},
}
FRAME_PAYLOAD_HANDLERS = {}
RESERVED_HIGHEST_BIT = 0x80000000
SETTINGS = {
    # See: https://http2.github.io/http2-spec/#SettingValues
    0x1: "SETTINGS_HEADER_TABLE_SIZE",
    0x2: "SETTINGS_ENABLE_PUSH",
    0x3: "SETTINGS_MAX_CONCURRENT_STREAMS",
    0x4: "SETTINGS_INITIAL_WINDOW_SIZE",
    0x5: "SETTINGS_MAX_FRAME_SIZE",
    0x6: "SETTINGS_MAX_HEADER_LIST_SIZE",
    # See: https://tools.ietf.org/html/rfc8441
    0x8: "SETTINGS_ENABLE_CONNECT_PROTOCOL",
    # See: https://github.com/grpc/proposal/blob/master/G1-true-binary-metadata.md
    0xFE03: "GRPC_ALLOW_TRUE_BINARY_METADATA",
}


def simple_hexdump(bytes_, row_size=16):
    """Convert a bytestring into hex characters.

    This is called "simple" because it doesn't print the index in the leftmost
    column or the printable characters in the rightmost column (as the CLI
    ``hexdump -C`` does).

    Args:
        bytes_ (bytes): The bytestring to convert.
        row_size (int): The number of bytes that should go in each row of
            output. If ``row_size`` is ``-1``, then all output will go in
            a single row.

    Returns:
        str: The hexdump of ``bytes_``.
    """
    # NOTE: This utilizes the fact that iterating over a bytestring produces
    #       the corresponding integers for each character.
    if row_size == -1:
        return " ".join(f"{c:02x}" for c in bytes_)

    rows = []
    for i in range(0, len(bytes_), row_size):
        rows.append(" ".join(f"{c:02x}" for c in bytes_[i : i + row_size]))
    return "\n".join(rows)


def describe_flags(frame_type, flags):
    """Convert a set of flags into a description.

    Args:
        frame_type (str): The type of the current frame.
        flags (int): The flags for the current frame.

    Returns:
        str: The "pretty" description of the flags.

    Raises:
        RuntimeError: If not all bit flags are accounted for.
    """
    flag_map = FLAGS_DEFINED[frame_type]

    remaining = flags
    description_parts = []
    for flag_value in sorted(flag_map.keys()):
        if remaining & flag_value == flag_value:
            remaining -= flag_value
            description_parts.append(
                f"{flag_map[flag_value]}:{hex(flag_value)}"
            )

    if remaining != 0:
        raise RuntimeError("Some flags not accounted for", frame_type, flags)

    if not description_parts:
        return "UNSET"

    return " | ".join(description_parts)


def default_payload_handler(frame_payload, unused_flags):
    """Default handler for an HTTP/2 frame payload.

    Acts as identity function.

    Args:
        frame_payload (bytes): The frame payload to be parsed.
        unused_flags (int): The flags for the frame payload.

    Returns:
        str: The frame payload returned as-is with a prefix.
    """
    return f"Frame Payload = {frame_payload}"


def handle_headers_payload(frame_payload, flags):
    """Handle a HEADERS HTTP/2 frame payload.

    .. HEADERS spec: https://http2.github.io/http2-spec/#HEADERS

    See `HEADERS spec`_.

    Args:
        frame_payload (bytes): The frame payload to be parsed.
        flags (int): The flags for the frame payload.

    Returns:
        str: A list of the headers in the payload and the hexdump for
        ``frame_payload``.

    Raises:
        NotImplementedError: If ``flags`` has ``PADDED`` set.
        NotImplementedError: If ``flags`` has ``PRIORITY`` set.
    """
    if flags & FLAG_PADDED == FLAG_PADDED:
        raise NotImplementedError(
            "PADDED flag not currently supported for headers"
        )
    if flags & FLAG_PRIORITY == FLAG_PRIORITY:
        raise NotImplementedError(
            "PRIORITY flag not currently supported for headers"
        )

    lines = ["Headers ="]
    headers = HPACK_DECODER.decode(frame_payload)
    lines.extend(f"   {key!r} -> {value!r}" for key, value in headers)
    lines.append("Hexdump =")
    lines.append(textwrap.indent(simple_hexdump(frame_payload), "   "))
    return "\n".join(lines)


def handle_settings_payload(frame_payload, unused_flags):
    """Handle a SETTINGS HTTP/2 frame payload.

    .. SETTINGS spec: https://http2.github.io/http2-spec/#SETTINGS

    See `SETTINGS spec`_.

    Args:
        frame_payload (bytes): The frame payload to be parsed.
        unused_flags (int): The flags for the frame payload.

    Returns:
        str: A list of all the settings in ``frame_payload``, as well as a
        hexdump for each 6-octet setting.

    Raises:
        ValueError: If the length of ``frame_payload`` is not a multiple of 6.
    """
    num_settings, remainder = divmod(len(frame_payload), 6)
    if remainder != 0:
        raise ValueError(
            "The length of the frame payload is not a multiple of 6.",
            frame_payload,
        )

    if num_settings == 0:
        return ""

    lines = ["Settings ="]
    for setting in range(num_settings):
        start = 6 * setting

        setting_id, = STRUCT_H.unpack(frame_payload[start : start + 2])
        setting_id_str = SETTINGS.get(setting_id, "UNKNOWN")
        setting_value, = STRUCT_L.unpack(frame_payload[start + 2 : start + 6])
        setting_hex = simple_hexdump(
            frame_payload[start : start + 6], row_size=-1
        )

        lines.append(f"   {setting_id_str}: {setting_value} ({setting_hex})")

    return "\n".join(lines)


def handle_ping_payload(frame_payload, unused_flags):
    """Handle a PING HTTP/2 frame payload.

    .. PING spec: https://http2.github.io/http2-spec/#PING

    See `PING spec`_.

    Args:
        frame_payload (bytes): The frame payload to be parsed.
        unused_flags (int): The flags for the frame payload.

    Returns:
        str: The opaque data in ``frame_payload`` as a hexdump.

    Raises:
        ValueError: If the length of ``frame_payload`` is not 8.
    """
    if len(frame_payload) != 8:
        raise ValueError(
            "The length of the frame payload is not 8.", frame_payload
        )

    opaque_data = simple_hexdump(frame_payload, row_size=-1)
    return f"Opaque Data = {opaque_data}"


def handle_window_update_payload(frame_payload, unused_flags):
    """Handle a WINDOW_UPDATE HTTP/2 frame payload.

    .. WINDOW_UPDATE spec: https://http2.github.io/http2-spec/#WINDOW_UPDATE

    See `WINDOW_UPDATE spec`_.

    Args:
        frame_payload (bytes): The frame payload to be parsed.
        unused_flags (int): The flags for the frame payload.

    Returns:
        str: Description of the reserved bit, window size increment and display
            of the hexdump for ``frame_payload``.

    Raises:
        ValueError: If the ``frame_payload`` does not have 4 bytes.
    """
    if len(frame_payload) != 4:
        raise ValueError("")

    window_size_increment, = STRUCT_L.unpack(frame_payload)
    reserved_bit = 0
    if window_size_increment & RESERVED_HIGHEST_BIT == RESERVED_HIGHEST_BIT:
        reserved_bit = 1
        window_size_increment -= RESERVED_HIGHEST_BIT

    return (
        f"Reserved Bit = {reserved_bit}, "
        f"Window Size Increment = {window_size_increment}"
        f"({simple_hexdump(frame_payload, row_size=-1)})"
    )


def next_h2_frame(h2_frames):
    """Parse the next HTTP/2 frame from a partially parsed TCP frame.

    .. frame header spec: https://http2.github.io/http2-spec/#FrameHeader

    Args:
        h2_frames (bytes): The remaining unparsed HTTP/2 frames (as raw bytes)
            from TCP frame sent via TCP.

    Returns:
        Tuple[List[str], bytes]: A pair of
        * The message parts for the parsed HTTP/2 frame.
        * The remaining bytes in ``h2_frames``; i.e. the frame that was just
          parsed will be removed.

    Raises:
        RuntimeError: If ``h2_frames`` contains fewer than 9 bytes. This is
            because all frames begin with a fixed 9-octet header followed by
            a variable-length payload. See `frame header spec`_.
        RuntimeError: If ``h2_frames`` contains fewer than ``9 + frame_length``
            bytes. The ``frame_length`` is determined by the first 3 bytes.
    """
    if len(h2_frames) < 9:
        raise RuntimeError(
            "Not large enough to contain an HTTP/2 frame", h2_frames
        )

    # Frame length
    frame_length, = STRUCT_L.unpack(b"\x00" + h2_frames[:3])
    frame_length_hex = simple_hexdump(h2_frames[:3], row_size=-1)
    parts = [f"Frame Length = {frame_length} ({frame_length_hex})"]
    # Frame Type
    frame_type = FRAME_TYPES[h2_frames[3]]
    frame_type_hex = simple_hexdump(h2_frames[3:4], row_size=-1)
    parts.append(f"Frame Type = {frame_type} ({frame_type_hex})")
    # Flags
    flags = h2_frames[4]
    flags_str = describe_flags(frame_type, flags)
    flags_hex = simple_hexdump(h2_frames[4:5], row_size=-1)
    parts.append(f"Flags = {flags_str} ({flags_hex})")
    # Stream Identifier
    stream_identifier, = STRUCT_L.unpack(h2_frames[5:9])
    stream_identifier_hex = simple_hexdump(h2_frames[5:9], row_size=-1)
    parts.append(
        f"Stream Identifier = {stream_identifier} ({stream_identifier_hex})"
    )
    # Frame Payload
    frame_payload = h2_frames[9 : 9 + frame_length]
    if len(frame_payload) != frame_length:
        raise RuntimeError(
            " HTTP/2 frame not large enough to contain frame payload",
            h2_frames,
        )
    handler = FRAME_PAYLOAD_HANDLERS.get(frame_type, default_payload_handler)
    frame_payload_part = handler(frame_payload, flags)
    if frame_payload_part != "":
        parts.append(frame_payload_part)

    return parts, h2_frames[9 + frame_length :]


def describe(h2_frames, connection_description, expect_preface):
    """Describe an HTTP/2 frame.

    .. connection header spec: https://http2.github.io/http2-spec/#ConnectionHeader

    Args:
        h2_frames (bytes): The raw bytes of a TCP frame containing HTTP/2
            frames that have been sent via TCP.
        connection_description (str): A description of the RECV->SEND
            relationship for a socket pair.
        expect_preface (bool): Indicates if the ``h2_frames`` should begin
            with the client connection preface. This should only be
            :data:`True` on the **first** TCP frame for the client socket.
            See `connection header spec`_.

    Returns:
        str: The description of ``h2_frames``, expected to be printed by the
            caller.

    Raises:
        RuntimeError: If ``expect_preface`` is :data:`True` but ``h2_frames``
            does not begin with the client connection preface.
    """
    parts = [HEADER, connection_description, ""]

    if expect_preface:
        if not h2_frames.startswith(PREFACE):
            raise RuntimeError(
                "Expected TCP frame to begin with client connection preface",
                h2_frames,
            )

        parts.extend([PREFACE_PRETTY, FOOTER])
        h2_frames = h2_frames[len(PREFACE) :]

    while h2_frames:
        frame_parts, h2_frames = next_h2_frame(h2_frames)
        parts.extend(frame_parts)
        parts.append(FOOTER)

    return "\n".join(parts)


# Register the frame payload handlers.
FRAME_PAYLOAD_HANDLERS["HEADERS"] = handle_headers_payload
FRAME_PAYLOAD_HANDLERS["WINDOW_UPDATE"] = handle_window_update_payload
FRAME_PAYLOAD_HANDLERS["SETTINGS"] = handle_settings_payload
FRAME_PAYLOAD_HANDLERS["PING"] = handle_ping_payload
