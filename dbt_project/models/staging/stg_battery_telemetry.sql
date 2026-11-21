WITH raw_battery AS (
    SELECT *
    FROM {{ source('raw_data', 'raw_battery_telemetry') }}
)

SELECT
    battery_id,
    timestamp AS telemetry_time,
    charge_pct,
    charge_rate_kw,
    cycles_count,
    temp_c,
    _loaded_at,
    _source_file
FROM raw_battery
