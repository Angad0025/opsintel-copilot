SELECT
    CAST(event_id    AS STRING)    AS event_id,
    CAST(admin_user  AS STRING)    AS admin_user,
    CAST(event_type  AS STRING)    AS event_type,
    CAST(target      AS STRING)    AS target,
    CAST(event_time  AS TIMESTAMP) AS event_time,
    CAST(ip_address  AS STRING)    AS ip_address,
    CAST(severity    AS STRING)    AS severity,
    CAST(description AS STRING)    AS description
FROM {{ source('bronze', 'bronze_admin_events') }}
WHERE event_id IS NOT NULL
