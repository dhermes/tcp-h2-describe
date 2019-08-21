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


VERSION = "0.0.2"
REQUIREMENTS = ("hpack >= 3.0.0",)
DESCRIPTION = (
    "Python library and CLI for running an HTTP/2 proxy that describes "
    "each frame"
)
LONG_DESCRIPTION = open("README.md", "r", encoding="utf-8").read()


def main():
    setuptools.setup(
        name="tcp-h2-describe",
        version=VERSION,
        description=DESCRIPTION,
        author="Danny Hermes",
        author_email="daniel.j.hermes@gmail.com",
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        scripts=(),
        url="https://github.com/dhermes/tcp-h2-describe",
        project_urls={
            "Issue Tracker": "https://github.com/dhermes/tcp-h2-describe"
        },
        keywords=["TCP", "HTTP/2", "Networking", "Proxy"],
        packages=("tcp_h2_describe",),
        package_dir={"": "src"},
        license="Apache 2.0",
        platforms="Posix; macOS; Windows",
        zip_safe=True,
        install_requires=REQUIREMENTS,
        entry_points={
            "console_scripts": (
                "tcp-h2-describe=tcp_h2_describe.__main__:main",
            )
        },
        classifiers=[
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
        ],
    )


if __name__ == "__main__":
    main()
