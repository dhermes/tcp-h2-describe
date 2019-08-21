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


PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
PREFACE_PRETTY = r"""Client Connection Preface
50 52 49 20 2a 20 48 54 54 50 2f 32 2e 30 0d 0a
0d 0a 53 4d 0d 0a 0d 0a
   ... decoded as raw bytes ...
   b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'"""
HEADER = "=" * 60
FOOTER = "-" * 40


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

    parts.extend([f"HTTP/2 frame: {h2_frames}", FOOTER])
    return "\n".join(parts)
