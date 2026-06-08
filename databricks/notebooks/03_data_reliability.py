# Databricks notebook source
# Databricks notebook source
# ============================================================
# OpsIntel Copilot
# Week 4 — Data Reliability Module
#
# Purpose:
# Read silver Delta tables, run 10 data reliability checks,
# generate gold quality results, enriched pipeline run summaries,
# incident events for the correlation engine, and RAG doc summaries.
#
# Inputs:
# - workspace.opsintel_copilot.silver_orders
# - workspace.opsintel_copilot.silver_pipeline_logs
#
# Outputs:
# - workspace.opsintel_copilot.gold_data_quality_results
# - workspace.opsintel_copilot.gold_pipeline_runs
# - workspace.opsintel_copilot.incident_events
# - s3://opsintel-copilot-angad-0025/rag-docs/quality/
# ============================================================

from pyspark.sql import functions as F
import json
from datetime import datetime


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

S3_BUCKET = "opsintel-copilot-angad-0025"
BASE_PATH = f"s3://{S3_BUCKET}"
GOLD_BASE_PATH = f"{BASE_PATH}/gold"
RAG_DOCS_QUALITY_PATH = f"{BASE_PATH}/rag-docs/quality"

CATALOG_NAME = "workspace"
SCHEMA_NAME = "opsintel_copilot"

# Reliability thresholds
NEGATIVE_AMOUNT_THRESHOLD       = 50     # fail if more than 50 negative records
BAD_RECORD_RATIO_THRESHOLD      = 0.05   # fail if more than 5% bad records
PIPELINE_FAILURE_RATE_THRESHOLD = 0.15   # fail if more than 15% failure rate
ROW_ANOMALY_THRESHOLD           = 100    # fail if more than 100 anomalous runs
FRESHNESS_GAP_THRESHOLD_HOURS   = 6.0   # fail if pipeline gap > 6 hours

VALID_CURRENCIES = ["USD", "EUR", "GBP", "INR"]


# ------------------------------------------------------------
# Use Unity Catalog catalog and schema
# ------------------------------------------------------------

spark.sql(f"USE CATALOG {CATALOG_NAME}")
spark.sql(f"USE SCHEMA {SCHEMA_NAME}")


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def full_table_name(table_name: str) -> str:
    return f"{CATALOG_NAME}.{SCHEMA_NAME}.{table_name}"


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


def add_quality_check(
    results: list,
    dataset_name: str,
    check_name: str,
    status: str,
    observed_value: float,
    threshold: float,
    bad_record_count: int,
    severity: str,
    details: str,
) -> None:
    results.append((
        dataset_name,
        check_name,
        status,
        float(observed_value),
        float(threshold),
        int(bad_record_count),
        severity,
        str(details),
    ))


# ------------------------------------------------------------
# Load silver tables
# ------------------------------------------------------------

print("Loading silver tables...")

silver_orders_df       = spark.table(full_table_name("silver_orders"))
silver_pipeline_df     = spark.table(full_table_name("silver_pipeline_logs"))

total_orders           = silver_orders_df.count()
total_pipeline_runs    = silver_pipeline_df.count()

print(f"silver_orders:        {total_orders:,} rows")
print(f"silver_pipeline_logs: {total_pipeline_runs:,} rows")
print("-" * 80)


# ============================================================
# ORDERS RELIABILITY CHECKS
# ============================================================

quality_check_results = []

# ------------------------------------------------------------
# Check 1: Negative Amount
# Orders where the price is below zero
# ------------------------------------------------------------

print("Check 1/10: negative_amount...")

negative_count = silver_orders_df.filter(F.col("amount") < 0).count()
negative_ratio = negative_count / total_orders if total_orders > 0 else 0.0

if negative_count > NEGATIVE_AMOUNT_THRESHOLD:
    neg_status   = "fail"
    neg_severity = "high"
elif negative_count > 0:
    neg_status   = "warn"
    neg_severity = "medium"
else:
    neg_status   = "pass"
    neg_severity = "none"

add_quality_check(
    quality_check_results, "orders", "negative_amount",
    neg_status, round(negative_ratio, 6), 0.0,
    negative_count, neg_severity,
    f"{negative_count:,} orders have a negative amount value ({negative_ratio:.2%} of total orders)",
)

print(f"  → {neg_status.upper()} | {negative_count:,} records")


