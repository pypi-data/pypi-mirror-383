from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ErrorResponse(_message.Message):
    __slots__ = ["error_code", "message"]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    error_code: str
    message: str
    def __init__(self, error_code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
