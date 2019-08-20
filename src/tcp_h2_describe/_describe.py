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


import tcp_h2_describe._display


def describe(h2_frame, connection_description):
    """Describe an HTTP/2 frame.

    Args:
        h2_frame (bytes): The raw bytes of an HTTP/2 frame that has been sent
            via TCP.
        connection_description (str): A description of the RECV->SEND
            relationship for a socket pair.
    """
    # NOTE: For now this is a dummy implementation.
    message = f"{connection_description}\n\nHTTP/2 frame: {h2_frame}"
    tcp_h2_describe._display.display(message)
