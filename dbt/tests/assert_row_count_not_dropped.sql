{% test row_count_not_dropped(model, column_name, threshold) %}
SELECT COUNT(*) AS row_count
FROM {{ model }}
HAVING COUNT(*) < {{ threshold }}
{% endtest %}
