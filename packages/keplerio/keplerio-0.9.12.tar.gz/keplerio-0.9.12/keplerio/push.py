import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, FloatType, LongType, DateType

logger = logging.getLogger("KeplerSDK")

# --- Configuration ---
REQUIRED_COLUMNS = {"id_kepler", "date_transaction", "pourcentage"}
ESSENTIAL_COLUMNS = ["assigned_to", "statut", "investigation_status", "commentaire", "id_client", "id_transaction"]
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
    Push a DataFrame into an Iceberg table.
    Adds essential and custom columns only if missing, preserves user-provided data.
    Logs everything: source schema, added columns, final schema.
    """

    if df.isEmpty():
        logger.warning("[KeplerSDK] Input DataFrame is empty. Nothing to push.")
        return

    # --- Check required columns ---
    missing_required = REQUIRED_COLUMNS - set(df.columns)
    if missing_required:
        raise ValueError(f"[KeplerSDK] Missing required columns: {missing_required}")

    # --- Cast required types ---
    df = df.withColumn("id_kepler", F.col("id_kepler").cast(LongType()))
    df = df.withColumn("date_transaction", F.to_date(F.col("date_transaction"), "yyyy-MM-dd"))
    df = df.withColumn("pourcentage", F.col("pourcentage").cast(FloatType()))
    df = df.withColumn("date_scoring", F.current_date())

    # --- Track columns added automatically ---
    added_columns = []

    # Add essential/custom columns only if missing
    for col in ESSENTIAL_COLUMNS + CUSTOM_COLUMNS:
        if col not in df.columns:
            df = df.withColumn(col, F.lit(None).cast(StringType()))
            added_columns.append(col)

    # --- Add partition columns ---
    df = df.withColumn("year", F.year(F.col("date_transaction")))
    df = df.withColumn("month", F.month(F.col("date_transaction")))
    df = df.withColumn("day", F.dayofmonth(F.col("date_transaction")))

    # --- Log schemas ---
    _log_schema_comparison(df, added_columns)

    # --- Ensure Iceberg table exists ---
    table_name = f"{database}.uc_{usecase_id}"
    table_path = f"{hdfs_base_path}/uc_{usecase_id}"

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


# ----------------------
# Helper for logging
# ----------------------
def _log_schema_comparison(df: DataFrame, added_columns=None):
    """
    Logs schema in a readable format:
    - Original columns preserved
    - Columns added automatically are marked
    """
    if added_columns is None:
        added_columns = []

    lines = []
    for f in df.schema.fields:
        suffix = " (added)" if f.name in added_columns else ""
        lines.append(f"{f.name}:{f.dataType.simpleString()}:{f.nullable}{suffix}")

    logger.info("[KeplerSDK] Final DataFrame schema (user + added columns):")
    for line in lines:
        logger.info("  " + line)

    if added_columns:
        logger.info(f"[KeplerSDK] Columns added automatically: {added_columns}")
    else:
        logger.info("[KeplerSDK] No new columns were added.")
