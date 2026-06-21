SELECT
    correlation_id,
    correlation_type,
    pipeline_run_id,
    pipeline_name,
    pipeline_failed_at,
    error_message,
    security_event_id,
    security_event_type,
    security_event_at,
    involved_user,
    time_diff_minutes,
    confidence_score,
    recommendation,
    correlated_at
FROM workspace.opsintel_copilot.correlation_records