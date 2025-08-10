# CapCutAPI Docker 部署指南

本项目已经完全Docker化，支持使用Docker和Docker Compose进行快速部署。

## 📋 前提条件

- Docker >= 20.10
- Docker Compose >= 2.0
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

## 🚀 快速启动

### 方法一：使用 Docker Compose（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/youyouhe/CapCutAPI.git
   cd CapCutAPI
   ```

2. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.example .env
   
   # 根据需要编辑环境变量
   nano .env
   ```

3. **启动服务**
   ```bash
   # 构建并启动所有服务
   docker-compose up -d
   
   # 或者使用指定的配置文件（如果网络有问题）
   docker-compose -f docker-compose.test.yml up -d
   ```

4. **验证部署**
   ```bash
   # 查看服务状态
   docker-compose ps
   
   # 查看日志
   docker-compose logs -f
   
   # 测试健康检查
   curl http://localhost:9000/health
   ```

### 方法二：仅使用 Docker

1. **构建镜像**
   ```bash
   # 构建镜像（如果有网络问题，可以尝试使用国内镜像源）
   docker build -t capcut-api:latest .
   
   # 或者使用简化的Dockerfile
   docker build -f Dockerfile.cn -t capcut-api:latest .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     --name capcut-api \
     -p 9000:9000 \
     -v $(pwd)/tmp:/app/tmp \
     -v $(pwd)/template:/app/template \
     -v $(pwd)/template_jianying:/app/template_jianying \
     -v $(pwd)/drafts:/app/drafts \
     -e CAPCUT_ENV=true \
     -e PORT=9000 \
     -e DRAFT_DOMAIN=https://www.install-ai-guider.top \
     --restart unless-stopped \
     capcut-api:latest
   ```

## ⚙️ 环境变量配置

### 基础配置
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `CAPCUT_ENV` | `true` | 是否使用CapCut环境（true）或剪映环境（false） |
| `DRAFT_DOMAIN` | `https://www.install-ai-guider.top` | 草稿域名 |
| `PREVIEW_ROUTER` | `/draft/downloader` | 预览路由 |
| `IS_UPLOAD_DRAFT` | `false` | 是否上传草稿文件到对象存储 |
| `PORT` | `9000` | 服务端口 |

### MinIO 配置
| 变量名 | 说明 |
|--------|------|
| `MINIO_ENDPOINT` | MinIO服务端点（如：http://minio:9000） |
| `MINIO_ACCESS_KEY` | MinIO访问密钥 |
| `MINIO_SECRET_KEY` | MinIO秘密密钥 |
| `MINIO_BUCKET_NAME` | MinIO存储桶名称 |

### 阿里云 OSS 配置
| 变量名 | 说明 |
|--------|------|
| `OSS_ENDPOINT` | OSS服务端点 |
| `OSS_ACCESS_KEY_ID` | OSS访问密钥ID |
| `OSS_ACCESS_KEY_SECRET` | OSS访问密钥秘密 |
| `OSS_BUCKET_NAME` | OSS存储桶名称 |

### MP4 OSS 配置
| 变量名 | 说明 |
|--------|------|
| `MP4_OSS_ENDPOINT` | MP4 OSS服务端点 |
| `MP4_OSS_ACCESS_KEY_ID` | MP4 OSS访问密钥ID |
| `MP4_OSS_ACCESS_KEY_SECRET` | MP4 OSS访问密钥秘密 |
| `MP4_OSS_BUCKET_NAME` | MP4 OSS存储桶名称 |
| `MP4_OSS_REGION` | MP4 OSS区域 |

## 📁 目录结构

### 容器内结构
```
/app/
├── capcut_server.py          # 主服务文件
├── settings/                 # 配置目录
├── tmp/                     # 临时文件目录
├── template/                # CapCut模板目录
├── template_jianying/       # 剪映模板目录
├── drafts/                  # 生成的草稿目录
└── pyJianYingDraft/         # 核心库目录
```

### 主机映射（建议）
```
CapCutAPI/
├── tmp/                     # → /app/tmp
├── template/                # → /app/template
├── template_jianying/       # → /app/template_jianying
└── drafts/                  # → /app/drafts
```

## 🔧 管理命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs -f capcut-api

# 查看最近100行日志
docker-compose logs --tail=100 capcut-api
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart capcut-api
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除卷
docker-compose down -v

# 停止并删除镜像（完全清理）
docker-compose down -v --rmi all
```

### 更新服务
```bash
# 重新构建并启动
docker-compose up -d --build

# 或者分步执行
docker-compose build
docker-compose up -d
```

## 🌐 访问服务

### API 服务
- **URL**: `http://localhost:9000`
- **健康检查**: `http://localhost:9000/health`
- **API文档**: 查看 `example.py` 中的使用示例

### MinIO 控制台（如果启用）
- **URL**: `http://localhost:9002`
- **用户名**: `minioadmin`
- **密码**: `minioadmin`

## 🔍 监控和日志

### 健康检查
容器内置健康检查，可以通过以下方式查看：
```bash
docker inspect capcut-api | grep -A 10 "Health"
```

### 日志收集
```bash
# 收集所有日志到文件
docker-compose logs > docker-compose.log 2>&1

# 实时监控日志
docker-compose logs -f --tail=100
```

### 性能监控
```bash
# 查看容器资源使用
docker stats capcut-api

# 查看容器详细信息
docker inspect capcut-api
```

## 🐛 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 检查容器状态
   docker-compose ps
   
   # 查看错误日志
   docker-compose logs capcut-api
   
   # 检查端口占用
   netstat -tlnp | grep 9000
   ```

2. **网络连接问题**
   ```bash
   # 检查Docker网络
   docker network ls
   
   # 检查容器网络
   docker network inspect capcut_capcut-network
   ```

3. **权限问题**
   ```bash
   # 确保目录权限正确
   chmod -R 755 tmp/ template/ template_jianying/
   chown -R $USER:$USER tmp/ template/ template_jianying/
   ```

4. **存储空间不足**
   ```bash
   # 清理Docker缓存
   docker system prune -a
   
   # 查看磁盘使用
   df -h
   ```

### 调试模式
```bash
# 以交互模式运行容器
docker run -it --rm \
  -p 9000:9000 \
  -v $(pwd)/tmp:/app/tmp \
  capcut-api:latest /bin/bash

# 或者直接在运行中的容器中调试
docker exec -it capcut-api /bin/bash
```

## 📈 生产环境建议

### 安全配置
1. 使用非root用户运行容器
2. 配置防火墙规则
3. 使用HTTPS（建议使用Nginx反向代理）
4. 定期更新镜像

### 性能优化
1. 配置适当的内存和CPU限制
2. 使用多阶段构建减少镜像大小
3. 配置日志轮转避免日志过大
4. 使用外部数据库（如需要）

### 备份策略
1. 定期备份重要目录（drafts/, template/）
2. 备份配置文件（.env, config.json）
3. 考虑使用持久化存储

## 🔄 版本更新

### 更新镜像
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose up -d
```

### 回滚版本
```bash
# 1. 查看可用镜像
docker images | grep capcut-api

# 2. 使用旧版本启动
docker run -d ... capcut-api:old-version
```

## 📚 相关文档

- [API使用示例](example.py)
- [配置文件示例](config.json.example)
- [环境变量配置](.env.example)
- [测试脚本](test_*.py)

---

如有问题，请查看日志文件或提交Issue。