# ------------------------------------------------------------
# Check 2: Invalid Currency
# Orders with a currency outside the known valid list
# ------------------------------------------------------------

print("Check 2/10: invalid_currency...")

invalid_currency_count = silver_orders_df.filter(
    ~F.col("currency").isin(VALID_CURRENCIES)
).count()

if invalid_currency_count > 0:
    curr_status   = "fail"
    curr_severity = "high"
else:
    curr_status   = "pass"
    curr_severity = "none"

add_quality_check(
    quality_check_results, "orders", "invalid_currency",
    curr_status, float(invalid_currency_count), 0.0,
    invalid_currency_count, curr_severity,
    f"{invalid_currency_count:,} orders have a currency not in {VALID_CURRENCIES}",
)

print(f"  → {curr_status.upper()} | {invalid_currency_count:,} records")


# ------------------------------------------------------------
# Check 3: Null Spike — Amount
# Unexpected rise in null values in the amount column
# ------------------------------------------------------------

print("Check 3/10: null_spike_amount...")

null_amount_count = silver_orders_df.filter(F.col("amount").isNull()).count()
null_amount_ratio = null_amount_count / total_orders if total_orders > 0 else 0.0

if null_amount_ratio > 0.05:
    na_status   = "fail"
    na_severity = "critical"
elif null_amount_ratio > 0.01:
    na_status   = "warn"
    na_severity = "medium"
elif null_amount_count > 0:
    na_status   = "warn"
    na_severity = "low"
else:
    na_status   = "pass"
    na_severity = "none"

add_quality_check(
    quality_check_results, "orders", "null_spike_amount",
    na_status, round(null_amount_ratio, 6), 0.01,
    null_amount_count, na_severity,
    f"{null_amount_count:,} orders have a null amount value ({null_amount_ratio:.2%} of total orders)",
)

print(f"  → {na_status.upper()} | {null_amount_count:,} records")


# ------------------------------------------------------------
# Check 4: Duplicate Records
# Same order_id appearing more than once after silver dedup
# ------------------------------------------------------------

print("Check 4/10: duplicate_records...")

distinct_order_ids = silver_orders_df.select("order_id").distinct().count()
dup_count          = total_orders - distinct_order_ids
dup_ratio          = dup_count / total_orders if total_orders > 0 else 0.0

if dup_ratio > 0.01:
    dup_status   = "fail"
    dup_severity = "high"
elif dup_count > 0:
    dup_status   = "warn"
    dup_severity = "medium"
else:
    dup_status   = "pass"
    dup_severity = "none"

add_quality_check(
    quality_check_results, "orders", "duplicate_records",
    dup_status, round(dup_ratio, 6), 0.01,
    dup_count, dup_severity,
    f"{dup_count:,} duplicate order_id records found ({dup_ratio:.2%} of total orders)",
)

print(f"  → {dup_status.upper()} | {dup_count:,} duplicates")


# ------------------------------------------------------------
# Check 5: Bad Record Ratio
# Overall percentage of problematic records across all checks
# ------------------------------------------------------------

print("Check 5/10: bad_record_ratio...")

total_bad_orders = negative_count + invalid_currency_count + null_amount_count
bad_ratio        = total_bad_orders / total_orders if total_orders > 0 else 0.0

if bad_ratio > BAD_RECORD_RATIO_THRESHOLD:
    bad_status   = "fail"
    bad_severity = "high"
elif bad_ratio > 0.01:
    bad_status   = "warn"
    bad_severity = "medium"
elif total_bad_orders > 0:
    bad_status   = "warn"
    bad_severity = "low"
else:
    bad_status   = "pass"
    bad_severity = "none"

add_quality_check(
    quality_check_results, "orders", "bad_record_ratio",
    bad_status, round(bad_ratio, 6), BAD_RECORD_RATIO_THRESHOLD,
    total_bad_orders, bad_severity,
    f"{total_bad_orders:,} total bad records across all orders checks ({bad_ratio:.2%} of total orders)",
)

print(f"  → {bad_status.upper()} | {total_bad_orders:,} bad records")
print("-" * 80)


# ============================================================
# PIPELINE RELIABILITY CHECKS
# ============================================================

# ------------------------------------------------------------
# Check 6: Pipeline Failure Rate
# What percentage of all pipeline runs ended in failure
# ------------------------------------------------------------

