WITH wind AS (
    SELECT
        telemetry_time,
        power_output_kw AS wind_power_kw
    FROM {{ ref('stg_wind_telemetry') }}
),
solar AS (
    SELECT
        telemetry_time,
        power_output_kw AS solar_power_kw
    FROM {{ ref('stg_solar_telemetry') }}
),
battery AS (
    SELECT
        telemetry_time,
        charge_rate_kw AS battery_charge_kw
    FROM {{ ref('stg_battery_telemetry') }}
)

SELECT
    w.telemetry_time,
    COALESCE(w.wind_power_kw, 0) AS wind_power_kw,
    COALESCE(s.solar_power_kw, 0) AS solar_power_kw,
    COALESCE(b.battery_charge_kw, 0) AS battery_charge_kw,
    (COALESCE(w.wind_power_kw, 0) + COALESCE(s.solar_power_kw, 0) + COALESCE(b.battery_charge_kw, 0)) AS total_power_kw
FROM wind w
FULL OUTER JOIN solar s ON w.telemetry_time = s.telemetry_time
FULL OUTER JOIN battery b ON w.telemetry_time = b.telemetry_time
