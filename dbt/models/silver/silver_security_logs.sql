SELECT
    event_id,
    event_type,
    user_email,
    source_ip,
    region,
    event_time,
    success,
    {{ flag_suspicious_event('event_type', 'brute_force') }}          AS is_brute_force,
    {{ flag_suspicious_event('event_type', 'privilege_escalation') }}  AS is_escalation,
    {{ flag_suspicious_event('event_type', 'impossible_travel') }}     AS is_impossible_travel,
    {{ flag_suspicious_event('event_type', 'large_data_export') }}     AS is_large_export,
    {{ flag_suspicious_event('event_type', 'api_token_rotation') }}    AS is_token_rotation
FROM {{ ref('stg_security_logs') }}
WHERE {{ is_valid_timestamp('event_time') }}
  AND event_id IS NOT NULL
