# AWS Setup

## Region

This project uses `us-east-1`.

## IAM User

Created IAM user for AWS CLI and Terraform:

`opsintel-terraform-user`

This user is used for local AWS CLI and Terraform access.

For the current development setup, this user has `AdministratorAccess`. In production, this should be replaced with least-privilege permissions.

## AWS CLI

AWS CLI was configured locally using:

`aws configure`

Settings used:

- Default region: `us-east-1`
- Default output format: `json`

AWS connection was verified using:

`aws sts get-caller-identity`

## S3 Data Lake Bucket

Terraform created the main S3 bucket:

`opsintel-copilot-angad-0025`

## S3 Folder Structure

The bucket contains:

- `raw/`
- `bronze/`
- `silver/`
- `gold/`
- `rag-docs/`
- `checkpoints/`

## Folder Meaning

`raw/` stores original incoming files.

`bronze/` stores structured raw data after Databricks ingestion.

`silver/` stores cleaned and validated data.

`gold/` stores final outputs such as incidents, alerts, quality results, correlations, and recommendations.

`rag-docs/` stores documents for the Bedrock RAG copilot.

`checkpoints/` stores pipeline progress/checkpoint information.

## Verification

Verified using:

`aws s3 ls`

`aws s3 ls s3://opsintel-copilot-angad-0025/`

Expected output:

- `PRE bronze/`
- `PRE checkpoints/`
- `PRE gold/`
- `PRE rag-docs/`
- `PRE raw/`
- `PRE silver/`

## Completed

- Installed AWS CLI
- Installed Terraform
- Created IAM user for Terraform access
- Created S3 bucket using Terraform
- Created raw, bronze, silver, gold, rag-docs, and checkpoints prefixes
- Verified bucket using AWS Console and AWS CLI