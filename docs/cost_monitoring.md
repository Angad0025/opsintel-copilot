cat > ~/Desktop/opsintel-copilot/docs/cost_monitoring.md << 'EOF'
# Cost Monitoring

## Monthly Cost Estimates

| Service | Configuration | Estimated Cost |
|---------|--------------|---------------|
| Databricks on AWS | Serverless SQL warehouse, auto-pause 10 min | $80-120/mo |
| RDS PostgreSQL | db.t3.micro, 20GB gp2, single-AZ | $15/mo |
| ECS Fargate | 2 tasks x 0.5 vCPU x 1GB RAM | $20/mo |
| S3 | ~5GB storage + requests | $2/mo |
| Amazon Bedrock | Claude Sonnet 4.6 per-query pricing | ~$0.003/query |
| ECR | 2 images ~500MB each | $0.50/mo |
| CloudWatch | Log ingestion + storage | $1/mo |
| Secrets Manager | 3 secrets | $0.12/mo |
| **Total** | | **~$120-160/mo** |

## Cost Optimization Decisions

- Databricks SQL warehouse set to auto-pause after 10 minutes idle
- RDS uses db.t3.micro (smallest instance) — sufficient for portfolio project
- ECS tasks use 0.5 vCPU / 1GB RAM — minimum for FastAPI and Streamlit
- S3 lifecycle rules expire raw/ files after 90 days
- CloudWatch log retention set to 7 days (not indefinite)
- Bedrock charged per query — no idle cost

## Cost Allocation Tags

Every AWS resource is tagged:
Project     = opsintel-copilot

Environment = dev

CostCenter  = data-engineering

Owner       = angad-singh

ManagedBy   = terraform

These tags appear in AWS Cost Explorer allowing per-project cost breakdown.

## CloudWatch Alarms

Three alarms are configured in `infra/terraform/cloudwatch.tf`:
- FastAPI ECS task count < 1 (task stopped)
- Streamlit ECS task count < 1 (task stopped)
- RDS connections > 80 (approaching connection limit)

## Stopping the Project to Save Costs

To stop ECS services when not in use:
```bash
aws ecs update-service --cluster opsintel-copilot --service opsintel-fastapi --desired-count 0 --region us-east-1
aws ecs update-service --cluster opsintel-copilot --service opsintel-streamlit --desired-count 0 --region us-east-1
```

To restart:
```bash
aws ecs update-service --cluster opsintel-copilot --service opsintel-fastapi --desired-count 1 --region us-east-1
aws ecs update-service --cluster opsintel-copilot --service opsintel-streamlit --desired-count 1 --region us-east-1
```
EOF