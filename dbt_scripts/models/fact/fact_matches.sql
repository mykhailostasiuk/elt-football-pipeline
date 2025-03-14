{{ config(
    materialized='incremental',
    unique_key='match_id'
) }}

WITH stg_matches AS (
    SELECT * FROM {{ ref("stg_matches") }}
)

SELECT * FROM stg_matches AS source_table

{% if is_incremental() %}
  WHERE source_table.match_id NOT IN (SELECT match_id FROM {{ this }})
  OR (
    source_table.match_id IN (SELECT match_id FROM {{ this }})
    AND (
        source_table.datetime_id != (SELECT datetime_id FROM {{ this }} WHERE source_table.match_id = match_id)
        OR source_table.home_team_id != (SELECT home_team_id FROM {{ this }} WHERE source_table.match_id = match_id)
        OR source_table.away_team_id != (SELECT away_team_id FROM {{ this }} WHERE source_table.match_id = match_id)
        OR source_table.area_id != (SELECT area_id FROM {{ this }} WHERE source_table.match_id = match_id)
        OR source_table.status != (SELECT status FROM {{ this }} WHERE source_table.match_id = match_id)
        OR source_table.competition_group != (SELECT competition_group FROM {{ this }} WHERE source_table.match_id = match_id)
    )
  )
{% endif %}