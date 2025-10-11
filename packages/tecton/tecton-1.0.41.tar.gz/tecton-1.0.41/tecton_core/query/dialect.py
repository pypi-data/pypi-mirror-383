import enum


class Dialect(str, enum.Enum):
    SNOWFLAKE = "snowflake"
    ATHENA = "athena"
    SPARK = "spark"
    DUCKDB = "duckdb"
    PANDAS = "pandas"
    TORCH = "torch"
    BIGQUERY = "bigquery"
