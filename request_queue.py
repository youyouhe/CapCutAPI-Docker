import threading
import queue
import time
from typing import Dict, Any, Optional
import logging
from enum import Enum

# 导入配置
from queue_config import (
    QUEUE_MAX_SIZE,
    QUEUE_MAX_WORKERS,
    QUEUE_MAX_TASK_AGE,
    QUEUE_LOG_LEVEL
)

# 设置日志
logger = logging.getLogger('flask_video_generator')

# 设置队列专用日志器
queue_logger = logging.getLogger('request_queue')
queue_logger.setLevel(getattr(logging, QUEUE_LOG_LEVEL, logging.INFO))

class TaskStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class RequestQueue:
    """内存请求队列管理器"""

    def __init__(self, max_queue_size: int = None, max_workers: int = None):
        """
        初始化请求队列

        Args:
            max_queue_size: 队列最大长度，超过此长度的请求将被拒绝
            max_workers: 最大并发处理数
        """
        # 使用配置文件中的默认值
        self.task_queue = queue.Queue(maxsize=max_queue_size or QUEUE_MAX_SIZE)
        self.task_results: Dict[str, Dict[str, Any]] = {}
        self.max_workers = max_workers or QUEUE_MAX_WORKERS
        self.workers = []
        self.is_running = False
        self.lock = threading.Lock()

        # 启动工作线程
        self.start_workers()

    def start_workers(self):
        """启动工作线程"""
        if self.is_running:
            return

        self.is_running = True
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_thread,
                name=f"RequestQueue-Worker-{i+1}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)

        logger.info(f"Request queue started with {self.max_workers} workers, max queue size: {self.task_queue.maxsize}")

    def stop_workers(self):
        """停止工作线程"""
        self.is_running = False
        # 添加 None 值来唤醒所有工作线程
        for _ in range(self.max_workers):
            try:
                self.task_queue.put(None, timeout=1)
            except queue.Full:
                pass

        # 等待所有工作线程结束
        for worker in self.workers:
            worker.join(timeout=2)

        self.workers.clear()
        logger.info("Request queue stopped")

    def _worker_thread(self):
        """工作线程主函数"""
        while self.is_running:
            try:
                # 从队列获取任务，超时1秒
                task_item = self.task_queue.get(timeout=1)

                # 检查是否是停止信号
                if task_item is None:
                    self.task_queue.task_done()
                    break

                task_id, func, args, kwargs = task_item

                logger.info(f"Worker processing task: {task_id}")

                # 更新任务状态为处理中
                self._update_task_status(task_id, TaskStatus.PROCESSING, "开始处理任务...")

                try:
                    # 执行任务
                    result = func(*args, **kwargs)

                    # 更新任务状态为完成
                    self._update_task_status(task_id, TaskStatus.COMPLETED, "任务完成", result)
                    logger.info(f"Task {task_id} completed successfully")

                except Exception as e:
                    # 更新任务状态为失败
                    self._update_task_status(task_id, TaskStatus.FAILED, f"任务失败: {str(e)}", None)
                    logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)

                finally:
                    # 标记任务完成
                    self.task_queue.task_done()

            except queue.Empty:
                # 超时，继续循环
                continue
            except Exception as e:
                logger.error(f"Worker thread error: {str(e)}", exc_info=True)

    def submit_task(self, task_id: str, func, *args, **kwargs) -> bool:
        """
        提交任务到队列

        Args:
            task_id: 任务ID
            func: 要执行的函数
            args: 函数参数
            kwargs: 函数关键字参数

        Returns:
            bool: 是否成功提交到队列
        """
        try:
            # 检查任务是否已存在
            with self.lock:
                if task_id in self.task_results:
                    logger.warning(f"Task {task_id} already exists, skipping...")
                    return False

            # 尝试添加到队列
            self.task_queue.put((task_id, func, args, kwargs), timeout=0.1)

            # 更新任务状态为排队中
            self._update_task_status(task_id, TaskStatus.QUEUED, "任务已排队，等待处理...")

            logger.info(f"Task {task_id} submitted to queue")
            return True

        except queue.Full:
            logger.warning(f"Queue is full, rejecting task {task_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to submit task {task_id}: {str(e)}")
            return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            Dict: 任务状态信息，如果任务不存在返回None
        """
        with self.lock:
            return self.task_results.get(task_id)

    def _update_task_status(self, task_id: str, status: TaskStatus, message: str, result: Any = None):
        """更新任务状态"""
        with self.lock:
            self.task_results[task_id] = {
                "status": status.value,
                "message": message,
                "result": result,
                "timestamp": time.time()
            }

    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列信息"""
        return {
            "queue_size": self.task_queue.qsize(),
            "max_queue_size": self.task_queue.maxsize,
            "active_workers": len([w for w in self.workers if w.is_alive()]),
            "max_workers": self.max_workers,
            "total_tasks": len(self.task_results),
            "is_running": self.is_running
        }

    def clean_old_tasks(self, max_age: int = None):
        """
        清理旧任务结果

        Args:
            max_age: 任务结果保留时间（秒），默认使用配置文件中的值
        """
        current_time = time.time()
        max_age = max_age or QUEUE_MAX_TASK_AGE

        with self.lock:
            old_tasks = []
            for task_id, task_info in self.task_results.items():
                if current_time - task_info["timestamp"] > max_age:
                    old_tasks.append(task_id)

            for task_id in old_tasks:
                del self.task_results[task_id]

            if old_tasks:
                logger.info(f"Cleaned {len(old_tasks)} old tasks from queue")

# 创建全局队列实例
request_queue = RequestQueue()