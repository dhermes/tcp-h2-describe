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

from __future__ import print_function

import setuptools


VERSION = "0.0.1"
REQUIREMENTS = ()


def main():
    setuptools.setup(
        name="tcp-h2-describe",
        version=VERSION,
        scripts=(),
        package_dir={"": "src"},
        packages=("tcp_h2_describe",),
        zip_safe=True,
        install_requires=REQUIREMENTS,
        entry_points={
            "console_scripts": (
                "tcp-h2-describe=tcp_h2_describe.__main__:main",
            )
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
        ],
    )


if __name__ == "__main__":
    main()
