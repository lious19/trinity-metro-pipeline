SELECT
    stop_id,
    stop_code,
    stop_name,
    stop_lat,
    stop_lon
FROM {{ source('raw', 'raw_stops') }}