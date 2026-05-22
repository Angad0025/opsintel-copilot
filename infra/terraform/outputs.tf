output "s3_bucket_name" {
  description = "Name of the OpsIntel Copilot S3 bucket"
  value       = aws_s3_bucket.opsintel_data_lake.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the OpsIntel Copilot S3 bucket"
  value       = aws_s3_bucket.opsintel_data_lake.arn
}