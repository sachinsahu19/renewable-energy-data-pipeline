import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv('../.env')

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        role=os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
    )

def execute_sql_file(conn, file_path):
    print(f"Executing {file_path}...")
    with open(file_path, 'r') as f:
        # Split by semicolon to execute multiple statements in one file
        sql_script = f.read()
        statements = sql_script.split(';')
        
        cursor = conn.cursor()
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"Error executing statement:\n{statement}\nError: {e}")
                    raise e
        cursor.close()
        print(f"Successfully executed {file_path}")

if __name__ == '__main__':
    conn = get_connection()
    try:
        execute_sql_file(conn, '01_setup_integration_stage.sql')
        execute_sql_file(conn, '02_raw_tables.sql')
        execute_sql_file(conn, '03_snowpipe_copy.sql')
    finally:
        conn.close()
