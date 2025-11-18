#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinIO清理功能测试脚本
"""

import os
import logging
import json
from datetime import datetime, timezone, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_configuration():
    """测试配置加载"""
    print("=== 测试配置加载 ===")

    try:
        from settings.local import MINIO_CONFIG, MINIO_CLEANUP_CONFIG

        print(f"MinIO配置: {json.dumps(MINIO_CONFIG, indent=2)}")
        print(f"清理配置: {json.dumps(MINIO_CLEANUP_CONFIG, indent=2)}")

        return True
    except Exception as e:
        print(f"配置加载失败: {e}")
        return False

def test_minio_connection():
    """测试MinIO连接"""
    print("\n=== 测试MinIO连接 ===")

    try:
        from minio_cleanup import get_minio_client

        client = get_minio_client()
        if client:
            print("MinIO客户端创建成功")

            # 测试列出存储桶
            buckets = client.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            print(f"发现的存储桶: {bucket_names}")

            return True
        else:
            print("MinIO客户端创建失败")
            return False

    except Exception as e:
        print(f"MinIO连接测试失败: {e}")
        return False

def test_cleanup_dry_run():
    """测试清理功能"""
    print("\n=== 测试清理功能 ===")

    try:
        from minio_cleanup import cleanup_old_drafts_safe
        from settings.local import MINIO_CLEANUP_CONFIG

        # 使用配置中的参数，但为了测试安全，强制使用试运行模式
        use_dry_run = MINIO_CLEANUP_CONFIG.get('dry_run', True)
        max_age = MINIO_CLEANUP_CONFIG.get('max_age_hours', 48)

        print(f"当前配置: dry_run={use_dry_run}, max_age_hours={max_age}")

        # 测试时强制使用试运行模式和较短的时间限制
        result = cleanup_old_drafts_safe(
            max_age_hours=1,  # 测试时使用较短的时间限制
            dry_run=True      # 测试始终使用试运行模式确保安全
        )

        print(f"清理结果: {json.dumps(result, indent=2, default=str)}")

        return result.get('success', False)
    except Exception as e:
        print(f"清理测试失败: {e}")
        return False

def test_scheduler():
    """测试调度器"""
    print("\n=== 测试调度器 ===")

    try:
        from scheduler import TaskScheduler

        # 创建独立的测试调度器
        test_scheduler = TaskScheduler()

        # 创建测试任务
        test_results = []

        def test_task():
            logger.info("执行测试任务")
            test_results.append("test_executed")
            return "Test task completed"

        test_scheduler.add_task(
            name='test_cleanup',
            func=test_task,
            interval_hours=1,
            start_immediately=True
        )

        print("测试任务已添加到调度器")

        # 启动调度器
        test_scheduler.start()
        print("调度器已启动")

        # 获取调度器状态
        status = test_scheduler.get_all_tasks_status()
        print(f"调度器状态: {json.dumps(status, indent=2, default=str)}")

        # 等待任务执行
        import time
        print("等待任务执行...")
        time.sleep(3)  # 给更多时间让任务执行

        print(f"测试任务执行结果: {test_results}")

        # 停止调度器
        test_scheduler.stop()

        return len(test_results) > 0

    except Exception as e:
        print(f"调度器测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")

    try:
        # 检查清理相关的函数是否定义
        from minio_cleanup import cleanup_old_drafts_safe
        from scheduler import get_scheduler_status

        print("✅ 清理模块导入成功")

        # 检查配置
        from settings.local import MINIO_CLEANUP_CONFIG
        if MINIO_CLEANUP_CONFIG and MINIO_CLEANUP_CONFIG.get('enabled'):
            print("✅ 清理配置已启用")
        else:
            print("⚠️ 清理配置未启用")

        # 检查核心函数是否可调用
        cleanup_callable = callable(cleanup_old_drafts_safe)
        status_callable = callable(get_scheduler_status)

        print(f"✅ 清理函数可用: {cleanup_callable}")
        print(f"✅ 状态查询函数可用: {status_callable}")

        return cleanup_callable and status_callable

    except Exception as e:
        print(f"API端点测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始MinIO清理功能测试...")
    print(f"测试时间: {datetime.now()}")

    tests = [
        ("配置加载", test_configuration),
        ("MinIO连接", test_minio_connection),
        ("清理功能（试运行）", test_cleanup_dry_run),
        ("调度器", test_scheduler),
        ("API端点", test_api_endpoints)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            print(f"\n开始测试: {test_name}")
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
            print(f"{test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            results[test_name] = f"ERROR: {e}"
            print(f"{test_name}: 错误 - {e}")

    # 输出测试总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    for test_name, result in results.items():
        print(f"{test_name:20} : {result}")

    passed = sum(1 for result in results.values() if result == "PASS")
    total = len(results)

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查配置和环境")

if __name__ == "__main__":
    main()