---

## Resume Bullets

**ELT Lakehouse:** Built a dbt + Databricks ELT lakehouse with staging, silver, and gold layers over AWS S3 Delta tables — implementing source freshness monitoring, reusable macros, 15+ schema and custom domain tests, SCD Type 2 snapshots, and Elementary observability.

**Correlation Engine:** Built a cross-domain PySpark correlation engine linking data pipeline failures with security events using configurable time-window rules, generating 1,496 confidence-scored incident summaries stored in RDS PostgreSQL and indexed in Bedrock RAG.

**Bedrock RAG:** Implemented an Amazon Bedrock Knowledge Base RAG system over S3 incident summaries, playbooks, and correlation records — enabling natural-language investigation queries grounded in evidence, served via FastAPI on ECS Fargate.

**Data Contracts:** Implemented data contracts in YAML defining schema, SLAs, ownership, and quality rules — enforced by dbt source tests and a contract validation layer in the data generator before any file reaches S3.

**CI/CD:** Configured GitHub Actions CI/CD running dbt test, SQLFluff SQL linting, and terraform validate on every pull request — zero manual testing, green badges on all commits.

**Infrastructure:** Provisioned all AWS infrastructure via Terraform including S3, ECS Fargate, ECR, RDS PostgreSQL, Bedrock, Secrets Manager, CloudWatch alarms, and cost allocation tags — zero manual console configuration.

---

## Quick Start

### Prerequisites
- AWS account with Bedrock access
- Databricks workspace on AWS
- Terraform >= 1.5.0
- Python 3.11+
- Docker

### Deploy Infrastructure
```bash
cd infra/terraform
terraform init
terraform apply -var='rds_password=YOUR_PASSWORD'
```

### Run dbt Pipeline
```bash
cd dbt
dbt deps
dbt run
dbt test
```

### Start Locally
```bash
# Terminal 1 — FastAPI
uvicorn services.api.main:app --reload --port 8000

# Terminal 2 — Streamlit
streamlit run services/dashboard/app.py
```

---

## Setup Guides

- [AWS Setup](docs/aws_setup.md)
- [Databricks Setup](docs/databricks_setup.md)
- [dbt Setup](docs/dbt_setup.md)
- [Bedrock RAG Setup](docs/bedrock_rag_setup.md)

---

*Built by Angaddeep Singh — Data Engineering Portfolio Project*