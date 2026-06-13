SELECT
    s.event_id                                                         AS security_event_id,
    s.event_type                                                       AS security_event_type,
    s.event_time                                                       AS security_event_time,
    s.severity,
    a.event_id                                                         AS admin_event_id,
    a.event_type                                                       AS admin_event_type,
    a.event_time                                                       AS admin_event_time,
    ABS(UNIX_TIMESTAMP(s.event_time)
      - UNIX_TIMESTAMP(a.event_time))                                  AS time_diff_seconds,
    CASE
        WHEN ABS(UNIX_TIMESTAMP(s.event_time)
               - UNIX_TIMESTAMP(a.event_time)) < 1800 THEN 0.9
        WHEN ABS(UNIX_TIMESTAMP(s.event_time)
               - UNIX_TIMESTAMP(a.event_time)) < 3600 THEN 0.7
        ELSE 0.4
    END                                                                AS confidence_score,
    CURRENT_TIMESTAMP()                                                AS correlated_at
FROM {{ ref('silver_security_logs') }} s
JOIN {{ ref('silver_admin_events') }}  a
  ON s.user_id = a.admin_user
WHERE (s.is_escalation = TRUE OR s.is_brute_force = TRUE)
  AND (a.is_config_change = TRUE OR a.is_escalation = TRUE)
  AND ABS(UNIX_TIMESTAMP(s.event_time)
        - UNIX_TIMESTAMP(a.event_time)) < 7200
