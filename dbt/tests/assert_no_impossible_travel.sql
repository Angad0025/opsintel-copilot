{% test no_impossible_travel(model, column_name) %}
SELECT user_id
FROM (
    SELECT
        user_id,
        COUNT(DISTINCT location)                          AS location_count,
        UNIX_TIMESTAMP(MAX(event_time))
          - UNIX_TIMESTAMP(MIN(event_time))              AS time_window_seconds
    FROM {{ model }}
    GROUP BY user_id
)
WHERE location_count > 1
  AND time_window_seconds < 3600
{% endtest %}
