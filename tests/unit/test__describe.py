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

import pytest

import tcp_h2_describe._describe


class Test_describe:
    @staticmethod
    def test_invalid_preface():
        h2_frames = b""
        connection_description = "client->server"

        with pytest.raises(RuntimeError) as exc_info:
            tcp_h2_describe._describe.describe(
                h2_frames, connection_description, True, None
            )

        expected_args = (
            "Expected TCP frame to begin with client connection preface",
            h2_frames,
        )
        assert exc_info.value.args == expected_args

    @staticmethod
    def test_with_preface():
        h2_frames = (
            b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n\x00\x00$\x04\x00\x00\x00\x00"
            b"\x00\x00\x01\x00\x00\x10\x00\x00\x02\x00\x00\x00\x01\x00\x04\x00"
            b"\x00\xff\xff\x00\x05\x00\x00@\x00\x00\x03\x00\x00\x00d\x00\x06"
            b"\x00\x01\x00\x00\x00\x00\x06\x04\x00\x00\x00\x00\x00\x00\x02"
            b"\x00\x00\x00\x00"
        )
        connection_description = "client->server"

        message = tcp_h2_describe._describe.describe(
            h2_frames, connection_description, True, None
        )
        expected = "\n".join(
            [
                tcp_h2_describe._describe.HEADER,
                connection_description,
                "",
                tcp_h2_describe._describe.PREFACE_PRETTY,
                tcp_h2_describe._describe.FOOTER,
                "Frame Length = 36 (00 00 24)",
                "Frame Type = SETTINGS (04)",
                "Flags = UNSET (00)",
                "Stream Identifier = 0 (00 00 00 00)",
                "Settings =",
                "   SETTINGS_HEADER_TABLE_SIZE:0x1 -> 4096 (00 01 | 00 00 10 00)",
                "   SETTINGS_ENABLE_PUSH:0x2 -> 1 (00 02 | 00 00 00 01)",
                "   SETTINGS_INITIAL_WINDOW_SIZE:0x4 -> 65535 (00 04 | 00 00 ff ff)",
                "   SETTINGS_MAX_FRAME_SIZE:0x5 -> 16384 (00 05 | 00 00 40 00)",
                "   SETTINGS_MAX_CONCURRENT_STREAMS:0x3 -> 100 (00 03 | 00 00 00 64)",
                "   SETTINGS_MAX_HEADER_LIST_SIZE:0x6 -> 65536 (00 06 | 00 01 00 00)",
                tcp_h2_describe._describe.FOOTER,
                "Frame Length = 6 (00 00 06)",
                "Frame Type = SETTINGS (04)",
                "Flags = UNSET (00)",
                "Stream Identifier = 0 (00 00 00 00)",
                "Settings =",
                "   SETTINGS_ENABLE_PUSH:0x2 -> 0 (00 02 | 00 00 00 00)",
                tcp_h2_describe._describe.FOOTER,
            ]
        )
        assert message == expected

    @staticmethod
    def test_without_preface():
        h2_frames = (
            b"\x00\x00$\x04\x00\x00\x00\x00\x00\x00\x01\x00\x00\x10\x00\x00"
            b"\x02\x00\x00\x00\x00\x00\x04\x00\x00\xff\xff\x00\x05\x00\x00@"
            b"\x00\x00\x03\x00\x00\x00d\x00\x06\x00\x01\x00\x00"
        )
        connection_description = "server->client"

        message = tcp_h2_describe._describe.describe(
            h2_frames, connection_description, False, None
        )
        expected = "\n".join(
            [
                tcp_h2_describe._describe.HEADER,
                connection_description,
                "",
                "Frame Length = 36 (00 00 24)",
                "Frame Type = SETTINGS (04)",
                "Flags = UNSET (00)",
                "Stream Identifier = 0 (00 00 00 00)",
                "Settings =",
                "   SETTINGS_HEADER_TABLE_SIZE:0x1 -> 4096 (00 01 | 00 00 10 00)",
                "   SETTINGS_ENABLE_PUSH:0x2 -> 0 (00 02 | 00 00 00 00)",
                "   SETTINGS_INITIAL_WINDOW_SIZE:0x4 -> 65535 (00 04 | 00 00 ff ff)",
                "   SETTINGS_MAX_FRAME_SIZE:0x5 -> 16384 (00 05 | 00 00 40 00)",
                "   SETTINGS_MAX_CONCURRENT_STREAMS:0x3 -> 100 (00 03 | 00 00 00 64)",
                "   SETTINGS_MAX_HEADER_LIST_SIZE:0x6 -> 65536 (00 06 | 00 01 00 00)",
                tcp_h2_describe._describe.FOOTER,
            ]
        )
        assert message == expected
