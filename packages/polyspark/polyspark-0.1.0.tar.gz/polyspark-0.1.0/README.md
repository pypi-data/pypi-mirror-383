# Polyspark

Generate PySpark DataFrames using [polyfactory](https://github.com/litestar-org/polyfactory) for testing and developing PySpark workflows.

[![Python Version](https://img.shields.io/pypi/pyversions/polyspark)](https://pypi.org/project/polyspark/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- 🏭 **Factory-based generation**: Leverage polyfactory's powerful factory pattern
- 🎯 **Type-safe**: Full support for dataclasses, Pydantic models, and TypedDicts
- 🔌 **No hard dependency**: PySpark is optional - generate data without it installed
- 🌳 **Complex types**: Support for arrays, maps, nested structs, and more
- 🎨 **Dual schema support**: Use Python type hints or PySpark schema objects
- 🚀 **Easy to use**: Simple API with sensible defaults

## Installation

```bash
pip install polyspark
```

Polyspark does **not** require PySpark as a dependency. Install PySpark separately when you need it:

```bash
pip install pyspark
```

For development with all optional dependencies:

```bash
pip install polyspark[dev]
```

## Quick Start

### The Easy Way (Recommended)

Use the `@spark_factory` decorator - no need for a separate factory class!

```python
from dataclasses import dataclass
from polyspark import spark_factory
from pyspark.sql import SparkSession

# Define your data model with decorator
@spark_factory
@dataclass
class User:
    id: int
    name: str
    email: str

# Generate a DataFrame - use methods directly on your class!
spark = SparkSession.builder.getOrCreate()
df = User.build_dataframe(spark, size=100)
df.show()
```

### Traditional Way (For Advanced Use Cases)

You can also create a separate factory class if you need more control:

```python
from polyspark import SparkFactory

class UserFactory(SparkFactory[User]):
    __model__ = User

df = UserFactory.build_dataframe(spark, size=100)
```

## Usage

### Decorator Pattern (Recommended)

The `@spark_factory` decorator is the simplest way to use polyspark. It adds factory methods directly to your model class:

```python
from dataclasses import dataclass
from polyspark import spark_factory

@spark_factory
@dataclass
class Product:
    product_id: int
    name: str
    price: float
    in_stock: bool

# Use methods directly on the class!
df = Product.build_dataframe(spark, size=50)
dicts = Product.build_dicts(size=100)  # No PySpark needed
```

**Benefits:**
- ✅ Single decorator instead of separate factory class
- ✅ Methods live on your model where they're discoverable
- ✅ Works with dataclasses, Pydantic, and TypedDicts
- ✅ Cleaner, more Pythonic code

### Basic Usage

#### Using Factory Classes

```python
from dataclasses import dataclass
from polyspark import SparkFactory

@dataclass
class Product:
    product_id: int
    name: str
    price: float
    in_stock: bool

class ProductFactory(SparkFactory[Product]):
    __model__ = Product

# Generate DataFrame
df = ProductFactory.build_dataframe(spark, size=50)
```

#### Using Convenience Function

```python
from polyspark import build_spark_dataframe

df = build_spark_dataframe(Product, spark, size=50)
```

### Working Without PySpark

Generate data as dictionaries without PySpark installed:

```python
# No PySpark required for this
dicts = ProductFactory.build_dicts(size=100)

# Later, convert to DataFrame when you have PySpark
df = ProductFactory.create_dataframe_from_dicts(spark, dicts)
```

### Pydantic Models

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserFactory(SparkFactory[User]):
    __model__ = User

df = UserFactory.build_dataframe(spark, size=100)
```

### Complex Types

#### Nested Structs

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Address:
    street: str
    city: str
    state: str
    zipcode: str

@dataclass
class Employee:
    employee_id: int
    name: str
    address: Address  # Nested struct
    skills: List[str]  # Array type

class EmployeeFactory(SparkFactory[Employee]):
    __model__ = Employee

df = EmployeeFactory.build_dataframe(spark, size=50)

# Access nested fields
df.select("name", "address.city", "address.state").show()
```

#### Maps and Arrays

```python
from typing import Dict, List

@dataclass
class Product:
    product_id: int
    name: str
    attributes: Dict[str, str]  # Map type
    tags: List[str]  # Array type
    prices_by_region: Dict[str, float]  # Map with float values

class ProductFactory(SparkFactory[Product]):
    __model__ = Product

df = ProductFactory.build_dataframe(spark, size=30)
```

#### Array of Structs

```python
@dataclass
class Project:
    project_id: int
    project_name: str
    budget: float

@dataclass
class Department:
    dept_id: int
    dept_name: str
    projects: List[Project]  # Array of structs

class DepartmentFactory(SparkFactory[Department]):
    __model__ = Department

df = DepartmentFactory.build_dataframe(spark, size=10)
```

### Explicit Schemas

You can provide explicit PySpark schemas:

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define explicit schema
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("email", StringType(), True),
])

df = UserFactory.build_dataframe(spark, size=100, schema=schema)
```

### Optional Types

Optional fields are automatically handled:

```python
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    nickname: Optional[str]  # Automatically nullable in schema
    bio: Optional[str] = None

class UserFactory(SparkFactory[User]):
    __model__ = User

df = UserFactory.build_dataframe(spark, size=50)
```

## Supported Types

### Basic Types

| Python Type | PySpark Type |
|-------------|--------------|
| `str` | `StringType` |
| `int` | `LongType` |
| `float` | `DoubleType` |
| `bool` | `BooleanType` |
| `bytes` / `bytearray` | `BinaryType` |
| `datetime.date` | `DateType` |
| `datetime.datetime` | `TimestampType` |
| `decimal.Decimal` | `DecimalType` |

### Complex Types

| Python Type | PySpark Type |
|-------------|--------------|
| `List[T]` | `ArrayType` |
| `Dict[K, V]` | `MapType` |
| Dataclass / Pydantic | `StructType` |
| `Optional[T]` | Nullable field |

### Nested Types

Any combination of the above types is supported:
- `List[List[int]]` → `ArrayType(ArrayType(LongType()))`
- `Dict[str, List[int]]` → `MapType(StringType(), ArrayType(LongType()))`
- `List[MyDataclass]` → `ArrayType(StructType(...))`

## API Reference

### `SparkFactory`

The main factory class for generating DataFrames.

#### Methods

##### `build_dataframe(spark, size=10, schema=None, **kwargs)`

Generate a PySpark DataFrame.

**Parameters:**
- `spark` (SparkSession): SparkSession instance
- `size` (int): Number of rows to generate (default: 10)
- `schema` (Optional): Explicit schema (StructType) or list of column names
- `**kwargs`: Additional arguments passed to polyfactory

**Returns:** PySpark DataFrame

**Raises:** `PySparkNotAvailableError` if PySpark is not installed

##### `build_dicts(size=10, **kwargs)`

Generate a list of dictionaries (no PySpark required).

**Parameters:**
- `size` (int): Number of records to generate
- `**kwargs`: Additional arguments passed to polyfactory

**Returns:** List[Dict[str, Any]]

##### `create_dataframe_from_dicts(spark, data, schema=None)`

Convert pre-generated dictionaries to a DataFrame.

**Parameters:**
- `spark` (SparkSession): SparkSession instance
- `data` (List[Dict]): List of dictionaries to convert
- `schema` (Optional): Explicit schema

**Returns:** PySpark DataFrame

### `build_spark_dataframe(model, spark, size=10, schema=None, **kwargs)`

Convenience function to build a DataFrame without creating a factory class.

**Parameters:**
- `model` (Type): Model type (dataclass, Pydantic, TypedDict)
- `spark` (SparkSession): SparkSession instance
- `size` (int): Number of rows to generate
- `schema` (Optional): Explicit schema
- `**kwargs`: Additional arguments for data generation

**Returns:** PySpark DataFrame

### Schema Utilities

#### `python_type_to_spark_type(python_type, nullable=True)`

Convert a Python type to a PySpark DataType.

#### `dataclass_to_struct_type(dataclass_type)`

Convert a dataclass to a PySpark StructType.

#### `pydantic_to_struct_type(model_type)`

Convert a Pydantic model to a PySpark StructType.

#### `infer_schema(model, schema=None)`

Infer or validate a PySpark schema from a model type.

### Runtime Checks

#### `is_pyspark_available()`

Check if PySpark is available at runtime.

**Returns:** bool

## Examples

Check out the [examples/](examples/) directory for complete examples:

- [basic_usage.py](examples/basic_usage.py) - Simple dataclass usage
- [pydantic_models.py](examples/pydantic_models.py) - Using Pydantic models
- [complex_types.py](examples/complex_types.py) - Arrays, maps, nested structs
- [direct_schema.py](examples/direct_schema.py) - Using PySpark schemas directly

## Testing

Polyspark uses pytest for testing. To run the tests:

```bash
# Install with dev dependencies
pip install polyspark[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=polyspark --cov-report=html
```

## Why Polyspark?

When developing PySpark applications, you often need test data. Creating realistic test DataFrames manually is tedious and error-prone. Polyspark combines the power of polyfactory's data generation with PySpark's DataFrame API.

### Key Benefits

1. **Type Safety**: Define your schema once using Python types
2. **Consistency**: Same data models for application code and tests
3. **Flexibility**: Works with dataclasses, Pydantic, and TypedDicts
4. **No Vendor Lock-in**: PySpark is not a hard dependency
5. **Rich Data**: Leverages polyfactory's sophisticated data generation
6. **Testing**: Perfect for unit tests, integration tests, and development

## How It Works

Polyspark uses Python protocols to define PySpark interfaces without importing PySpark. This allows:

1. Schema inference from Python type hints
2. Type-safe DataFrame generation
3. Graceful degradation when PySpark is not installed
4. No hard dependency on PySpark

The schema inference engine converts Python types to PySpark types:
- Type hints → PySpark schema
- polyfactory generates data → List of dicts
- PySpark creates DataFrame from dicts + schema

## Requirements

- Python 3.8+
- polyfactory >= 2.0.0
- typing-extensions >= 4.0.0
- PySpark >= 3.0.0 (optional, for DataFrame generation)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [polyfactory](https://github.com/litestar-org/polyfactory) - The excellent factory library that powers Polyspark
- [PySpark](https://spark.apache.org/docs/latest/api/python/) - The Python API for Apache Spark

## Related Projects

- [polyfactory](https://github.com/litestar-org/polyfactory) - Simple and powerful factories for mock data generation
- [PySpark](https://spark.apache.org/docs/latest/api/python/) - Python API for Apache Spark
- [Faker](https://github.com/joke2k/faker) - Library for generating fake data

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/odosmatthews/polyspark/issues) on GitHub.

