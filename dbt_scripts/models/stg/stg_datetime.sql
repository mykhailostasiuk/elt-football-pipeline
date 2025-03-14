{{ config(materialized='ephemeral') }}

WITH staged_datetime_tables AS (
    {% for table in matches_table_names() %}
        {{ stage_datetime_table(table) }}
        {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)

SELECT DISTINCT * FROM staged_datetime_tables