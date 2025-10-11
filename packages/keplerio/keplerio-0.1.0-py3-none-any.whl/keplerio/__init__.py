# keplerio/__init__.py
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import *
from pyspark.sql import functions as F
import json

# -------------------- Columns --------------------
CRITICAL_COLUMNS = ["id_kepler", "date_transaction"]
DATE_COLUMNS = ["date_transaction", "date_scoring"]
CANONICAL_COLUMNS = [
    "id_kepler", "id_client", "id_transaction",
    "date_scoring", "date_transaction",
    "pourcentage", "statut", "assigned_to",
    "commentaire", "investigation_status"
]
CUSTOM_COLUMNS = [f"custom{i}" for i in range(1, 21)]

# -------------------- Kepler Client --------------------
class KeplerClient:

    def __init__(self):
        """
        SDK uses a fixed path for all usecases: /kepler-SQL/uc_{usecaseid}
        Spark session is passed per call (supports local or remote Spark Connect).
        """
        self.base_hdfs_path = "/kepler-SQL"

    # -------------------- Validation --------------------
    @staticmethod
    def validate_dataframe(df: DataFrame):
        errors = []

        # Check critical columns exist
        for col in CRITICAL_COLUMNS:
            if col not in df.columns:
                errors.append(f"Missing critical column: {col}")
            else:
                null_count = df.filter(F.col(col).isNull()).count()
                if null_count > 0:
                    errors.append(f"Critical column '{col}' contains {null_count} null values")

        # Validate date format columns (yyyy-MM-dd)
        for col in DATE_COLUMNS:
            if col in df.columns:
                invalid_count = df.filter(~F.col(col).rlike(r"^\d{4}-\d{2}-\d{2}$")).count()
                if invalid_count > 0:
                    errors.append(f"Column '{col}' contains {invalid_count} rows with invalid date format (yyyy-MM-dd)")

        if errors:
            raise ValueError("DataFrame validation failed:\n" + "\n".join(errors))

    # -------------------- Map extra columns --------------------
    @staticmethod
    def map_extra_columns(df: DataFrame) -> DataFrame:
        extra_cols = [c for c in df.columns if c not in CANONICAL_COLUMNS]

        # Map custom1..custom20
        for i in range(20):
            if i < len(extra_cols):
                df = df.withColumn(f"custom{i+1}", F.col(extra_cols[i]).cast(StringType()))
            else:
                df = df.withColumn(f"custom{i+1}", F.lit(None).cast(StringType()))

        # Remaining columns into JSON
        remaining_cols = extra_cols[20:]
        if remaining_cols:
            df = df.withColumn("extra_json", F.to_json(F.struct(*[F.col(c) for c in remaining_cols])))
        else:
            df = df.withColumn("extra_json", F.lit(None))

        # Ensure canonical columns exist
        for col in CANONICAL_COLUMNS:
            if col not in df.columns:
                df = df.withColumn(col, F.lit(None))

        # Ensure date columns are properly formatted
        for col in DATE_COLUMNS:
            if col in df.columns:
                df = df.withColumn(col, F.date_format(F.col(col), "yyyy-MM-dd"))

        return df.select(CANONICAL_COLUMNS + CUSTOM_COLUMNS + ["extra_json"])

    # -------------------- Push usecase --------------------
    def push_usecase(self, usecase_id: str, df: DataFrame, spark: SparkSession, batch_size: int = 100000):
        """
        Push a Spark DataFrame to HDFS/Iceberg for a given usecase_id.
        Path is fixed: /kepler-SQL/uc_{usecaseid}
        """
        # 1️⃣ Validate DF
        self.validate_dataframe(df)

        # 2️⃣ Map canonical + custom + extra_json
        df_mapped = self.map_extra_columns(df)

        # 3️⃣ Repartition by date_transaction for efficient writes
        df_mapped = df_mapped.repartition(batch_size, "date_transaction")

        # 4️⃣ Write to fixed path
        path = f"{self.base_hdfs_path}/uc_{usecase_id}"
        df_mapped.write.mode("append") \
            .partitionBy("date_transaction") \
            .parquet(path)

        print(f"DataFrame successfully written to {path} ({df_mapped.count()} rows)")
