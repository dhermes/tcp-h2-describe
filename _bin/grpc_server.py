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

import concurrent.futures
import os
import random
import textwrap
import threading
import time

import grpc

import users_pb2
import users_pb2_grpc


_MAX_ID = 2 ** 64 - 1
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def _new_id(locked_container, max_attempts):
    """Compute a new (random) ID.

    The container is named ``locked_container``; the assumption is that the
    caller is using a mutex to prevent other code from modifying the container
    while this function executes.

    Args:
        locked_container (Container): A container that has IDs as indices,
            e.g. ``10 in locked_container``.
        max_attempts (int): The maximum number of random numbers to be
            generated.

    Returns:
        int: The randomly generated ID.

    Raises:
        RuntimeError: If no random number can be generated.
    """
    for _ in range(max_attempts):
        # NOTE: Don't use 0, because the 0-value corresponds to unset.
        new_id = random.randint(1, _MAX_ID)
        if new_id not in locked_container:
            return new_id

    raise RuntimeError(
        f"Failed to generate a new ID in {max_attempts} attempts"
    )


class Users:
    def __init__(self, *args, **kwargs):
        self._database = {}
        # NOTE: We hold this lock for **all** operations on ``_database``.
        self._lock = threading.Lock()
        super().__init__(*args, **kwargs)

    def AddUser(self, request, context):
        """Add a user to the database.

        Args:
            request (users_pb2.User): The request from the API.
            context (grpc._server._Context): A request context.

        Returns:
            users_pb2.AddUserResponse: The response containing the ID in the
            DB for the inserted user.
        """
        print(f"AddUser:\n{textwrap.indent(str(request), '   ')}")

        if request.id != 0:
            message = "`id` cannot be set on user creation"
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(message)
            return users_pb2.AddUserResponse()

        with self._lock:
            inserted_id = _new_id(self._database, 5)
            self._database[inserted_id] = (
                request.first_name,
                request.last_name,
            )
            return users_pb2.AddUserResponse(user_id=inserted_id)

    def GetUsers(self, request, unused_context):
        """Get all users from the database.

        Args:
            request (google.protobuf.empty_pb2.Empty): The request from
                the API.
            unused_context (grpc._server._Context): A request context.

        Returns:
            Generator[users_pb2.Users]: The response stream containing all
            users in the DB.
        """
        print("GetUsers: (empty)")

        with self._lock:
            user_ids = sorted(self._database.keys())
            for user_id in user_ids:
                # NOTE: This **does not** try to catch a ``KeyError`` because
                #       it assumes the ID **must** be in there.
                first_name, last_name = self._database[user_id]
                yield users_pb2.User(
                    id=user_id, first_name=first_name, last_name=last_name
                )


class UsersServicer(Users, users_pb2_grpc.UsersServicer):
    pass


def wait_for_termination(server):
    # See:
    # https://github.com/grpc/grpc/pull/19299
    # https://github.com/grpc/grpc/pull/19852
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


def serve(grpc_port):
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UsersServicer_to_server(UsersServicer(), server)

    server.add_insecure_port(f"[::]:{grpc_port}")
    print(f"Running Users service on port {grpc_port}")
    server.start()
    wait_for_termination(server)


def main():
    grpc_port = os.environ.get("GRPC_PORT", 50051)
    serve(grpc_port)


if __name__ == "__main__":
    main()
