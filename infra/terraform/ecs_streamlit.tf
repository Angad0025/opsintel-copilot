# =============================================================
# OpsIntel Copilot — ECS Fargate: Streamlit Dashboard
# =============================================================

# CloudWatch Log Group for Streamlit
resource "aws_cloudwatch_log_group" "streamlit" {
  name              = "/ecs/opsintel-streamlit"
  retention_in_days = 7
}

# ECS Task Definition for Streamlit
resource "aws_ecs_task_definition" "streamlit" {
  family                   = "opsintel-streamlit"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name  = "streamlit"
    image = "770912375813.dkr.ecr.us-east-1.amazonaws.com/opsintel-dashboard:latest"

    portMappings = [{
      containerPort = 8501
      protocol      = "tcp"
    }]

    environment = [
      { name = "AWS_DEFAULT_REGION", value = "us-east-1" },
      { name = "FASTAPI_URL",        value = "http://${aws_ecs_service.fastapi.name}:8000" }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/opsintel-streamlit"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }

    essential = true
  }])
}

# Security Group for Streamlit
resource "aws_security_group" "streamlit" {
  name        = "opsintel-streamlit-sg"
  description = "Security group for OpsIntel Streamlit ECS service"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 8501
    to_port     = 8501
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

# ECS Service for Streamlit
resource "aws_ecs_service" "streamlit" {
  name            = "opsintel-streamlit"
  cluster         = aws_ecs_cluster.opsintel.id
  task_definition = aws_ecs_task_definition.streamlit.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.streamlit.id]
    assign_public_ip = true
  }
}