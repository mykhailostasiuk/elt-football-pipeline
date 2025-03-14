-- depends_on: {{ ref('dim_area') }}

{{ config(materialized='ephemeral') }}

WITH staged_competition_tables AS (
    {% for table in matches_table_names() %}
        {{ stage_competition_table(table) }}
        {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)

SELECT DISTINCT * FROM staged_competition_tables