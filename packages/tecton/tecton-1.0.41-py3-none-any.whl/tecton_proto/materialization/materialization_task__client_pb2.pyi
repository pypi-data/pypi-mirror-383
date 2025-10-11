from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.args import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.common import compute_mode__client_pb2 as _compute_mode__client_pb2
from tecton_proto.common import fco_locator__client_pb2 as _fco_locator__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.data import batch_data_source__client_pb2 as _batch_data_source__client_pb2
from tecton_proto.materialization import materialization_states__client_pb2 as _materialization_states__client_pb2
from tecton_proto.materialization import spark_cluster__client_pb2 as _spark_cluster__client_pb2
from tecton_proto.online_store_writer import config__client_pb2 as _config__client_pb2
from tecton_proto.snowflake import location__client_pb2 as _location__client_pb2
from tecton_proto.spark_api import jobs__client_pb2 as _jobs__client_pb2
from tecton_proto.spark_common import libraries__client_pb2 as _libraries__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class Attempt(_message.Message):
    __slots__ = ["has_legacy_materialization_task_attempt", "workflow_id"]
    HAS_LEGACY_MATERIALIZATION_TASK_ATTEMPT_FIELD_NUMBER: ClassVar[int]
    WORKFLOW_ID_FIELD_NUMBER: ClassVar[int]
    has_legacy_materialization_task_attempt: bool
    workflow_id: _id__client_pb2.Id
    def __init__(self, workflow_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., has_legacy_materialization_task_attempt: bool = ...) -> None: ...

class BatchMaterializationParameters(_message.Message):
    __slots__ = ["batch_compaction_enabled", "bootstraps_online_store", "create_online_table", "create_online_table_parameters", "feature_end_time", "feature_start_time", "is_overwrite", "is_overwrite_backfill", "read_from_offline_store_for_online_write", "task_dependencies", "tile_count", "window_end_time", "window_start_time", "write_to_offline_feature_store", "write_to_online_feature_store"]
    BATCH_COMPACTION_ENABLED_FIELD_NUMBER: ClassVar[int]
    BOOTSTRAPS_ONLINE_STORE_FIELD_NUMBER: ClassVar[int]
    CREATE_ONLINE_TABLE_FIELD_NUMBER: ClassVar[int]
    CREATE_ONLINE_TABLE_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: ClassVar[int]
    IS_OVERWRITE_BACKFILL_FIELD_NUMBER: ClassVar[int]
    IS_OVERWRITE_FIELD_NUMBER: ClassVar[int]
    READ_FROM_OFFLINE_STORE_FOR_ONLINE_WRITE_FIELD_NUMBER: ClassVar[int]
    TASK_DEPENDENCIES_FIELD_NUMBER: ClassVar[int]
    TILE_COUNT_FIELD_NUMBER: ClassVar[int]
    WINDOW_END_TIME_FIELD_NUMBER: ClassVar[int]
    WINDOW_START_TIME_FIELD_NUMBER: ClassVar[int]
    WRITE_TO_OFFLINE_FEATURE_STORE_FIELD_NUMBER: ClassVar[int]
    WRITE_TO_ONLINE_FEATURE_STORE_FIELD_NUMBER: ClassVar[int]
    batch_compaction_enabled: bool
    bootstraps_online_store: bool
    create_online_table: bool
    create_online_table_parameters: CreateOnlineTableParameters
    feature_end_time: _timestamp_pb2.Timestamp
    feature_start_time: _timestamp_pb2.Timestamp
    is_overwrite: bool
    is_overwrite_backfill: bool
    read_from_offline_store_for_online_write: bool
    task_dependencies: MaterializationTaskDep
    tile_count: int
    window_end_time: _timestamp_pb2.Timestamp
    window_start_time: _timestamp_pb2.Timestamp
    write_to_offline_feature_store: bool
    write_to_online_feature_store: bool
    def __init__(self, window_start_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., window_end_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., feature_start_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., feature_end_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., tile_count: Optional[int] = ..., write_to_online_feature_store: bool = ..., write_to_offline_feature_store: bool = ..., is_overwrite_backfill: bool = ..., bootstraps_online_store: bool = ..., read_from_offline_store_for_online_write: bool = ..., create_online_table: bool = ..., create_online_table_parameters: Optional[Union[CreateOnlineTableParameters, Mapping]] = ..., batch_compaction_enabled: bool = ..., is_overwrite: bool = ..., task_dependencies: Optional[Union[MaterializationTaskDep, Mapping]] = ...) -> None: ...

