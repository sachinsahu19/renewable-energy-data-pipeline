import snowflake from 'snowflake-sdk';
import * as dotenv from 'dotenv';
import path from 'path';

// Load env from the root directory
dotenv.config({ path: path.resolve(process.cwd(), '../.env') });

export const getSnowflakeConnection = () => {
  return snowflake.createConnection({
    account: process.env.SNOWFLAKE_ACCOUNT || '',
    username: process.env.SNOWFLAKE_USER || '',
    password: process.env.SNOWFLAKE_PASSWORD || '',
    role: process.env.SNOWFLAKE_ROLE || 'ACCOUNTADMIN',
    warehouse: process.env.SNOWFLAKE_WAREHOUSE || 'COMPUTE_WH',
    database: process.env.SNOWFLAKE_DATABASE || 'RENEWABLE_ENERGY',
    schema: process.env.SNOWFLAKE_SCHEMA || 'RAW'
  });
};

export const executeQuery = (queryText: string): Promise<any[]> => {
  return new Promise((resolve, reject) => {
    const connection = getSnowflakeConnection();
    
    connection.connect((err, conn) => {
      if (err) {
        console.error('Unable to connect: ' + err.message);
        reject(err);
        return;
      }

      conn.execute({
        sqlText: queryText,
        complete: (err, stmt, rows) => {
          if (err) {
            console.error('Failed to execute statement due to the following error: ' + err.message);
            reject(err);
          } else {
            resolve(rows || []);
          }
          // Note: connection should ideally be closed or pooled in a real prod app
        }
      });
    });
  });
};
