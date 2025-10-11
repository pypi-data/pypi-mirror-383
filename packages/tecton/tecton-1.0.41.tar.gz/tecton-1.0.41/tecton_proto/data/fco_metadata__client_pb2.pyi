from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import framework_version__client_pb2 as _framework_version__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class FcoMetadata(_message.Message):
    __slots__ = ["created_at", "description", "family", "framework_version", "is_archived", "last_modified_by", "last_updated_at", "name", "owner", "scope", "source_filename", "source_lineno", "tags", "workspace", "workspace_state_id"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    CREATED_AT_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    FAMILY_FIELD_NUMBER: ClassVar[int]
    FRAMEWORK_VERSION_FIELD_NUMBER: ClassVar[int]
    IS_ARCHIVED_FIELD_NUMBER: ClassVar[int]
    LAST_MODIFIED_BY_FIELD_NUMBER: ClassVar[int]
    LAST_UPDATED_AT_FIELD_NUMBER: ClassVar[int]
    NAME_FIELD_NUMBER: ClassVar[int]
    OWNER_FIELD_NUMBER: ClassVar[int]
    SCOPE_FIELD_NUMBER: ClassVar[int]
    SOURCE_FILENAME_FIELD_NUMBER: ClassVar[int]
    SOURCE_LINENO_FIELD_NUMBER: ClassVar[int]
    TAGS_FIELD_NUMBER: ClassVar[int]
    WORKSPACE_FIELD_NUMBER: ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: ClassVar[int]
    created_at: _timestamp_pb2.Timestamp
    description: str
    family: str
    framework_version: _framework_version__client_pb2.FrameworkVersion
    is_archived: bool
    last_modified_by: str
    last_updated_at: _timestamp_pb2.Timestamp
    name: str
    owner: str
    scope: str
    source_filename: str
    source_lineno: str
    tags: _containers.ScalarMap[str, str]
    workspace: str
    workspace_state_id: _id__client_pb2.Id
    def __init__(self, name: Optional[str] = ..., description: Optional[str] = ..., created_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., owner: Optional[str] = ..., last_modified_by: Optional[str] = ..., is_archived: bool = ..., workspace: Optional[str] = ..., workspace_state_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., family: Optional[str] = ..., scope: Optional[str] = ..., source_lineno: Optional[str] = ..., source_filename: Optional[str] = ..., tags: Optional[Mapping[str, str]] = ..., framework_version: Optional[Union[_framework_version__client_pb2.FrameworkVersion, str]] = ..., last_updated_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...
