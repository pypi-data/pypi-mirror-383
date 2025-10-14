"""Polyspark - Generate PySpark DataFrames using polyfactory.

This package provides tools to generate PySpark DataFrames for testing and
development using the polyfactory library. It supports dataclasses, Pydantic
models, and TypedDicts without requiring PySpark as a hard dependency.
"""

from polyspark.factory import SparkFactory, build_spark_dataframe, spark_factory
from polyspark.schema import (
    dataclass_to_struct_type,
    infer_schema,
    pydantic_to_struct_type,
    python_type_to_spark_type,
    typed_dict_to_struct_type,
)
from polyspark.protocols import is_pyspark_available
from polyspark.exceptions import (
    PolysparkError,
    PySparkNotAvailableError,
    SchemaInferenceError,
    UnsupportedTypeError,
)

__version__ = "0.1.0"

__all__ = [
    # Main factory
    "SparkFactory",
    "build_spark_dataframe",
    "spark_factory",
    # Schema utilities
    "dataclass_to_struct_type",
    "infer_schema",
    "pydantic_to_struct_type",
    "python_type_to_spark_type",
    "typed_dict_to_struct_type",
    # Runtime checks
    "is_pyspark_available",
    # Exceptions
    "PolysparkError",
    "PySparkNotAvailableError",
    "SchemaInferenceError",
    "UnsupportedTypeError",
]

