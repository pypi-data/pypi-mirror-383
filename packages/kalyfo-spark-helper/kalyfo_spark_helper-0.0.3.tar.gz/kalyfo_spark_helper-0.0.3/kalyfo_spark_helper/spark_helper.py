"""Contains SparkHelper class to help create and configure a Spark session."""

from delta import configure_spark_with_delta_pip

from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

import os
import findspark
import shutil

from dotenv import load_dotenv
load_dotenv(override=True)


class SparkHelper:
    """A Spark helper class to create and configure a Spark session with optimized settings.
    
    Use it with try-finally block, and call create_spark_session() in the try block and stop_spark_session() in the finally block.
    
    Example usage:
    ```
    helper = SparkHelper()
    spark = helper.create_spark_session("My Spark App")
    try:
        # Your code here
    finally:
        helper.stop_spark_session()
    ```
    """

    def __init__(
        self, 
        available_memory_gb: int = int(os.getenv("AVAILABLE_MEMORY_GB", 0)),
        driver_memory_gb: int = 40,
        logical_cores: int = int(os.getenv("AVAILABLE_LOGICAL_CORES", os.cpu_count())),
        spark_memory_fraction: float = float(os.getenv("SPARK_MEMORY_FRACTION", 0.8)),
        spark_memory_storage_fraction: float = float(os.getenv("SPARK_MEMORY_STORAGE_FRACTION", 0.6)),
        logical_cores_per_executor: int = 5,
        target_parquet_file_size_mb: int = 1024,
        enable_delta_lake = True,
        driver_logical_cores: int = 1,
        timezone: str = os.getenv("TIMEZONE", "Europe/Athens"),
        spark_temp_dir: str | None = None,
        shuffle_partitions: int = 2001,
        default_parallelism: int = 2001,
    ):
        """Constructor for SparkHelper.
        
        Args:
            available_memory_gb (int): Total available memory in GB for Spark.
            driver_memory_gb (int): Memory in GB allocated to the Spark driver.
            logical_cores (int): Total logical CPU cores available.
            spark_memory_fraction (float): Fraction of JVM heap used for Spark memory.
            spark_memory_storage_fraction (float): Fraction of Spark memory used for storage.
            logical_cores_per_executor (int): Number of logical cores per Spark executor.
            target_parquet_file_size_mb (int): Target Parquet file size in MB when using Delta Lake.
            enable_delta_lake (bool): Whether to enable Delta Lake support.
            driver_logical_cores (int): Number of logical cores allocated to the Spark driver.
            timezone (str): Timezone for the Spark session.
            spark_temp_dir (str | None): Directory for Spark temporary files. If None, a temporary directory will be created.
            shuffle_partitions (int): Number of shuffle partitions for Spark SQL.
            default_parallelism (int): Default parallelism level for Spark.
        """
        if not available_memory_gb:
            raise ValueError(
                "Please provide available_memory_gb parameter or set "
                "AVAILABLE_MEMORY_GB environment variable."
            )

        if driver_memory_gb >= available_memory_gb:
            raise ValueError("Driver memory must be less than available memory.")
        
        self.timezone = timezone

        self.driver_logical_cores = driver_logical_cores
        self.spark_logical_cores = logical_cores - self.driver_logical_cores - 1  # Leave one core for system purposes.
        self.logical_cores_per_executor = logical_cores_per_executor
        self.enable_delta_lake = enable_delta_lake

        self.memory_offheap_gb = 8

        # Instances
        self.num_executors = self.spark_logical_cores // self.logical_cores_per_executor

        # NOTE: https://medium.com/@omkarspatil2611/memory-management-in-apache-spark-3ae1f4db9d2b
        self.executor_memory_gb = available_memory_gb  // self.num_executors
        self.driver_memory_gb = driver_memory_gb
        self.executor_memory_overhead_gb = max(0.384, 0.1 * self.executor_memory_gb)

        # NOTE: https://stackoverflow.com/questions/61263618/difference-between-spark-executor-memoryoverhead-and-spark-memory-offheap-size

        self.spark_memory_fraction = spark_memory_fraction
        self.spark_memory_storage_fraction = spark_memory_storage_fraction

        self.target_parquet_file_size_mb = target_parquet_file_size_mb

        self.shuffle_partitions = shuffle_partitions
        self.default_parallelism = default_parallelism

        # Use the storage directory defined in environment
        if spark_temp_dir:
            self.spark_temp_dir = spark_temp_dir
        else:
            import tempfile
            self.spark_temp_dir = os.path.join(tempfile.gettempdir(), "spark-temp")
        os.makedirs(self.spark_temp_dir, exist_ok=True)
        try:
            os.chmod(self.spark_temp_dir, 0o777)
        except Exception:
            pass

        self.spark = None

    def create_spark_session(self, app_name="SparkApp") -> SparkSession:
        """Creates and returns a Spark session with optimized settings."""
        # NOTE: https://github.com/maxpumperla/elephas/issues/183
        findspark.init()

        builder = SparkSession.builder \
            .appName(app_name) \
            .master(f"local[{self.spark_logical_cores}]")
            
        conf = SparkConf()
        conf.set("spark.driver.cores", str(self.driver_logical_cores))

        conf.set("spark.driver.memory", f"{int(self.driver_memory_gb)}g")
        conf.set("spark.executor.memory", f"{int(self.executor_memory_gb)}g")

        # NOTE: https://stackoverflow.com/questions/75033290/retried-waiting-for-gclocker-too-often-allocating-12488753-words
        executor_java_opts = (
            "-XX:+UseG1GC "
            "-XX:+UnlockDiagnosticVMOptions "
            "-XX:GCLockerRetryAllocationCount=100 "
            "-XX:G1HeapRegionSize=32m "
            "-XX:MaxGCPauseMillis=500 "
            "-XX:+ParallelRefProcEnabled "
            "-XX:+UseCompressedOops"
        )
        driver_java_opts = (
            "-XX:+UseG1GC "
            "-XX:+UnlockDiagnosticVMOptions "
            "-XX:GCLockerRetryAllocationCount=100 "
            "-XX:MaxMetaspaceSize=512M"
        )
        conf.set("spark.executor.extraJavaOptions", executor_java_opts)
        conf.set("spark.driver.extraJavaOptions", driver_java_opts)
        
        conf.set("spark.executor.cores", self.logical_cores_per_executor)  # 2 - 5 is recommended
        conf.set('spark.executor.instances', self.num_executors)

        conf.set("spark.memory.offHeap.enabled", True)
        conf.set("spark.memory.offHeap.size", f"{int(self.memory_offheap_gb)}g")

        conf.set("spark.sql.debug.maxToStringFields", "200")

        conf.set("spark.executor.memoryOverhead", f"{int(self.executor_memory_overhead_gb)}g") 

        conf.set("spark.sql.files.maxPartitionBytes", 256 * 1024 * 1024)  # 256 MB
        conf.set("spark.hadoop.parquet.block.size", 256 * 1024 * 1024)  # 256 MB
        
        conf.set("spark.checkpoint.compress", "true")
        conf.set("spark.storage.level", "MEMORY_AND_DISK")
            
        conf.set("spark.rpc.askTimeout", "300s")
        conf.set("spark.network.timeout", "300s")
        conf.set("spark.executor.heartbeatInterval", "100s")
        
        conf.set("spark.sql.session.timeZone", self.timezone)

        # NOTE: https://stackoverflow.com/questions/32349611/what-should-be-the-optimal-value-for-spark-sql-shuffle-partitions-or-how-do-we-i
        # NOTE: https://www.reddit.com/r/apachespark/comments/mmuuos/am_i_setting_sparkdefaultparallelism_too_low/
        conf.set("spark.sql.shuffle.partitions", str(self.shuffle_partitions))
        conf.set("spark.default.parallelism", str(self.default_parallelism))

        conf.set("spark.sql.autoBroadcastJoinThreshold", "300m")

        conf.set("spark.memory.fraction", str(self.spark_memory_fraction))
        conf.set("spark.memory.storageFraction", str(self.spark_memory_storage_fraction))

        conf.set("spark.eventLog.gcMetrics.youngGenerationGarbageCollectors", "G1 Young Generation")
        
        conf.set("spark.local.dir", self.spark_temp_dir)
        conf.set("spark.worker.dir", self.spark_temp_dir)

        conf.set("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "2")
        
        conf.set("spark.sql.inMemoryColumnarStorage.compressed", "true")
        conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")
        conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

        conf.set("spark.sql.adaptive.enabled", "true")
        conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
        conf.set("spark.sql.adaptive.coalescePartitions.minPartitionSize", str(self.logical_cores_per_executor * 2))
        conf.set("spark.sql.adaptive.coalescePartitions.initialPartitionNum", str(200))
        
        conf.set("spark.io.compression.codec", "lz4")
        conf.set("spark.shuffle.compress", "true")

        conf.set("spark.sql.files.ignoreCorruptFiles", "false")
        conf.set("spark.sql.parquet.enableVectorizedReader", "false")

        # Add Hadoop native libraries if available
        hadoop_home = os.environ.get('HADOOP_HOME')
        if hadoop_home:
            native_path = os.path.join(hadoop_home, 'lib', 'native')
            conf.set("spark.driver.extraLibraryPath", native_path)
            conf.set("spark.executor.extraLibraryPath", native_path)

        if self.enable_delta_lake:
            # NOTE: https://delta.io/blog/delta-lake-optimize/
            print("Using Delta Lake")

            # NOTE: https://docs.delta.io/latest/quick-start.html
            conf.set("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            conf.set("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

            conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
            conf.set("spark.databricks.delta.vacuum.parallelDelete.enabled" , "true")

            conf.set("spark.databricks.delta.autoCompact.enabled", "true")
            conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
            conf.set("spark.databricks.delta.autoCompact.minNumFiles", "10")
            conf.set("spark.databricks.delta.optimize.maxFileSize", str(1024 * 1024 * 1024))

            target_size_bytes = self.target_parquet_file_size_mb * 1024 * 1024
            conf.set("delta.targetFileSize", str(target_size_bytes))

            builder = builder.config(conf=conf)
            self.spark = configure_spark_with_delta_pip(builder).getOrCreate()
        else:
            builder = builder.config(conf=conf)
            self.spark = builder.getOrCreate()
        
        self.spark.sparkContext.setCheckpointDir(self.spark_temp_dir)
        self._verify_configuration()
        
        return self.spark
    
    def _verify_configuration(self) -> None:
        """Verify and log the actual Spark configuration settings."""
        if not self.spark:
            print("No active Spark session to verify")
            return None
        
        # Collect important configuration values using SparkContext's getConf()
        sc_conf = self.spark.sparkContext.getConf()
        
        config = {
            "Driver Memory": sc_conf.get("spark.driver.memory", "not set"),
            "Executor Memory": sc_conf.get("spark.executor.memory", "not set"),
            "Executor Cores": sc_conf.get("spark.executor.cores", "not set"),
            "Memory Fraction": sc_conf.get("spark.memory.fraction", "not set"),
            "Storage Fraction": sc_conf.get("spark.memory.storageFraction", "not set"),
            "Shuffle Partitions": sc_conf.get("spark.sql.shuffle.partitions", "not set"),
            "Default Parallelism": sc_conf.get("spark.default.parallelism", "not set"),
            "Local Directory": sc_conf.get("spark.local.dir", "not set")
        }
        
        print("=== Spark Configuration Verification ===")
        for key, value in config.items():
            print(f"{key}: {value}")
        print("=======================================")
    
    def delete_spark_temp_dir(self) -> None:
        """Deletes the Spark temporary directory."""
        if self.spark_temp_dir and os.path.exists(self.spark_temp_dir):
            try:
                shutil.rmtree(self.spark_temp_dir)
            except Exception as e:
                print(f"Warning: Could not remove temporary directory: {e}")
            
    def stop_spark_session(self) -> None:
        """Stops the Spark session."""
        print("Stopping Spark session")
        if self.spark:
            self.spark.stop()
            self.spark = None
        
        if self.spark_temp_dir and os.path.exists(self.spark_temp_dir):
            try:
                shutil.rmtree(self.spark_temp_dir)
            except Exception as e:
                print(f"Warning: Could not remove temporary directory: {e}")
            
        self.spark_temp_dir = None
