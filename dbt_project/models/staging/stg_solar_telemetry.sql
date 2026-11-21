WITH raw_solar AS (
    SELECT *
    FROM {{ source('raw_data', 'raw_solar_telemetry') }}
)

SELECT
    panel_id,
    timestamp AS telemetry_time,
    irradiance_w_m2,
    panel_temp_c,
    power_output_kw,
    inverter_status,
    dc_voltage,
    _loaded_at,
    _source_file
FROM raw_solar
