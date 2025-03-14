{{ config(
    materialized='incremental',
    unique_key='datetime_id'
) }}

WITH stg_datetime AS (
    SELECT * FROM {{ ref("stg_datetime") }}
)

SELECT * FROM stg_datetime

{% if is_incremental() %}
  WHERE datetime_id NOT IN (SELECT datetime_id FROM {{ this }})
{% endif %}