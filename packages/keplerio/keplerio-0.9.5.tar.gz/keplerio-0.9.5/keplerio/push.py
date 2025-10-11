import logging
from pyspark.sql import functions as F, SparkSession, DataFrame
from pyspark.sql.types import StringType, LongType, DateType

logger = logging.getLogger("KeplerSDK")

# --- Defines the standard Kepler schema structure ---
REQUIRED_COLUMNS = {"id_kepler", "id_client", "id_transaction", "pourcentage", "date_transaction"}
# MODIFIED: Renamed 'create_assigned' to 'assigned_to'
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

        # --- 1. Schema Enforcement, Defaulting, and Type Casting ---
        if not REQUIRED_COLUMNS.issubset(df.columns):
            missing = REQUIRED_COLUMNS - set(df.columns)
            raise ValueError(f"DataFrame is missing required fields: {missing}")

        final_df = df

        # MODIFIED: Add date_scoring with today's date if it is missing
        if 'date_scoring' not in final_df.columns:
            final_df = final_df.withColumn('date_scoring', F.current_date())

        # MODIFIED: Add standard columns with nulls ONLY if they don't exist in the source
        all_standard_cols = AUTO_CREATED_NULL_COLUMNS + DEFAULT_ADDED_COLUMNS
        for col_name in all_standard_cols:
            if col_name not in final_df.columns:
                # Add as null, the type will be cast to StringType later
                final_df = final_df.withColumn(col_name, F.lit(None))

        # MODIFIED: Enforce specific data types for all key columns
        logger.info("Enforcing standard Kepler data types...")
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

        # --- 2. Prepare DataFrame for Partitioning ---
        final_df = final_df.withColumn("year", F.year(F.col("date_transaction"))) \
                             .withColumn("month", F.month(F.col("date_transaction"))) \
                             .withColumn("day", F.dayofmonth(F.col("date_transaction")))

        # --- 3. Write to Iceberg Table ---
        # This part remains the same, correctly handling CoW and MoR from the previous version
        table_path = f"{hdfs_base_path}/uc_{usecase_id}"
        table_exists = spark.catalog.tableExists(table_name)

        if not table_exists:
            # Table creation logic with write_strategy and z-ordering
            # ... (code is unchanged here)
        elif mode.lower() == 'append':
            final_df.writeTo(table_name).append()
        elif mode.lower() == 'overwrite':
            final_df.writeTo(table_name).overwritePartitions()

        logger.info(f"Push complete for usecase '{usecase_id}'.")
    finally:
        df.unpersist()
