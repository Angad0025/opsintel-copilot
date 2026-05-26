# Databricks notebook source
# ============================================================
# OpsIntel Copilot
# Week 3 — Silver Data Quality Pipeline
#
# Purpose:
# Read bronze Delta tables, apply data quality checks,
# remove duplicates, validate timestamps, separate bad records,
# and write cleaned data into silver Delta tables.
#
# Inputs:
# - bronze_orders
# - bronze_security_logs
# - bronze_admin_events
#
# Outputs:
# - silver_orders
# - silver_security_logs
# - silver_admin_events
# - bad_records_summary
# ============================================================

from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

S3_BUCKET = "opsintel-copilot-angad-0025"
BASE_PATH = f"s3://{S3_BUCKET}"

SILVER_BASE_PATH = f"{BASE_PATH}/silver"
BAD_RECORDS_BASE_PATH = f"{BASE_PATH}/silver/bad_records_summary"

DATABASE_NAME = "opsintel_copilot"


spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
spark.sql(f"USE {DATABASE_NAME}")


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def table_exists(table_name: str) -> bool:
    """
    Checks if a table exists in the selected Databricks database.
    """
    return spark.catalog.tableExists(f"{DATABASE_NAME}.{table_name}")


def clean_column_names(df):
    """
    Standardizes column names to lowercase snake_case style.
    This helps make downstream SQL and PySpark easier.
    """
    cleaned_columns = []

    for col_name in df.columns:
        cleaned_name = (
            col_name.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace(".", "_")
        )
        cleaned_columns.append(cleaned_name)

    return df.toDF(*cleaned_columns)


