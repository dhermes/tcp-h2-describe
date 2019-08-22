# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: users.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='users.proto',
  package='users.v1',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0busers.proto\x12\x08users.v1\x1a\x1bgoogle/protobuf/empty.proto\"9\n\x04User\x12\x12\n\nfirst_name\x18\x01 \x01(\t\x12\x11\n\tlast_name\x18\x02 \x01(\t\x12\n\n\x02id\x18\x03 \x01(\x04\"\"\n\x0f\x41\x64\x64UserResponse\x12\x0f\n\x07user_id\x18\x01 \x01(\x04\x32w\n\x05Users\x12\x36\n\x07\x41\x64\x64User\x12\x0e.users.v1.User\x1a\x19.users.v1.AddUserResponse\"\x00\x12\x36\n\x08GetUsers\x12\x16.google.protobuf.Empty\x1a\x0e.users.v1.User\"\x00\x30\x01\x62\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_USER = _descriptor.Descriptor(
  name='User',
  full_name='users.v1.User',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='first_name', full_name='users.v1.User.first_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='last_name', full_name='users.v1.User.last_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='users.v1.User.id', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=54,
  serialized_end=111,
)


_ADDUSERRESPONSE = _descriptor.Descriptor(
  name='AddUserResponse',
  full_name='users.v1.AddUserResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user_id', full_name='users.v1.AddUserResponse.user_id', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=113,
  serialized_end=147,
)

DESCRIPTOR.message_types_by_name['User'] = _USER
DESCRIPTOR.message_types_by_name['AddUserResponse'] = _ADDUSERRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

User = _reflection.GeneratedProtocolMessageType('User', (_message.Message,), {
  'DESCRIPTOR' : _USER,
  '__module__' : 'users_pb2'
  # @@protoc_insertion_point(class_scope:users.v1.User)
  })
_sym_db.RegisterMessage(User)

AddUserResponse = _reflection.GeneratedProtocolMessageType('AddUserResponse', (_message.Message,), {
  'DESCRIPTOR' : _ADDUSERRESPONSE,
  '__module__' : 'users_pb2'
  # @@protoc_insertion_point(class_scope:users.v1.AddUserResponse)
  })
_sym_db.RegisterMessage(AddUserResponse)



_USERS = _descriptor.ServiceDescriptor(
  name='Users',
  full_name='users.v1.Users',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=149,
  serialized_end=268,
  methods=[
  _descriptor.MethodDescriptor(
    name='AddUser',
    full_name='users.v1.Users.AddUser',
    index=0,
    containing_service=None,
    input_type=_USER,
    output_type=_ADDUSERRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='GetUsers',
    full_name='users.v1.Users.GetUsers',
    index=1,
    containing_service=None,
    input_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    output_type=_USER,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_USERS)

DESCRIPTOR.services_by_name['Users'] = _USERS

# @@protoc_insertion_point(module_scope)
