# Databricks notebook source
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
# - workspace.opsintel_copilot.bronze_orders
# - workspace.opsintel_copilot.bronze_security_logs
# - workspace.opsintel_copilot.bronze_admin_events
# - workspace.opsintel_copilot.bronze_pipeline_logs
#
# Outputs:
# - workspace.opsintel_copilot.silver_orders
# - workspace.opsintel_copilot.silver_security_logs
# - workspace.opsintel_copilot.silver_admin_events
# - workspace.opsintel_copilot.silver_pipeline_logs
# - workspace.opsintel_copilot.bad_records_summary
# ============================================================

from pyspark.sql import functions as F


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

S3_BUCKET = "opsintel-copilot-angad-0025"
BASE_PATH = f"s3://{S3_BUCKET}"

SILVER_BASE_PATH = f"{BASE_PATH}/silver"
BAD_RECORDS_BASE_PATH = f"{SILVER_BASE_PATH}/bad_records_summary"

CATALOG_NAME = "workspace"
SCHEMA_NAME = "opsintel_copilot"


# ------------------------------------------------------------
# Use Unity Catalog catalog and schema
# ------------------------------------------------------------

spark.sql(f"USE CATALOG {CATALOG_NAME}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}")
spark.sql(f"USE SCHEMA {SCHEMA_NAME}")


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def full_table_name(table_name: str) -> str:
    return f"{CATALOG_NAME}.{SCHEMA_NAME}.{table_name}"


def table_exists(table_name: str) -> bool:
    return spark.catalog.tableExists(full_table_name(table_name))


def clean_column_names(df):
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
    table_full_name = full_table_name(table_name)

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .save(output_path)
    )

    spark.sql(f"DROP TABLE IF EXISTS {table_full_name}")

    spark.sql(f"""
        CREATE TABLE {table_full_name}
        USING DELTA
        LOCATION '{output_path}'
    """)


def add_bad_record_summary(summary_rows, dataset_name: str, rule_failed: str, bad_count: int):
    summary_rows.append(
        (
            dataset_name,
            rule_failed,
            int(bad_count),
        )
    )


def find_timestamp_column(df, candidates):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


# ------------------------------------------------------------
# Silver processing: Orders
# ------------------------------------------------------------

def process_orders(summary_rows):
    dataset_name = "orders"
    bronze_table = "bronze_orders"
    silver_table = "silver_orders"
    silver_path = f"{SILVER_BASE_PATH}/orders/"

    if not table_exists(bronze_table):
        raise ValueError(f"Missing required table: {full_table_name(bronze_table)}")

    df = spark.table(full_table_name(bronze_table))
    df = clean_column_names(df)

    original_count = df.count()

    timestamp_col = find_timestamp_column(
        df,
        [
            "created_at",
            "order_timestamp",
            "event_timestamp",
            "timestamp",
            "order_time",
        ],
    )

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

    for required_col in required_columns:
        df = df.filter(F.col(required_col).isNotNull())

    if timestamp_col:
        df = df.filter(F.col(timestamp_col).isNotNull())

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

    if "order_status" in df.columns:
        df = df.withColumn("order_status", F.lower(F.trim(F.col("order_status"))))

    if "currency" in df.columns:
        df = df.withColumn("currency", F.upper(F.trim(F.col("currency"))))

    if "region" in df.columns:
        df = df.withColumn("region", F.lower(F.trim(F.col("region"))))

    silver_df = (
        df
        .withColumn("_silver_load_timestamp", F.current_timestamp())
        .withColumn("_silver_load_date", F.current_date())
    )

    write_delta_table(silver_df, silver_table, silver_path)

    final_count = spark.table(full_table_name(silver_table)).count()

    print("Orders silver processing complete.")
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
        raise ValueError(f"Missing required table: {full_table_name(bronze_table)}")

    df = spark.table(full_table_name(bronze_table))
    df = clean_column_names(df)

    original_count = df.count()

    timestamp_col = find_timestamp_column(
        df,
        [
            "event_time",
            "event_timestamp",
            "timestamp",
            "login_timestamp",
            "created_at",
        ],
    )

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

    for candidate in ["event_id", "user_id", "user_email", "source_ip"]:
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

    if "event_type" in df.columns:
        df = df.withColumn("event_type", F.lower(F.trim(F.col("event_type"))))

    if "region" in df.columns:
        df = df.withColumn("region", F.lower(F.trim(F.col("region"))))

    if "success" in df.columns:
        df = df.withColumn("success", F.col("success").cast("boolean"))

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

    final_count = spark.table(full_table_name(silver_table)).count()

    print("Security logs silver processing complete.")
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
        raise ValueError(f"Missing required table: {full_table_name(bronze_table)}")

    df = spark.table(full_table_name(bronze_table))
    df = clean_column_names(df)

    original_count = df.count()

    timestamp_col = find_timestamp_column(
        df,
        [
            "event_time",
            "event_timestamp",
            "admin_event_timestamp",
            "timestamp",
            "created_at",
        ],
    )

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

    for candidate in ["admin_event_id", "event_id", "admin_user", "action"]:
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

    if "action" in df.columns:
        df = df.withColumn("action", F.lower(F.trim(F.col("action"))))

    if "target_service" in df.columns:
        df = df.withColumn("target_service", F.lower(F.trim(F.col("target_service"))))

    if "region" in df.columns:
        df = df.withColumn("region", F.lower(F.trim(F.col("region"))))

    dedup_key = None

    if "admin_event_id" in df.columns:
        dedup_key = "admin_event_id"
    elif "event_id" in df.columns:
        dedup_key = "event_id"

    if dedup_key:
        before_dedup = df.count()
        df = df.dropDuplicates([dedup_key])
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

    final_count = spark.table(full_table_name(silver_table)).count()

    print("Admin events silver processing complete.")
    print(f"Original bronze rows: {original_count}")
    print(f"Final silver rows: {final_count}")
    print("-" * 80)


