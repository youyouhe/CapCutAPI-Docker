#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度器
用于管理定时清理任务等周期性任务
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Callable, Optional
from minio_cleanup import cleanup_old_drafts_safe
from settings.local import MINIO_CONFIG, MINIO_CLEANUP_CONFIG

# 配置日志
logger = logging.getLogger('flask_video_generator')

class TaskScheduler:
    """
    简单的定时任务调度器
    """

    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False
        self.scheduler_thread = None
        self.lock = threading.Lock()

    def add_task(self, name: str, func: Callable, interval_hours: int = 24,
                 start_immediately: bool = False, **kwargs):
        """
        添加定时任务

        Args:
            name: 任务名称
            func: 任务函数
            interval_hours: 执行间隔（小时）
            start_immediately: 是否立即开始
            **kwargs: 传递给任务函数的参数
        """
        with self.lock:
            self.tasks[name] = {
                'func': func,
                'interval': timedelta(hours=interval_hours),
                'last_run': None,
                'next_run': datetime.now() if start_immediately else datetime.now() + timedelta(hours=interval_hours),
                'kwargs': kwargs,
                'enabled': True,
                'run_count': 0,
                'last_error': None
            }

        logger.info(f"Added scheduled task: {name} (interval: {interval_hours}h)")

    def remove_task(self, name: str):
        """
        移除定时任务
        """
        with self.lock:
            if name in self.tasks:
                del self.tasks[name]
                logger.info(f"Removed scheduled task: {name}")
            else:
                logger.warning(f"Task not found: {name}")

    def enable_task(self, name: str, enabled: bool = True):
        """
        启用/禁用任务
        """
        with self.lock:
            if name in self.tasks:
                self.tasks[name]['enabled'] = enabled
                logger.info(f"Task {name} {'enabled' if enabled else 'disabled'}")
            else:
                logger.warning(f"Task not found: {name}")

    def get_task_status(self, name: str) -> Optional[Dict]:
        """
        获取任务状态
        """
        with self.lock:
            return self.tasks.get(name)

    def get_all_tasks_status(self) -> Dict[str, Dict]:
        """
        获取所有任务状态
        """
        with self.lock:
            return {name: {
                'enabled': task['enabled'],
                'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                'next_run': task['next_run'].isoformat() if task['next_run'] else None,
                'run_count': task['run_count'],
                'last_error': task['last_error'],
                'interval_hours': task['interval'].total_seconds() / 3600
            } for name, task in self.tasks.items()}

    def start(self):
        """
        启动调度器
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Task scheduler started")

    def stop(self):
        """
        停止调度器
        """
        if not self.running:
            logger.warning("Scheduler is not running")
            return

        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Task scheduler stopped")

    def _run_scheduler(self):
        """
        调度器主循环
        """
        while self.running:
            try:
                current_time = datetime.now()

                with self.lock:
                    for name, task in self.tasks.items():
                        if not task['enabled']:
                            continue

                        if current_time >= task['next_run']:
                            self._run_task(name, task)

                # 每分钟检查一次
                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)

    def _run_task(self, name: str, task: Dict):
        """
        执行单个任务
        """
        logger.info(f"Running scheduled task: {name}")

        try:
            # 运行任务函数
            result = task['func'](**task['kwargs'])

            # 更新任务状态
            task['last_run'] = datetime.now()
            task['next_run'] = task['last_run'] + task['interval']
            task['run_count'] += 1
            task['last_error'] = None

            logger.info(f"Task {name} completed successfully. "
                       f"Run count: {task['run_count']}, "
                       f"Next run: {task['next_run']}")

        except Exception as e:
            task['last_error'] = str(e)
            logger.error(f"Task {name} failed: {e}")

# 全局调度器实例
scheduler = TaskScheduler()

def init_scheduler():
    """
    初始化调度器并添加默认任务
    """
    global scheduler

    # 检查MinIO配置和清理配置
    if (MINIO_CONFIG and MINIO_CONFIG.get('endpoint') and
        MINIO_CLEANUP_CONFIG and MINIO_CLEANUP_CONFIG.get('enabled')):

        # 添加MinIO清理任务
        scheduler.add_task(
            name='minio_cleanup',
            func=cleanup_old_drafts_safe,
            interval_hours=MINIO_CLEANUP_CONFIG.get('interval_hours', 24),
            start_immediately=False,  # 不立即开始，等第一个周期
            max_age_hours=MINIO_CLEANUP_CONFIG.get('max_age_hours', 48),
            dry_run=MINIO_CLEANUP_CONFIG.get('dry_run', True)
        )

        logger.info(f"MinIO cleanup task added to scheduler (interval: {MINIO_CLEANUP_CONFIG.get('interval_hours', 24)}h, "
                   f"max_age: {MINIO_CLEANUP_CONFIG.get('max_age_hours', 48)}h, "
                   f"dry_run: {MINIO_CLEANUP_CONFIG.get('dry_run', True)})")
    else:
        if not MINIO_CONFIG or not MINIO_CONFIG.get('endpoint'):
            logger.info("MinIO not configured, skipping cleanup task")
        elif not MINIO_CLEANUP_CONFIG or not MINIO_CLEANUP_CONFIG.get('enabled'):
            logger.info("MinIO cleanup disabled in configuration, skipping cleanup task")

    # 启动调度器
    scheduler.start()
    logger.info("Task scheduler initialized and started")

def get_scheduler_status() -> Dict:
    """
    获取调度器状态
    """
    return {
        'running': scheduler.running,
        'tasks': scheduler.get_all_tasks_status()
    }

def add_custom_task(name: str, func: Callable, interval_hours: int, **kwargs):
    """
    添加自定义任务
    """
    scheduler.add_task(name, func, interval_hours, **kwargs)

def remove_task(name: str):
    """
    移除任务
    """
    scheduler.remove_task(name)

def enable_task(name: str, enabled: bool = True):
    """
    启用/禁用任务
    """
    scheduler.enable_task(name, enabled)

if __name__ == "__main__":
    # 测试调度器
    logging.basicConfig(level=logging.INFO)

    # 初始化调度器
    init_scheduler()

    try:
        # 保持程序运行
        while True:
            time.sleep(60)
            status = get_scheduler_status()
            print(f"Scheduler status: {status}")
    except KeyboardInterrupt:
        print("\nShutting down scheduler...")
        scheduler.stop()