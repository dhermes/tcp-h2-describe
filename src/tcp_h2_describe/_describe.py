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
_STRUCT_L = struct.Struct(">L")


def _simple_hexdump(bytes_, row_size=16):
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


def _next_h2_frame(h2_frames):
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
    frame_length, = _STRUCT_L.unpack(b"\x00" + h2_frames[:3])
    frame_length_hex = _simple_hexdump(h2_frames[:3], row_size=-1)
    parts = [f"Frame Length = {frame_length} ({frame_length_hex})"]
    # Frame Type
    frame_type = h2_frames[3]
    frame_type_hex = _simple_hexdump(h2_frames[3:4], row_size=-1)
    parts.append(f"Frame Type = {frame_type} ({frame_type_hex})")
    # Flags
    flags = h2_frames[4]
    flags_hex = _simple_hexdump(h2_frames[4:5], row_size=-1)
    parts.append(f"Flags = {flags} ({flags_hex})")
    # Stream Identifier
    stream_identifier, = _STRUCT_L.unpack(h2_frames[5:9])
    stream_identifier_hex = _simple_hexdump(h2_frames[5:9], row_size=-1)
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
        frame_parts, h2_frames = _next_h2_frame(h2_frames)
        parts.extend(frame_parts)
        parts.append(FOOTER)

    return "\n".join(parts)
