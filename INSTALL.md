# CapCutAPI 安装指南

## 🚀 一键安装

### 方法 1：使用专用一键安装脚本（推荐）

```bash
# 下载项目
git clone https://github.com/youyouhe/CapCutAPI-Docker.git
cd CapCutAPI-Docker

# 一键安装
sudo bash install-oneclick.sh
```

### 方法 2：直接使用主安装脚本

```bash
# 下载项目
git clone https://github.com/youyouhe/CapCutAPI-Docker.git
cd CapCutAPI-Docker

# 一键安装（自动模式）
sudo bash start_host.sh --auto

# 或者交互式安装
sudo bash start_host.sh
```

## 📋 安装选项

| 命令 | 说明 |
|------|------|
| `sudo bash install-oneclick.sh` | 简化版一键安装，推荐使用 |
| `sudo bash start_host.sh --auto` | 完整功能一键安装 |
| `sudo bash start_host.sh` | 交互式安装，有确认提示 |
| `bash start_host.sh` | 普通用户模式安装 |

## 🐳 Docker 安装（可选）

如果您更习惯使用 Docker：

```bash
# 使用 docker-compose
docker-compose -f docker-compose.test.yml up -d

# 或者使用 Dockerfile
docker build -f Dockerfile.cn -t capcut-api .
docker run -p 9000:9000 capcut-api
```

## ✅ 安装完成后

安装完成后，您将看到类似以下的信息：

```
🎉 部署完成！
🌐 访问地址:
  本地访问: http://localhost:9000
  局域网访问: http://192.168.1.100:9000
  外网访问: http://123.45.67.89:9000

🔍 健康检查: curl http://localhost:9000/health
⚠️  防火墙设置: sudo ufw allow 9000
```

## 🛠️ 故障排除

### Python 3.11 安装失败

如果 Python 3.11 安装失败，脚本会自动回退到系统默认 Python 版本。

### 防火墙问题

如果外网无法访问，请检查防火墙设置：

```bash
# Ubuntu/Debian
sudo ufw allow 9000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload
```

### 权限问题

建议使用 root 权限运行安装脚本以确保所有依赖正确安装。

### 服务启动失败

检查日志输出，常见问题：
- 端口被占用：脚本会提示更换端口
- 依赖安装失败：检查网络连接
- 配置文件错误：检查 `config.json` 格式

## 📖 更多信息

- 📖 API 文档：查看项目 README
- 🐛 问题反馈：[GitHub Issues](https://github.com/youyouhe/CapCutAPI-Docker/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/youyouhe/CapCutAPI-Docker/discussions)

## 🔧 手动安装

如果自动安装失败，您可以参考 `start_host.sh` 脚本进行手动安装。