def write_delta_table(df, table_name: str, output_path: str) -> None:
    """
    Writes a DataFrame to S3 in Delta format and registers it as a table.
    """
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(output_path)
    )

    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {DATABASE_NAME}.{table_name}
        USING DELTA
        LOCATION '{output_path}'
    """)


def add_bad_record_summary(summary_rows, dataset_name: str, rule_failed: str, bad_count: int):
    """
    Adds one row to the bad records summary list.
    """
    summary_rows.append(
        (
            dataset_name,
            rule_failed,
            int(bad_count),
        )
    )


# ------------------------------------------------------------
# Silver processing: Orders
# ------------------------------------------------------------

def process_orders(summary_rows):
    dataset_name = "orders"
    bronze_table = "bronze_orders"
    silver_table = "silver_orders"
    silver_path = f"{SILVER_BASE_PATH}/orders/"

    if not table_exists(bronze_table):
        raise ValueError(f"Missing required table: {DATABASE_NAME}.{bronze_table}")

    df = spark.table(f"{DATABASE_NAME}.{bronze_table}")
    df = clean_column_names(df)

    original_count = df.count()

    # Try to detect common timestamp column names.
    timestamp_candidates = [
        "order_timestamp",
        "created_at",
        "event_timestamp",
        "timestamp",
        "order_time",
    ]

    timestamp_col = None
    for candidate in timestamp_candidates:
        if candidate in df.columns:
            timestamp_col = candidate
            break

    if timestamp_col:
        df = df.withColumn(timestamp_col, F.to_timestamp(F.col(timestamp_col)))
        invalid_timestamp_count = df.filter(F.col(timestamp_col).isNull()).count()
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "invalid_or_missing_timestamp",
            invalid_timestamp_count,
        )
    else:
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "missing_timestamp_column",
            original_count,
        )

    # Required field checks.
    required_columns = []

    for candidate in ["order_id", "customer_id"]:
        if candidate in df.columns:
            required_columns.append(candidate)

    for required_col in required_columns:
        bad_count = df.filter(F.col(required_col).isNull()).count()
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            f"missing_{required_col}",
            bad_count,
        )

    # Remove rows with missing required fields.
    for required_col in required_columns:
        df = df.filter(F.col(required_col).isNotNull())

    # Remove rows with invalid timestamp if timestamp column exists.
    if timestamp_col:
        df = df.filter(F.col(timestamp_col).isNotNull())

    # Remove duplicates.
    if "order_id" in df.columns:
        before_dedup = df.count()
        df = df.dropDuplicates(["order_id"])
        after_dedup = df.count()
        duplicate_count = before_dedup - after_dedup
    else:
        before_dedup = df.count()
        df = df.dropDuplicates()
        after_dedup = df.count()
        duplicate_count = before_dedup - after_dedup

    add_bad_record_summary(
        summary_rows,
        dataset_name,
        "duplicate_records_removed",
        duplicate_count,
    )

    silver_df = (
        df
        .withColumn("_silver_load_timestamp", F.current_timestamp())
        .withColumn("_silver_load_date", F.current_date())
    )

    write_delta_table(silver_df, silver_table, silver_path)

    final_count = spark.table(f"{DATABASE_NAME}.{silver_table}").count()

    print(f"Orders silver processing complete.")
    print(f"Original bronze rows: {original_count}")
    print(f"Final silver rows: {final_count}")
    print("-" * 80)


# ------------------------------------------------------------
# Silver processing: Security Logs
# ------------------------------------------------------------

def process_security_logs(summary_rows):
    dataset_name = "security_logs"
    bronze_table = "bronze_security_logs"
    silver_table = "silver_security_logs"
    silver_path = f"{SILVER_BASE_PATH}/security_logs/"

    if not table_exists(bronze_table):
        raise ValueError(f"Missing required table: {DATABASE_NAME}.{bronze_table}")

    df = spark.table(f"{DATABASE_NAME}.{bronze_table}")
    df = clean_column_names(df)

    original_count = df.count()

    timestamp_candidates = [
        "event_timestamp",
        "timestamp",
        "login_timestamp",
        "created_at",
        "event_time",
    ]

    timestamp_col = None
    for candidate in timestamp_candidates:
        if candidate in df.columns:
            timestamp_col = candidate
            break

    if timestamp_col:
        df = df.withColumn(timestamp_col, F.to_timestamp(F.col(timestamp_col)))
        invalid_timestamp_count = df.filter(F.col(timestamp_col).isNull()).count()
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "invalid_or_missing_timestamp",
            invalid_timestamp_count,
        )
    else:
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "missing_timestamp_column",
            original_count,
        )

    required_columns = []

    for candidate in ["event_id", "user_id", "ip_address"]:
        if candidate in df.columns:
            required_columns.append(candidate)

    for required_col in required_columns:
        bad_count = df.filter(F.col(required_col).isNull()).count()
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            f"missing_{required_col}",
            bad_count,
        )

    for required_col in required_columns:
        df = df.filter(F.col(required_col).isNotNull())

    if timestamp_col:
        df = df.filter(F.col(timestamp_col).isNotNull())

    # Standardize severity if present.
    if "severity" in df.columns:
        df = df.withColumn("severity", F.upper(F.trim(F.col("severity"))))

    # Standardize event type if present.
    if "event_type" in df.columns:
        df = df.withColumn("event_type", F.lower(F.trim(F.col("event_type"))))

    if "event_id" in df.columns:
        before_dedup = df.count()
        df = df.dropDuplicates(["event_id"])
        after_dedup = df.count()
        duplicate_count = before_dedup - after_dedup
    else:
        before_dedup = df.count()
        df = df.dropDuplicates()
        after_dedup = df.count()
        duplicate_count = before_dedup - after_dedup

    add_bad_record_summary(
        summary_rows,
        dataset_name,
        "duplicate_records_removed",
        duplicate_count,
    )

    silver_df = (
        df
        .withColumn("_silver_load_timestamp", F.current_timestamp())
        .withColumn("_silver_load_date", F.current_date())
    )

    write_delta_table(silver_df, silver_table, silver_path)

    final_count = spark.table(f"{DATABASE_NAME}.{silver_table}").count()

    print(f"Security logs silver processing complete.")
    print(f"Original bronze rows: {original_count}")
    print(f"Final silver rows: {final_count}")
    print("-" * 80)


# ------------------------------------------------------------
# Silver processing: Admin Events
# ------------------------------------------------------------

def process_admin_events(summary_rows):
    dataset_name = "admin_events"
    bronze_table = "bronze_admin_events"
    silver_table = "silver_admin_events"
    silver_path = f"{SILVER_BASE_PATH}/admin_events/"

    if not table_exists(bronze_table):
        raise ValueError(f"Missing required table: {DATABASE_NAME}.{bronze_table}")

    df = spark.table(f"{DATABASE_NAME}.{bronze_table}")
    df = clean_column_names(df)

    original_count = df.count()

    timestamp_candidates = [
        "event_timestamp",
        "timestamp",
        "admin_event_timestamp",
        "created_at",
        "event_time",
    ]

    timestamp_col = None
    for candidate in timestamp_candidates:
        if candidate in df.columns:
            timestamp_col = candidate
            break

    if timestamp_col:
        df = df.withColumn(timestamp_col, F.to_timestamp(F.col(timestamp_col)))
        invalid_timestamp_count = df.filter(F.col(timestamp_col).isNull()).count()
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "invalid_or_missing_timestamp",
            invalid_timestamp_count,
        )
    else:
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "missing_timestamp_column",
            original_count,
        )

    required_columns = []

    for candidate in ["event_id", "admin_user", "action"]:
        if candidate in df.columns:
            required_columns.append(candidate)

    for required_col in required_columns:
        bad_count = df.filter(F.col(required_col).isNull()).count()
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            f"missing_{required_col}",
            bad_count,
        )

    for required_col in required_columns:
        df = df.filter(F.col(required_col).isNotNull())

    if timestamp_col:
        df = df.filter(F.col(timestamp_col).isNotNull())

    # Standardize action if present.
    if "action" in df.columns:
        df = df.withColumn("action", F.lower(F.trim(F.col("action"))))

    # Standardize risk level if present.
    if "risk_level" in df.columns:
        df = df.withColumn("risk_level", F.upper(F.trim(F.col("risk_level"))))

    if "event_id" in df.columns:
        before_dedup = df.count()
        df = df.dropDuplicates(["event_id"])
        after_dedup = df.count()
        duplicate_count = before_dedup - after_dedup
    else:
        before_dedup = df.count()
        df = df.dropDuplicates()
        after_dedup = df.count()
        duplicate_count = before_dedup - after_dedup

    add_bad_record_summary(
        summary_rows,
        dataset_name,
        "duplicate_records_removed",
        duplicate_count,
    )

    silver_df = (
        df
        .withColumn("_silver_load_timestamp", F.current_timestamp())
        .withColumn("_silver_load_date", F.current_date())
    )

    write_delta_table(silver_df, silver_table, silver_path)

    final_count = spark.table(f"{DATABASE_NAME}.{silver_table}").count()

    print(f"Admin events silver processing complete.")
    print(f"Original bronze rows: {original_count}")
    print(f"Final silver rows: {final_count}")
    print("-" * 80)


# ------------------------------------------------------------
# Run all silver processing jobs
# ------------------------------------------------------------

bad_record_summary_rows = []

process_orders(bad_record_summary_rows)
process_security_logs(bad_record_summary_rows)
process_admin_events(bad_record_summary_rows)


# ------------------------------------------------------------
# Create bad records summary table
# ------------------------------------------------------------

bad_records_summary_df = spark.createDataFrame(
    bad_record_summary_rows,
    [
        "dataset_name",
        "rule_failed",
        "bad_record_count",
    ],
)

bad_records_summary_df = (
    bad_records_summary_df
    .withColumn("summary_created_at", F.current_timestamp())
    .withColumn("summary_created_date", F.current_date())
)

write_delta_table(
    bad_records_summary_df,
    "bad_records_summary",
    BAD_RECORDS_BASE_PATH,
)


# ------------------------------------------------------------
# Display final validation summary
# ------------------------------------------------------------

final_summary_rows = [
    (
        "orders",
        "bronze_orders",
        spark.table(f"{DATABASE_NAME}.bronze_orders").count(),
        "silver_orders",
        spark.table(f"{DATABASE_NAME}.silver_orders").count(),
    ),
    (
        "security_logs",
        "bronze_security_logs",
        spark.table(f"{DATABASE_NAME}.bronze_security_logs").count(),
        "silver_security_logs",
        spark.table(f"{DATABASE_NAME}.silver_security_logs").count(),
    ),
    (
        "admin_events",
        "bronze_admin_events",
        spark.table(f"{DATABASE_NAME}.bronze_admin_events").count(),
        "silver_admin_events",
        spark.table(f"{DATABASE_NAME}.silver_admin_events").count(),
    ),
]

final_summary_df = spark.createDataFrame(
    final_summary_rows,
    [
        "dataset_name",
        "bronze_table",
        "bronze_count",
        "silver_table",
        "silver_count",
    ],
)

display(final_summary_df)

display(spark.table(f"{DATABASE_NAME}.bad_records_summary"))