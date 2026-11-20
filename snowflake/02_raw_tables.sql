USE DATABASE RENEWABLE_ENERGY;
USE SCHEMA RAW;

-- Wind Telemetry
CREATE OR REPLACE TABLE raw_wind_telemetry (
    turbine_id VARCHAR(50),
    timestamp TIMESTAMP_NTZ,
    wind_speed_mps FLOAT,
    blade_rpm FLOAT,
    power_output_kw FLOAT,
    vibration_mm_s FLOAT,
    gearbox_temp_c FLOAT,
    status VARCHAR(50),
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file VARCHAR(255)
);

-- Solar Telemetry
CREATE OR REPLACE TABLE raw_solar_telemetry (
    panel_id VARCHAR(50),
    timestamp TIMESTAMP_NTZ,
    irradiance_w_m2 FLOAT,
    panel_temp_c FLOAT,
    power_output_kw FLOAT,
    inverter_status VARCHAR(50),
    dc_voltage FLOAT,
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file VARCHAR(255)
);

-- Battery Telemetry
CREATE OR REPLACE TABLE raw_battery_telemetry (
    battery_id VARCHAR(50),
    timestamp TIMESTAMP_NTZ,
    charge_pct FLOAT,
    charge_rate_kw FLOAT,
    cycles_count INTEGER,
    temp_c FLOAT,
    _loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    _source_file VARCHAR(255)
);
