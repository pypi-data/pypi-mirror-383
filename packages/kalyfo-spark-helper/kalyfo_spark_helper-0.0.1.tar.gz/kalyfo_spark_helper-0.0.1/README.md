# Spark Helper

A Python utility library for creating and configuring optimized Apache Spark sessions with Delta Lake support.

## Features

- **Optimized Spark Configuration**: Pre-configured settings for optimal performance
- **Delta Lake Support**: Built-in support for Delta Lake operations
- **Memory Management**: Intelligent memory allocation for driver and executors
- **Customizable**: Extensive configuration options via parameters or environment variables
- **Timezone Support**: Configure session timezone
- **Resource Monitoring**: Built-in configuration verification

## Installation

```bash
pip install kalyfo-spark-helper
```

## Quick Start

```python
from kalyfo_spark_helper import SparkHelper

# Create a Spark helper instance
spark_helper = SparkHelper(
    available_memory_gb=64,
    driver_memory_gb=40,
    cores=16
)

# Create a Spark session
spark = spark_helper.create_spark_session("My Spark App")

try:
    # Your Spark code here
    df = spark.read.parquet("data.parquet")
    df.show()
finally:
    # Always stop the session when done
    spark_helper.stop_spark_session()
```

## Configuration

### Basic Parameters

- `available_memory_gb`: Total memory available for Spark (required)
- `driver_memory_gb`: Memory allocated to the driver (default: 40GB)
- `logical_cores`: Number of logical CPU cores to use (default: all available cores)
- `logical_cores_per_executor`: Logical cores per executor (default: 5, 2-5 recommended)
- `enable_delta_lake`: Enable Delta Lake support (default: True)

### Environment Variables

You can also configure Spark Helper using environment variables:

```bash
export AVAILABLE_MEMORY_GB=64
export AVAILABLE_LOGICAL_CORES=16
export SPARK_MEMORY_FRACTION=0.8
export SPARK_MEMORY_STORAGE_FRACTION=0.6
export TIMEZONE="Europe/Athens"
```

or by creating a .env file:

```
AVAILABLE_MEMORY_GB=64
AVAILABLE_LOGICAL_CORES=16
SPARK_MEMORY_FRACTION=0.8
SPARK_MEMORY_STORAGE_FRACTION=0.6
TIMEZONE="Europe/Athens"
```

## Advanced Usage

### Custom Memory Settings

```python
from kalyfo_spark_helper import SparkHelper

spark_helper = SparkHelper(
    available_memory_gb=128,
    driver_memory_gb=40,
    logical_cores=32,
    spark_memory_fraction=0.8,
    spark_memory_storage_fraction=0.6,
    logical_cores_per_executor=5
)
```

## Requirements

- Python >= 3.9
- PySpark == 4.0.1
- delta-spark == 4.0.0
- findspark == 2.0.1
- python-dotenv == 1.1.1

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the [GitHub repository](https://github.com/konstantinoskalyfommatos/kalyfo-spark-helper/issues).