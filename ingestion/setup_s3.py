import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def create_bucket():
    s3_client = boto3.client('s3')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    
    if not bucket_name:
        print("Error: S3_BUCKET_NAME is not set in environment.")
        return

    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Successfully created bucket: {bucket_name}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists and is owned by you.")
        elif error_code == 'BucketAlreadyExists':
            print(f"Bucket {bucket_name} already exists and is owned by someone else.")
        else:
            print(f"Failed to create bucket: {e}")

if __name__ == '__main__':
    create_bucket()
