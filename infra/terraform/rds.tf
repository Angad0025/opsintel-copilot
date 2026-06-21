resource "aws_db_subnet_group" "opsintel" {
  name       = "opsintel-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids
  tags = {
    Project     = "opsintel-copilot"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_security_group" "rds" {
  name        = "opsintel-rds-sg"
  description = "Allow PostgreSQL access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project     = "opsintel-copilot"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_db_instance" "opsintel" {
  identifier             = "opsintel-copilot-db"
  engine                 = "postgres"
  engine_version         = "16.9"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  db_name                = "opsintel"
  username               = "opsintel_admin"
  password               = var.rds_password
  db_subnet_group_name   = aws_db_subnet_group.opsintel.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = true
  skip_final_snapshot    = true
  deletion_protection    = false

  tags = {
    Project     = "opsintel-copilot"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

output "rds_endpoint" {
  value = aws_db_instance.opsintel.endpoint
}