print("Check 6/10: pipeline_failure_rate...")

failed_runs  = silver_pipeline_df.filter(F.col("status") == "failed").count()
failure_rate = failed_runs / total_pipeline_runs if total_pipeline_runs > 0 else 0.0

if failure_rate > PIPELINE_FAILURE_RATE_THRESHOLD:
    pfr_status   = "fail"
    pfr_severity = "critical"
elif failure_rate > 0.05:
    pfr_status   = "warn"
    pfr_severity = "high"
else:
    pfr_status   = "pass"
    pfr_severity = "none"

add_quality_check(
    quality_check_results, "pipeline_logs", "pipeline_failure_rate",
    pfr_status, round(failure_rate, 6), PIPELINE_FAILURE_RATE_THRESHOLD,
    failed_runs, pfr_severity,
    f"{failed_runs:,} pipeline runs failed ({failure_rate:.2%} failure rate across all pipelines)",
)

print(f"  → {pfr_status.upper()} | {failed_runs:,} failed runs")


# ------------------------------------------------------------
# Check 7: Row Count Anomaly
# Pipeline runs explicitly flagged with row count problems
# ------------------------------------------------------------

print("Check 7/10: row_count_anomaly...")

row_anomaly_count = silver_pipeline_df.filter(
    F.col("error_message") == "row_count_anomaly_detected"
).count()

if row_anomaly_count > ROW_ANOMALY_THRESHOLD:
    rca_status   = "fail"
    rca_severity = "high"
elif row_anomaly_count > 0:
    rca_status   = "warn"
    rca_severity = "medium"
else:
    rca_status   = "pass"
    rca_severity = "none"

add_quality_check(
    quality_check_results, "pipeline_logs", "row_count_anomaly",
    rca_status, float(row_anomaly_count), float(ROW_ANOMALY_THRESHOLD),
    row_anomaly_count, rca_severity,
    f"{row_anomaly_count:,} pipeline runs reported row_count_anomaly_detected",
)

print(f"  → {rca_status.upper()} | {row_anomaly_count:,} runs")


# ------------------------------------------------------------
# Check 8: Null Spike in Pipeline Runs
# Runs that reported null spike errors in processed data
# ------------------------------------------------------------

print("Check 8/10: null_spike_pipeline...")

null_spike_runs = silver_pipeline_df.filter(
    F.col("error_message").isin([
        "null_spike_detected",
        "minor_null_spike_detected",
    ])
).count()

if null_spike_runs > ROW_ANOMALY_THRESHOLD:
    nsp_status   = "fail"
    nsp_severity = "high"
elif null_spike_runs > 0:
    nsp_status   = "warn"
    nsp_severity = "medium"
else:
    nsp_status   = "pass"
    nsp_severity = "none"

add_quality_check(
    quality_check_results, "pipeline_logs", "null_spike_pipeline",
    nsp_status, float(null_spike_runs), float(ROW_ANOMALY_THRESHOLD),
    null_spike_runs, nsp_severity,
    f"{null_spike_runs:,} pipeline runs reported null spike errors in processed data",
)

print(f"  → {nsp_status.upper()} | {null_spike_runs:,} runs")


# ------------------------------------------------------------
# Check 9: Schema Drift
# Runs flagged with schema errors + expected columns missing
# from silver tables themselves
# ------------------------------------------------------------

print("Check 9/10: schema_drift...")

schema_drift_runs = silver_pipeline_df.filter(
    F.col("error_message").isin([
        "schema_mismatch_detected",
        "missing_required_column",
    ])
).count()

expected_orders_cols   = ["order_id", "customer_id", "amount", "currency", "order_status", "region", "created_at"]
expected_pipeline_cols = ["run_id", "pipeline_name", "status", "start_time", "end_time", "duration_seconds", "records_processed"]

missing_orders_cols   = [c for c in expected_orders_cols   if c not in silver_orders_df.columns]
missing_pipeline_cols = [c for c in expected_pipeline_cols if c not in silver_pipeline_df.columns]

total_schema_issues = schema_drift_runs + len(missing_orders_cols) + len(missing_pipeline_cols)

if len(missing_orders_cols) > 0 or len(missing_pipeline_cols) > 0:
    sd_status   = "fail"
    sd_severity = "critical"
elif schema_drift_runs > 50:
    sd_status   = "fail"
    sd_severity = "high"