class CanaryParams(_message.Message):
    __slots__ = ["canary_id", "canary_library_overrides", "canary_online_config", "canary_run_name", "canary_spark_cluster_environment", "canary_streaming_checkpoint_path"]
    CANARY_ID_FIELD_NUMBER: ClassVar[int]
    CANARY_LIBRARY_OVERRIDES_FIELD_NUMBER: ClassVar[int]
    CANARY_ONLINE_CONFIG_FIELD_NUMBER: ClassVar[int]
    CANARY_RUN_NAME_FIELD_NUMBER: ClassVar[int]
    CANARY_SPARK_CLUSTER_ENVIRONMENT_FIELD_NUMBER: ClassVar[int]
    CANARY_STREAMING_CHECKPOINT_PATH_FIELD_NUMBER: ClassVar[int]
    canary_id: str
    canary_library_overrides: _containers.RepeatedCompositeFieldContainer[_libraries__client_pb2.Library]
    canary_online_config: _config__client_pb2.OnlineStoreWriterConfiguration
    canary_run_name: str
    canary_spark_cluster_environment: _spark_cluster__client_pb2.SparkClusterEnvironment
    canary_streaming_checkpoint_path: str
    def __init__(self, canary_id: Optional[str] = ..., canary_online_config: Optional[Union[_config__client_pb2.OnlineStoreWriterConfiguration, Mapping]] = ..., canary_streaming_checkpoint_path: Optional[str] = ..., canary_library_overrides: Optional[Iterable[Union[_libraries__client_pb2.Library, Mapping]]] = ..., canary_spark_cluster_environment: Optional[Union[_spark_cluster__client_pb2.SparkClusterEnvironment, Mapping]] = ..., canary_run_name: Optional[str] = ...) -> None: ...

class CreateOnlineTableParameters(_message.Message):
    __slots__ = ["import_path_prefix"]
    IMPORT_PATH_PREFIX_FIELD_NUMBER: ClassVar[int]
    import_path_prefix: str
    def __init__(self, import_path_prefix: Optional[str] = ...) -> None: ...

