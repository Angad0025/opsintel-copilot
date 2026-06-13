SELECT
    admin_event_id,
    admin_user,
    action,
    target_service,
    region,
    event_time,
    {{ flag_suspicious_event('action', 'config_change') }}        AS is_config_change,
    {{ flag_suspicious_event('action', 'privilege_escalation') }} AS is_escalation,
    {{ flag_suspicious_event('action', 'user_deletion') }}        AS is_user_deletion
FROM {{ ref('stg_admin_events') }}
WHERE {{ is_valid_timestamp('event_time') }}
  AND admin_event_id IS NOT NULL
