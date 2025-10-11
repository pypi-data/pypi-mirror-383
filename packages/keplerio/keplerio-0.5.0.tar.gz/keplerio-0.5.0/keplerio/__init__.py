from pyspark.sql import functions as F
from pyspark.sql.utils import AnalysisException

class KeplerClient:
    def __init__(self, base_hdfs_path: str = "/kepler-SQL"):
        self.base_hdfs_path = base_hdfs_path

    def push_usecase(self, usecase_id: str, df, spark, batch_size: int = None):
        """
        Validate, format, and insert Spark DataFrame into Iceberg table for the given usecase.
        Automatically creates the table if it doesn't exist.
        """

        try:
            # 1️⃣ Validate required columns
            required_cols = ["id_kepler", "id_client", "id_transaction", "date_transaction"]
            for col_name in required_cols:
                if col_name not in df.columns:
                    raise ValueError(f"Missing required column: {col_name}")

            # 2️⃣ Normalize date formats
            for date_col in ["date_transaction", "date_scoring"]:
                if date_col in df.columns:
                    df = df.withColumn(
                        date_col,
                        F.date_format(F.to_date(F.col(date_col), "yyyy-MM-dd"), "yyyy-MM-dd")
                    )

            # 3️⃣ Define paths and table name
            table_name = f"kepler.uc_{usecase_id}"
            hdfs_path = f"{self.base_hdfs_path}/uc_{usecase_id}"

            # 4️⃣ Create Iceberg table if it doesn’t exist
            try:
                spark.sql(f"DESCRIBE TABLE {table_name}")
                print(f"✅ Table {table_name} already exists.")
            except AnalysisException:
                print(f"⚙️ Creating Iceberg table {table_name} at {hdfs_path} ...")
                (
                    df.writeTo(table_name)
                    .using("iceberg")
                    .tableProperty("location", hdfs_path)
                    .partitionedBy("date_transaction")
                    .create()
                )
                print(f"✅ Table {table_name} created successfully.")

            # 5️⃣ Append DataFrame to Iceberg table
            print(f"📦 Appending data to {table_name} ...")
            (
                df.writeTo(table_name)
                .append()
            )

            print(f"✅ Data successfully inserted into {table_name}")

        except Exception as e:
            print(f"❌ Failed to push DataFrame for usecase {usecase_id}: {e}")
            raise