class DatasetGenerationParameters(_message.Message):
    __slots__ = ["batch_config", "cluster_config", "dataset", "dataset_name", "datetime_range", "expected_schema", "extra_config", "feature_service", "feature_view", "from_source", "result_path", "spine"]
    class BatchConfigInput(_message.Message):
        __slots__ = ["batch_source", "end", "start"]
        BATCH_SOURCE_FIELD_NUMBER: ClassVar[int]
        END_FIELD_NUMBER: ClassVar[int]
        START_FIELD_NUMBER: ClassVar[int]
        batch_source: _batch_data_source__client_pb2.BatchDataSource
        end: _timestamp_pb2.Timestamp
        start: _timestamp_pb2.Timestamp
        def __init__(self, batch_source: Optional[Union[_batch_data_source__client_pb2.BatchDataSource, Mapping]] = ..., start: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., end: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...
    class DateTimeRangeInput(_message.Message):
        __slots__ = ["end", "entities_path", "max_lookback", "start"]
        END_FIELD_NUMBER: ClassVar[int]
        ENTITIES_PATH_FIELD_NUMBER: ClassVar[int]
        MAX_LOOKBACK_FIELD_NUMBER: ClassVar[int]
        START_FIELD_NUMBER: ClassVar[int]
        end: _timestamp_pb2.Timestamp
        entities_path: str
        max_lookback: _timestamp_pb2.Timestamp
        start: _timestamp_pb2.Timestamp
        def __init__(self, start: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., end: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., max_lookback: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., entities_path: Optional[str] = ...) -> None: ...
    class ExtraConfigEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: str
        def __init__(self, key: Optional[str] = ..., value: Optional[str] = ...) -> None: ...
    class SpineInput(_message.Message):
        __slots__ = ["path", "timestamp_key"]
        PATH_FIELD_NUMBER: ClassVar[int]
        TIMESTAMP_KEY_FIELD_NUMBER: ClassVar[int]
        path: str
        timestamp_key: str
        def __init__(self, path: Optional[str] = ..., timestamp_key: Optional[str] = ...) -> None: ...
    BATCH_CONFIG_FIELD_NUMBER: ClassVar[int]
    CLUSTER_CONFIG_FIELD_NUMBER: ClassVar[int]
    DATASET_FIELD_NUMBER: ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: ClassVar[int]
    DATETIME_RANGE_FIELD_NUMBER: ClassVar[int]
    EXPECTED_SCHEMA_FIELD_NUMBER: ClassVar[int]
    EXTRA_CONFIG_FIELD_NUMBER: ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: ClassVar[int]
    FROM_SOURCE_FIELD_NUMBER: ClassVar[int]
    RESULT_PATH_FIELD_NUMBER: ClassVar[int]
    SPINE_FIELD_NUMBER: ClassVar[int]
    batch_config: DatasetGenerationParameters.BatchConfigInput
    cluster_config: _feature_view__client_pb2.ClusterConfig
    dataset: _fco_locator__client_pb2.IdFcoLocator
    dataset_name: str
    datetime_range: DatasetGenerationParameters.DateTimeRangeInput
    expected_schema: _schema__client_pb2.Schema
    extra_config: _containers.ScalarMap[str, str]
    feature_service: _fco_locator__client_pb2.IdFcoLocator
    feature_view: _fco_locator__client_pb2.IdFcoLocator
    from_source: bool
    result_path: str
    spine: DatasetGenerationParameters.SpineInput
    def __init__(self, from_source: bool = ..., feature_service: Optional[Union[_fco_locator__client_pb2.IdFcoLocator, Mapping]] = ..., feature_view: Optional[Union[_fco_locator__client_pb2.IdFcoLocator, Mapping]] = ..., dataset: Optional[Union[_fco_locator__client_pb2.IdFcoLocator, Mapping]] = ..., dataset_name: Optional[str] = ..., spine: Optional[Union[DatasetGenerationParameters.SpineInput, Mapping]] = ..., datetime_range: Optional[Union[DatasetGenerationParameters.DateTimeRangeInput, Mapping]] = ..., batch_config: Optional[Union[DatasetGenerationParameters.BatchConfigInput, Mapping]] = ..., result_path: Optional[str] = ..., cluster_config: Optional[Union[_feature_view__client_pb2.ClusterConfig, Mapping]] = ..., extra_config: Optional[Mapping[str, str]] = ..., expected_schema: Optional[Union[_schema__client_pb2.Schema, Mapping]] = ...) -> None: ...

class DeletionParameters(_message.Message):
    __slots__ = ["offline", "offline_join_keys_path", "online", "online_join_keys_full_path", "online_join_keys_path"]
    OFFLINE_FIELD_NUMBER: ClassVar[int]
    OFFLINE_JOIN_KEYS_PATH_FIELD_NUMBER: ClassVar[int]
    ONLINE_FIELD_NUMBER: ClassVar[int]
    ONLINE_JOIN_KEYS_FULL_PATH_FIELD_NUMBER: ClassVar[int]
    ONLINE_JOIN_KEYS_PATH_FIELD_NUMBER: ClassVar[int]
    offline: bool
    offline_join_keys_path: str
    online: bool
    online_join_keys_full_path: str
    online_join_keys_path: str
    def __init__(self, online_join_keys_path: Optional[str] = ..., online_join_keys_full_path: Optional[str] = ..., offline_join_keys_path: Optional[str] = ..., online: bool = ..., offline: bool = ...) -> None: ...

class DeltaMaintenanceParameters(_message.Message):
    __slots__ = ["execute_compaction", "execute_sorting", "generate_manifest", "period_end", "vacuum", "vacuum_retention_hours"]
    EXECUTE_COMPACTION_FIELD_NUMBER: ClassVar[int]
    EXECUTE_SORTING_FIELD_NUMBER: ClassVar[int]
    GENERATE_MANIFEST_FIELD_NUMBER: ClassVar[int]
    PERIOD_END_FIELD_NUMBER: ClassVar[int]
    VACUUM_FIELD_NUMBER: ClassVar[int]
    VACUUM_RETENTION_HOURS_FIELD_NUMBER: ClassVar[int]
    execute_compaction: bool
    execute_sorting: bool
    generate_manifest: bool
    period_end: _timestamp_pb2.Timestamp
    vacuum: bool
    vacuum_retention_hours: int
    def __init__(self, generate_manifest: bool = ..., period_end: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., execute_compaction: bool = ..., vacuum: bool = ..., execute_sorting: bool = ..., vacuum_retention_hours: Optional[int] = ...) -> None: ...

class FeatureExportParameters(_message.Message):
    __slots__ = ["export_store_path", "feature_end_time", "feature_start_time", "parent_materialization_task_id"]
    EXPORT_STORE_PATH_FIELD_NUMBER: ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: ClassVar[int]
    PARENT_MATERIALIZATION_TASK_ID_FIELD_NUMBER: ClassVar[int]
    export_store_path: str
    feature_end_time: _timestamp_pb2.Timestamp
    feature_start_time: _timestamp_pb2.Timestamp
    parent_materialization_task_id: _id__client_pb2.Id
    def __init__(self, parent_materialization_task_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., feature_start_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., feature_end_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., export_store_path: Optional[str] = ...) -> None: ...

class IngestMaterializationParameters(_message.Message):
    __slots__ = ["ingest_path", "write_to_offline_feature_store", "write_to_online_feature_store"]
    INGEST_PATH_FIELD_NUMBER: ClassVar[int]
    WRITE_TO_OFFLINE_FEATURE_STORE_FIELD_NUMBER: ClassVar[int]
    WRITE_TO_ONLINE_FEATURE_STORE_FIELD_NUMBER: ClassVar[int]
    ingest_path: str
    write_to_offline_feature_store: bool
    write_to_online_feature_store: bool
    def __init__(self, write_to_online_feature_store: bool = ..., write_to_offline_feature_store: bool = ..., ingest_path: Optional[str] = ...) -> None: ...

class MaterializationTask(_message.Message):
    __slots__ = ["attempt_status_message", "attempts", "batch_parameters", "canary_params", "compute_mode", "created_at", "dataset_generation_parameters", "deletion_parameters", "delta_maintenance_parameters", "error_message", "feature_export_parameters", "id_feature_service_locator", "id_feature_view_locator", "ingest_parameters", "managed_retries", "manually_triggered", "materialization_serial_version", "materialization_task_id", "number_of_attempts_from_old_executions", "plan_id", "spark_cluster_environment_version", "state_transitions", "stream_parameters", "tecton_environment", "tecton_runtime_version", "updated_at"]
    ATTEMPTS_FIELD_NUMBER: ClassVar[int]
    ATTEMPT_STATUS_MESSAGE_FIELD_NUMBER: ClassVar[int]
    BATCH_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    CANARY_PARAMS_FIELD_NUMBER: ClassVar[int]
    COMPUTE_MODE_FIELD_NUMBER: ClassVar[int]
    CREATED_AT_FIELD_NUMBER: ClassVar[int]
    DATASET_GENERATION_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    DELETION_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    DELTA_MAINTENANCE_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: ClassVar[int]
    FEATURE_EXPORT_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    ID_FEATURE_SERVICE_LOCATOR_FIELD_NUMBER: ClassVar[int]
    ID_FEATURE_VIEW_LOCATOR_FIELD_NUMBER: ClassVar[int]
    INGEST_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    MANAGED_RETRIES_FIELD_NUMBER: ClassVar[int]
    MANUALLY_TRIGGERED_FIELD_NUMBER: ClassVar[int]
    MATERIALIZATION_SERIAL_VERSION_FIELD_NUMBER: ClassVar[int]
    MATERIALIZATION_TASK_ID_FIELD_NUMBER: ClassVar[int]
    NUMBER_OF_ATTEMPTS_FROM_OLD_EXECUTIONS_FIELD_NUMBER: ClassVar[int]
    PLAN_ID_FIELD_NUMBER: ClassVar[int]
    SPARK_CLUSTER_ENVIRONMENT_VERSION_FIELD_NUMBER: ClassVar[int]
    STATE_TRANSITIONS_FIELD_NUMBER: ClassVar[int]
    STREAM_PARAMETERS_FIELD_NUMBER: ClassVar[int]
    TECTON_ENVIRONMENT_FIELD_NUMBER: ClassVar[int]
    TECTON_RUNTIME_VERSION_FIELD_NUMBER: ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: ClassVar[int]
    attempt_status_message: str
    attempts: _containers.RepeatedCompositeFieldContainer[Attempt]
    batch_parameters: BatchMaterializationParameters
    canary_params: CanaryParams
    compute_mode: _compute_mode__client_pb2.BatchComputeMode
    created_at: _timestamp_pb2.Timestamp
    dataset_generation_parameters: DatasetGenerationParameters
    deletion_parameters: DeletionParameters
    delta_maintenance_parameters: DeltaMaintenanceParameters
    error_message: str
    feature_export_parameters: FeatureExportParameters
    id_feature_service_locator: _fco_locator__client_pb2.IdFcoLocator
    id_feature_view_locator: _fco_locator__client_pb2.IdFcoLocator
    ingest_parameters: IngestMaterializationParameters
    managed_retries: bool
    manually_triggered: bool
    materialization_serial_version: int
    materialization_task_id: _id__client_pb2.Id
    number_of_attempts_from_old_executions: int
    plan_id: _id__client_pb2.Id
    spark_cluster_environment_version: int
    state_transitions: _containers.RepeatedCompositeFieldContainer[MaterializationTaskStateTransition]
    stream_parameters: StreamMaterializationParameters
    tecton_environment: str
    tecton_runtime_version: str
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, materialization_task_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., plan_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., id_feature_view_locator: Optional[Union[_fco_locator__client_pb2.IdFcoLocator, Mapping]] = ..., id_feature_service_locator: Optional[Union[_fco_locator__client_pb2.IdFcoLocator, Mapping]] = ..., materialization_serial_version: Optional[int] = ..., tecton_runtime_version: Optional[str] = ..., tecton_environment: Optional[str] = ..., compute_mode: Optional[Union[_compute_mode__client_pb2.BatchComputeMode, str]] = ..., batch_parameters: Optional[Union[BatchMaterializationParameters, Mapping]] = ..., stream_parameters: Optional[Union[StreamMaterializationParameters, Mapping]] = ..., ingest_parameters: Optional[Union[IngestMaterializationParameters, Mapping]] = ..., deletion_parameters: Optional[Union[DeletionParameters, Mapping]] = ..., delta_maintenance_parameters: Optional[Union[DeltaMaintenanceParameters, Mapping]] = ..., feature_export_parameters: Optional[Union[FeatureExportParameters, Mapping]] = ..., dataset_generation_parameters: Optional[Union[DatasetGenerationParameters, Mapping]] = ..., spark_cluster_environment_version: Optional[int] = ..., state_transitions: Optional[Iterable[Union[MaterializationTaskStateTransition, Mapping]]] = ..., number_of_attempts_from_old_executions: Optional[int] = ..., error_message: Optional[str] = ..., created_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., updated_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., attempts: Optional[Iterable[Union[Attempt, Mapping]]] = ..., canary_params: Optional[Union[CanaryParams, Mapping]] = ..., manually_triggered: bool = ..., managed_retries: bool = ..., attempt_status_message: Optional[str] = ...) -> None: ...

