# Databricks notebook source
# ============================================================
# OpsIntel Copilot
# Week 3 — Bronze Ingestion Pipeline
#
# Purpose:
# Read raw CSV datasets from AWS S3 and convert them into
# Delta Lake bronze tables with ingestion metadata.
#
# Datasets:
# - orders
# - security_logs
# - admin_events
#
# Output:
# - bronze_orders
# - bronze_security_logs
# - bronze_admin_events
# ============================================================

from pyspark.sql import functions as F


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

S3_BUCKET = "opsintel-copilot-angad-0025"
BASE_PATH = f"s3://{S3_BUCKET}"

RAW_BASE_PATH = f"{BASE_PATH}/raw"
BRONZE_BASE_PATH = f"{BASE_PATH}/bronze"

DATABASE_NAME = "opsintel_copilot"


# ------------------------------------------------------------
# Dataset configuration
# ------------------------------------------------------------

DATASETS = {
    "orders": {
        "raw_path": f"{RAW_BASE_PATH}/orders/",
        "bronze_path": f"{BRONZE_BASE_PATH}/orders/",
        "table_name": "bronze_orders",
    },
    "security_logs": {
        "raw_path": f"{RAW_BASE_PATH}/security_logs/",
        "bronze_path": f"{BRONZE_BASE_PATH}/security_logs/",
        "table_name": "bronze_security_logs",
    },
    "admin_events": {
        "raw_path": f"{RAW_BASE_PATH}/admin_events/",
        "bronze_path": f"{BRONZE_BASE_PATH}/admin_events/",
        "table_name": "bronze_admin_events",
    },
}


# ------------------------------------------------------------
# Create database
# ------------------------------------------------------------

spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
spark.sql(f"USE {DATABASE_NAME}")


# ------------------------------------------------------------
# Helper function: read raw CSV and write bronze Delta table
# ------------------------------------------------------------

def ingest_to_bronze(dataset_name: str, config: dict) -> None:
    """
    Reads raw CSV data from S3, adds bronze ingestion metadata,
    writes it as Delta format, and registers it as a Databricks table.
    """

    raw_path = config["raw_path"]
    bronze_path = config["bronze_path"]
    table_name = config["table_name"]

    print(f"Starting bronze ingestion for dataset: {dataset_name}")
    print(f"Raw path: {raw_path}")
    print(f"Bronze path: {bronze_path}")
    print(f"Table name: {DATABASE_NAME}.{table_name}")

    raw_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("mode", "PERMISSIVE")
        .csv(raw_path)
    )

    bronze_df = (
        raw_df
        .withColumn("_dataset_name", F.lit(dataset_name))
        .withColumn("_ingestion_timestamp", F.current_timestamp())
        .withColumn("_bronze_load_date", F.current_date())
        .withColumn("_source_file", F.input_file_name())
    )

    (
        bronze_df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(bronze_path)
    )

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {DATABASE_NAME}.{table_name}
        USING DELTA
        LOCATION '{bronze_path}'
    """)

    row_count = spark.table(f"{DATABASE_NAME}.{table_name}").count()

    print(f"Completed bronze ingestion for dataset: {dataset_name}")
    print(f"Rows written to {DATABASE_NAME}.{table_name}: {row_count}")
    print("-" * 80)


# ------------------------------------------------------------
# Run bronze ingestion for all configured datasets
# ------------------------------------------------------------

for dataset_name, config in DATASETS.items():
    ingest_to_bronze(dataset_name, config)


# ------------------------------------------------------------
# Bronze validation summary
# ------------------------------------------------------------

summary_rows = []

for dataset_name, config in DATASETS.items():
    table_name = config["table_name"]
    count_value = spark.table(f"{DATABASE_NAME}.{table_name}").count()

    summary_rows.append((dataset_name, table_name, count_value))

summary_df = spark.createDataFrame(
    summary_rows,
    ["dataset_name", "bronze_table_name", "record_count"]
)

display(summary_df)