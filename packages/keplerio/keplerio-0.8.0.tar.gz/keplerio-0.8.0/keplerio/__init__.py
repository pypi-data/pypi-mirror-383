import logging
from pyspark.sql import functions as F, SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType, DateType, FloatType

# (Logging setup remains the same)
logger = logging.getLogger("KeplerSDK")
# ...

class KeplerClient:
    """
    Production-grade SDK to push Spark DataFrames into partitioned and optimized Iceberg tables.
    Features multi-level partitioning (year, month) and automatic schema evolution.
    """

    def __init__(self, database: str = "kepler", hdfs_base_path: str = "/kepler-SQL"):
        self.database = database
        self.hdfs_base_path = hdfs_base_path
        logger.info(f"KeplerClient initialized for database '{self.database}' at '{self.hdfs_base_path}'")

    def push_usecase(self, usecase_id: str, df, spark: SparkSession):
        """
        Validates, prepares, and appends a DataFrame to a use-case-specific Iceberg table.
        - Partitions data by year and month derived from 'date_transaction'.
        - Automatically adds new columns from the source DataFrame to the table schema.
        - Configures the table to be optimized with Z-Ordering on 'id_kepler'.
        """
        table_name = f"{self.database}.uc_{usecase_id}"
        logger.info(f"Starting push for usecase '{usecase_id}' to table '{table_name}'")

        try:
            df.cache()
            input_count = df.count()
            logger.info(f"Source DataFrame has {input_count} rows to process.")
            
            if input_count == 0:
                logger.warning("Input DataFrame is empty. Nothing to push.")
                return

            # --- 1. Validate required fields ---
            required_fields = {"id_kepler", "date_transaction"}
            if not required_fields.issubset(df.columns):
                missing = required_fields - set(df.columns)
                raise ValueError(f"Missing required fields: {missing}")

            # --- 2. Prepare DataFrame for partitioning and writing ---
            # Add year and month columns for partitioning
            final_df = df.withColumn("year", F.year(F.col("date_transaction"))) \
                         .withColumn("month", F.month(F.col("date_transaction")))

            # Ensure date columns are in the correct format
            for date_col in ["date_transaction", "date_scoring"]:
                if date_col in final_df.columns:
                    final_df = final_df.withColumn(date_col, F.to_date(F.col(date_col)))

            # --- 3. Create or Append to Iceberg Table ---
            table_path = f"{self.hdfs_base_path}/uc_{usecase_id}"
            
            if not spark.catalog.tableExists(table_name):
                logger.info(f"Table '{table_name}' does not exist. Creating new partitioned Iceberg table.")
                print(f"--> Creating table {table_name}. Check Spark UI for progress.")
                
                final_df.writeTo(table_name) \
                    .tableProperty("location", table_path) \
                    .tableProperty("write.zorder.column-names", "id_kepler") \
                    .partitionedBy("year", "month") \
                    .create()
                
                logger.info(f"Successfully created table '{table_name}' partitioned by year and month.")
            else:
                logger.info(f"Table '{table_name}' exists. Appending data.")
                # NEW: Iceberg's append automatically handles schema evolution. No special code is needed.
                logger.info("New columns in the DataFrame will be automatically added to the table schema.")
                print(f"--> Appending {input_count} rows to {table_name}. Check Spark UI for progress.")
                
                final_df.writeTo(table_name).append()
                
                logger.info(f"Successfully appended data to table '{table_name}'.")

            final_count = spark.table(table_name).count()
            logger.info(f"Data push complete. Table '{table_name}' now contains {final_count} rows.")

        except Exception as e:
            logger.error(f"Data push for usecase '{usecase_id}' failed: {e}", exc_info=True)
            raise
        finally:
            df.unpersist()
            logger.debug("Unpersisted the source DataFrame.")
