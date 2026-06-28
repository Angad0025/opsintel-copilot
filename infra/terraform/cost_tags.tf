# =============================================================
# OpsIntel Copilot — Cost Allocation Tags
# Applied to all resources for cost tracking
# =============================================================

locals {
  cost_tags = {
    Project     = "opsintel-copilot"
    Environment = "dev"
    CostCenter  = "data-engineering"
    Owner       = "angad-singh"
    ManagedBy   = "terraform"
  }
}

# Cost allocation tags are applied to every resource
# via tags = local.cost_tags in each .tf file
#
# Monthly cost estimates:
# Databricks cluster:    $80-120/mo (auto-pause after 10 min idle)
# RDS db.t3.micro:       $15/mo
# ECS Fargate (2 tasks): $20/mo
# S3 storage:            $2/mo
# Bedrock (per query):   ~$0.003 per RAG query
# ECR storage:           $0.50/mo
# CloudWatch logs:       $1/mo
# Total estimate:        ~$120-160/mo