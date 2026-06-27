# =============================================================
# OpsIntel Copilot — ECS Fargate: FastAPI Backend
# =============================================================

# ECS Cluster (shared by both FastAPI and Streamlit)
resource "aws_ecs_cluster" "opsintel" {
  name = "opsintel-copilot"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# CloudWatch Log Group for FastAPI
resource "aws_cloudwatch_log_group" "fastapi" {
  name              = "/ecs/opsintel-fastapi"
  retention_in_days = 7
}

# ECS Task Definition for FastAPI
resource "aws_ecs_task_definition" "fastapi" {
  family                   = "opsintel-fastapi"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name  = "fastapi"
    image = "770912375813.dkr.ecr.us-east-1.amazonaws.com/opsintel-api:latest"

    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "AWS_DEFAULT_REGION", value = "us-east-1" }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/opsintel-fastapi"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }

    essential = true
  }])
}

# Security Group for FastAPI
resource "aws_security_group" "fastapi" {
  name        = "opsintel-fastapi-sg"
  description = "Security group for OpsIntel FastAPI ECS service"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS Service for FastAPI
resource "aws_ecs_service" "fastapi" {
  name            = "opsintel-fastapi"
  cluster         = aws_ecs_cluster.opsintel.id
  task_definition = aws_ecs_task_definition.fastapi.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.fastapi.id]
    assign_public_ip = true
  }
}