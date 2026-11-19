import os
import time
import glob
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import argparse

load_dotenv()

DATA_DIR = os.getenv('SIMULATOR_DATA_DIR', '../data')
BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(f"Failed to upload {file_name}: {e}")
        return False
    return True

def sync_directory(watch=False):
    if not BUCKET_NAME:
        print("Error: S3_BUCKET_NAME is not set.")
        return

    raw_dir = os.path.join(DATA_DIR, 'raw')
    if not os.path.exists(raw_dir):
        print(f"Data directory {raw_dir} does not exist.")
        return

    print(f"Syncing data from {raw_dir} to s3://{BUCKET_NAME}/raw/...")
    uploaded_files = set()

    while True:
        # Find all parquet files
        search_pattern = os.path.join(raw_dir, '**', '*.parquet')
        all_files = glob.glob(search_pattern, recursive=True)
        
        for local_file in all_files:
            if local_file not in uploaded_files:
                # Calculate S3 object key (e.g. raw/wind_telemetry/dt=.../hour=.../file.parquet)
                relative_path = os.path.relpath(local_file, DATA_DIR)
                # Ensure using forward slashes for S3 keys
                s3_key = relative_path.replace('\\', '/')
                
                print(f"Uploading {s3_key}...")
                success = upload_file(local_file, BUCKET_NAME, s3_key)
                
                if success:
                    uploaded_files.add(local_file)

        if not watch:
            print("Sync complete.")
            break
            
        time.sleep(10)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload simulator data to S3')
    parser.add_argument('--watch', action='store_true', help='Watch directory for new files continuously')
    args = parser.parse_args()
    
    sync_directory(watch=args.watch)