elif schema_drift_runs > 0:
    sd_status   = "warn"
    sd_severity = "medium"
else:
    sd_status   = "pass"
    sd_severity = "none"

add_quality_check(
    quality_check_results, "pipeline_logs", "schema_drift",
    sd_status, float(total_schema_issues), 0.0,
    schema_drift_runs, sd_severity,
    (
        f"{schema_drift_runs:,} runs flagged schema errors. "
        f"Missing orders cols: {missing_orders_cols or 'none'}. "
        f"Missing pipeline cols: {missing_pipeline_cols or 'none'}."
    ),
)

print(f"  → {sd_status.upper()} | {total_schema_issues} total schema issues")


# ------------------------------------------------------------
# Check 10: Freshness Failure
# Use the latest timestamp in the data as reference 'now',
# then check how long since each pipeline last ran.
# This avoids false positives from frozen synthetic data.
# ------------------------------------------------------------

print("Check 10/10: freshness_failure...")

reference_now_row = silver_pipeline_df.agg(
    F.max("start_time").alias("max_time")
).collect()[0]

reference_now     = reference_now_row["max_time"]
reference_now_str = reference_now.strftime("%Y-%m-%d %H:%M:%S")

print(f"  Reference 'now' = {reference_now_str} (max timestamp in dataset)")

latest_per_pipeline = (
    silver_pipeline_df
    .groupBy("pipeline_name")
    .agg(F.max("start_time").alias("latest_run_time"))
    .withColumn(
        "hours_since_last_run",
        (
            F.unix_timestamp(F.lit(reference_now_str)) -
            F.unix_timestamp(F.col("latest_run_time"))
        ) / 3600.0,
    )
)

stale_pipeline_count = latest_per_pipeline.filter(
    F.col("hours_since_last_run") > FRESHNESS_GAP_THRESHOLD_HOURS
).count()

if stale_pipeline_count > 0:
    fresh_status   = "fail"
    fresh_severity = "high"
else:
    fresh_status   = "pass"
    fresh_severity = "none"

add_quality_check(
    quality_check_results, "pipeline_logs", "freshness_failure",
    fresh_status, float(stale_pipeline_count), 0.0,
    stale_pipeline_count, fresh_severity,
    (
        f"{stale_pipeline_count} pipeline(s) have not run within "
        f"{FRESHNESS_GAP_THRESHOLD_HOURS}h of the latest data point "
        f"(reference: {reference_now_str})"
    ),
)

print(f"  → {fresh_status.upper()} | {stale_pipeline_count} stale pipelines")
print("-" * 80)


# ============================================================
# GOLD TABLE 1: gold_data_quality_results
# One row per check — the main quality findings table
# ============================================================

print("Building gold_data_quality_results...")

quality_results_df = spark.createDataFrame(
    quality_check_results,
    [
        "dataset_name",
        "check_name",
        "status",
        "observed_value",
        "threshold",
        "bad_record_count",
        "severity",
        "details",
    ],
)

quality_results_df = (
    quality_results_df
    .withColumn("result_id",      F.expr("uuid()"))
    .withColumn("run_timestamp",  F.current_timestamp())
    .withColumn("run_date",       F.current_date())
)

write_delta_table(
    quality_results_df,
    "gold_data_quality_results",
    f"{GOLD_BASE_PATH}/data_quality_results/",
)

print(f"gold_data_quality_results: {quality_results_df.count()} rows written")
print("-" * 80)


# ============================================================
# GOLD TABLE 2: gold_pipeline_runs
# Every pipeline run enriched with reliability flags and scores
# ============================================================

print("Building gold_pipeline_runs...")

# Compute per-pipeline statistics (used for is_slow flag)
pipeline_stats_df = silver_pipeline_df.groupBy("pipeline_name").agg(
    F.round(F.avg("duration_seconds"),   1).alias("avg_duration_seconds"),
    F.round(F.percentile_approx("duration_seconds", 0.9), 1).alias("p90_duration_seconds"),
    F.round(F.avg("records_processed"),  0).alias("avg_records_processed"),
    F.count("*").alias("total_runs_per_pipeline"),
    F.sum(F.when(F.col("status") == "failed", 1).otherwise(0)).alias("failed_runs_per_pipeline"),
)

# Join stats back to every run row
gold_pipeline_runs_df = silver_pipeline_df.join(
    pipeline_stats_df,
    on="pipeline_name",
    how="left",
)

