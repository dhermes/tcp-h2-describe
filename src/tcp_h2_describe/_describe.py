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


PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
PREFACE_PRETTY = r"""Client Connection Preface
50 52 49 20 2a 20 48 54 54 50 2f 32 2e 30 0d 0a
0d 0a 53 4d 0d 0a 0d 0a
   --- decoded as raw bytes ---
   b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'"""
HEADER = "=" * 60
FOOTER = "-" * 40
STRUCT_L = struct.Struct(">L")
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
FLAGS_DEFINED = {
    # See: https://http2.github.io/http2-spec/#DATA
    "DATA": {0x1: "END_STREAM", 0x8: "PADDED"},
    # See: https://http2.github.io/http2-spec/#HEADERS
    "HEADERS": {
        0x1: "END_STREAM",
        0x4: "END_HEADERS",
        0x8: "PADDED",
        0x20: "PRIORITY",
    },
    # See: https://http2.github.io/http2-spec/#PRIORITY
    "PRIORITY": {},
    # See: https://http2.github.io/http2-spec/#RST_STREAM
    "RST_STREAM": {},
    # See: https://http2.github.io/http2-spec/#SETTINGS
    "SETTINGS": {0x1: "ACK"},
    # See: https://http2.github.io/http2-spec/#PUSH_PROMISE
    "PUSH_PROMISE": {0x4: "END_HEADERS", 0x8: "PADDED"},
    # See: https://http2.github.io/http2-spec/#PING
    "PING": {0x1: "ACK"},
    # See: https://http2.github.io/http2-spec/#GOAWAY
    "GOAWAY": {},
    # See: https://http2.github.io/http2-spec/#WINDOW_UPDATE
    "WINDOW_UPDATE": {},
    # See: https://http2.github.io/http2-spec/#CONTINUATION
    "CONTINUATION": {0x4: "END_HEADERS"},
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
    flags = describe_flags(frame_type, h2_frames[4])
    flags_hex = simple_hexdump(h2_frames[4:5], row_size=-1)
    parts.append(f"Flags = {flags} ({flags_hex})")
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
    parts.append(f"Frame Payload = {frame_payload}")

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
