# OpsIntel Copilot Architecture

OpsIntel Copilot is an AWS-native AI Data Reliability and Security Investigation Platform.

## High-Level Flow

Synthetic data generators  
↓  
Amazon S3 raw/  
↓  
Databricks bronze layer  
↓  
Databricks silver layer  
↓  
Databricks gold layer  
↓  
Amazon RDS PostgreSQL + S3 rag-docs/  
↓  
Amazon Bedrock Knowledge Base  
↓  
FastAPI backend  
↓  
Streamlit dashboard  

## Current Storage Layer

The project uses Amazon S3 as the main data lake storage layer.

Current bucket:

`opsintel-copilot-angad-0025`

## Medallion Layout

- `raw/` — original files exactly as received
- `bronze/` — structured raw data
- `silver/` — cleaned and validated data
- `gold/` — final incidents, alerts, summaries, and correlations
- `rag-docs/` — documents for Bedrock RAG
- `checkpoints/` — pipeline progress tracking

## Raw Layer

Stores untouched incoming files such as orders data, pipeline logs, security logs, admin events, API token events, and warehouse export events.

## Bronze Layer

Stores structured raw data created by Databricks ingestion jobs.

## Silver Layer

Stores cleaned, validated, and deduplicated records.

## Gold Layer

Stores final investigation outputs such as:

- data quality results
- pipeline runs
- security alerts
- incidents
- incident timelines
- correlations
- recommendations

## RAG Documents Layer

Stores investigation documents used by the copilot, such as:

- incident summaries
- pipeline failure runbooks
- security playbooks
- timeline summaries
- correlation explanations

## Week 1 Status

Completed:

- GitHub repository initialized
- Terraform foundation created
- AWS CLI configured
- S3 data lake bucket created
- Raw, bronze, silver, gold, rag-docs, and checkpoints prefixes created
- S3 bucket verified through AWS Console and AWS CLI