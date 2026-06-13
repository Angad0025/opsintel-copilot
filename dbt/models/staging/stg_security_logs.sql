SELECT
    CAST(event_id    AS STRING)    AS event_id,
    CAST(user_id     AS STRING)    AS user_id,
    CAST(event_type  AS STRING)    AS event_type,
    CAST(ip_address  AS STRING)    AS ip_address,
    CAST(location    AS STRING)    AS location,
    CAST(event_time  AS TIMESTAMP) AS event_time,
    CAST(severity    AS STRING)    AS severity
FROM {{ source('bronze', 'bronze_security_logs') }}
WHERE event_id IS NOT NULL
