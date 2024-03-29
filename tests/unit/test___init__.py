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

import tcp_h2_describe


def test___version__():
    # NOTE: This hardcodes the version here to make sure `pkg_resources` picks
    #       up the version in `setup.py`.
    assert tcp_h2_describe.__version__ == "0.1.1.dev1"
