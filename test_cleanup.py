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
    """测试清理功能（试运行模式）"""
    print("\n=== 测试清理功能（试运行模式） ===")

    try:
        from minio_cleanup import cleanup_old_drafts_safe

        result = cleanup_old_drafts_safe(
            max_age_hours=1,  # 测试时使用较短的时间
            dry_run=True
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
        from scheduler import TaskScheduler, scheduler

        # 创建测试任务
        test_results = []

        def test_task(task_name):
            logger.info(f"执行测试任务: {task_name}")
            test_results.append(task_name)
            return f"Task {task_name} completed"

        scheduler.add_task(
            name='test_cleanup',
            func=test_task,
            interval_hours=1,
            start_immediately=True,
            task_name='test_cleanup'
        )

        print("测试任务已添加到调度器")

        # 获取调度器状态
        status = scheduler.get_all_tasks_status()
        print(f"调度器状态: {json.dumps(status, indent=2, default=str)}")

        # 等待任务执行
        import time
        time.sleep(2)

        print(f"测试任务执行结果: {test_results}")

        # 清理测试任务
        scheduler.remove_task('test_cleanup')

        return len(test_results) > 0

    except Exception as e:
        print(f"调度器测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")

    # 这里只是检查API端点是否正确定义，不实际调用
    try:
        import capcut_server

        # 检查是否有清理相关的路由
        routes = []
        for rule in capcut_server.app.url_map.iter_rules():
            if 'cleanup' in rule.rule:
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'rule': rule.rule
                })

        print(f"发现的清理相关API端点: {json.dumps(routes, indent=2)}")

        return len(routes) >= 2  # 应该至少有两个清理相关的端点

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