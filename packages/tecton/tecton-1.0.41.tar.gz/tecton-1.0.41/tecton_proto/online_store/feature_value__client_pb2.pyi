from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class ArrayValue(_message.Message):
    __slots__ = ["array_values", "bool_values", "float32_values", "float64_values", "int64_values", "map_values", "null_indices", "string_values", "struct_values"]
    ARRAY_VALUES_FIELD_NUMBER: ClassVar[int]
    BOOL_VALUES_FIELD_NUMBER: ClassVar[int]
    FLOAT32_VALUES_FIELD_NUMBER: ClassVar[int]
    FLOAT64_VALUES_FIELD_NUMBER: ClassVar[int]
    INT64_VALUES_FIELD_NUMBER: ClassVar[int]
    MAP_VALUES_FIELD_NUMBER: ClassVar[int]
    NULL_INDICES_FIELD_NUMBER: ClassVar[int]
    STRING_VALUES_FIELD_NUMBER: ClassVar[int]
    STRUCT_VALUES_FIELD_NUMBER: ClassVar[int]
    array_values: _containers.RepeatedCompositeFieldContainer[ArrayValue]
    bool_values: _containers.RepeatedScalarFieldContainer[bool]
    float32_values: _containers.RepeatedScalarFieldContainer[float]
    float64_values: _containers.RepeatedScalarFieldContainer[float]
    int64_values: _containers.RepeatedScalarFieldContainer[int]
    map_values: _containers.RepeatedCompositeFieldContainer[MapValue]
    null_indices: _containers.RepeatedScalarFieldContainer[int]
    string_values: _containers.RepeatedScalarFieldContainer[str]
    struct_values: _containers.RepeatedCompositeFieldContainer[StructValue]
    def __init__(self, string_values: Optional[Iterable[str]] = ..., array_values: Optional[Iterable[Union[ArrayValue, Mapping]]] = ..., struct_values: Optional[Iterable[Union[StructValue, Mapping]]] = ..., map_values: Optional[Iterable[Union[MapValue, Mapping]]] = ..., bool_values: Optional[Iterable[bool]] = ..., int64_values: Optional[Iterable[int]] = ..., float32_values: Optional[Iterable[float]] = ..., float64_values: Optional[Iterable[float]] = ..., null_indices: Optional[Iterable[int]] = ...) -> None: ...

class BatchCompactedDataRow(_message.Message):
    __slots__ = ["compacted_tile"]
    COMPACTED_TILE_FIELD_NUMBER: ClassVar[int]
    compacted_tile: FeatureValueList
    def __init__(self, compacted_tile: Optional[Union[FeatureValueList, Mapping]] = ...) -> None: ...

class BatchCompactedDataRowV2(_message.Message):
    __slots__ = ["compacted_tiles"]
    COMPACTED_TILES_FIELD_NUMBER: ClassVar[int]
    compacted_tiles: _containers.RepeatedCompositeFieldContainer[FeatureValueList]
    def __init__(self, compacted_tiles: Optional[Iterable[Union[FeatureValueList, Mapping]]] = ...) -> None: ...

class CachedFeatureView(_message.Message):
    __slots__ = ["effective_time", "feature_statuses", "feature_values", "updated_at"]
    EFFECTIVE_TIME_FIELD_NUMBER: ClassVar[int]
    FEATURE_STATUSES_FIELD_NUMBER: ClassVar[int]
    FEATURE_VALUES_FIELD_NUMBER: ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: ClassVar[int]
    effective_time: _timestamp_pb2.Timestamp
    feature_statuses: _containers.RepeatedScalarFieldContainer[int]
    feature_values: _containers.RepeatedCompositeFieldContainer[FeatureValue]
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, feature_values: Optional[Iterable[Union[FeatureValue, Mapping]]] = ..., feature_statuses: Optional[Iterable[int]] = ..., effective_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., updated_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...

class FeatureValue(_message.Message):
    __slots__ = ["array_value", "bool_value", "float32_value", "float64_value", "int64_value", "map_value", "null_value", "string_value", "struct_value"]
    ARRAY_VALUE_FIELD_NUMBER: ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: ClassVar[int]
    FLOAT32_VALUE_FIELD_NUMBER: ClassVar[int]
    FLOAT64_VALUE_FIELD_NUMBER: ClassVar[int]
    INT64_VALUE_FIELD_NUMBER: ClassVar[int]
    MAP_VALUE_FIELD_NUMBER: ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: ClassVar[int]
    STRUCT_VALUE_FIELD_NUMBER: ClassVar[int]
    array_value: ArrayValue
    bool_value: bool
    float32_value: float
    float64_value: float
    int64_value: int
    map_value: MapValue
    null_value: NullValue
    string_value: str
    struct_value: StructValue
    def __init__(self, array_value: Optional[Union[ArrayValue, Mapping]] = ..., float64_value: Optional[float] = ..., float32_value: Optional[float] = ..., int64_value: Optional[int] = ..., bool_value: bool = ..., string_value: Optional[str] = ..., null_value: Optional[Union[NullValue, Mapping]] = ..., struct_value: Optional[Union[StructValue, Mapping]] = ..., map_value: Optional[Union[MapValue, Mapping]] = ...) -> None: ...

class FeatureValueList(_message.Message):
    __slots__ = ["feature_values"]
    FEATURE_VALUES_FIELD_NUMBER: ClassVar[int]
    feature_values: _containers.RepeatedCompositeFieldContainer[FeatureValue]
    def __init__(self, feature_values: Optional[Iterable[Union[FeatureValue, Mapping]]] = ...) -> None: ...

class MapValue(_message.Message):
    __slots__ = ["keys", "values"]
    KEYS_FIELD_NUMBER: ClassVar[int]
    VALUES_FIELD_NUMBER: ClassVar[int]
    keys: ArrayValue
    values: ArrayValue
    def __init__(self, keys: Optional[Union[ArrayValue, Mapping]] = ..., values: Optional[Union[ArrayValue, Mapping]] = ...) -> None: ...

class NullValue(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class RedisTAFVData(_message.Message):
    __slots__ = ["anchor_time", "feature_values", "written_by_batch"]
    ANCHOR_TIME_FIELD_NUMBER: ClassVar[int]
    FEATURE_VALUES_FIELD_NUMBER: ClassVar[int]
    WRITTEN_BY_BATCH_FIELD_NUMBER: ClassVar[int]
    anchor_time: int
    feature_values: _containers.RepeatedCompositeFieldContainer[FeatureValue]
    written_by_batch: bool
    def __init__(self, anchor_time: Optional[int] = ..., written_by_batch: bool = ..., feature_values: Optional[Iterable[Union[FeatureValue, Mapping]]] = ...) -> None: ...

class StructValue(_message.Message):
    __slots__ = ["values"]
    VALUES_FIELD_NUMBER: ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[FeatureValue]
    def __init__(self, values: Optional[Iterable[Union[FeatureValue, Mapping]]] = ...) -> None: ...
