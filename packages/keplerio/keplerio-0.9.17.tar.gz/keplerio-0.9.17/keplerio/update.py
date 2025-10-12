import logging
from pyspark.sql import SparkSession, DataFrame

logger = logging.getLogger("KeplerSDK")

def update_kepler(spark: SparkSession, usecase_id: str, updates, join_key="id_kepler",
                  transaction_date=None, database="kepler"):
    table_name = f"{database}.uc_{usecase_id}"
    view_name = f"updates_{usecase_id}"

    # Convert dict to DataFrame
    if isinstance(updates, dict):
        if join_key not in updates:
            raise ValueError(f"Join key '{join_key}' missing in dict")
        key_val = updates[join_key]
        cols = [join_key] + [k for k in updates if k != join_key]
        vals = [key_val] + [v for k, v in updates.items() if k != join_key]
        updates = spark.createDataFrame([tuple(vals)], cols)
    elif not isinstance(updates, DataFrame):
        raise TypeError("updates must be a Spark DataFrame or a dict")

    if join_key not in updates.columns:
        raise ValueError(f"Join key '{join_key}' not in updates")

    updates.createOrReplaceTempView(view_name)

    on_clause = f"target.{join_key} = source.{join_key}"
    if transaction_date:
        on_clause += f" AND target.date_transaction = '{transaction_date}'"
        logger.info(f"[KeplerSDK] Applying partition pruning for date {transaction_date}")

    set_cols = [col for col in updates.columns if col != join_key]
    if not set_cols:
        raise ValueError("No columns to update besides join key")
    set_clause = ", ".join([f"target.{col} = source.{col}" for col in set_cols])

    # Count before update (optional, approximate)
    before_count = spark.table(table_name).count()

    sql = f"""
        MERGE INTO {table_name} AS target
        USING {view_name} AS source
        ON {on_clause}
        WHEN MATCHED THEN UPDATE SET {set_clause}
    """
    spark.sql(sql)

    # Count after update
    after_count = spark.table(table_name).count()
    update_count = min(after_count - before_count + updates.count(), updates.count())

    logger.info(f"[KeplerSDK] Update completed for table '{table_name}', approx. updated rows: {update_count}")
