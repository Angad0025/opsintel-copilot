SELECT
    CAST(event_id    AS STRING)    AS event_id,
    CAST(event_type  AS STRING)    AS event_type,
    CAST(user_email  AS STRING)    AS user_email,
    CAST(source_ip   AS STRING)    AS source_ip,
    CAST(region      AS STRING)    AS region,
    CAST(event_time  AS TIMESTAMP) AS event_time,
    CAST(success     AS BOOLEAN)   AS success
FROM {{ source('bronze', 'bronze_security_logs') }}
WHERE event_id IS NOT NULL