class MaterializationTaskAttempt(_message.Message):
    __slots__ = ["attempt_number", "cluster_config", "created_at", "execution_environment", "materialization_task_attempt_id", "materialization_task_id", "online_store_copier_tasks", "run_id", "run_page_url", "snowflake_data", "state_transitions", "updated_at"]
    class OnlineStoreCopierTasksEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: str
        value: OnlineStoreCopierTask
        def __init__(self, key: Optional[str] = ..., value: Optional[Union[OnlineStoreCopierTask, Mapping]] = ...) -> None: ...
    ATTEMPT_NUMBER_FIELD_NUMBER: ClassVar[int]
    CLUSTER_CONFIG_FIELD_NUMBER: ClassVar[int]
    CREATED_AT_FIELD_NUMBER: ClassVar[int]
    EXECUTION_ENVIRONMENT_FIELD_NUMBER: ClassVar[int]
    MATERIALIZATION_TASK_ATTEMPT_ID_FIELD_NUMBER: ClassVar[int]
    MATERIALIZATION_TASK_ID_FIELD_NUMBER: ClassVar[int]
    ONLINE_STORE_COPIER_TASKS_FIELD_NUMBER: ClassVar[int]
    RUN_ID_FIELD_NUMBER: ClassVar[int]
    RUN_PAGE_URL_FIELD_NUMBER: ClassVar[int]
    SNOWFLAKE_DATA_FIELD_NUMBER: ClassVar[int]
    STATE_TRANSITIONS_FIELD_NUMBER: ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: ClassVar[int]
    attempt_number: int
    cluster_config: _feature_view__client_pb2.ClusterConfig
    created_at: _timestamp_pb2.Timestamp
    execution_environment: _spark_cluster__client_pb2.SparkExecutionEnvironment
    materialization_task_attempt_id: _id__client_pb2.Id
    materialization_task_id: _id__client_pb2.Id
    online_store_copier_tasks: _containers.MessageMap[str, OnlineStoreCopierTask]
    run_id: str
    run_page_url: str
    snowflake_data: SnowflakeData
    state_transitions: _containers.RepeatedCompositeFieldContainer[MaterializationTaskAttemptStateTransition]
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, materialization_task_attempt_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., materialization_task_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., execution_environment: Optional[Union[_spark_cluster__client_pb2.SparkExecutionEnvironment, str]] = ..., run_id: Optional[str] = ..., run_page_url: Optional[str] = ..., state_transitions: Optional[Iterable[Union[MaterializationTaskAttemptStateTransition, Mapping]]] = ..., attempt_number: Optional[int] = ..., created_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., updated_at: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., cluster_config: Optional[Union[_feature_view__client_pb2.ClusterConfig, Mapping]] = ..., online_store_copier_tasks: Optional[Mapping[str, OnlineStoreCopierTask]] = ..., snowflake_data: Optional[Union[SnowflakeData, Mapping]] = ...) -> None: ...

