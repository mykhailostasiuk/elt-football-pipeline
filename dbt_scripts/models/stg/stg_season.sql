-- depends_on: {{ ref('dim_team') }}
-- depends_on: {{ ref('dim_competition') }}

{{ config(materialized='ephemeral') }}

WITH staged_season_tables AS (
    {% for table in matches_table_names() %}
        {{ stage_season_table(table) }}
        {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
)

SELECT DISTINCT
    staged_season_tables.season_id,
    CAST(dim_competition.scd_id AS STRING) AS competition_id,
    CAST(dim_team.scd_id AS STRING) AS winner_id,
    staged_season_tables.start_date,
    staged_season_tables.end_date,
    staged_season_tables.current_matchday,
    staged_season_tables.matches_played,
    staged_season_tables.matches_remaining,
    staged_season_tables.matches_total,
    staged_season_tables.status
FROM staged_season_tables
LEFT JOIN {{ ref("dim_team") }} AS dim_team
ON winner_name = dim_team.name AND dim_team.end_date IS NULL
LEFT JOIN {{ ref("dim_competition") }} AS dim_competition
ON staged_season_tables.competition_id = dim_competition.competition_id AND dim_competition.end_date IS NULL