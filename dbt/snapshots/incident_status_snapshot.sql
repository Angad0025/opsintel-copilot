{% snapshot incident_status_snapshot %}
{{
    config(
        target_schema='opsintel_copilot_snapshots',
        unique_key='event_id',
        strategy='check',
        check_cols=['is_brute_force', 'is_escalation', 'is_impossible_travel']
    )
}}
SELECT
    event_id,
    event_type,
    user_email,
    is_brute_force,
    is_escalation,
    is_impossible_travel,
    event_time
FROM {{ ref('silver_security_logs') }}
{% endsnapshot %}
