-- depends_on: {{ ref('dim_competition') }}

{{ config(materialized='ephemeral') }}

WITH staged_team_tables AS (
    {% for table in teams_table_names() %}
        {{ stage_team_table(table) }}
        {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)

SELECT DISTINCT
    team_id,
    area_id,
    name,
    emblem,
    colors,
    foundation_year,
    website,
    {{ clean_nulls('address') }} AS address,
    stadion
FROM staged_team_tables