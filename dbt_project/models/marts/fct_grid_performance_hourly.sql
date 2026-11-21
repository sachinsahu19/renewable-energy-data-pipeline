WITH hourly_summary AS (
    SELECT
        DATE_TRUNC('hour', telemetry_time) AS telemetry_hour,
        AVG(wind_power_kw) AS avg_wind_power_kw,
        AVG(solar_power_kw) AS avg_solar_power_kw,
        AVG(battery_charge_kw) AS avg_battery_charge_kw,
        AVG(total_power_kw) AS avg_total_power_kw
    FROM {{ ref('int_grid_power_summary') }}
    GROUP BY 1
)

SELECT
    telemetry_hour,
    ROUND(avg_wind_power_kw, 2) AS avg_wind_power_kw,
    ROUND(avg_solar_power_kw, 2) AS avg_solar_power_kw,
    ROUND(avg_battery_charge_kw, 2) AS avg_battery_charge_kw,
    ROUND(avg_total_power_kw, 2) AS avg_total_power_kw
FROM hourly_summary
ORDER BY telemetry_hour DESC
