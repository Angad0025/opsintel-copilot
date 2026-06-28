# =============================================================
# OpsIntel Copilot — CloudWatch Alarms
# =============================================================

# CloudWatch log groups are defined in ecs_fastapi.tf
# and ecs_streamlit.tf

# Alarm: FastAPI ECS task stopped
resource "aws_cloudwatch_metric_alarm" "fastapi_task_count" {
  alarm_name          = "opsintel-fastapi-task-stopped"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "FastAPI ECS task count dropped below 1"

  dimensions = {
    ClusterName = "opsintel-copilot"
    ServiceName = "opsintel-fastapi"
  }
}

# Alarm: Streamlit ECS task stopped
resource "aws_cloudwatch_metric_alarm" "streamlit_task_count" {
  alarm_name          = "opsintel-streamlit-task-stopped"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "Streamlit ECS task count dropped below 1"

  dimensions = {
    ClusterName = "opsintel-copilot"
    ServiceName = "opsintel-streamlit"
  }
}

# Alarm: RDS high connections
resource "aws_cloudwatch_metric_alarm" "rds_connections" {
  alarm_name          = "opsintel-rds-high-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS connection count exceeded 80"

  dimensions = {
    DBInstanceIdentifier = "opsintel-copilot-db"
  }
}