SELECT
    event_id,
    user_id,
    event_type,
    location,
    event_time,
    severity,
    is_brute_force,
    is_escalation,
    is_impossible_travel,
    is_large_export,
    is_token_rotation,
    CURRENT_TIMESTAMP() AS alert_generated_at
FROM {{ ref('silver_security_logs') }}
WHERE is_brute_force       = TRUE
   OR is_escalation        = TRUE
   OR is_impossible_travel = TRUE
   OR is_large_export      = TRUE
   OR is_token_rotation    = TRUE