# Add reliability flags
gold_pipeline_runs_df = (
    gold_pipeline_runs_df
    .withColumn("is_failed",
        F.col("status") == F.lit("failed"))
    .withColumn("is_warning",
        F.col("status") == F.lit("warning"))
    .withColumn("is_slow",
        F.col("duration_seconds") > F.col("p90_duration_seconds"))
    .withColumn("is_row_count_anomaly",
        F.col("error_message") == F.lit("row_count_anomaly_detected"))
    .withColumn("is_null_spike",
        F.col("error_message").isin(["null_spike_detected", "minor_null_spike_detected"]))
    .withColumn("is_schema_drift",
        F.col("error_message").isin(["schema_mismatch_detected", "missing_required_column"]))
    .withColumn(
        "reliability_score",
        F.greatest(
            F.lit(0),
            F.lit(100)
            - F.when(F.col("is_failed"),            F.lit(50)).otherwise(F.lit(0))
            - F.when(F.col("is_warning"),           F.lit(10)).otherwise(F.lit(0))
            - F.when(F.col("is_slow"),              F.lit(15)).otherwise(F.lit(0))
            - F.when(F.col("is_row_count_anomaly"), F.lit(15)).otherwise(F.lit(0))
            - F.when(F.col("is_null_spike"),        F.lit(15)).otherwise(F.lit(0))
            - F.when(F.col("is_schema_drift"),      F.lit(25)).otherwise(F.lit(0))
        ),
    )
    .withColumn("_gold_load_timestamp", F.current_timestamp())
    .withColumn("_gold_load_date",      F.current_date())
)

write_delta_table(
    gold_pipeline_runs_df,
    "gold_pipeline_runs",
    f"{GOLD_BASE_PATH}/pipeline_runs/",
)

total_gold_runs = spark.table(full_table_name("gold_pipeline_runs")).count()
print(f"gold_pipeline_runs: {total_gold_runs:,} rows written")
print("-" * 80)


# ============================================================
# GOLD TABLE 3: incident_events
# The shared event diary — week 5 (security) appends to this
# same table so the week 6 correlation engine can join them.
# ============================================================

print("Building incident_events...")

# Source A: one event per failed or warning pipeline run
# These have real timestamps — perfect for time-window correlation
pipeline_incident_df = (
    gold_pipeline_runs_df
    .filter(F.col("is_failed") | F.col("is_warning"))
    .select(
        F.expr("uuid()").alias("event_id"),
        F.col("start_time").alias("event_time"),
        F.lit("data_reliability").alias("source"),
        F.when(
            F.col("is_failed"),
            F.concat(F.lit("pipeline_"), F.col("error_message")),
        ).otherwise(F.lit("pipeline_warning")).alias("event_type"),
        F.col("pipeline_name").alias("entity"),
        F.when(F.col("is_schema_drift"), F.lit("critical"))
         .when(F.col("is_failed"),       F.lit("high"))
         .otherwise(                     F.lit("medium")).alias("severity"),
        F.concat(
            F.lit("Pipeline "),
            F.col("pipeline_name"),
            F.lit(" | status: "),
            F.col("status"),
            F.lit(" | error: "),
            F.col("error_message"),
            F.lit(" | duration: "),
            F.col("duration_seconds").cast("string"),
            F.lit("s | records_processed: "),
            F.col("records_processed").cast("string"),
        ).alias("description"),
        F.to_json(F.struct(
            F.col("run_id"),
            F.col("pipeline_name"),
            F.col("status"),
            F.col("start_time"),
            F.col("end_time"),
            F.col("duration_seconds"),
            F.col("records_processed"),
            F.col("error_message"),
            F.col("trigger_type"),
            F.col("is_slow"),
            F.col("is_row_count_anomaly"),
            F.col("reliability_score"),
        )).alias("evidence"),
        F.current_timestamp().alias("created_at"),
    )
)

# Source B: one event per quality check that failed or warned
quality_incident_df = (
    quality_results_df
    .filter(F.col("status").isin(["fail", "warn"]))
    .select(
        F.expr("uuid()").alias("event_id"),
        F.col("run_timestamp").alias("event_time"),
        F.lit("data_reliability").alias("source"),
        F.col("check_name").alias("event_type"),
        F.col("dataset_name").alias("entity"),
        F.col("severity"),
        F.col("details").alias("description"),
        F.to_json(F.struct(
            F.col("check_name"),
            F.col("dataset_name"),
            F.col("status"),
            F.col("observed_value"),
            F.col("threshold"),
            F.col("bad_record_count"),
        )).alias("evidence"),
        F.current_timestamp().alias("created_at"),
    )
)

