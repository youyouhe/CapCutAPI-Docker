"""
本地配置模块，用于从本地配置文件中加载配置
支持环境变量和配置文件的加载
"""

import os
import json5  # 替换原来的json模块

# 配置文件路径
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

# 从环境变量加载配置（优先级最高）
IS_CAPCUT_ENV = os.getenv('CAPCUT_ENV', 'true').lower() == 'true'
DRAFT_DOMAIN = os.getenv('DRAFT_DOMAIN', 'https://www.install-ai-guider.top')
PREVIEW_ROUTER = os.getenv('PREVIEW_ROUTER', '/draft/downloader')
IS_UPLOAD_DRAFT = os.getenv('IS_UPLOAD_DRAFT', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', '9000'))
SECRET_KEY = os.getenv('SECRET_KEY', '')

# MinIO配置
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', '')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', '')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', '')

# OSS配置
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT', '')
OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID', '')
OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET', '')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME', '')

# MP4 OSS配置
MP4_OSS_ENDPOINT = os.getenv('MP4_OSS_ENDPOINT', '')
MP4_OSS_ACCESS_KEY_ID = os.getenv('MP4_OSS_ACCESS_KEY_ID', '')
MP4_OSS_ACCESS_KEY_SECRET = os.getenv('MP4_OSS_ACCESS_KEY_SECRET', '')
MP4_OSS_BUCKET_NAME = os.getenv('MP4_OSS_BUCKET_NAME', '')
MP4_OSS_REGION = os.getenv('MP4_OSS_REGION', '')

# 配置变量
OSS_CONFIG = []
MP4_OSS_CONFIG = []

# MinIO配置
MINIO_CONFIG = {
    "endpoint": MINIO_ENDPOINT,
    "access_key": MINIO_ACCESS_KEY,
    "secret_key": MINIO_SECRET_KEY,
    "bucket_name": MINIO_BUCKET_NAME
}

# 如果环境变量中有OSS配置，则使用环境变量
if OSS_ENDPOINT and OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET and OSS_BUCKET_NAME:
    OSS_CONFIG = [{
        "bucket_name": OSS_BUCKET_NAME,
        "access_key_id": OSS_ACCESS_KEY_ID,
        "access_key_secret": OSS_ACCESS_KEY_SECRET,
        "endpoint": OSS_ENDPOINT
    }]

# 如果环境变量中有MP4 OSS配置，则使用环境变量
if MP4_OSS_ENDPOINT and MP4_OSS_ACCESS_KEY_ID and MP4_OSS_ACCESS_KEY_SECRET and MP4_OSS_BUCKET_NAME:
    MP4_OSS_CONFIG = [{
        "bucket_name": MP4_OSS_BUCKET_NAME,
        "access_key_id": MP4_OSS_ACCESS_KEY_ID,
        "access_key_secret": MP4_OSS_ACCESS_KEY_SECRET,
        "region": MP4_OSS_REGION,
        "endpoint": MP4_OSS_ENDPOINT
    }]

# 尝试加载本地配置文件（优先级低于环境变量）
if os.path.exists(CONFIG_FILE_PATH):
    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            # 使用json5.load替代json.load
            local_config = json5.load(f)
            
            # 只在环境变量未设置时使用配置文件的值
            if 'CAPCUT_ENV' not in os.environ and "is_capcut_env" in local_config:
                IS_CAPCUT_ENV = local_config["is_capcut_env"]
            
            if 'DRAFT_DOMAIN' not in os.environ and "draft_domain" in local_config:
                DRAFT_DOMAIN = local_config["draft_domain"]

            if 'PORT' not in os.environ and "port" in local_config:
                PORT = local_config["port"]

            if 'PREVIEW_ROUTER' not in os.environ and "preview_router" in local_config:
                PREVIEW_ROUTER = local_config["preview_router"]
            
            if 'IS_UPLOAD_DRAFT' not in os.environ and "is_upload_draft" in local_config:
                IS_UPLOAD_DRAFT = local_config["is_upload_draft"]

            if 'SECRET_KEY' not in os.environ and "secret_key" in local_config:
                SECRET_KEY = local_config["secret_key"]

            # 如果环境变量中没有OSS配置，则使用配置文件的值
            if not OSS_CONFIG and "oss_config" in local_config:
                OSS_CONFIG = local_config["oss_config"]
            
            # 如果环境变量中没有MP4 OSS配置，则使用配置文件的值
            if not MP4_OSS_CONFIG and "mp4_oss_config" in local_config:
                MP4_OSS_CONFIG = local_config["mp4_oss_config"]
                
            # 如果MinIO配置为空且配置文件中有值，则使用配置文件的值
            if not MINIO_CONFIG["endpoint"] and "minio_config" in local_config:
                MINIO_CONFIG = local_config["minio_config"]

    except Exception as e:
        # 配置文件加载失败，使用默认配置
        pass

# 导出所有配置变量
__all__ = [
    'IS_CAPCUT_ENV',
    'DRAFT_DOMAIN',
    'PREVIEW_ROUTER',
    'IS_UPLOAD_DRAFT',
    'PORT',
    'SECRET_KEY',
    'OSS_CONFIG',
    'MP4_OSS_CONFIG',
    'MINIO_CONFIG'
]
