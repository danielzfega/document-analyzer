import boto3
from config import settings
from botocore.exceptions import NoCredentialsError
from botocore.client import Config

# Minio client setup
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.MINIO_ENDPOINT,
    aws_access_key_id=settings.MINIO_ACCESS_KEY,
    aws_secret_access_key=settings.MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1' # Minio default region often needed for compat
)

def upload_file_to_minio(file_obj, object_name):
    try:
        s3_client.upload_fileobj(file_obj, settings.MINIO_BUCKET_NAME, object_name)
        return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{object_name}"
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except Exception as e:
        print(f"Error uploading to Minio: {e}")
        return None
