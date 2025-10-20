#!/bin/bash

# CapCutAPI 主机部署一键启动脚本
# 支持 Ubuntu/Debian 和 CentOS/RHEL 系统

set -e

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用 root 用户运行此脚本"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "无法检测操作系统版本"
        exit 1
    fi

    log_info "检测到操作系统: $OS $VER"
}

# 检查 Python 版本
check_python() {
    log_info "检查 Python 环境..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        log_info "当前 Python 版本: $PYTHON_VERSION"

        # 检查是否为 Python 3.8 或更高版本
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python 版本符合要求 (>= 3.8)"
        else
            log_error "Python 版本过低，需要 Python 3.8 或更高版本"
            install_python
        fi
    else
        log_warning "未找到 Python3，正在安装..."
        install_python
    fi
}

# 安装 Python (根据不同系统)
install_python() {
    log_info "正在安装 Python 3.11..."

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # Ubuntu/Debian
        sudo apt update
        sudo apt install -y software-properties-common
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update
        sudo apt install -y python3.11 python3.11-pip python3.11-venv
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        # CentOS/RHEL
        if command -v dnf &> /dev/null; then
            sudo dnf install -y python3.11 python3.11-pip
        else
            sudo yum install -y python3.11 python3.11-pip
        fi
    fi

    # 创建软链接
    if ! command -v python3 &> /dev/null; then
        sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
    fi

    log_success "Python 3.11 安装完成"
}

# 安装系统依赖
install_system_deps() {
    log_info "正在安装系统依赖..."

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt update
        sudo apt install -y curl ffmpeg libsm6 libxext6 libxrender-dev libgomp1 libglib2.0-0
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        if command -v dnf &> /dev/null; then
            sudo dnf install -y curl ffmpeg libSM libXext libXrender gomp glib2
        else
            sudo yum install -y curl ffmpeg libSM libXext libXrender gomp glib2
        fi
    fi

    log_success "系统依赖安装完成"
}

# 检查并安装 FFmpeg
check_ffmpeg() {
    if ! command -v ffmpeg &> /dev/null; then
        log_warning "FFmpeg 未安装，正在安装..."
        install_system_deps
    else
        log_success "FFmpeg 已安装: $(ffmpeg -version | head -n1)"
    fi
}

# 创建虚拟环境
create_venv() {
    log_info "创建 Python 虚拟环境..."

    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        log_success "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在"
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 升级 pip
    pip install --upgrade pip
}

# 安装 Python 依赖
install_python_deps() {
    log_info "正在安装 Python 依赖包..."

    # 激活虚拟环境
    source venv/bin/activate

    # 安装依赖
    pip install -r requirements.txt

    log_success "Python 依赖安装完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."

    # 检查 config.json
    if [[ ! -f "config.json" ]]; then
        if [[ -f "config.json.example" ]]; then
            cp config.json.example config.json
            log_info "已从 config.json.example 创建 config.json"
            log_warning "请根据需要修改 config.json 配置"
        else
            log_error "缺少 config.json 配置文件"
            exit 1
        fi
    else
        log_success "config.json 已存在"
    fi

    # 检查 .env 文件
    if [[ ! -f ".env" ]]; then
        log_warning ".env 文件不存在，将使用默认配置"
        log_info "建议创建 .env 文件配置存储参数"
    else
        log_success ".env 文件已存在"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."

    mkdir -p tmp template template_jianying settings drafts

    log_success "目录创建完成"
}

# 检查端口占用
check_port() {
    local port=${1:-9000}

    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_warning "端口 $port 已被占用"
            return 1
        else
            log_success "端口 $port 可用"
            return 0
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tuln | grep ":$port " >/dev/null 2>&1; then
            log_warning "端口 $port 已被占用"
            return 1
        else
            log_success "端口 $port 可用"
            return 0
        fi
    else
        log_info "无法检查端口占用情况 (缺少 lsof 或 netstat)"
        return 0
    fi
}

# 启动服务
start_service() {
    local port=${PORT:-9000}

    log_info "准备启动 CapCutAPI 服务..."

    # 检查端口
    if ! check_port $port; then
        read -p "端口 $port 已被占用，是否使用其他端口? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入新端口号: " new_port
            export PORT=$new_port
        else
            log_error "启动取消"
            exit 1
        fi
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 设置环境变量
    export PYTHONPATH=$(pwd)
    export FLASK_APP=capcut_server.py
    export FLASK_ENV=production
    export PYTHONUNBUFFERED=1

    log_info "启动服务中... (端口: ${PORT:-9000})"
    log_info "按 Ctrl+C 停止服务"

    # 启动服务
    python3 capcut_server.py
}

# 主函数
main() {
    echo "========================================"
    echo "    CapCutAPI 主机部署一键启动脚本"
    echo "========================================"
    echo

    # 检查 root 权限
    check_root

    # 检测操作系统
    detect_os

    # 检查 Python 环境
    check_python

    # 安装系统依赖
    install_system_deps

    # 检查 FFmpeg
    check_ffmpeg

    # 创建虚拟环境
    create_venv

    # 安装 Python 依赖
    install_python_deps

    # 检查配置文件
    check_config

    # 创建必要目录
    create_directories

    # 启动服务
    start_service
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi