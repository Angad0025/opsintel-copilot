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