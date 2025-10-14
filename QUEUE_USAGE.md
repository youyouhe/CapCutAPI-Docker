# 内存队列使用说明

## 概述

CapCut API 现在支持内存队列机制，用于处理并发请求。当多个 `/save_draft` 请求同时到达时，它们会被放入队列中依次处理，避免资源竞争和系统过载。

## 工作原理

1. **请求提交**：客户端发送 `/save_draft` 请求
2. **队列排队**：请求被添加到内存队列中
3. **后台处理**：工作线程从队列中取出任务并执行
4. **状态查询**：客户端可以通过 `/query_draft_status` 查询处理进度
5. **结果返回**：处理完成后返回草稿URL

## 配置参数

在 `queue_config.py` 中可以配置以下参数：

- `QUEUE_MAX_SIZE`: 队列最大长度（默认：50）
- `QUEUE_MAX_WORKERS`: 最大并发工作线程数（默认：2）
- `QUEUE_MAX_TASK_AGE`: 任务结果保留时间（默认：3600秒）
- `QUEUE_LOG_LEVEL`: 队列日志级别（默认：INFO）

## API 接口

### 1. 提交保存草稿任务

```http
POST /save_draft
Content-Type: application/json
X-API-KEY: your_api_key

{
    "draft_id": "your_draft_id",
    "draft_folder": "optional_folder_path"
}
```

**响应示例：**
```json
{
    "success": true,
    "output": {
        "task_id": "your_draft_id",
        "message": "任务已提交到队列，请使用 query_draft_status 查询处理进度",
        "queue_info": {
            "queue_size": 0,
            "max_queue_size": 50,
            "active_workers": 1,
            "max_workers": 2,
            "total_tasks": 1,
            "is_running": true
        }
    }
}
```

### 2. 查询任务状态

```http
POST /query_draft_status
Content-Type: application/json
X-API-KEY: your_api_key

{
    "task_id": "your_draft_id"
}
```

**响应示例：**
```json
{
    "success": true,
    "output": {
        "status": "processing",
        "message": "开始处理任务...",
        "progress": 50,
        "draft_url": "",
        "queue_info": {
            "queue_size": 1,
            "max_queue_size": 50,
            "active_workers": 2,
            "max_workers": 2,
            "total_tasks": 2,
            "is_running": true
        }
    }
}
```

**状态说明：**
- `queued`: 任务在队列中等待处理（进度：0%）
- `processing`: 任务正在处理中（进度：50%）
- `completed`: 任务完成（进度：100%）
- `failed`: 任务失败（进度：0%）

### 3. 查看队列信息

```http
GET /queue_info
X-API-KEY: your_api_key
```

**响应示例：**
```json
{
    "success": true,
    "output": {
        "queue_size": 2,
        "max_queue_size": 50,
        "active_workers": 2,
        "max_workers": 2,
        "total_tasks": 5,
        "is_running": true
    }
}
```

## 使用建议

### 1. 客户端轮询策略

建议客户端采用指数退避策略进行状态查询：

```python
import time
import requests

def poll_task_status(task_id, api_key, max_retries=30):
    base_delay = 1
    for attempt in range(max_retries):
        response = requests.post(
            "http://your-api:9000/query_draft_status",
            json={"task_id": task_id},
            headers={"X-API-KEY": api_key}
        )

        result = response.json()
        if result["success"]:
            status = result["output"]["status"]
            progress = result["output"]["progress"]

            print(f"Task {task_id}: {status} ({progress}%)")

            if status in ["completed", "failed"]:
                return result

        # 指数退避
        delay = min(base_delay * (2 ** attempt), 10)
        time.sleep(delay)

    return None
```

### 2. 错误处理

- **队列已满**：当队列满时，API会返回错误信息，建议客户端稍后重试
- **任务重复**：相同draft_id的重复任务会被拒绝，但会返回已存在任务的状态
- **任务失败**：检查草稿ID是否有效，网络连接是否正常

### 3. 性能优化

- 根据服务器性能调整 `QUEUE_MAX_WORKERS` 参数
- 监控队列长度，避免长时间堆积
- 定期清理旧任务结果

## 日志监控

队列系统会记录详细的日志信息：

- 任务提交和完成
- 工作线程状态
- 队列大小变化
- 错误和异常信息

日志级别可在 `queue_config.py` 中配置。

## 故障处理

### 队列停止响应

1. 检查服务器内存和CPU使用情况
2. 查看应用日志中的错误信息
3. 重启应用服务

### 任务处理失败

1. 检查 `save_draft_background` 函数的执行日志
2. 验证草稿ID是否存在于缓存中
3. 检查文件下载和处理权限

### 内存泄漏

1. 定期清理旧任务结果
2. 监控内存使用情况
3. 适当调整 `QUEUE_MAX_TASK_AGE` 参数