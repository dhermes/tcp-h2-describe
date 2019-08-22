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

import nox
import pathlib


nox.options.error_on_external_run = True
DEFAULT_INTERPRETER = "3.7"
HERE = pathlib.Path(__file__).resolve().parent


def get_path(*parts, relative=True):
    full_path = parts
    if not relative:
        full_path = HERE.parts + parts
    return str(pathlib.Path(*full_path))


@nox.session(py=[DEFAULT_INTERPRETER])
def unit(session):
    """Run unit tests."""
    # Install all dependencies.
    session.install("--upgrade", "pytest")
    # Install this package.
    session.install("--upgrade", ".")

    # Run pytest against the unit tests.
    run_args = ["pytest"] + session.posargs + [get_path("tests", "unit")]
    session.run(*run_args)


@nox.session(py=DEFAULT_INTERPRETER)
def generate_pb(session):
    """(Re)-generate ``*_pb2.py`` files from ``protobuf`` definitions."""
    # Install all dependencies.
    session.install("--upgrade", "grpcio-tools")
    # Generate the ``*_pb2.py`` files.
    src_dest = get_path("_grpc", relative=False)
    session.run(
        "python",
        "-m",
        "grpc_tools.protoc",
        "-I" + get_path("_grpc"),
        "--python_out",
        src_dest,
        "--grpc_python_out",
        src_dest,
        get_path("_grpc", "users.proto"),
    )
