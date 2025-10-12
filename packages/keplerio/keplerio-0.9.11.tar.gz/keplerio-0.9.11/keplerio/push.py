import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, FloatType, LongType, DateType

logger = logging.getLogger("KeplerSDK")

# Required columns that must exist in the input DataFrame
REQUIRED_INPUT_COLUMNS = {"id_kepler", "date_transaction", "pourcentage"}

# Essential columns to auto-add if missing
ESSENTIAL_COLUMNS = ["assigned_to", "statut", "investigation_status", "commentaire", "id_client", "id_transaction"]

# Custom columns to auto-add
CUSTOM_COLUMNS = [f"custom{i}" for i in range(1, 21)]

def push_to_kepler(
    df: DataFrame,
    usecase_id: str,
    spark: SparkSession,
    mode: str = "append",
    database: str = "kepler",
    hdfs_base_path: str = "/kepler-SQL"
):
    """
    Push a DataFrame into an Iceberg table with full control.
    Adds essential columns and custom1-20 columns if missing.
    Logs all transformations.
    """
    table_name = f"{database}.uc_{usecase_id}"
    table_path = f"{hdfs_base_path}/uc_{usecase_id}"

    if df.isEmpty():
        logger.warning("[KeplerSDK] Input DataFrame is empty. Nothing to push.")
        return

    # --- Check mandatory columns ---
    missing_required = REQUIRED_INPUT_COLUMNS - set(df.columns)
    if missing_required:
        raise ValueError(f"[KeplerSDK] Missing required columns: {missing_required}")

    # --- Ensure data types ---
    df = df.withColumn("id_kepler", F.col("id_kepler").cast(LongType()))
    df = df.withColumn("date_transaction", F.to_date(F.col("date_transaction"), "yyyy-MM-dd"))
    df = df.withColumn("pourcentage", F.col("pourcentage").cast(FloatType()))
    df = df.withColumn("date_scoring", F.current_date())

    # --- Add essential columns if missing ---
    added_columns = []
    for col in ESSENTIAL_COLUMNS:
        if col not in df.columns:
            df = df.withColumn(col, F.lit(None).cast(StringType()))
            added_columns.append(col)

    # --- Add custom1..custom20 if missing ---
    for col in CUSTOM_COLUMNS:
        if col not in df.columns:
            df = df.withColumn(col, F.lit(None).cast(StringType()))
            added_columns.append(col)

    # --- Add partition columns ---
    df = df.withColumn("year", F.year(F.col("date_transaction")))
    df = df.withColumn("month", F.month(F.col("date_transaction")))
    df = df.withColumn("day", F.dayofmonth(F.col("date_transaction")))

    # --- Log transformations ---
    logger.info(f"[KeplerSDK] Original DataFrame columns: {df.columns}")
    logger.info(f"[KeplerSDK] Columns added automatically: {added_columns}")
    logger.info(f"[KeplerSDK] Final DataFrame schema:")
    df.printSchema()

    # --- Ensure table exists ---
    if not spark.catalog.tableExists(table_name):
        logger.info(f"[KeplerSDK] Creating Iceberg table {table_name}")
        df.writeTo(table_name) \
            .tableProperty("location", table_path) \
            .tableProperty("format-version", "2") \
            .partitionedBy("year", "month", "day") \
            .create()
    else:
        logger.info(f"[KeplerSDK] Table {table_name} exists, schema evolution will handle new columns")

    # --- Write data ---
    if mode.lower() == "append":
        df.writeTo(table_name).append()
    elif mode.lower() == "overwrite":
        df.writeTo(table_name).overwritePartitions()
    else:
        raise ValueError("[KeplerSDK] mode must be 'append' or 'overwrite'")

    logger.info(f"[KeplerSDK] Push completed successfully for usecase '{usecase_id}'")
