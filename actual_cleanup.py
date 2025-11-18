#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际执行MinIO清理脚本
使用当前配置进行真实的文件清理
"""

import os
import logging
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数：实际执行清理"""
    print("="*60)
    print("🚀 实际执行MinIO文件清理")
    print("="*60)
    print(f"执行时间: {datetime.now()}")

    try:
        # 导入配置和清理函数
        from settings.local import MINIO_CLEANUP_CONFIG, MINIO_CONFIG
        from minio_cleanup import cleanup_old_drafts_safe

        # 显示当前配置
        print(f"\n📋 当前配置:")
        print(f"  - MinIO端点: {MINIO_CONFIG.get('endpoint', '未配置')}")
        print(f"  - 存储桶: {MINIO_CONFIG.get('bucket_name', '未配置')}")
        print(f"  - 清理启用: {MINIO_CLEANUP_CONFIG.get('enabled', False)}")
        print(f"  - 清理间隔: {MINIO_CLEANUP_CONFIG.get('interval_hours', 24)} 小时")
        print(f"  - 文件保留时间: {MINIO_CLEANUP_CONFIG.get('max_age_hours', 48)} 小时")
        print(f"  - 试运行模式: {MINIO_CLEANUP_CONFIG.get('dry_run', True)}")

        if not MINIO_CLEANUP_CONFIG.get('enabled', False):
            print("\n❌ 清理功能未启用！")
            print("请在 .env 文件中设置 MINIO_CLEANUP_ENABLED=true")
            return

        if MINIO_CLEANUP_CONFIG.get('dry_run', True):
            print("\n⚠️ 当前为试运行模式，不会实际删除文件")
            print("要启用实际删除，请在 .env 文件中设置 MINIO_CLEANUP_DRY_RUN=false")
        else:
            print("\n🔥 实际删除模式已启用！文件将被永久删除！")

        # 确认执行
        if not MINIO_CLEANUP_CONFIG.get('dry_run', True):
            confirm = input("\n❓ 确认要执行实际清理吗？(yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ 用户取消操作")
                return

        print(f"\n🧹 开始清理超过 {MINIO_CLEANUP_CONFIG.get('max_age_hours', 48)} 小时的文件...")

        # 执行清理
        result = cleanup_old_drafts_safe(
            max_age_hours=MINIO_CLEANUP_CONFIG.get('max_age_hours', 48),
            dry_run=MINIO_CLEANUP_CONFIG.get('dry_run', True)
        )

        # 显示结果
        print(f"\n📊 清理结果:")
        if result.get('success'):
            print(f"✅ 清理成功完成")
            print(f"  - 检查的文件数: {result.get('objects_checked', 0)}")
            print(f"  - 删除的文件数: {result.get('deleted_count', 0)}")
            print(f"  - 失败的文件数: {result.get('failed_count', 0)}")
            print(f"  - 释放空间: {result.get('total_size', 0)} 字节 "
                  f"({result.get('total_size', 0) / (1024**3):.2f} GB)")

            if result.get('failed_deletions'):
                print(f"  - 删除失败的文件: {result.get('failed_deletions')}")
        else:
            print(f"❌ 清理失败: {result.get('error', '未知错误')}")

    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保在正确的环境中运行此脚本")
    except Exception as e:
        print(f"❌ 执行清理时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()