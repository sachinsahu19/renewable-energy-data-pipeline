USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS RENEWABLE_ENERGY;
USE DATABASE RENEWABLE_ENERGY;
CREATE SCHEMA IF NOT EXISTS RAW;
USE SCHEMA RAW;

-- 1. Create a Storage Integration to allow Snowflake to access the S3 bucket
CREATE STORAGE INTEGRATION IF NOT EXISTS s3_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::998038918532:role/snowflake_access_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://renewable-energy-grid-raw/');

-- Retrieve the IAM user ARN and external ID that Snowflake created for this integration
-- You will need to use these to configure the Trust Policy in your AWS IAM Role
DESC INTEGRATION s3_integration;

-- 2. Create the External Stage
CREATE OR REPLACE STAGE s3_raw_data_stage
  URL = 's3://renewable-energy-grid-raw/'
  STORAGE_INTEGRATION = s3_integration
  FILE_FORMAT = (TYPE = PARQUET);
