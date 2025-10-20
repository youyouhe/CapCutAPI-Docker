#!/bin/bash

# CapCutAPI 系统初始化脚本 (root用户)
# 负责系统更新、软件安装、用户创建等需要root权限的操作

set -euo pipefail

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查当前用户权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo bash install_root.sh"
        exit 1
    fi
    log_success "root权限检查通过"
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

# 系统初始化和基础软件安装
init_system() {
    log_info "开始系统初始化..."

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # Ubuntu/Debian 系统初始化
        log_info "更新软件包列表..."
        apt update

        log_info "升级系统软件包..."
        apt upgrade -y

        log_info "安装基础工具..."
        apt install -y \
            curl \
            wget \
            git \
            unzip \
            tar \
            build-essential \
            software-properties-common \
            apt-transport-https \
            ca-certificates \
            gnupg \
            lsb-release \
            net-tools \
            lsof \
            htop \
            vim \
            nano \
            python3 \
            python3-pip \
            python3-venv \
            python3-dev

        log_success "Ubuntu/Debian 系统初始化完成"

    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        # CentOS/RHEL 系统初始化
        if command -v dnf &> /dev/null; then
            log_info "更新软件包列表..."
            dnf update -y

            log_info "升级系统软件包..."
            dnf upgrade -y

            log_info "安装基础工具..."
            dnf groupinstall -y "Development Tools"
            dnf install -y \
                curl \
                wget \
                git \
                unzip \
                tar \
                net-tools \
                lsof \
                htop \
                vim \
                nano \
                epel-release \
                python3 \
                python3-pip \
                python3-devel
        else
            log_info "更新软件包列表..."
            yum update -y

            log_info "升级系统软件包..."
            yum upgrade -y

            log_info "安装基础工具..."
            yum groupinstall -y "Development Tools"
            yum install -y \
                curl \
                wget \
                git \
                unzip \
                tar \
                net-tools \
                lsof \
                htop \
                vim \
                nano \
                epel-release \
                python3 \
                python3-pip \
                python3-devel
        fi

        log_success "CentOS/RHEL 系统初始化完成"
    fi
}

