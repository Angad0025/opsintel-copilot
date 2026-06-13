{% macro is_valid_currency(column_name) %}
    {{ column_name }} IN ('USD', 'EUR', 'GBP', 'INR')
{% endmacro %}
