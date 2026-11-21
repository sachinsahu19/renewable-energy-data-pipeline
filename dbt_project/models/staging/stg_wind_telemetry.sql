WITH raw_wind AS (
    SELECT *
    FROM {{ source('raw_data', 'raw_wind_telemetry') }}
)

SELECT
    turbine_id,
    timestamp AS telemetry_time,
    wind_speed_mps,
    blade_rpm,
    power_output_kw,
    vibration_mm_s,
    gearbox_temp_c,
    status,
    _loaded_at,
    _source_file
FROM raw_wind
