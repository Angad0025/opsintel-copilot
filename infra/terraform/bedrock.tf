# =============================================================
# OpsIntel Copilot — Bedrock Configuration
# Knowledge Base is created via AWS Console (managed KB)
# This file documents the Bedrock resources used
# =============================================================

# Bedrock Knowledge Base is managed via AWS Console
# Knowledge Base ID: ZMTLLFQNTO
# Data Source: s3://opsintel-copilot-angad-0025/rag-docs/
# Embeddings: Titan Text Embeddings V2 (1024 dimensions)
# Vector Store: Managed (OpenSearch Serverless)
# Model: us.anthropic.claude-sonnet-4-6

# IAM policy for Bedrock access is defined in iam.tf
# under aws_iam_role_policy.ecs_task_policy