{% snapshot incident_status_snapshot %}
{{
    config(
        target_schema='opsintel_copilot_snapshots',
        unique_key='event_id',
        strategy='check',
        check_cols=['severity', 'is_brute_force', 'is_escalation']
    )
}}
SELECT
    event_id,
    user_id,
    event_type,
    severity,
    is_brute_force,
    is_escalation,
    is_impossible_travel,
    event_time
FROM {{ ref('silver_security_logs') }}
{% endsnapshot %}
