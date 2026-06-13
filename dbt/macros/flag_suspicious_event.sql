{% macro flag_suspicious_event(event_col, event_type) %}
    CASE WHEN {{ event_col }} = '{{ event_type }}' THEN TRUE ELSE FALSE END
{% endmacro %}