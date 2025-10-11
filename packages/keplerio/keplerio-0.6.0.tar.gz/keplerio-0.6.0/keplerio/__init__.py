import os
import json
import logging
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DateType, FloatType

# -------------------- Logging setup --------------------
logger = logging.getLogger("KeplerSDK")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)


class KeplerClient:
    """
    Production-grade SDK to validate and push Spark DataFrames into Iceberg tables on HDFS.
    """

    def __init__(self, hdfs_base_path: str = "/kepler-SQL"):
        self.hdfs_base_path = hdfs_base_path

    # -------------------- Schema definition --------------------
    def get_base_schema(self):
        base_fields = [
            StructField("id_kepler", LongType(), False),
            StructField("id_client", StringType(), True),
            StructField("id_transaction", StringType(), True),
            StructField("date_scoring", DateType(), True),
            StructField("date_transaction", DateType(), False),
            StructField("pourcentage", FloatType(), True),
            StructField("statut", StringType(), True),
            StructField("assigned_to", StringType(), True),
            StructField("commentaire", StringType(), True),
            StructField("investigation_status", StringType(), True),
        ]
        # Add custom1..custom20 columns
        custom_fields = [StructField(f"custom{i}", StringType(), True) for i in range(1, 21)]
        return StructType(base_fields + custom_fields)

    # -------------------- Main function --------------------
    def push_usecase(self, usecase_id: str, df, spark, batch_size: int = 5000):
        """
        Validate schema, ensure required fields, fill missing custom columns,
        create or append to Iceberg table, and log results.
        """
        logger.info(f"Starting push for usecase '{usecase_id}'")

        try:
            base_schema = self.get_base_schema()
            base_fields = [f.name for f in base_schema]
            df_fields = df.columns

            # -------------------- Validate required fields --------------------
            required_fields = ["id_kepler", "date_transaction"]
            missing_fields = [f for f in required_fields if f not in df_fields]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")

            # -------------------- Add missing custom columns --------------------
            for i in range(1, 21):
                cname = f"custom{i}"
                if cname not in df_fields:
                    df = df.withColumn(cname, F.lit(None))
                    logger.debug(f"Added missing column '{cname}' as null")

            # -------------------- Handle extra columns --------------------
            extra_columns = [f for f in df_fields if f not in base_fields]
            if extra_columns:
                metadata_path = os.path.join(self.hdfs_base_path, f"uc_{usecase_id}", "extra_columns.json")
                os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
                with open(metadata_path, "w") as f:
                    json.dump({"extra_columns": extra_columns}, f, indent=4)
                logger.warning(f"Extra columns detected: {extra_columns}. Metadata saved to {metadata_path}")

            # -------------------- Enforce date format --------------------
            for date_col in ["date_transaction", "date_scoring"]:
                if date_col in df.columns:
                    df = df.withColumn(date_col, F.to_date(F.col(date_col), "yyyy-MM-dd"))

            # -------------------- Prepare paths --------------------
            table_path = f"{self.hdfs_base_path}/uc_{usecase_id}"
            table_name = f"kepler.uc_{usecase_id}"
            logger.info(f"Target Iceberg table: {table_name}")
            logger.info(f"Storage path: {table_path}")

            # -------------------- Create or append --------------------
            if not self.table_exists(spark, table_name):
                logger.info(f"Creating new Iceberg table {table_name}")
                df.writeTo(table_name).tableProperty("location", table_path).create()
                logger.info(f"Table {table_name} created successfully.")
            else:
                logger.info(f"Appending data to existing table {table_name}")
                df.writeTo(table_name).append()

            count = df.count()
            logger.info(f"Data push completed successfully. {count} rows written to {table_name}")

        except Exception as e:
            logger.error(f"Data push for usecase '{usecase_id}' failed: {e}", exc_info=True)
            raise

    # -------------------- Helper: check if table exists --------------------
    def table_exists(self, spark, table_name: str) -> bool:
        try:
            tables = [t.name for t in spark.catalog.listTables("kepler")]
            return table_name.split(".")[-1] in tables
        except Exception:
            return False
