import boto3
import os
from botocore.config import Config

def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('R2_ENDPOINT'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        config=Config(signature_version='s3v4'),
        region_name='auto'
    )

def upload_file_to_r2(file_bytes: bytes, filename: str, content_type: str = 'image/jpeg') -> str:
    client = get_r2_client()
    bucket = os.getenv('R2_BUCKET_NAME', 'wsm-platform-files')
    key = f"uploads/{filename}"
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"/uploads/{filename}"

def delete_file_from_r2(path: str):
    try:
        client = get_r2_client()
        bucket = os.getenv('R2_BUCKET_NAME', 'wsm-platform-files')
        key = path.lstrip('/')
        client.delete_object(Bucket=bucket, Key=key)
    except:
        pass
