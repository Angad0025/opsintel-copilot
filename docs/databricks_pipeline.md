cat > docs/databricks_pipeline.md <<'EOF'
# Databricks Bronze and Silver Pipeline

## Overview

Week 3 of OpsIntel Copilot builds the Databricks lakehouse ingestion and cleaning layer.

The pipeline reads raw CSV datasets from the AWS S3 raw layer, converts them into Delta Lake bronze tables, applies data quality checks, and writes cleaned silver Delta tables back to S3.

## Pipeline Flow

```txt
AWS S3 Raw CSV Data
        ↓
Databricks Bronze Ingestion Notebook
        ↓
Bronze Delta Tables
        ↓
Databricks Silver Data Quality Notebook
        ↓
Silver Delta Tables
        ↓
Bad Records Summary
```

## Source Bucket

```txt
s3://opsintel-copilot-angad-0025/
```

## Raw Input Paths

```txt
s3://opsintel-copilot-angad-0025/raw/orders/
s3://opsintel-copilot-angad-0025/raw/security_logs/
s3://opsintel-copilot-angad-0025/raw/admin_events/
```

## Bronze Output Paths

```txt
s3://opsintel-copilot-angad-0025/bronze/orders/
s3://opsintel-copilot-angad-0025/bronze/security_logs/
s3://opsintel-copilot-angad-0025/bronze/admin_events/
```

## Silver Output Paths

```txt
s3://opsintel-copilot-angad-0025/silver/orders/
s3://opsintel-copilot-angad-0025/silver/security_logs/
s3://opsintel-copilot-angad-0025/silver/admin_events/
s3://opsintel-copilot-angad-0025/silver/bad_records_summary/
```

## Databricks Notebooks

### 01_bronze_ingestion.py

This notebook reads raw CSV files from S3 and creates bronze Delta tables.

Bronze tables created:

```txt
bronze_orders
bronze_security_logs
bronze_admin_events
```

The bronze layer keeps the raw structure while adding ingestion metadata.

Metadata columns added:

```txt
_dataset_name
_ingestion_timestamp
_bronze_load_date
_source_file
```

These columns support traceability, auditability, debugging, and source-file investigation.

### 02_silver_data_quality.py

This notebook reads bronze Delta tables and creates cleaned silver Delta tables.

Silver tables created:

```txt
silver_orders
silver_security_logs
silver_admin_events
```

Data quality operations include:

```txt
standardizing column names
casting timestamp fields
checking required fields
removing invalid timestamp records
removing records with missing required IDs
removing duplicate records
standardizing severity, event type, action, and risk-level fields
tracking bad record counts
```

## Bad Records Summary

The pipeline creates a bad records summary table:

```txt
bad_records_summary
```

This table tracks failed data quality rules across datasets.

Example rules:

```txt
invalid_or_missing_timestamp
missing_order_id
missing_customer_id
missing_event_id
missing_user_id
missing_ip_address
missing_admin_user
missing_action
duplicate_records_removed
```

This supports the OpsIntel Copilot goal of investigating data reliability and security issues.

## Delta Tables

The Databricks database used for Week 3 is:

```txt
opsintel_copilot
```

Expected Delta tables:

```txt
bronze_orders
bronze_security_logs
bronze_admin_events

silver_orders
silver_security_logs
silver_admin_events

bad_records_summary
```

## SQL Validation

The file below contains SQL checks for validating table counts, bronze-vs-silver differences, sample records, bad record summaries, and ingestion metadata.

```txt
databricks/sql/create_delta_tables.sql
```

## Week 3 Outcome

By the end of Week 3, OpsIntel Copilot has a Databricks Delta Lake bronze and silver pipeline over AWS S3.

The system can read raw operational and security data from S3, convert it into bronze Delta tables, clean it into silver Delta tables, enforce basic data quality rules, remove duplicates, validate timestamps, and track bad records.
