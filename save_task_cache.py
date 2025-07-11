from collections import OrderedDict
import threading
from typing import Dict, Any

# 使用OrderedDict实现LRU缓存，限制最大数量为1000
DRAFT_TASKS: Dict[str, dict] = OrderedDict()  # 使用 Dict 进行类型提示
MAX_TASKS_CACHE_SIZE = 1000


def update_tasks_cache(task_id: str, task_status: dict) -> None:
    """更新任务状态LRU缓存
    
    :param task_id: 任务ID
    :param task_status: 任务状态信息字典
    """

    if task_id in DRAFT_TASKS:
        # 如果键存在，删除旧的项
        DRAFT_TASKS.pop(task_id)
    elif len(DRAFT_TASKS) >= MAX_TASKS_CACHE_SIZE:
        # 如果缓存已满，删除最久未使用的项（第一个项）
        DRAFT_TASKS.popitem(last=False)
    # 添加新项到末尾（最近使用）
    DRAFT_TASKS[task_id] = task_status

def update_task_field(task_id: str, field: str, value: Any) -> None:
    """更新任务状态中的单个字段
    
    :param task_id: 任务ID
    :param field: 要更新的字段名
    :param value: 字段的新值
    """
    if task_id in DRAFT_TASKS:
        # 复制当前状态，修改指定字段，然后更新缓存
        task_status = DRAFT_TASKS[task_id].copy()
        task_status[field] = value
        # 删除旧项并添加更新后的项
        DRAFT_TASKS.pop(task_id)
        DRAFT_TASKS[task_id] = task_status
    else:
        # 如果任务不存在，创建一个默认状态并设置指定字段
        task_status = {
            "status": "initialized",
            "message": "任务已初始化",
            "progress": 0,
            "completed_files": 0,
            "total_files": 0,
            "draft_url": ""
        }
        task_status[field] = value
        # 如果缓存已满，删除最久未使用的项
        if len(DRAFT_TASKS) >= MAX_TASKS_CACHE_SIZE:
            DRAFT_TASKS.popitem(last=False)
        # 添加新项
        DRAFT_TASKS[task_id] = task_status

def update_task_fields(task_id: str, **fields) -> None:
    """更新任务状态中的多个字段
    
    :param task_id: 任务ID
    :param fields: 要更新的字段及其值，以关键字参数形式提供
    """
    if task_id in DRAFT_TASKS:
        # 复制当前状态，修改指定字段，然后更新缓存
        task_status = DRAFT_TASKS[task_id].copy()
        for field, value in fields.items():
            task_status[field] = value
        # 删除旧项并添加更新后的项
        DRAFT_TASKS.pop(task_id)
        DRAFT_TASKS[task_id] = task_status
    else:
        # 如果任务不存在，创建一个默认状态并设置指定字段
        task_status = {
            "status": "initialized",
            "message": "任务已初始化",
            "progress": 0,
            "completed_files": 0,
            "total_files": 0,
            "draft_url": ""
        }
        for field, value in fields.items():
            task_status[field] = value
        # 如果缓存已满，删除最久未使用的项
        if len(DRAFT_TASKS) >= MAX_TASKS_CACHE_SIZE:
            DRAFT_TASKS.popitem(last=False)
        # 添加新项
        DRAFT_TASKS[task_id] = task_status

def increment_task_field(task_id: str, field: str, increment: int = 1) -> None:
    """增加任务状态中的数值字段
    
    :param task_id: 任务ID
    :param field: 要增加的字段名
    :param increment: 增加的值，默认为1
    """
    if task_id in DRAFT_TASKS:
        # 复制当前状态，增加指定字段，然后更新缓存
        task_status = DRAFT_TASKS[task_id].copy()
        if field in task_status and isinstance(task_status[field], (int, float)):
            task_status[field] += increment
        else:
            task_status[field] = increment
        # 删除旧项并添加更新后的项
        DRAFT_TASKS.pop(task_id)
        DRAFT_TASKS[task_id] = task_status

def get_task_status(task_id: str) -> dict:
    """获取任务状态
    
    :param task_id: 任务ID
    :return: 任务状态信息字典
    """
    task_status = DRAFT_TASKS.get(task_id, {
        "status": "not_found",
        "message": "任务不存在",
        "progress": 0,
        "completed_files": 0,
        "total_files": 0,
        "draft_url": ""
    })
    
    # 如果找到了任务，更新其在LRU缓存中的位置
    if task_id in DRAFT_TASKS:
        # 先删除，再添加到末尾，实现LRU更新
        update_tasks_cache(task_id, task_status)
        
    return task_status

def create_task(task_id: str) -> None:
    """创建新任务并初始化状态
    
    :param task_id: 任务ID
    """
    task_status = {
        "status": "initialized",
        "message": "任务已初始化",
        "progress": 0,
        "completed_files": 0,
        "total_files": 0,
        "draft_url": ""
    }
    update_tasks_cache(task_id, task_status)