class MaterializationTaskAttemptStateTransition(_message.Message):
    __slots__ = ["attempt_state", "state_message", "termination_reason", "timestamp"]
    ATTEMPT_STATE_FIELD_NUMBER: ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: ClassVar[int]
    TERMINATION_REASON_FIELD_NUMBER: ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: ClassVar[int]
    attempt_state: _materialization_states__client_pb2.MaterializationTaskAttemptState
    state_message: str
    termination_reason: _jobs__client_pb2.RunTerminationReason
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, attempt_state: Optional[Union[_materialization_states__client_pb2.MaterializationTaskAttemptState, str]] = ..., state_message: Optional[str] = ..., termination_reason: Optional[Union[_jobs__client_pb2.RunTerminationReason, str]] = ..., timestamp: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...

class MaterializationTaskDep(_message.Message):
    __slots__ = ["offline_store_dependency"]
    OFFLINE_STORE_DEPENDENCY_FIELD_NUMBER: ClassVar[int]
    offline_store_dependency: OfflineStoreDependency
    def __init__(self, offline_store_dependency: Optional[Union[OfflineStoreDependency, Mapping]] = ...) -> None: ...

class MaterializationTaskStateTransition(_message.Message):
    __slots__ = ["task_state", "timestamp"]
    TASK_STATE_FIELD_NUMBER: ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: ClassVar[int]
    task_state: _materialization_states__client_pb2.MaterializationTaskState
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, task_state: Optional[Union[_materialization_states__client_pb2.MaterializationTaskState, str]] = ..., timestamp: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...

