SELECT
    CAST(admin_event_id  AS STRING)    AS admin_event_id,
    CAST(admin_user      AS STRING)    AS admin_user,
    CAST(action          AS STRING)    AS action,
    CAST(target_service  AS STRING)    AS target_service,
    CAST(region          AS STRING)    AS region,
    CAST(event_time      AS TIMESTAMP) AS event_time
FROM `workspace`.`opsintel_copilot`.`bronze_admin_events`
WHERE admin_event_id IS NOT NULL