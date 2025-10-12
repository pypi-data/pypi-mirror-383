import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, FloatType, LongType, DateType

logger = logging.getLogger("KeplerSDK")

REQUIRED_INPUT_COLUMNS = {"id_kepler", "date_transaction", "pourcentage"}
ESSENTIAL_COLUMNS = ["assigned_to", "statut", "investigation_status", "commentaire", "id_client", "id_transaction"]
CUSTOM_COLUMNS = [f"custom{i}" for i in range(1, 21)]

def push_to_kepler(df: DataFrame, usecase_id: str, spark: SparkSession,
                   mode: str = "append", database: str = "kepler",
                   hdfs_base_path: str = "/kepler-SQL"):
    table_name = f"{database}.uc_{usecase_id}"
    table_path = f"{hdfs_base_path}/uc_{usecase_id}"

    if df.isEmpty():
        logger.warning("[KeplerSDK] Input DataFrame is empty. Nothing to push.")
        return

    missing_required = REQUIRED_INPUT_COLUMNS - set(df.columns)
    if missing_required:
        logger.error(f"[KeplerSDK] Missing required columns: {missing_required}")
        raise ValueError(f"Missing required columns: {missing_required}")

    # Enforce types
    df = df.withColumn("id_kepler", F.col("id_kepler").cast(LongType()))
    df = df.withColumn("date_transaction", F.to_date(F.col("date_transaction"), "yyyy-MM-dd"))
    df = df.withColumn("pourcentage", F.col("pourcentage").cast(FloatType()))
    df = df.withColumn("date_scoring", F.current_date())

    added_columns = []
    for col in ESSENTIAL_COLUMNS + CUSTOM_COLUMNS:
        if col not in df.columns:
            df = df.withColumn(col, F.lit(None).cast(StringType()))
            added_columns.append(col)

    df = df.withColumn("year", F.year(F.col("date_transaction"))) \
           .withColumn("month", F.month(F.col("date_transaction"))) \
           .withColumn("day", F.dayofmonth(F.col("date_transaction")))

    logger.info(f"[KeplerSDK] Original columns: {list(df.columns)}")
    if added_columns:
        logger.info(f"[KeplerSDK] Columns auto-added: {added_columns}")
    logger.info(f"[KeplerSDK] Final columns: {list(df.columns)}")

    if not spark.catalog.tableExists(table_name):
        logger.info(f"[KeplerSDK] Creating Iceberg MOR table: {table_name}")
        df.writeTo(table_name) \
            .tableProperty("location", table_path) \
            .tableProperty("format-version", "2") \
            .tableProperty("write.zorder.column-names", "id_kepler") \
            .tableProperty("write.update.mode", "merge-on-read") \
            .tableProperty("write.delete.mode", "merge-on-read") \
            .tableProperty("write.merge.mode", "merge-on-read") \
            .partitionedBy("year", "month", "day") \
            .create()
        inserted_count = df.count()
    else:
        df.writeTo(table_name).append()
        inserted_count = df.count()

    logger.info(f"[KeplerSDK] Push completed for usecase '{usecase_id}', inserted rows: {inserted_count}")