# ------------------------------------------------------------
# Silver processing: Pipeline Logs
# ------------------------------------------------------------

def process_pipeline_logs(summary_rows):
    dataset_name = "pipeline_logs"
    bronze_table = "bronze_pipeline_logs"
    silver_table = "silver_pipeline_logs"
    silver_path = f"{SILVER_BASE_PATH}/pipeline_logs/"

    if not table_exists(bronze_table):
        raise ValueError(f"Missing required table: {full_table_name(bronze_table)}")

    df = spark.table(full_table_name(bronze_table))
    df = clean_column_names(df)

    original_count = df.count()

    # Convert start_time to timestamp (primary event time)
    if "start_time" in df.columns:
        df = df.withColumn("start_time", F.to_timestamp(F.col("start_time")))
        invalid_start_count = df.filter(F.col("start_time").isNull()).count()
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "invalid_or_missing_start_time",
            invalid_start_count,
        )
    else:
        add_bad_record_summary(
            summary_rows,
            dataset_name,
            "missing_start_time_column",
            original_count,
        )

    # Convert end_time to timestamp as well
    if "end_time" in df.columns:
        df = df.withColumn("end_time", F.to_timestamp(F.col("end_time")))

    # Check required columns
    required_columns = []

    for candidate in ["run_id", "pipeline_name"]:
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

    if "start_time" in df.columns:
        df = df.filter(F.col("start_time").isNotNull())

    # Deduplicate on run_id
    if "run_id" in df.columns:
        before_dedup = df.count()
        df = df.dropDuplicates(["run_id"])
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

    # Standardise string columns
    if "status" in df.columns:
        df = df.withColumn("status", F.lower(F.trim(F.col("status"))))

    if "pipeline_name" in df.columns:
        df = df.withColumn("pipeline_name", F.lower(F.trim(F.col("pipeline_name"))))

    if "region" in df.columns:
        df = df.withColumn("region", F.lower(F.trim(F.col("region"))))

    if "trigger_type" in df.columns:
        df = df.withColumn("trigger_type", F.lower(F.trim(F.col("trigger_type"))))

    if "error_message" in df.columns:
        df = df.withColumn("error_message", F.lower(F.trim(F.col("error_message"))))

    # Cast numeric columns to correct types
    if "duration_seconds" in df.columns:
        df = df.withColumn("duration_seconds", F.col("duration_seconds").cast("integer"))

    if "records_processed" in df.columns:
        df = df.withColumn("records_processed", F.col("records_processed").cast("integer"))

    silver_df = (
        df
        .withColumn("_silver_load_timestamp", F.current_timestamp())
        .withColumn("_silver_load_date", F.current_date())
    )

    write_delta_table(silver_df, silver_table, silver_path)

    final_count = spark.table(full_table_name(silver_table)).count()

    print("Pipeline logs silver processing complete.")
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
process_pipeline_logs(bad_record_summary_rows)


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
        full_table_name("bronze_orders"),
        spark.table(full_table_name("bronze_orders")).count(),
        full_table_name("silver_orders"),
        spark.table(full_table_name("silver_orders")).count(),
    ),
    (
        "security_logs",
        full_table_name("bronze_security_logs"),
        spark.table(full_table_name("bronze_security_logs")).count(),
        full_table_name("silver_security_logs"),
        spark.table(full_table_name("silver_security_logs")).count(),
    ),
    (
        "admin_events",
        full_table_name("bronze_admin_events"),
        spark.table(full_table_name("bronze_admin_events")).count(),
        full_table_name("silver_admin_events"),
        spark.table(full_table_name("silver_admin_events")).count(),
    ),
    (
        "pipeline_logs",
        full_table_name("bronze_pipeline_logs"),
        spark.table(full_table_name("bronze_pipeline_logs")).count(),
        full_table_name("silver_pipeline_logs"),
        spark.table(full_table_name("silver_pipeline_logs")).count(),
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

display(spark.table(full_table_name("bad_records_summary")))
