from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetUserByIdResponse(_message.Message):
    __slots__ = ["display_name", "user_name"]
    DISPLAY_NAME_FIELD_NUMBER: ClassVar[int]
    USER_NAME_FIELD_NUMBER: ClassVar[int]
    display_name: str
    user_name: str
    def __init__(self, user_name: Optional[str] = ..., display_name: Optional[str] = ...) -> None: ...
