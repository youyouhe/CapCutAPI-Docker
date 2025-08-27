
import oss2
import os
from minio import Minio
from urllib.parse import urljoin
from settings.local import OSS_CONFIG, MP4_OSS_CONFIG, MINIO_CONFIG

def upload_to_oss(path):
    # Check if MinIO configuration exists and is properly configured
    if MINIO_CONFIG and isinstance(MINIO_CONFIG, dict) and MINIO_CONFIG.get('endpoint'):
        return upload_to_minio(path)
    else:
        # Create OSS client
        auth = oss2.Auth(OSS_CONFIG['access_key_id'], OSS_CONFIG['access_key_secret'])
        bucket = oss2.Bucket(auth, OSS_CONFIG['endpoint'], OSS_CONFIG['bucket_name'])
        
        # Upload file
        object_name = os.path.basename(path)
        bucket.put_object_from_file(object_name, path)
        
        # Generate signed URL (valid for 24 hours)
        url = bucket.sign_url('GET', object_name, 24 * 60 * 60)
        
        # Clean up temporary file
        os.remove(path)
        
        return url

def upload_to_minio(path):
    """Upload file to MinIO storage"""
    try:
        print(f"Starting MinIO upload for file: {path}")
        print(f"MinIO config: {MINIO_CONFIG}")
        
        # Create MinIO client
        client = Minio(
            MINIO_CONFIG['endpoint'].replace('http://', '').replace('https://', ''),
            access_key=MINIO_CONFIG['access_key'],
            secret_key=MINIO_CONFIG['secret_key'],
            secure=MINIO_CONFIG['endpoint'].startswith('https://')
        )
        
        print(f"MinIO client created successfully")
        
        # Check if bucket exists, create if it doesn't
        bucket_name = MINIO_CONFIG['bucket_name']
        if not client.bucket_exists(bucket_name):
            print(f"Bucket {bucket_name} does not exist, creating it...")
            client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} created successfully")
        else:
            print(f"Bucket {bucket_name} already exists")
        
        # Upload file
        object_name = os.path.basename(path)
        print(f"Uploading object: {object_name} from path: {path}")
        result = client.fput_object(
            MINIO_CONFIG['bucket_name'],
            object_name,
            path
        )
        
        print(f"File uploaded successfully. Result: {result}")
        
        # Generate presigned URL (valid for 24 hours)
        from datetime import timedelta
        url = client.presigned_get_object(
            MINIO_CONFIG['bucket_name'],
            object_name,
            expires=timedelta(hours=24)
        )
        
        print(f"Presigned URL generated: {url}")
        
        # Clean up temporary file
        os.remove(path)
        print(f"Temporary file cleaned up: {path}")
        
        return url
    except Exception as e:
        print(f"MinIO upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback to local file if upload fails
        return f"file://{os.path.abspath(path)}"

def upload_mp4_to_oss(path):
    """Special method for uploading MP4 files, using custom domain and v4 signature"""
    # Directly use credentials from the configuration file
    auth = oss2.AuthV4(MP4_OSS_CONFIG['access_key_id'], MP4_OSS_CONFIG['access_key_secret'])
    
    # Create OSS client with custom domain
    bucket = oss2.Bucket(
        auth, 
        MP4_OSS_CONFIG['endpoint'], 
        MP4_OSS_CONFIG['bucket_name'], 
        region=MP4_OSS_CONFIG['region'], 
        is_cname=True
    )
    
    # Upload file
    object_name = os.path.basename(path)
    bucket.put_object_from_file(object_name, path)
    
    # Generate pre-signed URL (valid for 24 hours), set slash_safe to True to avoid path escaping
    url = bucket.sign_url('GET', object_name, 24 * 60 * 60, slash_safe=True)
    
    # Clean up temporary file
    os.remove(path)
    
    return url