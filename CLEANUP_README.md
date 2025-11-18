# MinIO清理功能使用说明

本文档介绍CapCutAPI的MinIO自动清理功能，用于定期清理超过48小时的draft文件。

## 功能概述

1. **预签名URL有效期延长**: 从24小时延长到48小时
2. **自动清理机制**: 每日自动清理超过48小时的draft文件
3. **灵活配置**: 支持配置清理间隔、文件保留时间、试运行模式
4. **API管理**: 提供手动触发和状态查询的API接口

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# MinIO清理配置
MINIO_CLEANUP_ENABLED=false                              # 是否启用定时清理任务
MINIO_CLEANUP_INTERVAL_HOURS=24                          # 清理任务运行间隔（小时）
MINIO_CLEANUP_MAX_AGE_HOURS=48                           # 文件最大保存时间（小时）
MINIO_CLEANUP_DRY_RUN=true                               # 是否为试运行模式
```

### 配置文件配置

在 `config.json` 文件中添加：

```json
{
  "minio_cleanup_config": {
    "enabled": false,           // 是否启用定时清理任务
    "interval_hours": 24,       // 清理任务间隔（小时）
    "max_age_hours": 48,        // 文件最大保存时间（小时）
    "dry_run": true            // 是否为试运行模式
  }
}
```

## 使用方法

### 1. 启用自动清理

将 `MINIO_CLEANUP_ENABLED` 设置为 `true`：

```bash
# 修改 .env 文件
MINIO_CLEANUP_ENABLED=true
MINIO_CLEANUP_DRY_RUN=false    # 设置为false以实际删除文件
```

或修改 `config.json`：

```json
{
  "minio_cleanup_config": {
    "enabled": true,
    "dry_run": false
  }
}
```

### 2. 重启服务

```bash
python capcut_server.py
```

服务启动时会显示清理配置信息：

```
MinIO清理任务: 已启用
清理间隔: 24 小时
文件保留时间: 48 小时
试运行模式: 否
```

### 3. 手动触发清理

使用API手动触发清理任务：

```bash
# 试运行模式（不实际删除文件）
curl -X POST http://localhost:9000/cleanup/minio \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-secret-key" \
  -d '{"dry_run": true, "max_age_hours": 48}'

# 实际删除文件
curl -X POST http://localhost:9000/cleanup/minio \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-secret-key" \
  -d '{"dry_run": false, "max_age_hours": 48}'
```

### 4. 查看清理状态

```bash
curl -X GET http://localhost:9000/cleanup/status \
  -H "X-API-KEY: your-secret-key"
```

## 测试功能

运行测试脚本验证功能：

```bash
python test_cleanup.py
```

测试脚本会检查：
- 配置加载是否正常
- MinIO连接是否可用
- 清理功能（试运行模式）
- 调度器是否正常工作
- API端点是否正确定义

## 安全建议

### 1. 试运行模式

在生产环境中，建议先启用试运行模式：

```bash
MINIO_CLEANUP_ENABLED=true
MINIO_CLEANUP_DRY_RUN=true
```

运行一段时间后，检查日志确认没有误删重要文件，再关闭试运行模式：

```bash
MINIO_CLEANUP_DRY_RUN=false
```

### 2. 监控日志

定期检查清理任务的执行日志：

```bash
# 查看服务日志
tail -f capcut_server.log | grep -i cleanup
```

### 3. 备份重要文件

确保重要文件有备份机制，避免误删造成数据丢失。

## 故障排除

### 1. 清理任务未执行

检查以下配置：
- `MINIO_CLEANUP_ENABLED` 是否为 `true`
- MinIO配置是否正确（endpoint、access_key、secret_key、bucket_name）
- 调度器是否正常启动

### 2. 清理任务失败

检查日志中的错误信息：
- MinIO连接权限
- 存储桶是否存在
- 网络连接是否正常

### 3. API调用失败

确认：
- API密钥配置是否正确
- 请求头是否包含正确的 `X-API-KEY`
- 服务是否正常运行

## 技术实现

### 文件结构

```
├── minio_cleanup.py      # MinIO清理核心逻辑
├── scheduler.py          # 定时任务调度器
├── settings/local.py     # 配置管理（已更新）
├── capcut_server.py      # 主服务器（已更新，集成调度器和API）
├── test_cleanup.py       # 测试脚本
└── CLEANUP_README.md     # 本文档
```

### 核心组件

1. **minio_cleanup.py**:
   - MinIO客户端连接管理
   - 文件时间检查和删除逻辑
   - 试运行模式支持

2. **scheduler.py**:
   - 定时任务调度器
   - 任务状态管理
   - 线程安全设计

3. **配置系统**:
   - 环境变量优先级
   - 配置文件支持
   - 灵活的参数设置

4. **API接口**:
   - `/cleanup/minio` - 手动触发清理
   - `/cleanup/status` - 查看清理状态

## 更新日志

### v1.0.0
- ✅ 预签名URL有效期延长到48小时
- ✅ 实现每日自动清理机制
- ✅ 添加灵活的配置选项
- ✅ 提供API管理接口
- ✅ 完整的测试覆盖
- ✅ 安全的试运行模式
- ✅ 详细的日志记录

---

**注意**: 在生产环境中使用前，请务必在测试环境中充分验证清理功能，避免误删重要文件。