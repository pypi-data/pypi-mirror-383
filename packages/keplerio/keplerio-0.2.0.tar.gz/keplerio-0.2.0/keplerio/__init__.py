from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KeplerSDK")

class KeplerClient:
    def __init__(self, base_hdfs_path="/kepler-SQL"):
        self.base_hdfs_path = base_hdfs_path

    def push_usecase(self, usecase_id: str, df: DataFrame, spark: SparkSession, batch_size: int = None):
        """
        Push a Spark DataFrame to HDFS / Iceberg.
        Validates critical columns, formats dates, logs progress, raises errors if invalid.
        """
        critical_cols = ["id_kepler", "date_transaction", "date_scoring"]
        missing_cols = [c for c in critical_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Critical columns missing: {missing_cols}")

        # Ensure date format yyyy-MM-dd
        for col in ["date_transaction", "date_scoring"]:
            df = df.withColumn(col, F.date_format(F.col(col), "yyyy-MM-dd"))

        # Optional: map extra columns to JSON
        extra_cols = [c for c in df.columns if c not in critical_cols + ["id_client", "id_transaction",
                                                                       "pourcentage", "statut", "assigned_to",
                                                                       "commentaire", "investigation_status"] +
                      [f"custom{i}" for i in range(1, 21)]]
        if extra_cols:
            df = df.withColumn("extra_json", F.to_json(F.struct(*extra_cols)))

        path = f"{self.base_hdfs_path}/uc_{usecase_id}"

        logger.info(f"Starting push to {path} with {df.count()} rows...")

        try:
            writer = df.write.mode("append").partitionBy("date_transaction")
            if batch_size:
                # Optional: implement batch processing
                raise NotImplementedError("Batch writing not implemented yet")
            else:
                writer.parquet(path)

            logger.info(f"DataFrame successfully written to {path}")
        except Exception as e:
            logger.error(f"Failed to push DataFrame for usecase {usecase_id}: {e}")
            raise e
