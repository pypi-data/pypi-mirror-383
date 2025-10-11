from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.auditlog import metadata__client_pb2 as _metadata__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ComputeIdentity(_message.Message):
    __slots__ = ["databricks_service_principal"]
    DATABRICKS_SERVICE_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    databricks_service_principal: DatabricksServicePrincipal
    def __init__(self, databricks_service_principal: _Optional[_Union[DatabricksServicePrincipal, _Mapping]] = ...) -> None: ...

class DatabricksServicePrincipal(_message.Message):
    __slots__ = ["application_id"]
    APPLICATION_ID_FIELD_NUMBER: _ClassVar[int]
    application_id: str
    def __init__(self, application_id: _Optional[str] = ...) -> None: ...

class Workspace(_message.Message):
    __slots__ = ["capabilities", "compute_identities", "created_at", "name"]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_IDENTITIES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    capabilities: WorkspaceCapabilities
    compute_identities: _containers.RepeatedCompositeFieldContainer[ComputeIdentity]
    created_at: _timestamp_pb2.Timestamp
    name: str
    def __init__(self, name: _Optional[str] = ..., capabilities: _Optional[_Union[WorkspaceCapabilities, _Mapping]] = ..., compute_identities: _Optional[_Iterable[_Union[ComputeIdentity, _Mapping]]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class WorkspaceCapabilities(_message.Message):
    __slots__ = ["materializable", "offline_store_subdirectory_enabled"]
    MATERIALIZABLE_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_SUBDIRECTORY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    materializable: bool
    offline_store_subdirectory_enabled: bool
    def __init__(self, materializable: bool = ..., offline_store_subdirectory_enabled: bool = ...) -> None: ...
