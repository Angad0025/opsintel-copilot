{% macro is_valid_timestamp(column_name) %}
    {{ column_name }} IS NOT NULL
    AND {{ column_name }} >= '2020-01-01'
    AND {{ column_name }} <= CURRENT_TIMESTAMP()
{% endmacro %}
