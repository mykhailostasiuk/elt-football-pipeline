{{ config(
    materialized='incremental',
    unique_key='season_id'
) }}

WITH stg_season AS (
    SELECT * FROM {{ ref("stg_season") }}
)

SELECT * FROM stg_season

{% if is_incremental() %}
  WHERE stg_season.season_id NOT IN (SELECT season_id FROM {{ this }})
  OR (
    stg_season.season_id IN (SELECT season_id FROM {{ this }})
    AND (
        stg_season.current_matchday != (SELECT current_matchday FROM {{ this }} WHERE stg_season.season_id = season_id)
        OR stg_season.start_date != (SELECT start_date FROM {{ this }} WHERE stg_season.season_id = season_id)
        OR stg_season.end_date != (SELECT end_date FROM {{ this }} WHERE stg_season.season_id = season_id)
        OR stg_season.winner_id != (SELECT winner_id FROM {{ this }} WHERE stg_season.season_id = season_id)
        OR stg_season.matches_played != (SELECT matches_played FROM {{ this }} WHERE stg_season.season_id = season_id)
        OR stg_season.status != (SELECT status FROM {{ this }} WHERE stg_season.season_id = season_id)
    )
  )
{% endif %}
