# Renewable Energy Grid - dbt Project

This project transforms the raw telemetry data from Snowflake into analytical models.

## Models
1. **Staging**: `stg_wind_telemetry`, `stg_solar_telemetry`, `stg_battery_telemetry` - cleans and normalizes column names.
2. **Intermediate**: `int_grid_power_summary` - Joins all telemetry streams by time.
3. **Marts**: `fct_grid_performance_hourly` - Aggregates data hourly for dashboard consumption.

## Setup
Run `dbt deps`
Run `dbt build` to run models and tests.
