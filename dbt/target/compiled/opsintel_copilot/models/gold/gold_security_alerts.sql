SELECT
    event_id,
    event_type,
    user_email,
    source_ip,
    region,
    event_time,
    success,
    is_brute_force,
    is_escalation,
    is_impossible_travel,
    is_large_export,
    is_token_rotation,
    CURRENT_TIMESTAMP() AS alert_generated_at
FROM `workspace`.`opsintel_copilot`.`silver_security_logs`
WHERE is_brute_force       = TRUE
   OR is_escalation        = TRUE
   OR is_impossible_travel = TRUE
   OR is_large_export      = TRUE
   OR is_token_rotation    = TRUE