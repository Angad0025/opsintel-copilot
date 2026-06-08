# Data Reliability Module

## Overview

The Data Reliability Module is a PySpark-based quality engine built on Databricks that
reads cleaned silver Delta tables and runs automated checks to detect data problems
and pipeline failures. Findings are written to gold Delta tables and a shared incident
diary that the Correlation Engine (Week 6) uses to connect data failures with security events.

---

## Notebook

`databricks/notebooks/03_data_reliability.py`

---

## Inputs

| Table | Description |
|---|---|
| `workspace.opsintel_copilot.silver_orders` | 100,000 cleaned order records |
| `workspace.opsintel_copilot.silver_pipeline_logs` | 25,000 cleaned pipeline run records |

---

## The 10 Reliability Checks

### Orders Checks

| Check | What It Detects | Threshold |
|---|---|---|
| `negative_amount` | Orders where the price is below zero | > 50 records = FAIL |
| `invalid_currency` | Currency values outside USD, EUR, GBP, INR | Any = FAIL |
| `null_spike_amount` | Unexpected null values in the amount column | > 1% = WARN, > 5% = FAIL |
| `duplicate_records` | Same order_id appearing more than once | > 1% = FAIL |
| `bad_record_ratio` | Overall percentage of bad records across all checks | > 5% = FAIL |

### Pipeline Checks

| Check | What It Detects | Threshold |
|---|---|---|
| `pipeline_failure_rate` | Percentage of all pipeline runs that ended in failure | > 15% = FAIL |
| `row_count_anomaly` | Runs explicitly flagged with row count problems | > 100 = FAIL |
| `null_spike_pipeline` | Runs that reported null spike errors in processed data | > 100 = FAIL |
| `schema_drift` | Runs with schema errors and missing expected columns | Any missing col = FAIL |
| `freshness_failure` | Pipelines with a gap exceeding 6 hours from the latest data point | Any stale pipeline = FAIL |

The freshness check uses the latest timestamp in the dataset as a reference point
rather than the real clock. This avoids false positives when working with fixed
synthetic data and produces meaningful gap detection regardless of when the check runs.

---

## Outputs

### Gold Delta Tables

#### `gold_data_quality_results`

One row per check. The primary quality findings table.

| Column | Description |
|---|---|
| `result_id` | Unique UUID per check result |
| `dataset_name` | orders or pipeline_logs |
| `check_name` | Name of the check that ran |
| `status` | pass / warn / fail |
| `observed_value` | The actual measured value (ratio or count) |
| `threshold` | The threshold used to determine pass/warn/fail |
| `bad_record_count` | Number of records that failed the check |
| `severity` | none / low / medium / high / critical |
| `details` | Human-readable finding description |
| `run_timestamp` | When the check ran |

---

#### `gold_pipeline_runs`

Every pipeline run (25,000 rows) enriched with reliability flags and scores.

| Column | Description |
|---|---|
| `run_id` | Unique pipeline run identifier |
| `pipeline_name` | Name of the pipeline |
| `status` | success / failed / warning |
| `is_failed` | Boolean — run ended in failure |
| `is_warning` | Boolean — run ended with warnings |
| `is_slow` | Boolean — duration exceeded the pipeline's 90th percentile |
| `is_row_count_anomaly` | Boolean — run flagged row_count_anomaly_detected |
| `is_null_spike` | Boolean — run flagged null spike errors |
| `is_schema_drift` | Boolean — run flagged schema mismatch or missing column |
| `reliability_score` | 0–100 score. Penalties: failed (-50), slow (-15), null spike (-15), schema drift (-25) |
| `avg_duration_seconds` | Average duration for this pipeline across all runs |
| `p90_duration_seconds` | 90th percentile duration for this pipeline (slow threshold) |

---

#### `incident_events`

The shared incident diary. Both this module (Week 4) and the Security Intelligence
Module (Week 5) write into this same table so the Correlation Engine (Week 6) can
join reliability and security events on a time window.

| Column | Description |
|---|---|
| `event_id` | Unique UUID per event |
| `event_time` | Timestamp of the event (pipeline start_time for run events) |
| `source` | data_reliability (Week 4) or security (Week 5) |
| `event_type` | e.g. pipeline_failed, pipeline_warning, negative_amount |
| `entity` | The pipeline name or dataset that triggered the event |
| `severity` | low / medium / high / critical |
| `description` | Human-readable event description |
| `evidence` | JSON blob with full context (run_id, error_message, scores, etc.) |
| `created_at` | When the event was written |

Two types of events are written:
- **Per pipeline run** — one event per failed or warning run (carries a real timestamp for correlation)
- **Per quality check** — one event per failed or warned check (summary-level finding)

---

### S3 RAG Document

A JSON summary is written to S3 after every run so Amazon Bedrock Knowledge Bases
can answer natural-language questions about data quality findings.

**Location:** `s3://opsintel-copilot-angad-0025/rag-docs/quality/data_quality_summary_YYYY-MM-DD.json`

**Contents:** check summary counts, key findings, per-pipeline failure rates,
incident event count, and recommended remediation actions.

---

## Sample Findings (Week 4 Run)

| Check | Status | Finding |
|---|---|---|
| `negative_amount` | FAIL | 1,984 orders with negative prices (1.98% of total) |
| `bad_record_ratio` | WARN | 1,984 total bad records (1.98%) |
| `pipeline_failure_rate` | WARN | 2,529 failed runs (10.1% failure rate) |
| `null_spike_pipeline` | FAIL | 773 runs reported null spike errors |
| `row_count_anomaly` | FAIL | 257 runs flagged with row count anomaly |
| `schema_drift` | FAIL | 400 runs flagged with schema errors |
| `invalid_currency` | PASS | 0 invalid currencies found |
| `duplicate_records` | PASS | 0 duplicates found |
| `null_spike_amount` | PASS | 0 null amounts found |
| `freshness_failure` | PASS | All pipelines running within freshness threshold |

---

## How It Connects to the Rest of the Platform

```
silver_orders + silver_pipeline_logs
        ↓
03_data_reliability.py
        ↓
gold_data_quality_results  ← Dashboard reads this
gold_pipeline_runs         ← Dashboard reads this
incident_events            ← Correlation Engine reads this (Week 6)
S3 rag-docs/quality/       ← Bedrock Knowledge Base reads this (Week 7)
```

The `incident_events` table is the most important output for the platform's
investigation capability. Each failed pipeline run becomes a timestamped event.
When Week 5 adds security events to the same table, the Week 6 Correlation Engine
can ask: *did a suspicious admin login happen within 30 minutes of this pipeline failure?*