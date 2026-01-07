# Databricks notebook source
# DBTITLE 1,Setup Configuration
storage_account_name = dbutils.widgets.get("storage_account_name")
# In production, use dbutils.secrets.get()
storage_account_key = dbutils.widgets.get("storage_account_key")

spark.conf.set(
    f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
    storage_account_key
)

# DBTITLE 1,Define Paths
bronze_base_path = f"abfss://bronze@{storage_account_name}.dfs.core.windows.net/npi_data"
silver_base_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/npi_delta"

# DBTITLE 1,Read Bronze Data (Parquet)
from pyspark.sql.functions import col, current_timestamp, input_file_name

print(f"Reading data from {bronze_base_path}...")
bronze_df = spark.read.parquet(bronze_base_path)

# DBTITLE 1,Data Cleaning & Enrichment
# 1. Deduplication based on NPI number and newest ingestion timestamp
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

window_spec = Window.partitionBy("number").orderBy(col("ingestion_timestamp").desc())

silver_df = bronze_df.withColumn("row_num", row_number().over(window_spec)) \
    .filter(col("row_num") == 1) \
    .drop("row_num")

# 2. Add processing metadata
silver_df = silver_df.withColumn("silver_processed_timestamp", current_timestamp())

# DBTITLE 1,Write to Silver Layer (Delta Table)
print(f"Writing data to {silver_base_path}...")

silver_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save(silver_base_path)

print("Bronze to Silver transformation complete.")
