# OpsIntel Copilot

OpsIntel Copilot is an AWS-native AI Data Reliability and Security Investigation Platform.

## Project Goal

This project investigates data pipeline failures and suspicious security activity using AWS, Databricks, Delta Lake, Amazon RDS PostgreSQL, Amazon Bedrock, FastAPI, Streamlit, ECS Fargate, CloudWatch, Terraform, and GitHub.

## What the System Does

The platform will:

- Ingest operational and security logs into Amazon S3
- Process raw data using Databricks and Delta Lake
- Build bronze, silver, and gold lakehouse layers
- Detect data quality and pipeline reliability issues
- Detect suspicious security activity
- Build incident timelines
- Correlate data failures with security events
- Provide a RAG-powered investigation copilot using Amazon Bedrock
- Display results through FastAPI and Streamlit

## Planned Architecture

Raw data lands in Amazon S3. Databricks on AWS processes the data into Delta Lake tables. Curated incident and reliability metadata is stored in Amazon RDS PostgreSQL. Incident summaries and playbooks are stored in S3 for Amazon Bedrock Knowledge Bases. FastAPI exposes backend APIs, and Streamlit provides the dashboard.

## Current Week 1 Progress

- Initialized Git repository
- Created GitHub repository
- Created project folder structure
- Added Terraform foundation
- Installed AWS CLI and Terraform
- Configured AWS CLI with IAM user access
- Created S3 data lake bucket using Terraform
- Added S3 prefixes for raw, bronze, silver, gold, rag-docs, and checkpoints
- Verified S3 bucket through AWS Console and AWS CLI
- Added AWS setup documentation
- Added architecture documentation
- Added architecture diagram draft

## Tech Stack

- AWS S3
- Databricks on AWS
- Delta Lake
- Amazon RDS PostgreSQL
- Amazon Bedrock
- FastAPI
- Streamlit
- ECS Fargate
- ECR
- CloudWatch
- Terraform
- GitHub