#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinIO文件清理工具
用于定期清理超过48小时的draft文件
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from minio import Minio
from settings.local import MINIO_CONFIG

# 配置日志
logger = logging.getLogger('flask_video_generator')

def get_minio_client():
    """
    创建MinIO客户端连接
    """
    if not MINIO_CONFIG or not MINIO_CONFIG.get('endpoint'):
        logger.error("MinIO configuration not found")
        return None

    try:
        client = Minio(
            MINIO_CONFIG['endpoint'].replace('http://', '').replace('https://', ''),
            access_key=MINIO_CONFIG['access_key'],
            secret_key=MINIO_CONFIG['secret_key'],
            secure=MINIO_CONFIG['endpoint'].startswith('https://')
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create MinIO client: {e}")
        return None

def cleanup_old_drafts(bucket_name=None, max_age_hours=48, dry_run=False):
    """
    清理超过指定时间的draft文件

    Args:
        bucket_name: 存储桶名称，默认使用配置中的值
        max_age_hours: 最大保存时间（小时），默认48小时
        dry_run: 是否为试运行模式，True时不实际删除文件

    Returns:
        dict: 清理结果统计
    """
    if not MINIO_CONFIG:
        logger.error("MinIO configuration not available")
        return {
            'success': False,
            'error': 'MinIO configuration not available',
            'deleted_count': 0,
            'total_size': 0
        }

    if not bucket_name:
        bucket_name = MINIO_CONFIG['bucket_name']

    client = get_minio_client()
    if not client:
        return {
            'success': False,
            'error': 'Failed to create MinIO client',
            'deleted_count': 0,
            'total_size': 0
        }

    # 检查存储桶是否存在
    try:
        if not client.bucket_exists(bucket_name):
            logger.warning(f"Bucket {bucket_name} does not exist")
            return {
                'success': True,
                'message': f'Bucket {bucket_name} does not exist',
                'deleted_count': 0,
                'total_size': 0,
                'objects_checked': 0
            }
    except Exception as e:
        logger.error(f"Failed to check bucket existence: {e}")
        return {
            'success': False,
            'error': f'Failed to check bucket existence: {e}',
            'deleted_count': 0,
            'total_size': 0
        }

    # 计算时间阈值
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=max_age_hours)

    deleted_count = 0
    total_size = 0
    objects_checked = 0
    failed_deletions = []

    try:
        # 列出所有对象
        objects = client.list_objects(bucket_name, recursive=True)

        for obj in objects:
            objects_checked += 1

            # 跳过目录对象（以/结尾）
            if obj.object_name.endswith('/'):
                continue

            # 检查对象是否超过指定时间
            if obj.last_modified and obj.last_modified < time_threshold:
                obj_size = obj.size or 0
                total_size += obj_size

                if dry_run:
                    logger.info(f"[DRY RUN] Would delete: {obj.object_name} "
                              f"(age: {now - obj.last_modified}, size: {obj_size} bytes)")
                else:
                    try:
                        client.remove_object(bucket_name, obj.object_name)
                        logger.info(f"Deleted: {obj.object_name} "
                                  f"(age: {now - obj.last_modified}, size: {obj_size} bytes)")
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Failed to delete {obj.object_name}: {e}")
                        failed_deletions.append(obj.object_name)

        result_message = f"Cleanup completed. Checked {objects_checked} objects"
        if dry_run:
            result_message = f"[DRY RUN] {result_message}"

        logger.info(f"{result_message}, would delete {deleted_count + len(failed_deletions)} objects, "
                   f"total size: {total_size} bytes")

        return {
            'success': True,
            'deleted_count': deleted_count,
            'failed_count': len(failed_deletions),
            'failed_deletions': failed_deletions,
            'total_size': total_size,
            'objects_checked': objects_checked,
            'time_threshold': time_threshold.isoformat(),
            'dry_run': dry_run,
            'message': result_message
        }

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return {
            'success': False,
            'error': f'Error during cleanup: {e}',
            'deleted_count': deleted_count,
            'total_size': total_size,
            'objects_checked': objects_checked
        }

def cleanup_old_drafts_safe(bucket_name=None, max_age_hours=48, dry_run=True):
    """
    安全版本的清理函数，包含更多检查和日志

    Args:
        bucket_name: 存储桶名称
        max_age_hours: 最大保存时间（小时）
        dry_run: 是否为试运行模式，默认为True

    Returns:
        dict: 清理结果
    """
    logger.info(f"Starting MinIO cleanup (dry_run={dry_run}, max_age_hours={max_age_hours})")

    # 检查配置
    if not MINIO_CONFIG:
        logger.error("MinIO configuration not available")
        return {'success': False, 'error': 'MinIO configuration not available'}

    # 执行清理
    result = cleanup_old_drafts(bucket_name, max_age_hours, dry_run)

    # 记录结果
    if result['success']:
        logger.info(f"MinIO cleanup completed successfully. "
                   f"Deleted: {result['deleted_count']}, "
                   f"Failed: {result.get('failed_count', 0)}, "
                   f"Total size freed: {result['total_size']} bytes")
    else:
        logger.error(f"MinIO cleanup failed: {result.get('error', 'Unknown error')}")

    return result

if __name__ == "__main__":
    # 测试清理功能
    logging.basicConfig(level=logging.INFO)

    # 试运行模式
    print("Running MinIO cleanup in DRY RUN mode...")
    result = cleanup_old_drafts_safe(dry_run=True)
    print(f"Result: {result}")

    # 如果要实际执行，取消注释下面的代码
    # print("Running actual MinIO cleanup...")
    # result = cleanup_old_drafts_safe(dry_run=False)
    # print(f"Result: {result}")