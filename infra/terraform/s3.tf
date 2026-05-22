resource "aws_s3_bucket" "opsintel_data_lake" {
  bucket = var.s3_bucket_name

  tags = {
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "opsintel_data_lake_versioning" {
  bucket = aws_s3_bucket.opsintel_data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "opsintel_data_lake_encryption" {
  bucket = aws_s3_bucket.opsintel_data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "raw_folder" {
  bucket  = aws_s3_bucket.opsintel_data_lake.id
  key     = "raw/"
  content = ""
}

resource "aws_s3_object" "bronze_folder" {
  bucket  = aws_s3_bucket.opsintel_data_lake.id
  key     = "bronze/"
  content = ""
}

resource "aws_s3_object" "silver_folder" {
  bucket  = aws_s3_bucket.opsintel_data_lake.id
  key     = "silver/"
  content = ""
}

resource "aws_s3_object" "gold_folder" {
  bucket  = aws_s3_bucket.opsintel_data_lake.id
  key     = "gold/"
  content = ""
}

resource "aws_s3_object" "rag_docs_folder" {
  bucket  = aws_s3_bucket.opsintel_data_lake.id
  key     = "rag-docs/"
  content = ""
}

resource "aws_s3_object" "checkpoints_folder" {
  bucket  = aws_s3_bucket.opsintel_data_lake.id
  key     = "checkpoints/"
  content = ""
}