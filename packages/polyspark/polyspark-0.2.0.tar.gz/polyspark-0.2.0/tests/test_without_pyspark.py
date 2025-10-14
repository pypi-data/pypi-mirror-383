"""Tests for graceful degradation when PySpark is not available."""

from dataclasses import dataclass
from unittest.mock import patch

import pytest

from polyspark import SparkFactory, is_pyspark_available
from polyspark.exceptions import PySparkNotAvailableError


@dataclass
class SimpleModel:
    id: int
    name: str


class TestWithoutPyspark:
    """Test behavior when PySpark is not installed."""

    def test_is_pyspark_available(self):
        # This test will vary based on whether pyspark is actually installed
        result = is_pyspark_available()
        assert isinstance(result, bool)

    def test_build_dicts_without_pyspark(self):
        """build_dicts should work without PySpark."""

        class ModelFactory(SparkFactory[SimpleModel]):
            __model__ = SimpleModel

        # This should work regardless of PySpark availability
        dicts = ModelFactory.build_dicts(size=5)

        assert len(dicts) == 5
        assert all(isinstance(d, dict) for d in dicts)
        assert all(set(d.keys()) == {"id", "name"} for d in dicts)

    @patch("polyspark.factory.is_pyspark_available", return_value=False)
    def test_build_dataframe_raises_without_pyspark(self, mock_check):
        """build_dataframe should raise clear error without PySpark."""

        class ModelFactory(SparkFactory[SimpleModel]):
            __model__ = SimpleModel

        with pytest.raises(PySparkNotAvailableError) as exc_info:
            ModelFactory.build_dataframe(None, size=10)

        assert "PySpark is required" in str(exc_info.value)
        assert "pip install pyspark" in str(exc_info.value)

    @patch("polyspark.factory.is_pyspark_available", return_value=False)
    def test_create_dataframe_from_dicts_raises_without_pyspark(self, mock_check):
        """create_dataframe_from_dicts should raise clear error without PySpark."""

        class ModelFactory(SparkFactory[SimpleModel]):
            __model__ = SimpleModel

        dicts = ModelFactory.build_dicts(size=5)

        with pytest.raises(PySparkNotAvailableError):
            ModelFactory.create_dataframe_from_dicts(None, dicts)
