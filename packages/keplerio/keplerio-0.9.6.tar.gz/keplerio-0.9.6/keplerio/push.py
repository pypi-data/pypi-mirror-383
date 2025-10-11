import logging
from pyspark.sql import functions as F, SparkSession, DataFrame
from pyspark.sql.types import StringType, LongType, DateType

logger = logging.getLogger("KeplerSDK")

# --- Defines the standard Kepler schema structure ---
REQUIRED_COLUMNS = {"id_kepler", "id_client", "id_transaction", "pourcentage", "date_transaction"}
AUTO_CREATED_NULL_COLUMNS = [
    "assigned_to", "statut", "commentaire", "investigation_status"
] + [f"custom_{i}" for i in range(1, 21)]
DEFAULT_ADDED_COLUMNS = ["logs_kepler", "files_kepler"]

def push_to_kepler(
    df: DataFrame,
    usecase_id: str,
    spark: SparkSession,
    mode: str = 'append',
    write_strategy: str = 'copy-on-write',
    database: str = "kepler",
    hdfs_base_path: str = "/kepler-SQL",
    zorder_columns: list = None
):
    """
    Standardizes, prepares, and writes a DataFrame to a partitioned Iceberg table.
    """
    if zorder_columns is None:
        zorder_columns = ['id_kepler', 'id_transaction']
        
    table_name = f"{database}.uc_{usecase_id}"
    logger.info(f"Starting push for '{table_name}' in '{mode}' mode using '{write_strategy}' strategy.")

    try:
        df.cache()
        if df.count() == 0:
            logger.warning("Input DataFrame is empty. Nothing to push.")
            return

        final_df = df
        if 'date_scoring' not in final_df.columns:
            final_df = final_df.withColumn('date_scoring', F.current_date())

        all_standard_cols = AUTO_CREATED_NULL_COLUMNS + DEFAULT_ADDED_COLUMNS
        for col_name in all_standard_cols:
            if col_name not in final_df.columns:
                final_df = final_df.withColumn(col_name, F.lit(None))

        string_cols_to_cast = [
            "id_client", "id_transaction", "pourcentage",
            "assigned_to", "statut", "commentaire", "investigation_status"
        ] + [f"custom_{i}" for i in range(1, 21)]

        for col in string_cols_to_cast:
            if col in final_df.columns:
                final_df = final_df.withColumn(col, F.col(col).cast(StringType()))
        
        final_df = final_df.withColumn('id_kepler', F.col('id_kepler').cast(LongType()))
        final_df = final_df.withColumn('date_transaction', F.to_date(F.col('date_transaction')))
        final_df = final_df.withColumn('date_scoring', F.to_date(F.col('date_scoring')))

        final_df = final_df.withColumn("year", F.year(F.col("date_transaction"))) \
                             .withColumn("month", F.month(F.col("date_transaction"))) \
                             .withColumn("day", F.dayofmonth(F.col("date_transaction")))

        table_path = f"{hdfs_base_path}/uc_{usecase_id}"
        table_exists = spark.catalog.tableExists(table_name)

        if not table_exists:
            # --- THIS IS THE CORRECTED BLOCK ---
            logger.info(f"Table '{table_name}' does not exist. Creating new table.")
            writer = final_df.writeTo(table_name) \
                .tableProperty("location", table_path) \
                .tableProperty("write.zorder.column-names", ",".join(zorder_columns)) \
                .partitionedBy("year", "month", "day")

            if write_strategy == 'merge-on-read':
                writer.tableProperty("write.update.mode", "merge-on-read")
                writer.tableProperty("write.delete.mode", "merge-on-read")
                writer.tableProperty("write.merge.mode", "merge-on-read")
                logger.info("Table created with Merge-on-Read strategy for fast updates.")

            writer.create()
            logger.info(f"Table created with Z-Ordering on {zorder_columns}.")
            # --- END OF CORRECTED BLOCK ---
        elif mode.lower() == 'append':
            final_df.writeTo(table_name).append()
        elif mode.lower() == 'overwrite':
            final_df.writeTo(table_name).overwritePartitions()

        logger.info(f"Push complete for usecase '{usecase_id}'.")
    finally:
        df.unpersist()
