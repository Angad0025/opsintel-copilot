SELECT
    security_event_id,
    security_event_type,
    security_event_time,
    user_email,
    admin_event_id,
    admin_action,
    admin_event_time,
    time_diff_seconds,
    confidence_score,
    correlated_at
FROM workspace.opsintel_copilot.correlation_records