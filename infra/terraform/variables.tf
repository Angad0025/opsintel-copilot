variable "aws_region" {
  description = "AWS region for project resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile name"
  type        = string
  default     = "default"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "opsintel-copilot"
}

variable "s3_bucket_name" {
  description = "Main S3 bucket for OpsIntel Copilot data lake"
  type        = string
  default     = "opsintel-copilot-angad-0025"
}

variable "rds_password" {
  description = "Master password for RDS PostgreSQL instance"
  type        = string
  sensitive   = true
}