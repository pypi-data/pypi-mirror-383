import logging
from pyspark.sql import functions as F, SparkSession, DataFrame
from pyspark.sql.types import StringType, LongType, DateType

logger = logging.getLogger("KeplerSDK")

# --- Schema Constants ---
REQUIRED_COLUMNS = {"id_kepler", "id_client", "id_transaction", "pourcentage", "date_transaction"}

def push_to_kepler(
    df: DataFrame,
    usecase_id: str,
    spark: SparkSession,
    mode: str = 'append',
    write_strategy: str = 'merge-on-read',  # CHANGED TO MERGE-ON-READ
    database: str = "kepler",
    hdfs_base_path: str = "/kepler-SQL",
    zorder_columns: list = None
):
    """
    Optimized for both updates and Drill queries using Merge-on-Read strategy.
    
    Args:
        df: Input DataFrame with core columns and optional custom columns
        usecase_id: Unique identifier for the use case
        spark: Spark session
        mode: 'append' or 'overwrite'
        write_strategy: 'merge-on-read' (recommended) or 'copy-on-write'
        database: Database name
        hdfs_base_path: Base HDFS path for table storage
        zorder_columns: Columns for Z-ordering optimization
    """
    if zorder_columns is None:
        zorder_columns = ['id_kepler', 'id_transaction']
        
    table_name = f"{database}.uc_{usecase_id}"
    table_path = f"{hdfs_base_path}/uc_{usecase_id}"
    
    logger.info(f"Starting push to '{table_name}' with {len(df.columns)} columns using '{write_strategy}' strategy")

    try:
        # Quick empty check
        if df.rdd.isEmpty():
            logger.warning("Input DataFrame is empty. Nothing to push.")
            return

        # Apply only essential transformations
        final_df = _apply_essential_transformations(df)
        
        # Check table existence
        table_exists = spark.catalog.tableExists(table_name)
        
        if not table_exists:
            _create_optimized_iceberg_table(final_df, table_name, table_path, zorder_columns, write_strategy)
            logger.info(f"Created new table '{table_name}' with '{write_strategy}' strategy")
        else:
            _log_schema_evolution(final_df, table_name, spark)
        
        # Write data
        _write_to_iceberg(final_df, table_name, mode)
        
        logger.info(f"Push completed successfully for '{usecase_id}' using {write_strategy}")

    except Exception as e:
        logger.error(f"Push failed for '{usecase_id}': {str(e)}")
        raise

def _apply_essential_transformations(df: DataFrame) -> DataFrame:
    """
    Apply only essential transformations optimized for Drill queries.
    """
    # Add partitioning columns (essential for Drill partition pruning)
    df_transformed = df \
        .withColumn("year", F.year(F.col("date_transaction"))) \
        .withColumn("month", F.month(F.col("date_transaction"))) \
        .withColumn("day", F.dayofmonth(F.col("date_transaction")))
    
    # Add date_scoring if missing
    if 'date_scoring' not in df_transformed.columns:
        df_transformed = df_transformed.withColumn('date_scoring', F.current_date())
    
    # Apply critical type fixes for Drill compatibility
    df_transformed = _apply_drill_optimized_types(df_transformed)
    
    return df_transformed

def _apply_drill_optimized_types(df: DataFrame) -> DataFrame:
    """Apply type optimizations for better Drill performance."""
    select_exprs = []
    
    for col_name in df.columns:
        if col_name == 'id_kepler':
            select_exprs.append(F.col('id_kepler').cast(LongType()).alias('id_kepler'))
        elif col_name == 'date_transaction':
            select_exprs.append(F.to_date(F.col('date_transaction')).alias('date_transaction'))
        elif col_name == 'date_scoring':
            select_exprs.append(F.to_date(F.col('date_scoring')).alias('date_scoring'))
        elif col_name in ['id_client', 'id_transaction', 'pourcentage']:
            # String types are well handled by Drill
            select_exprs.append(F.col(col_name).cast(StringType()).alias(col_name))
        else:
            # Leave other columns as-is
            select_exprs.append(F.col(col_name))
    
    return df.select(*select_exprs)

def _create_optimized_iceberg_table(
    df: DataFrame, 
    table_name: str, 
    table_path: str, 
    zorder_columns: list, 
    write_strategy: str
):
    """Create Iceberg table optimized for updates and Drill queries."""
    writer = df.writeTo(table_name) \
        .tableProperty("location", table_path) \
        .tableProperty("write.zorder.column-names", ",".join(zorder_columns)) \
        .partitionedBy("year", "month", "day") \
        .tableProperty("format-version", "2")  # Required for merge-on-read
    
    # Configure merge-on-read for fast updates
    if write_strategy == 'merge-on-read':
        writer.tableProperty("write.update.mode", "merge-on-read") \
              .tableProperty("write.delete.mode", "merge-on-read") \
              .tableProperty("write.merge.mode", "merge-on-read") \
              .tableProperty("read.split.open-cost", "134217728")  # Optimize for Drill
    else:
        # copy-on-write settings
        writer.tableProperty("write.update.mode", "copy-on-write") \
              .tableProperty("write.delete.mode", "copy-on-write") \
              .tableProperty("write.merge.mode", "copy-on-write")
    
    writer.create()

def _log_schema_evolution(df: DataFrame, table_name: str, spark: SparkSession):
    """Log schema changes for monitoring."""
    try:
        table_df = spark.table(table_name)
        new_columns = set(df.columns) - set(table_df.columns)
        
        if new_columns:
            logger.info(f"Schema evolution: adding new columns {list(new_columns)}")
    except Exception as e:
        logger.debug(f"Could not check schema evolution: {str(e)}")

def _write_to_iceberg(df: DataFrame, table_name: str, mode: str):
    """Write DataFrame to Iceberg table."""
    if mode.lower() == 'append':
        df.writeTo(table_name).append()
    elif mode.lower() == 'overwrite':
        df.writeTo(table_name).overwritePartitions()
    else:
        raise ValueError(f"Unsupported mode: {mode}. Use 'append' or 'overwrite'")

# --- Helper function for Drill-specific optimizations ---
def configure_drill_optimized_table(
    usecase_id: str,
    spark: SparkSession,
    database: str = "kepler"
):
    """
    Apply additional table properties optimized for Apache Drill queries.
    Run this once after table creation.
    """
    table_name = f"{database}.uc_{usecase_id}"
    
    # Set properties for better Drill performance
    properties = {
        "read.split.target-size": "134217728",  # 128MB - optimal for Drill
        "read.split.metadata-target-size": "33554432",  # 32MB
        "format-version": "2",
        "commit.retry.num-retries": "5"
    }
    
    for key, value in properties.items():
        spark.sql(f"ALTER TABLE {table_name} SET TBLPROPERTIES ('{key}' = '{value}')")
    
    logger.info(f"Applied Drill optimizations to {table_name}")
