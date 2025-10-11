# keplerio

Python SDK to push Spark DataFrames to HDFS/Iceberg for Kepler usecases.

- Validates critical columns (id_kepler, date_transaction)
- Formats date columns (yyyy-MM-dd)
- Supports canonical + custom + extra_json columns
- Partitions by date_transaction for efficient queries
- Works with local or remote Spark Connect clusters
# keplerio
