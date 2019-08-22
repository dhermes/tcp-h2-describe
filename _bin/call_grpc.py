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

import os
import textwrap

import google.protobuf.empty_pb2
import grpc

import users_pb2
import users_pb2_grpc


_EMPTY = google.protobuf.empty_pb2.Empty()


def insert_user(stub, first_name, last_name):
    user = users_pb2.User(first_name=first_name, last_name=last_name)
    response = stub.AddUser(user)
    print(f"Inserted user:\n{textwrap.indent(str(response), '   ')}")


def main():
    grpc_port = os.environ.get("GRPC_PORT", 50051)

    address = f"localhost:{grpc_port}"
    with grpc.insecure_channel(address) as channel:
        stub = users_pb2_grpc.UsersStub(channel)
        # Insert users.
        insert_user(stub, "Bob", "Green")
        insert_user(stub, "Alice", "Redmond")
        # Get users.
        print("Retrieving users:")
        for user in stub.GetUsers(_EMPTY):
            print(f"   User:\n{textwrap.indent(str(user), '      ')}")


if __name__ == "__main__":
    main()