# 安装 Python 3.11
install_python311() {
    log_info "检查 Python 3.11 安装状态..."

    if command -v python3.11 &> /dev/null; then
        log_success "Python 3.11 已安装: $(python3.11 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")"
        return 0
    fi

    log_info "正在安装 Python 3.11..."

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # Ubuntu/Debian 安装 Python 3.11
        apt install -y software-properties-common

        # 添加 deadsnakes PPA
        if ! grep -q "deadsnakes" /etc/apt/sources.list.d/* 2>/dev/null; then
            add-apt-repository ppa:deadsnakes/ppa -y
        fi

        apt update

        # 安装 Python 3.11
        apt install -y \
            python3.11 \
            python3.11-pip \
            python3.11-venv \
            python3.11-dev \
            python3.11-distutils \
            python3.11-lib2to3

    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        # CentOS/RHEL 安装 Python 3.11
        if command -v dnf &> /dev/null; then
            dnf install -y python3.11 python3.11-pip python3.11-devel
        else
            yum install -y python3.11 python3.11-pip python3.11-devel
        fi
    fi

    # 验证安装
    if command -v python3.11 &> /dev/null; then
        log_success "Python 3.11 安装成功: $(python3.11 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")"
    else
        log_warning "Python 3.11 安装失败，将使用系统默认Python"
    fi
}

# 安装项目特定系统依赖
install_system_deps() {
    log_info "正在安装 CapCutAPI 项目依赖..."

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        log_info "安装视频处理和图像处理库..."
        apt install -y \
            ffmpeg \
            libsm6 \
            libxext6 \
            libxrender-dev \
            libgomp1 \
            libglib2.0-0 \
            libgl1-mesa-glx \
            libglib2.0-0 \
            libgtk-3-0 \
            libavcodec-dev \
            libavformat-dev \
            libswscale-dev

        log_success "Ubuntu/Debian 项目依赖安装完成"

    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        log_info "安装视频处理和图像处理库..."
        if command -v dnf &> /dev/null; then
            dnf install -y \
                ffmpeg \
                ffmpeg-devel \
                libSM \
                libXext \
                libXrender \
                gomp \
                glib2 \
                mesa-libGL \
                gtk3 \
                avcodec-devel \
                avformat-devel \
                swscale-devel
        else
            yum install -y \
                ffmpeg \
                ffmpeg-devel \
                libSM \
                libXext \
                libXrender \
                gomp \
                glib2 \
                mesa-libGL \
                gtk3 \
                avcodec-devel \
                avformat-devel \
                swscale-devel
        fi

        log_success "CentOS/RHEL 项目依赖安装完成"
    fi
}

# 创建 CapCutAPI 专用用户
create_capcut_user() {
    local username="capcut"

    log_info "创建专用用户: $username"

    # 检查用户是否已存在
    if id "$username" &>/dev/null; then
        log_warning "用户 $username 已存在"
        return 0
    fi

    # 创建用户
    adduser --disabled-password --gecos "" "$username" || {
        log_error "用户创建失败"
        return 1
    }

    # 添加到管理员组
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        usermod -aG sudo "$username"
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        usermod -aG wheel "$username"
    fi

    # 设置 sudo 免密码
    echo "$username ALL=(ALL) NOPASSWD:ALL" | tee "/etc/sudoers.d/$username" >/dev/null

    log_success "用户 $username 创建完成"
}

# 设置用户环境
setup_user_environment() {
    local username="capcut"
    local project_dir="/home/$username/CapCutAPI-Docker"

    log_info "为专用用户设置环境..."

    # 创建项目目录
    mkdir -p "$project_dir"

    # 克隆项目源码到专用用户目录
    log_info "正在为专用用户下载项目源码..."
    local repo_url="https://github.com/youyouhe/CapCutAPI-Docker.git"

    # 如果目录已存在，先删除
    if [[ -d "$project_dir" ]]; then
        log_warning "项目目录已存在，正在删除旧版本..."
        rm -rf "$project_dir"
    fi

    # 克隆项目
    git clone "$repo_url" "$project_dir" || {
        log_error "项目克隆失败，请检查网络连接"
        return 1
    }

    # 设置目录权限
    chown -R "$username:$username" "$project_dir"

    # 为专用用户配置 Python 环境
    if command -v python3.11 &> /dev/null; then
        log_info "为专用用户配置 Python 3.11 环境..."

        # 创建用户的 bash 配置文件，设置 Python 别名
        cat >> "/home/$username/.bashrc" << EOF

# Python 3.11 环境配置
if command -v python3.11 &> /dev/null; then
    alias python3='python3.11'
    alias pip3='pip3.11'
    export PATH="/usr/bin/python3.11:\$PATH"
fi
EOF
    fi

    log_success "用户环境设置完成，项目源码已下载"
    echo "$project_dir"
}

# 主函数
main() {
    echo "========================================"
    echo "    CapCutAPI 系统初始化脚本 (root)"
    echo "========================================"
    echo

    # 检查root权限
    check_root

    # 检测操作系统
    detect_os

    log_info "=== 开始系统初始化 ==="

    # 系统初始化
    init_system

    # 安装 Python 3.11
    install_python311

    # 安装项目依赖
    install_system_deps

    # 创建专用用户
    create_capcut_user

    # 设置用户环境
    project_dir=$(setup_user_environment)

    echo
    echo "========================================"
    echo "       系统初始化完成！"
    echo "========================================"
    echo "项目位置: $project_dir"
    echo "专用用户: capcut"
    echo
    echo "接下来请使用以下命令切换到专用用户："
    echo "  su - capcut"
    echo "  cd CapCutAPI-Docker"
    echo "  bash install_user.sh"
    echo
    echo "或者直接运行："
    echo "  su - capcut -c 'cd CapCutAPI-Docker && bash install_user.sh'"
    echo
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi