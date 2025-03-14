-- depends_on: {{ ref('dim_datetime') }}
-- depends_on: {{ ref('dim_team') }}
-- depends_on: {{ ref('dim_competition') }}
-- depends_on: {{ ref('dim_area') }}
-- depends_on: {{ ref('dim_season') }}

{{ config(materialized='ephemeral') }}

WITH staged_matches_tables AS (
    {% for table in matches_table_names() %}
        {{ stage_matches_table(table) }}
        {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)

SELECT DISTINCT * FROM staged_matches_tables
