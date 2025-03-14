{% macro stage_datetime_table(source_name) %}
    SELECT CAST(
        CONCAT(
            CAST(EXTRACT(YEAR FROM utcDate) AS STRING),
            LPAD(CAST(EXTRACT(MONTH FROM utcDate) AS STRING), 2, '0'),
            LPAD(CAST(EXTRACT(DAY FROM utcDate) AS STRING), 2, '0'),
            LPAD(CAST(EXTRACT(HOUR FROM utcDate) AS STRING), 2, '0'),
            LPAD(CAST(EXTRACT(MINUTE FROM utcDate) AS STRING), 2, '0'),
            LPAD(CAST(EXTRACT(SECOND FROM utcDate) AS STRING), 2, '0')
            ) AS INT
        ) AS datetime_id,
        utcDate                                      AS utc_timestamp,
        DATE(utcDate)                                AS utc_date,
        TIME(utcDate)                                AS utc_time,
        CAST(EXTRACT(YEAR FROM utcDate) AS INT)      AS year,
        CAST(EXTRACT(QUARTER FROM utcDate) AS INT)   AS quarter,
        CAST(EXTRACT(MONTH FROM utcDate) AS INT)     AS month,
        CAST(EXTRACT(DAY FROM utcDate) AS INT)       AS day,
        CAST(EXTRACT(WEEK FROM utcDate) AS INT)      AS week,
        CAST(EXTRACT(DAYOFWEEK FROM utcDate) AS INT) AS weekday,
        FORMAT_TIMESTAMP('%A', utcDate)              AS weekday_name,
        CAST(EXTRACT(HOUR FROM utcDate) AS INT)      AS hours,
        CAST(EXTRACT(MINUTE FROM utcDate) AS INT)    AS minutes,
        CAST(EXTRACT(SECOND FROM utcDate) AS INT)    AS seconds,
    FROM {{ source ("football_raw", source_name) }} AS source_table, UNNEST (source_table.matches) AS matches_unnested
{% endmacro %}

{% macro stage_season_table(source_name) %}
    SELECT
        CAST(matches_unnested.season.id AS SMALLINT) AS season_id,
        CAST(matches_unnested.competition.id AS INT) AS competition_id,
        CAST(matches_unnested.season.winner AS STRING) AS winner_name,
        CAST(matches_unnested.season.startDate AS DATE) AS start_date,
        CAST(matches_unnested.season.endDate AS DATE) AS end_date,
        {% if source_name == "CL_matches" %}
            NULL AS current_matchday,
        {% else %}
            CAST(matches_unnested.season.currentMatchday AS TINYINT) AS current_matchday,
        {% endif %}
        CAST(resultSet.played AS SMALLINT) AS matches_played,
        CAST(resultSet.count - resultSet.played AS SMALLINT) AS matches_remaining,
        CAST(resultSet.count AS SMALLINT) AS matches_total,
        CASE
            WHEN resultSet.count - resultSet.played = 0 THEN 'FINISHED'
            ELSE 'ONGOING'
        END AS status
    FROM {{ source("football_raw", source_name) }} AS source_table, UNNEST (source_table.matches) AS matches_unnested
{% endmacro %}

{% macro stage_competition_table(source_name) %}
    SELECT
        CAST(source_table.competition.id AS SMALLINT) AS competition_id,
        CAST(matches_unnested.area.id AS SMALLINT) AS area_id,
        CAST(source_table.competition.name AS STRING) AS name,
        CAST(source_table.competition.type AS STRING) AS type,
        CAST(source_table.competition.emblem AS STRING) AS emblem,
    FROM {{ source("football_raw", source_name) }} AS source_table, UNNEST(source_table.matches) AS matches_unnested
{% endmacro %}

{% macro stage_team_table(source_name) %}
    SELECT
        CAST(teams_unnested.id AS SMALLINT) AS team_id,
        CAST(teams_unnested.area.id AS SMALLINT) AS area_id,
        CAST(teams_unnested.name AS STRING) AS name,
        CAST(teams_unnested.crest AS STRING) AS emblem,
        CAST(teams_unnested.clubColors AS STRING) AS colors,
        CAST(teams_unnested.founded AS SMALLINT) AS foundation_year,
        CAST(teams_unnested.website AS STRING) AS website,
        CAST(teams_unnested.address AS STRING) AS address,
        CAST(teams_unnested.venue AS STRING) AS stadion,
    FROM {{ source("football_raw", source_name) }} AS source_table, UNNEST (source_table.teams) AS teams_unnested
    JOIN {{ ref('dim_competition') }} AS dim_competition
    ON source_table.competition.id = dim_competition.competition_id
{% endmacro %}

{% macro stage_matches_table(source_name) %}
    SELECT
        CAST(matches_unnested.id AS INT) AS match_id,
        CAST(dim_competition.scd_id AS STRING) AS competition_id,
        CAST(dim_season.season_id AS SMALLINT) AS season_id,
        CAST(dim_datetime.datetime_id AS INT) AS datetime_id,
        CAST(dim_team_home.scd_id AS STRING) AS home_team_id,
        CAST(dim_team_away.scd_id AS STRING) AS away_team_id,
        CAST(dim_area.area_id AS SMALLINT) AS area_id,
        CAST(matches_unnested.score.halfTime.home AS TINYINT) AS half_time_home_goals,
        CAST(matches_unnested.score.halfTime.away AS TINYINT) AS half_time_away_goals,
        CAST(matches_unnested.score.fullTime.home AS TINYINT) AS full_time_home_goals,
        CAST(matches_unnested.score.fullTime.away AS TINYINT) AS full_time_away_goals,
        CAST(matches_unnested.score.winner AS STRING) AS winner,
        CAST(matches_unnested.score.duration AS STRING) AS duration,
        CAST(matches_unnested.status AS STRING) AS status,
        CASE
            WHEN dim_competition.type != "LEAGUE" THEN NULL
            ELSE CAST(matches_unnested.matchday AS TINYINT)
        END AS season_matchday,
        CASE
            WHEN dim_competition.type = "LEAGUE" THEN NULL
            ELSE CAST(matches_unnested.stage AS STRING)
        END AS competition_stage,
        CASE
            WHEN dim_competition.type = "LEAGUE" THEN NULL
            ELSE CAST(matches_unnested.group AS STRING)
        END AS competition_group,
    FROM {{ source("football_raw", source_name) }} AS source_table, UNNEST (source_table.matches) AS matches_unnested
    LEFT JOIN {{ ref('dim_datetime') }} AS dim_datetime
    ON matches_unnested.utcDate = dim_datetime.utc_timestamp
    LEFT JOIN {{ ref('dim_team') }} AS dim_team_home
    ON matches_unnested.homeTeam.id = dim_team_home.team_id AND dim_team_home.end_date IS NULL
    LEFT JOIN {{ ref('dim_team') }} AS dim_team_away
    ON matches_unnested.awayTeam.id = dim_team_away.team_id AND dim_team_away.end_date IS NULL
    LEFT JOIN {{ ref('dim_competition') }} AS dim_competition
    ON source_table.competition.id = dim_competition.competition_id AND dim_competition.end_date IS NULL
    LEFT JOIN {{ ref('dim_area') }} AS dim_area
    ON matches_unnested.area.id = dim_area.area_id
    LEFT JOIN {{ ref('dim_season') }} AS dim_season
    ON matches_unnested.season.id = dim_season.season_id
{% endmacro %}