cat > ~/Desktop/opsintel-copilot/docs/security.md << 'EOF'
# Security Strategy

## Zero Secrets in Codebase

All credentials are stored in AWS Secrets Manager. No .env files exist in production. No credentials are hardcoded in any file committed to GitHub.

## Secrets Stored

| Secret Name | Contents |
|-------------|---------|
| opsintel/rds/credentials | RDS username and password |
| opsintel/databricks/token | Databricks API token |
| opsintel/bedrock/api_key | Bedrock API key |

## How FastAPI Accesses Secrets

FastAPI uses `services/api/secrets_client.py` which calls AWS Secrets Manager at runtime using IAM-based access. The ECS task role has `secretsmanager:GetSecretValue` permission scoped to `arn:aws:secretsmanager:us-east-1:770912375813:secret:opsintel/*`.

```python
import boto3, json

def get_secret(secret_name: str) -> dict:
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

## IAM Roles

Two ECS IAM roles are defined in `infra/terraform/iam.tf`:

**ECS Task Execution Role** — allows ECS to pull images from ECR and write logs to CloudWatch.

**ECS Task Role** — allows the running container to access S3, Secrets Manager, Bedrock, and CloudWatch Logs. Scoped to specific resources, not wildcard.

## GitHub Secrets

GitHub Actions uses repository secrets for CI/CD:
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `DATABRICKS_HTTP_PATH`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

These are never printed in logs and never committed to the repo.

## .gitignore

The `.gitignore` excludes:
- `.env` files
- `*.tfvars` files containing real values
- `terraform.tfstate` (contains resource IDs)
- `profiles.yml` with real credentials
EOF