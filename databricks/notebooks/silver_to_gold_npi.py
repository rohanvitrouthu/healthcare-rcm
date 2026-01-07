# Databricks notebook source
# DBTITLE 1,Setup Configuration
storage_account_name = dbutils.widgets.get("storage_account_name")
storage_account_key = dbutils.widgets.get("storage_account_key")

spark.conf.set(
    f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
    storage_account_key
)

# DBTITLE 1,Define Paths
silver_base_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/npi_delta"
gold_base_path = f"abfss://gold@{storage_account_name}.dfs.core.windows.net/dim_provider"

# DBTITLE 1,Read Silver Data (Delta)
print(f"Reading data from {silver_base_path}...")
silver_df = spark.read.format("delta").load(silver_base_path)

# DBTITLE 1,Gold Layer Transformation (Star Schema Structure)
# Selecting and renaming columns for the Provider Dimension
from pyspark.sql.functions import col, current_timestamp, lit

gold_df = silver_df.select(
    col("number").alias("npi_id"),
    col("basic.first_name").alias("first_name"),
    col("basic.last_name").alias("last_name"),
    col("basic.organization_name").alias("organization_name"),
    col("basic.credential").alias("credential"),
    col("basic.gender").alias("gender"),
    col("basic.enumeration_date").alias("enumeration_date"),
    lit(True).alias("is_current"),
    lit(False).alias("is_quarantined")
)

# Add auditing metadata
gold_df = gold_df.withColumn("gold_processed_timestamp", current_timestamp())

# DBTITLE 1,Write to Gold Layer (Delta Table)
print(f"Writing data to {gold_base_path}...")

gold_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save(gold_base_path)

print("Silver to Gold transformation complete. Provider Dimension is ready.")
