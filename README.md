# OpsIntel Copilot

OpsIntel Copilot is an AWS-native AI Data Reliability and Security Investigation Platform.

The project is designed to investigate data pipeline failures, data quality issues, suspicious security activity, and operational incidents using AWS, Databricks, Delta Lake, Amazon Bedrock, FastAPI, Streamlit, Terraform, and GitHub.

---

## Project Goal

The goal of OpsIntel Copilot is to build a cloud-native investigation platform that can answer questions such as:

- Why did a data pipeline fail?
- Was the failure caused by bad data, schema drift, access issues, or expired tokens?
- Did suspicious security activity happen near the pipeline failure?
- Were there risky admin changes before the incident?
- Was there suspicious warehouse export activity?
- What remediation steps should an engineer follow?

The final system will combine data engineering, security analytics, incident correlation, and RAG-based investigation.

---

## What the System Does

The platform will:

- Ingest operational, pipeline, security, token, and warehouse export logs into Amazon S3
- Process raw data using Databricks on AWS
- Build bronze, silver, and gold Delta Lake layers
- Detect data quality and pipeline reliability issues
- Detect suspicious security activity
- Track admin changes and API token events
- Identify suspicious warehouse exports
- Build incident timelines
- Correlate data failures with security and admin events
- Generate investigation summaries and recommendations
- Provide a RAG-powered investigation copilot using Amazon Bedrock
- Display results through FastAPI and Streamlit

---

## Planned Architecture

Raw operational and security data lands in Amazon S3. Databricks on AWS processes the raw data into Delta Lake bronze, silver, and gold layers.

Curated incident, reliability, security, and correlation metadata will be stored in Amazon RDS PostgreSQL. Incident summaries, playbooks, and runbooks will be stored in S3 and later connected to Amazon Bedrock Knowledge Bases for RAG-powered investigation.

FastAPI will expose backend APIs, and Streamlit will provide the dashboard interface.

---

## High-Level Data Flow

```txt
Synthetic data generators
        ↓
AWS S3 raw layer
        ↓
Databricks on AWS
        ↓
Bronze Delta tables
        ↓
Silver cleaned tables
        ↓
Gold incident and analytics tables
        ↓
RDS PostgreSQL + S3 rag-docs
        ↓
Amazon Bedrock Knowledge Base
        ↓
FastAPI backend
        ↓
Streamlit dashboard
---

## Week 3 — Databricks Bronze/Silver Pipeline

### Goal

Build the Databricks lakehouse ingestion and cleaning layer over the AWS S3 data lake.

The Week 3 pipeline reads raw CSV datasets from S3, converts them into Delta Lake bronze tables, applies data quality checks, and writes cleaned silver Delta tables back to S3.

### Cloud Setup Completed

Databricks was connected to AWS S3 using IAM role-based access and Unity Catalog.

```txt
AWS IAM Role:
opsintel-databricks-s3-role

AWS IAM Policy:
opsintel-databricks-s3-policy

Databricks Storage Credential:
opsintel_databricks_s3_credential

Databricks External Location:
opsintel_s3_external_location

S3 Data Lake:
s3://opsintel-copilot-angad-0025/
```

### Pipeline Flow

```txt
AWS S3 raw CSV data
        ↓
Databricks bronze ingestion notebook
        ↓
Bronze Delta tables
        ↓
Databricks silver data quality notebook
        ↓
Silver Delta tables
        ↓
Bad records summary
```

### Databricks Notebooks

```txt
databricks/notebooks/01_bronze_ingestion.py
databricks/notebooks/02_silver_data_quality.py
databricks/sql/create_delta_tables.sql
```

### Raw Input Datasets

```txt
s3://opsintel-copilot-angad-0025/raw/orders/
s3://opsintel-copilot-angad-0025/raw/security_logs/
s3://opsintel-copilot-angad-0025/raw/admin_events/
```

### Bronze Delta Tables Created

```txt
workspace.opsintel_copilot.bronze_orders
workspace.opsintel_copilot.bronze_security_logs
workspace.opsintel_copilot.bronze_admin_events
```

Validation counts:

```txt
bronze_orders          100,000 records
bronze_security_logs   100,000 records
bronze_admin_events     10,000 records
```

Bronze ingestion metadata added:

```txt
_dataset_name
_ingestion_timestamp
_bronze_load_date
_source_file
```

### Silver Delta Tables Created

```txt
workspace.opsintel_copilot.silver_orders
workspace.opsintel_copilot.silver_security_logs
workspace.opsintel_copilot.silver_admin_events
workspace.opsintel_copilot.bad_records_summary
```

Validation counts:

```txt
silver_orders          100,000 records
silver_security_logs   100,000 records
silver_admin_events     10,000 records
```

### Data Quality Checks Implemented

```txt
Standardized column names
Validated timestamp fields
Checked required IDs and user fields
Removed duplicate records
Standardized status, currency, region, event type, action, and service fields
Tracked bad record counts in bad_records_summary
```

### Week 3 Outcome

By the end of Week 3, OpsIntel Copilot has a working Databricks Delta Lake bronze and silver pipeline over AWS S3.

The project can now read raw operational and security datasets from S3, create bronze Delta tables, clean and validate data into silver Delta tables, and track data quality results through a bad records summary table.

### Week 3 Resume-Ready Summary

Built and validated Databricks Delta Lake bronze and silver pipelines over AWS S3 using PySpark, Unity Catalog, IAM role-based access, Delta tables, timestamp validation, deduplication, and data quality checks across operational and security datasets.

