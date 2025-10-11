from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AutoscalingConfig(_message.Message):
    __slots__ = ["max_nodes", "min_nodes"]
    MAX_NODES_FIELD_NUMBER: ClassVar[int]
    MIN_NODES_FIELD_NUMBER: ClassVar[int]
    max_nodes: int
    min_nodes: int
    def __init__(self, min_nodes: Optional[int] = ..., max_nodes: Optional[int] = ...) -> None: ...

class ProvisionedScalingConfig(_message.Message):
    __slots__ = ["desired_nodes"]
    DESIRED_NODES_FIELD_NUMBER: ClassVar[int]
    desired_nodes: int
    def __init__(self, desired_nodes: Optional[int] = ...) -> None: ...
