import logging
from pyspark.sql import functions as F, SparkSession, DataFrame
from pyspark.sql.types import StringType

logger = logging.getLogger("KeplerSDK")

REQUIRED_COLUMNS = {"id_kepler", "id_client", "id_transaction", "pourcentage"}
AUTO_CREATED_NULL_COLUMNS = [
    "create_assigned", "statut", "commentaire", "investigation_status"
] + [f"custom_{i}" for i in range(1, 21)]
DEFAULT_ADDED_COLUMNS = ["logs_kepler", "files_kepler"]

def push_to_kepler(
    df: DataFrame,
    usecase_id: str,
    spark: SparkSession,
    mode: str = 'append',
    database: str = "kepler",
    hdfs_base_path: str = "/kepler-SQL",
    zorder_columns: list = None
):
    """
    Standardizes, prepares, and writes a DataFrame to a partitioned Iceberg table.
    Enforces a core schema by adding required columns with nulls if they are missing.

    Args:
        df (DataFrame): The source Spark DataFrame.
        usecase_id (str): A unique identifier for the use case.
        spark (SparkSession): The active SparkSession.
        mode (str): Write mode, 'append' (default) or 'overwrite'.
        database (str): The Spark catalog database name.
        hdfs_base_path (str): The base HDFS path for table data.
        zorder_columns (list): Columns to use for Z-Ordering. Defaults to ['id_kepler', 'id_transaction'].
    """
    if zorder_columns is None:
        zorder_columns = ['id_kepler', 'id_transaction']
    table_name = f"{database}.uc_{usecase_id}"
    logger.info(f"Starting push for usecase '{usecase_id}' to '{table_name}' in '{mode}' mode.")

    if mode.lower() not in ['append', 'overwrite']:
        raise ValueError(f"Invalid mode '{mode}'. Choose 'append' or 'overwrite'.")

    try:
        df.cache()
        if df.count() == 0:
            logger.warning("Input DataFrame is empty. Nothing to push.")
            return

        # --- 1. Schema Enforcement & Augmentation ---
        if not REQUIRED_COLUMNS.issubset(df.columns):
            missing = REQUIRED_COLUMNS - set(df.columns)
            raise ValueError(f"DataFrame is missing required fields: {missing}")

        logger.info("Enforcing Kepler schema. Adding missing standard columns as null.")
        final_df = df
        all_standard_cols = AUTO_CREATED_NULL_COLUMNS + DEFAULT_ADDED_COLUMNS
        for col_name in all_standard_cols:
            if col_name not in final_df.columns:
                final_df = final_df.withColumn(col_name, F.lit(None).cast(StringType()))

        # --- 2. Prepare DataFrame for Partitioning ---
        final_df = final_df.withColumn("year", F.year(F.col("date_transaction"))) \
                             .withColumn("month", F.month(F.col("date_transaction"))) \
                             .withColumn("day", F.dayofmonth(F.col("date_transaction")))

        # --- 3. Write to Iceberg Table ---
        table_path = f"{hdfs_base_path}/uc_{usecase_id}"
        table_exists = spark.catalog.tableExists(table_name)

        if not table_exists:
            logger.info(f"Table '{table_name}' does not exist. Creating new table.")
            final_df.writeTo(table_name) \
                .tableProperty("location", table_path) \
                .tableProperty("write.zorder.column-names", ",".join(zorder_columns)) \
                .partitionedBy("year", "month", "day") \
                .create()
            logger.info(f"Successfully created table '{table_name}' with Z-Ordering on {zorder_columns}.")
        elif mode.lower() == 'append':
            logger.info(f"Appending data to '{table_name}'.")
            final_df.writeTo(table_name).append()
        elif mode.lower() == 'overwrite':
            logger.info(f"Overwriting partitions in '{table_name}'.")
            final_df.writeTo(table_name).overwritePartitions()

        logger.info(f"Push complete for usecase '{usecase_id}'.")

    except Exception as e:
        logger.error(f"Data push for usecase '{usecase_id}' failed: {e}", exc_info=True)
        raise
    finally:
        df.unpersist()
