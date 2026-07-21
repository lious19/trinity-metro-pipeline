{{ config(materialized='table') }}

SELECT
    st.trip_id,
    st.stop_id,
    t.route_id,
    t.service_id,
    t.direction_id,
    st.stop_sequence,
    st.timepoint,
    st.arrival_time AS arrival_time_raw,
    (SPLIT_PART(st.arrival_time, ':', 1)::int * 3600
   + SPLIT_PART(st.arrival_time, ':', 2)::int * 60
   + SPLIT_PART(st.arrival_time, ':', 3)::int)  AS arrival_time_seconds,
    (SPLIT_PART(st.arrival_time, ':', 1)::int >= 24) AS is_after_midnight
FROM {{ source('raw', 'raw_stop_times') }} st
JOIN {{ source('raw', 'raw_trips') }} t
    ON st.trip_id = t.trip_id
