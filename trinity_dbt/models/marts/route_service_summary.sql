{{ config(materialized='table') }}

SELECT
    route_id,
    route_long_name,
    COUNT(*)                                          AS total_stop_events,
    COUNT(DISTINCT trip_id)                           AS total_trips,
    COUNT(DISTINCT stop_id)                           AS unique_stops_served,
    SUM(CASE WHEN is_after_midnight THEN 1 ELSE 0 END) AS after_midnight_events,
    ROUND(
        100.0 * SUM(CASE WHEN is_after_midnight THEN 1 ELSE 0 END) / COUNT(*),
        2
    )                                                  AS pct_after_midnight
FROM {{ ref('fct_stop_events') }}
GROUP BY route_id, route_long_name
ORDER BY total_stop_events DESC