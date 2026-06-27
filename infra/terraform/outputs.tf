output "s3_bucket_name" {
  description = "Name of the OpsIntel Copilot S3 bucket"
  value       = aws_s3_bucket.opsintel_data_lake.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the OpsIntel Copilot S3 bucket"
  value       = aws_s3_bucket.opsintel_data_lake.arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.opsintel.name
}

output "fastapi_service_name" {
  description = "FastAPI ECS service name"
  value       = aws_ecs_service.fastapi.name
}

output "streamlit_service_name" {
  description = "Streamlit ECS service name"
  value       = aws_ecs_service.streamlit.name
}