class OfflineStoreDependency(_message.Message):
    __slots__ = ["feature_end_time", "feature_start_time"]
    FEATURE_END_TIME_FIELD_NUMBER: ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: ClassVar[int]
    feature_end_time: _timestamp_pb2.Timestamp
    feature_start_time: _timestamp_pb2.Timestamp
    def __init__(self, feature_start_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ..., feature_end_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...

class OnlineStoreCopierTask(_message.Message):
    __slots__ = ["attempts", "completed_rows", "last_progress_request_id", "last_progress_send_time", "total_rows"]
    ATTEMPTS_FIELD_NUMBER: ClassVar[int]
    COMPLETED_ROWS_FIELD_NUMBER: ClassVar[int]
    LAST_PROGRESS_REQUEST_ID_FIELD_NUMBER: ClassVar[int]
    LAST_PROGRESS_SEND_TIME_FIELD_NUMBER: ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: ClassVar[int]
    attempts: _containers.RepeatedCompositeFieldContainer[OnlineStoreCopierTaskAttempt]
    completed_rows: int
    last_progress_request_id: str
    last_progress_send_time: _timestamp_pb2.Timestamp
    total_rows: int
    def __init__(self, attempts: Optional[Iterable[Union[OnlineStoreCopierTaskAttempt, Mapping]]] = ..., total_rows: Optional[int] = ..., completed_rows: Optional[int] = ..., last_progress_request_id: Optional[str] = ..., last_progress_send_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...

class OnlineStoreCopierTaskAttempt(_message.Message):
    __slots__ = ["state_transitions"]
    STATE_TRANSITIONS_FIELD_NUMBER: ClassVar[int]
    state_transitions: _containers.RepeatedCompositeFieldContainer[OnlineStoreCopierTaskStateTransition]
    def __init__(self, state_transitions: Optional[Iterable[Union[OnlineStoreCopierTaskStateTransition, Mapping]]] = ...) -> None: ...

class OnlineStoreCopierTaskStateTransition(_message.Message):
    __slots__ = ["state", "state_message", "timestamp"]
    STATE_FIELD_NUMBER: ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: ClassVar[int]
    state: _materialization_states__client_pb2.OnlineStoreCopierTaskState
    state_message: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, state: Optional[Union[_materialization_states__client_pb2.OnlineStoreCopierTaskState, str]] = ..., state_message: Optional[str] = ..., timestamp: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...

class SnowflakeData(_message.Message):
    __slots__ = ["base_location", "total_offline_rows", "total_online_rows"]
    BASE_LOCATION_FIELD_NUMBER: ClassVar[int]
    TOTAL_OFFLINE_ROWS_FIELD_NUMBER: ClassVar[int]
    TOTAL_ONLINE_ROWS_FIELD_NUMBER: ClassVar[int]
    base_location: _location__client_pb2.StageLocation
    total_offline_rows: int
    total_online_rows: int
    def __init__(self, base_location: Optional[Union[_location__client_pb2.StageLocation, Mapping]] = ..., total_online_rows: Optional[int] = ..., total_offline_rows: Optional[int] = ...) -> None: ...

class StreamHandoffConfig(_message.Message):
    __slots__ = ["enabled", "previous_task_id"]
    ENABLED_FIELD_NUMBER: ClassVar[int]
    PREVIOUS_TASK_ID_FIELD_NUMBER: ClassVar[int]
    enabled: bool
    previous_task_id: _id__client_pb2.Id
    def __init__(self, enabled: bool = ..., previous_task_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ...) -> None: ...

class StreamMaterializationParameters(_message.Message):
    __slots__ = ["stream_handoff_config"]
    STREAM_HANDOFF_CONFIG_FIELD_NUMBER: ClassVar[int]
    stream_handoff_config: StreamHandoffConfig
    def __init__(self, stream_handoff_config: Optional[Union[StreamHandoffConfig, Mapping]] = ...) -> None: ...
