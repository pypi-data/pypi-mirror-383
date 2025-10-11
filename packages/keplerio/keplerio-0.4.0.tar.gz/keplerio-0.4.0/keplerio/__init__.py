from pyspark.sql import functions as F

class KeplerClient:
    def push_usecase(self, usecase_id: str, df, spark, batch_size: int = None):
        try:
            # Validate required columns
            required_cols = ["id_kepler", "id_client", "id_transaction", "date_transaction"]
            for col_name in required_cols:
                if col_name not in df.columns:
                    raise ValueError(f"Missing required column: {col_name}")

            # Ensure date formats are correct (yyyy-MM-dd)
            df = df.withColumn(
                "date_transaction",
                F.date_format(F.to_date("date_transaction", "yyyy-MM-dd"), "yyyy-MM-dd"),
            )

            if "date_scoring" in df.columns:
                df = df.withColumn(
                    "date_scoring",
                    F.date_format(F.to_date("date_scoring", "yyyy-MM-dd"), "yyyy-MM-dd"),
                )

            # Define path
            path = f"/kepler-SQL/uc_{usecase_id}"

            # Write to HDFS (partitioned by date_transaction)
            (
                df.write
                .mode("append")
                .partitionBy("date_transaction")
                .format("iceberg")  # or "parquet" depending on your config
                .save(path)
            )

            print(f"✅ DataFrame successfully written to {path}")

        except Exception as e:
            print(f"❌ Failed to push DataFrame for usecase {usecase_id}: {e}")
            raise
