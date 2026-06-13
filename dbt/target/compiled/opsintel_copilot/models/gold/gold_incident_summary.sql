SELECT
    DATE_TRUNC('hour', event_time)                                     AS incident_hour,
    region,
    COUNT(*)                                                           AS total_events,
    SUM(CASE WHEN is_brute_force       THEN 1 ELSE 0 END)             AS brute_force_count,
    SUM(CASE WHEN is_escalation        THEN 1 ELSE 0 END)             AS escalation_count,
    SUM(CASE WHEN is_impossible_travel THEN 1 ELSE 0 END)             AS impossible_travel_count,
    SUM(CASE WHEN is_large_export      THEN 1 ELSE 0 END)             AS large_export_count,
    CURRENT_TIMESTAMP()                                                AS summary_generated_at
FROM `workspace`.`opsintel_copilot`.`silver_security_logs`
GROUP BY DATE_TRUNC('hour', event_time), region