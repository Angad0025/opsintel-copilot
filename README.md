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
- Created project folder structure
- Added Terraform foundation folders
- Added documentation folders
- Added service folders for generators, API, and dashboard
- Added Databricks folders for notebooks, jobs, and SQL

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