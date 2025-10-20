# CapCutAPI 主机部署指南

## 一键部署脚本

本项目提供了完整的一键部署脚本 `start_host.sh`，支持在新服务器上自动完成所有部署步骤。

## 使用方法

### 在全新服务器上部署

1. **下载并运行脚本（以 root 用户）**
```bash
# 下载脚本
curl -fsSL https://raw.githubusercontent.com/youyouhe/CapCutAPI-Docker/main/start_host.sh -o start_host.sh
chmod +x start_host.sh

# 运行脚本
./start_host.sh
```

2. **脚本会自动完成以下操作：**
   - ✅ 系统更新 (`apt update && apt upgrade`)
   - ✅ 安装基础工具包 (`git`, `curl`, `wget`, `vim` 等)
   - ✅ 创建专用用户 `capcut`（可选）
   - ✅ 安装 Python 3.11 环境
   - ✅ 安装系统依赖 (`ffmpeg`, 视频处理库等)
   - ✅ 下载项目源码 (`git clone`)
   - ✅ 创建 Python 虚拟环境
   - ✅ 安装 Python 依赖包
   - ✅ 配置文件初始化
   - ✅ 启动 CapCutAPI 服务

### 分步部署（推荐）

如果你想更清楚地了解部署过程，可以手动执行以下步骤：

#### 1. 系统初始化
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y curl wget git unzip tar build-essential
```

#### 2. 创建专用用户（推荐）
```bash
# 创建用户
sudo adduser capcut
sudo usermod -aG sudo capcut

# 设置 sudo 免密码
echo "capcut ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/capcut

# 切换到新用户
su - capcut
```

#### 3. 下载项目
```bash
# 克隆项目
git clone https://github.com/youyouhe/CapCutAPI-Docker.git
cd CapCutAPI-Docker

# 运行一键部署脚本
./start_host.sh
```

## 系统要求

### 支持的操作系统
- **Ubuntu**: 18.04, 20.04, 22.04 或更高版本
- **Debian**: 10, 11, 12 或更高版本
- **CentOS**: 7, 8, 9
- **RHEL**: 8, 9

### 硬件要求
- **CPU**: 2 核心或以上
- **内存**: 4GB 或以上
- **磁盘**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 权限要求
- 具有 sudo 权限的用户
- 不建议直接使用 root 用户

## 脚本功能详解

### 1. 用户管理
- 检测当前用户权限
- 可选创建专用用户 `capcut`
- 自动配置 sudo 权限

### 2. 系统初始化
- 系统软件包更新
- 安装开发工具包
- 安装网络和系统工具

### 3. 环境搭建
- Python 3.11 安装和配置
- FFmpeg 和视频处理库
- 系统依赖包安装

### 4. 项目部署
- 自动下载项目源码
- 创建虚拟环境
- 安装 Python 依赖
- 配置文件初始化

### 5. 服务启动
- 端口冲突检测
- 环境变量配置
- 服务健康检查

## 配置说明

### 主要配置文件
- `config.json`: 主配置文件
- `.env`: 环境变量配置
- `requirements.txt`: Python 依赖

### 服务配置
- **默认端口**: 9000
- **健康检查**: `/health`
- **虚拟环境**: `./venv`

## 常见问题

### Q: 脚本运行失败怎么办？
A: 检查以下项目：
1. 网络连接是否正常
2. 是否有 sudo 权限
3. 操作系统是否支持
4. 磁盘空间是否充足

### Q: 如何修改服务端口？
A: 可以通过以下方式修改：
1. 修改 `.env` 文件中的 `PORT` 变量
2. 运行时设置环境变量：`PORT=8080 ./start_host.sh`

### Q: 如何重启服务？
A: 使用以下命令：
```bash
# 进入项目目录
cd ~/CapCutAPI-Docker

# 激活虚拟环境
source venv/bin/activate

# 启动服务
python3 capcut_server.py
```

### Q: 如何查看服务状态？
A: 执行健康检查：
```bash
curl http://localhost:9000/health
```

### Q: 如何更新项目？
A: 更新项目代码：
```bash
cd ~/CapCutAPI-Docker
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## 安全建议

1. **使用专用用户**：不要使用 root 用户运行服务
2. **防火墙配置**：只开放必要的端口
3. **定期更新**：保持系统和依赖包的更新
4. **监控日志**：关注服务运行状态

## 技术支持

如遇到问题，请：
1. 检查脚本输出的错误信息
2. 查看系统日志：`/var/log/syslog`
3. 在 GitHub 提交 Issue
4. 联系技术支持团队

---

**注意**: 脚本会自动检测运行环境并进行相应的配置。首次运行可能需要较长时间，请耐心等待。