
import oss2
import os
from settings.local import OSS_CONFIG, MP4_OSS_CONFIG

def upload_to_oss(path):
    # 创建OSS客户端
    auth = oss2.Auth(OSS_CONFIG['access_key_id'], OSS_CONFIG['access_key_secret'])
    bucket = oss2.Bucket(auth, OSS_CONFIG['endpoint'], OSS_CONFIG['bucket_name'])
    
    # 上传文件
    object_name = os.path.basename(path)
    bucket.put_object_from_file(object_name, path)
    
    # 生成签名URL（24小时有效）
    url = bucket.sign_url('GET', object_name, 24 * 60 * 60)
    
    # 清理临时文件
    os.remove(path)
    
    return url

def upload_mp4_to_oss(path):
    """专门用于上传MP4文件的方法，使用自定义域名和v4签名"""
    # 直接使用配置文件中的凭证
    auth = oss2.AuthV4(MP4_OSS_CONFIG['access_key_id'], MP4_OSS_CONFIG['access_key_secret'])
    
    # 创建OSS客户端，使用自定义域名
    bucket = oss2.Bucket(
        auth, 
        MP4_OSS_CONFIG['endpoint'], 
        MP4_OSS_CONFIG['bucket_name'], 
        region=MP4_OSS_CONFIG['region'], 
        is_cname=True
    )
    
    # 上传文件
    object_name = os.path.basename(path)
    bucket.put_object_from_file(object_name, path)
    
    # 生成预签名URL（24小时有效），设置slash_safe为True避免路径转义
    url = bucket.sign_url('GET', object_name, 24 * 60 * 60, slash_safe=True)
    
    # 清理临时文件
    os.remove(path)
    
    return url