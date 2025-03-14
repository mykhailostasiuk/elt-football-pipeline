{% macro clean_nulls(column) %}
    CASE
        WHEN TRIM(REPLACE({{ column }}, 'null', '')) = '' THEN NULL
        ELSE TRIM(REPLACE({{ column }}, 'null', ''))
    END
{% endmacro %}