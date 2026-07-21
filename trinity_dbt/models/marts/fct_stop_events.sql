{{ config(materialized='table') }}

SELECT
    f.trip_id,
    f.route_id,
    r.route_short_name,
    r.route_long_name,
    f.stop_id,
    s.stop_name,
    s.stop_lat,
    s.stop_lon,
    f.service_id,
    f.direction_id,
    f.stop_sequence,
    f.arrival_time_seconds,
    f.is_after_midnight
FROM {{ ref('stg_scheduled_stop_event') }} f
JOIN {{ ref('stg_route') }} r ON f.route_id = r.route_id
JOIN {{ ref('stg_stop') }} s ON f.stop_id = s.stop_id