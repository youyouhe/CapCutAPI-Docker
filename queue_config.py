"""
队列配置文件
用于管理请求队列的各项参数
"""

# 队列配置
QUEUE_MAX_SIZE = 50  # 队列最大长度
QUEUE_MAX_WORKERS = 2  # 最大并发工作线程数
QUEUE_TASK_TIMEOUT = 3600  # 单个任务超时时间（秒）
QUEUE_CLEANUP_INTERVAL = 300  # 清理旧任务的间隔时间（秒）
QUEUE_MAX_TASK_AGE = 3600  # 任务结果保留时间（秒）

# 队列优先级配置
QUEUE_PRIORITY_HIGH = 1    # 高优先级
QUEUE_PRIORITY_NORMAL = 2  # 普通优先级
QUEUE_PRIORITY_LOW = 3     # 低优先级

# 队列状态配置
QUEUE_STATUS_ENABLED = True  # 是否启用队列（如果为False，则直接处理请求）

# 日志配置
QUEUE_LOG_LEVEL = "INFO"  # 队列日志级别: DEBUG, INFO, WARNING, ERROR

# 监控配置
QUEUE_MONITOR_ENABLED = True  # 是否启用队列监控
QUEUE_MONITOR_INTERVAL = 60   # 监控数据收集间隔（秒）