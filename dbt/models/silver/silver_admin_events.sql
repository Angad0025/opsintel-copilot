SELECT
    event_id,
    admin_user,
    event_type,
    target,
    event_time,
    ip_address,
    severity,
    description,
    {{ flag_suspicious_event('event_type', 'config_change') }}        AS is_config_change,
    {{ flag_suspicious_event('event_type', 'privilege_escalation') }} AS is_escalation,
    {{ flag_suspicious_event('event_type', 'user_deletion') }}        AS is_user_deletion
FROM {{ ref('stg_admin_events') }}
WHERE {{ is_valid_timestamp('event_time') }}
  AND event_id IS NOT NULL
