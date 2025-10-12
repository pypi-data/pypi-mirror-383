import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, FloatType, LongType, DateType

# ---------------------------
# Setup logger for Jupyter
# ---------------------------
logger = logging.getLogger("KeplerSDK")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[KeplerSDK] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ---------------------------
# Column definitions
# ---------------------------
REQUIRED_INPUT_COLUMNS = {"id_kepler", "date_transaction", "pourcentage"}
ESSENTIAL_COLUMNS = ["assigned_to", "statut", "investigation_status", "commentaire", "id_client", "id_transaction"]
CUSTOM_COLUMNS = [f"custom{i}" for i in range(1, 21)]

# ---------------------------
# Main push function
# ---------------------------
def push_to_kepler(
    df: DataFrame,
    usecase_id: str,
    spark: SparkSession,
    mode: str = "append",
    database: str = "kepler",
    hdfs_base_path: str = "/kepler-SQL",
    file_format: str = "avro",       # can be 'avro' or 'parquet'
    shuffle_partitions: int = 10     # control number of shuffle partitions
):
    """
    Push a DataFrame to Iceberg MOR table optimized for fast writes.
    """
    table_name = f"{database}.uc_{usecase_id}"
    table_path = f"{hdfs_base_path}/uc_{usecase_id}"

    # ---------------------------
    # Validate input
    # ---------------------------
    if df.isEmpty():
        logger.warning("Input DataFrame is empty. Nothing to push.")
        return

    missing_required = REQUIRED_INPUT_COLUMNS - set(df.columns)
    if missing_required:
        logger.error(f"Missing required columns: {missing_required}")
        raise ValueError(f"Missing required columns: {missing_required}")

    # ---------------------------
    # Cast required columns
    # ---------------------------
    df = df.withColumn("id_kepler", F.col("id_kepler").cast(LongType())) \
           .withColumn("date_transaction", F.to_date(F.col("date_transaction"), "yyyy-MM-dd")) \
           .withColumn("pourcentage", F.col("pourcentage").cast(FloatType())) \
           .withColumn("date_scoring", F.current_date())

    # ---------------------------
    # Add missing optional columns
    # ---------------------------
    added_columns = []
    for col in ESSENTIAL_COLUMNS + CUSTOM_COLUMNS:
        if col not in df.columns:
            df = df.withColumn(col, F.lit(None).cast(StringType()))
            added_columns.append(col)

    # ---------------------------
    # Partitioning columns
    # ---------------------------
    df = df.withColumn("year", F.year(F.col("date_transaction"))) \
           .withColumn("month", F.month(F.col("date_transaction"))) \
           .withColumn("day", F.dayofmonth(F.col("date_transaction")))

    # ---------------------------
    # Reduce shuffle with repartition
    # ---------------------------
    df = df.repartition(shuffle_partitions, "year", "month", "day")

    # ---------------------------
    # Log info
    # ---------------------------
    logger.info(f"Original columns: {list(df.columns)}")
    if added_columns:
        logger.info(f"Columns auto-added: {added_columns}")
    logger.info(f"Final columns: {list(df.columns)}")
    logger.info(f"Number of shuffle partitions: {shuffle_partitions}")

    # ---------------------------
    # Write to Iceberg
    # ---------------------------
    if not spark.catalog.tableExists(table_name):
        logger.info(f"Creating Iceberg MOR table: {table_name}")
        df.writeTo(table_name) \
            .tableProperty("location", table_path) \
            .tableProperty("format-version", "2") \
            .tableProperty("write.zorder.column-names", "id_kepler") \
            .tableProperty("write.update.mode", "merge-on-read") \
            .tableProperty("write.delete.mode", "merge-on-read") \
            .tableProperty("write.merge.mode", "merge-on-read") \
            .partitionedBy("year", "month", "day") \
            .format(file_format) \
            .create()
        logger.info("Initial write completed.")
    else:
        df.writeTo(table_name).format(file_format).append()
        logger.info("Append completed.")
