# =============================================================
# OpsIntel Copilot — ECR Repositories
# Docker image registry for FastAPI and Streamlit
# =============================================================

# ECR repositories are created via AWS CLI
# (Terraform import not needed since they already exist)
#
# opsintel-api:
#   770912375813.dkr.ecr.us-east-1.amazonaws.com/opsintel-api
#
# opsintel-dashboard:
#   770912375813.dkr.ecr.us-east-1.amazonaws.com/opsintel-dashboard
#
# Images are built with:
#   docker build --platform linux/amd64 -f services/api/Dockerfile -t opsintel-api .
#   docker build --platform linux/amd64 -f services/dashboard/Dockerfile -t opsintel-dashboard .
#
# Images are tagged and pushed with:
#   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 770912375813.dkr.ecr.us-east-1.amazonaws.com
#   docker tag opsintel-api:latest 770912375813.dkr.ecr.us-east-1.amazonaws.com/opsintel-api:latest
#   docker push 770912375813.dkr.ecr.us-east-1.amazonaws.com/opsintel-api:latest