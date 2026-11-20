USE DATABASE RENEWABLE_ENERGY;
USE SCHEMA RAW;

-- Manual COPY INTO statements (Fallback)
-- Wind
COPY INTO raw_wind_telemetry
FROM (
  SELECT 
    $1:turbine_id::VARCHAR,
    $1:timestamp::TIMESTAMP_NTZ,
    $1:wind_speed_mps::FLOAT,
    $1:blade_rpm::FLOAT,
    $1:power_output_kw::FLOAT,
    $1:vibration_mm_s::FLOAT,
    $1:gearbox_temp_c::FLOAT,
    $1:status::VARCHAR,
    CURRENT_TIMESTAMP(),
    METADATA$FILENAME
  FROM @s3_raw_data_stage/raw/wind_telemetry/
)
FILE_FORMAT = (TYPE = PARQUET);

-- Solar
COPY INTO raw_solar_telemetry
FROM (
  SELECT 
    $1:panel_id::VARCHAR,
    $1:timestamp::TIMESTAMP_NTZ,
    $1:irradiance_w_m2::FLOAT,
    $1:panel_temp_c::FLOAT,
    $1:power_output_kw::FLOAT,
    $1:inverter_status::VARCHAR,
    $1:dc_voltage::FLOAT,
    CURRENT_TIMESTAMP(),
    METADATA$FILENAME
  FROM @s3_raw_data_stage/raw/solar_telemetry/
)
FILE_FORMAT = (TYPE = PARQUET);

-- Battery
COPY INTO raw_battery_telemetry
FROM (
  SELECT 
    $1:battery_id::VARCHAR,
    $1:timestamp::TIMESTAMP_NTZ,
    $1:charge_pct::FLOAT,
    $1:charge_rate_kw::FLOAT,
    $1:cycles_count::INTEGER,
    $1:temp_c::FLOAT,
    CURRENT_TIMESTAMP(),
    METADATA$FILENAME
  FROM @s3_raw_data_stage/raw/battery_telemetry/
)
FILE_FORMAT = (TYPE = PARQUET);


-- Snowpipe Definitions for continuous auto-ingestion
CREATE OR REPLACE PIPE wind_telemetry_pipe AUTO_INGEST = TRUE AS
COPY INTO raw_wind_telemetry
FROM (
  SELECT 
    $1:turbine_id::VARCHAR,
    $1:timestamp::TIMESTAMP_NTZ,
    $1:wind_speed_mps::FLOAT,
    $1:blade_rpm::FLOAT,
    $1:power_output_kw::FLOAT,
    $1:vibration_mm_s::FLOAT,
    $1:gearbox_temp_c::FLOAT,
    $1:status::VARCHAR,
    CURRENT_TIMESTAMP(),
    METADATA$FILENAME
  FROM @s3_raw_data_stage/raw/wind_telemetry/
)
FILE_FORMAT = (TYPE = PARQUET);

CREATE OR REPLACE PIPE solar_telemetry_pipe AUTO_INGEST = TRUE AS
COPY INTO raw_solar_telemetry
FROM (
  SELECT 
    $1:panel_id::VARCHAR,
    $1:timestamp::TIMESTAMP_NTZ,
    $1:irradiance_w_m2::FLOAT,
    $1:panel_temp_c::FLOAT,
    $1:power_output_kw::FLOAT,
    $1:inverter_status::VARCHAR,
    $1:dc_voltage::FLOAT,
    CURRENT_TIMESTAMP(),
    METADATA$FILENAME
  FROM @s3_raw_data_stage/raw/solar_telemetry/
)
FILE_FORMAT = (TYPE = PARQUET);

CREATE OR REPLACE PIPE battery_telemetry_pipe AUTO_INGEST = TRUE AS
COPY INTO raw_battery_telemetry
FROM (
  SELECT 
    $1:battery_id::VARCHAR,
    $1:timestamp::TIMESTAMP_NTZ,
    $1:charge_pct::FLOAT,
    $1:charge_rate_kw::FLOAT,
    $1:cycles_count::INTEGER,
    $1:temp_c::FLOAT,
    CURRENT_TIMESTAMP(),
    METADATA$FILENAME
  FROM @s3_raw_data_stage/raw/battery_telemetry/
)
FILE_FORMAT = (TYPE = PARQUET);

-- To enable Auto-Ingest, you will need to get the SQS queue ARN for each pipe 
-- and configure it as an event notification on the S3 bucket:
-- SHOW PIPES;