# Union both sources into the shared incident diary
incident_events_df = pipeline_incident_df.unionByName(quality_incident_df)

write_delta_table(
    incident_events_df,
    "incident_events",
    f"{GOLD_BASE_PATH}/incident_events/",
)

total_incidents = spark.table(full_table_name("incident_events")).count()
print(f"incident_events: {total_incidents:,} rows written")
print("-" * 80)


# ============================================================
# RAG DOCS SUMMARY
# Write a JSON summary to S3 so Bedrock can read it later
# ============================================================

print("Writing RAG docs quality summary to S3...")

passed_checks = sum(1 for r in quality_check_results if r[2] == "pass")
warned_checks = sum(1 for r in quality_check_results if r[2] == "warn")
failed_checks = sum(1 for r in quality_check_results if r[2] == "fail")

key_findings = [
    r[7] for r in quality_check_results if r[2] in ("fail", "warn")
]

pipeline_stats_rows = (
    silver_pipeline_df
    .groupBy("pipeline_name")
    .agg(
        F.count("*").alias("total_runs"),
        F.sum(F.when(F.col("status") == "failed", 1).otherwise(0)).alias("failed_runs"),
    )
    .withColumn("failure_rate", F.round(F.col("failed_runs") / F.col("total_runs"), 4))
    .orderBy(F.col("failure_rate").desc())
    .collect()
)

pipeline_failure_rates = {
    row["pipeline_name"]: float(row["failure_rate"])
    for row in pipeline_stats_rows
}

summary_data = {
    "summary_type": "data_quality_summary",
    "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "data_reference_date": reference_now_str,
    "datasets_checked": ["orders", "pipeline_logs"],
    "checks_summary": {
        "total_checks": len(quality_check_results),
        "passed": passed_checks,
        "warned": warned_checks,
        "failed": failed_checks,
    },
    "key_findings": key_findings,
    "pipeline_failure_rates_by_pipeline": pipeline_failure_rates,
    "incident_events_generated": total_incidents,
    "recommended_actions": [
        "Investigate the source of negative amount orders — check pricing logic in checkout-service.",
        "Review failed pipeline runs and cluster for recurring error_message patterns.",
        "Run the correlation engine to check if pipeline failures coincide with suspicious admin changes.",
        "Monitor pipelines approaching the freshness gap threshold.",
    ],
}

summary_date  = datetime.now().strftime("%Y-%m-%d")
rag_doc_path  = f"{RAG_DOCS_QUALITY_PATH}/data_quality_summary_{summary_date}.json"

dbutils.fs.put(
    rag_doc_path,
    json.dumps(summary_data, indent=2),
    overwrite=True,
)

print(f"RAG summary written to: {rag_doc_path}")
print("-" * 80)


# ============================================================
# VALIDATION — display final outputs
# ============================================================

print("Week 4 complete. Displaying output summaries...")
print("=" * 80)

# All quality check results
display(
    spark.table(full_table_name("gold_data_quality_results"))
    .select("dataset_name", "check_name", "status", "severity", "bad_record_count", "observed_value", "details")
    .orderBy("dataset_name", "check_name")
)

# Pipeline run summary by pipeline and status
display(
    spark.table(full_table_name("gold_pipeline_runs"))
    .groupBy("pipeline_name", "status")
    .agg(
        F.count("*").alias("run_count"),
        F.round(F.avg("reliability_score"), 1).alias("avg_reliability_score"),
        F.sum(F.when(F.col("is_slow"),              F.lit(1)).otherwise(F.lit(0))).alias("slow_runs"),
        F.sum(F.when(F.col("is_row_count_anomaly"), F.lit(1)).otherwise(F.lit(0))).alias("row_anomaly_runs"),
    )
    .orderBy("pipeline_name", "status")
)

# Incident events summary
display(
    spark.table(full_table_name("incident_events"))
    .groupBy("source", "event_type", "severity")
    .agg(F.count("*").alias("event_count"))
    .orderBy(F.col("event_count").desc())
)