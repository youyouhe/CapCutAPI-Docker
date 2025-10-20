#!/bin/bash

# CapCutAPI 主机部署一键启动脚本
# 支持 Ubuntu/Debian 和 CentOS/RHEL 系统

set -euo pipefail  # 严格模式：遇到错误立即退出，未定义变量报错，管道中任意命令失败则退出

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

# 检查当前用户和权限
check_user_and_sudo() {
    log_info "检查用户权限和 sudo 配置..."

    # 检查当前用户
    CURRENT_USER=$(whoami)
    log_info "当前用户: $CURRENT_USER"

    # 如果是 root 用户，执行系统初始化并创建专用用户
    if [[ $EUID -eq 0 ]]; then
        log_info "以 root 用户运行，将执行系统初始化和用户创建"
        log_info "部署完成后将自动切换到专用用户"
        return 0
    else
        # 检查是否有 sudo 权限
        if ! sudo -n true 2>/dev/null; then
            log_warning "需要 sudo 权限来安装系统依赖"
            log_info "请输入 sudo 密码进行权限验证..."
            sudo -v || {
                log_error "sudo 权限验证失败，无法继续安装"
                exit 1
            }
        fi
        log_success "权限验证通过"
        return 0
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

    # 创建用户 (root 权限运行，不需要 sudo)
    adduser --disabled-password --gecos "" "$username" || {
        log_error "用户创建失败"
        return 1
    }

    # 添加到 sudo 组 (Ubuntu/Debian)
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        usermod -aG sudo "$username"
    # 添加到 wheel 组 (CentOS/RHEL)
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        usermod -aG wheel "$username"
    fi

    # 设置 sudo 免密码
    echo "$username ALL=(ALL) NOPASSWD:ALL" | tee "/etc/sudoers.d/$username" >/dev/null

    log_success "用户 $username 创建完成"
}

# 设置 Python 默认版本
setup_python_environment() {
    local username="capcut"

    log_info "为专用用户配置 Python 环境..."

    # 检查是否安装了 Python 3.11
    if command -v python3.11 &> /dev/null; then
        log_info "检测到 Python 3.11，设置为默认版本"

        # 创建用户的 bash 配置文件，设置 Python 别名
        cat >> "/home/$username/.bashrc" << EOF

# Python 3.11 环境配置
if command -v python3.11 &> /dev/null; then
    alias python3='python3.11'
    alias pip3='pip3.11'
    export PATH="/usr/bin/python3.11:\$PATH"
fi
EOF

        # 为 root 用户也设置相同的配置（如果需要）
        cat >> "/root/.bashrc" << EOF

# Python 3.11 环境配置
if command -v python3.11 &> /dev/null; then
    alias python3='python3.11'
    alias pip3='pip3.11'
    export PATH="/usr/bin/python3.11:\$PATH"
fi
EOF

        log_success "Python 3.11 环境配置完成"
    else
        log_info "使用系统默认 Python 版本"
    fi
}

# 为专用用户设置环境
setup_user_environment() {
    local username="capcut"
    local project_dir="/home/$username/CapCutAPI-Docker"

    log_info "为专用用户设置环境..."

    # 创建项目目录
    mkdir -p "$project_dir"

    # 复制项目文件到用户目录（如果当前目录有项目文件）
    if [[ -f "start_host.sh" ]]; then
        log_info "复制项目文件到专用用户目录..."
        cp -r . "$project_dir/" 2>/dev/null || {
            log_warning "无法复制项目文件，将稍后下载"
        }
    fi

    # 设置目录权限
    chown -R "$username:$username" "$project_dir"

    log_success "用户环境设置完成"
    echo "$project_dir"
}

# 系统初始化和基础软件安装
init_system() {
    log_info "开始系统初始化..."

    # 确定使用 sudo 还是直接执行
    local cmd_prefix=""
    if [[ $EUID -ne 0 ]]; then
        cmd_prefix="sudo"
    fi

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # Ubuntu/Debian 系统初始化
        log_info "更新软件包列表..."
        $cmd_prefix apt update

        log_info "升级系统软件包..."
        $cmd_prefix apt upgrade -y

        log_info "安装基础工具..."
        $cmd_prefix apt install -y \
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
            $cmd_prefix dnf update -y

            log_info "升级系统软件包..."
            $cmd_prefix dnf upgrade -y

            log_info "安装基础工具..."
            $cmd_prefix dnf groupinstall -y "Development Tools"
            $cmd_prefix dnf install -y \
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
            $cmd_prefix yum update -y

            log_info "升级系统软件包..."
            $cmd_prefix yum upgrade -y

            log_info "安装基础工具..."
            $cmd_prefix yum groupinstall -y "Development Tools"
            $cmd_prefix yum install -y \
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

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用 root 用户运行此脚本"
        log_info "建议创建普通用户并使用 sudo 运行此脚本"
        echo
        log_info "创建新用户的示例命令："
        echo "sudo adduser capcut"
        echo "sudo usermod -aG sudo capcut"
        echo "su - capcut"
        echo
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
        log_info "添加 deadsnakes PPA 源..."
        sudo apt install -y software-properties-common
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update

        log_info "安装 Python 3.11 及相关包..."
        sudo apt install -y \
            python3.11 \
            python3.11-pip \
            python3.11-venv \
            python3.11-dev \
            python3.11-distutils \
            python3.11-lib2to3

    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        # CentOS/RHEL
        log_info "从 EPEL 源安装 Python..."
        if command -v dnf &> /dev/null; then
            sudo dnf install -y python3.11 python3.11-pip python3.11-devel
        else
            sudo yum install -y python3.11 python3.11-pip python3.11-devel
        fi
    fi

    # 创建软链接
    if ! command -v python3 &> /dev/null; then
        sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
    fi

    # 创建 pip 软链接
    if ! command -v pip3 &> /dev/null; then
        sudo ln -sf /usr/bin/pip3.11 /usr/bin/pip3
    fi

    log_success "Python 3.11 安装完成"
}

# 安装项目特定系统依赖
install_system_deps() {
    log_info "正在安装 CapCutAPI 项目依赖..."

    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        log_info "安装视频处理和图像处理库..."
        sudo apt install -y \
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
            sudo dnf install -y \
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
            sudo yum install -y \
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

# 检查并下载项目源码
check_project_source() {
    log_info "检查项目源码..."

    # 检查是否在项目目录中
    if [[ -f "capcut_server.py" && -f "requirements.txt" && -d "pyJianYingDraft" ]]; then
        log_success "项目源码已存在"
        return 0
    fi

    log_info "未找到项目源码，开始下载..."

    # GitHub 仓库配置
    local repo_url="https://github.com/youyouhe/CapCutAPI-Docker.git"
    local project_name="CapCutAPI-Docker"
    local clone_dir="${HOME}/${project_name}"

    # 如果目录已存在，先删除
    if [[ -d "$clone_dir" ]]; then
        log_warning "项目目录已存在，正在删除旧版本..."
        rm -rf "$clone_dir"
    fi

    # 克隆项目
    log_info "正在从 GitHub 克隆项目..."
    git clone "$repo_url" "$clone_dir" || {
        log_error "项目克隆失败，请检查网络连接"
        exit 1
    }

    # 进入项目目录
    cd "$clone_dir"
    log_success "项目下载完成，当前目录: $(pwd)"

    # 验证项目完整性
    if [[ -f "capcut_server.py" && -f "requirements.txt" && -f "start_host.sh" ]]; then
        log_success "项目文件验证通过"
    else
        log_error "项目文件不完整"
        exit 1
    fi
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

# 以专用用户身份运行应用部署
run_as_user() {
    local username="capcut"
    local project_dir="/home/$username/CapCutAPI-Docker"

    log_info "切换到专用用户继续应用部署..."

    # 创建应用部署脚本
    cat > "$project_dir/deploy_as_user.sh" << 'EOF'
#!/bin/bash
set -euo pipefail

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    fi
    log_info "检测到操作系统: $OS $VER"
}

# 检查 Python 版本
check_python() {
    log_info "检查 Python 环境..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        log_info "当前 Python 版本: $PYTHON_VERSION"
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python 版本符合要求 (>= 3.8)"
        else
            log_error "Python 版本过低，需要 Python 3.8 或更高版本"
            exit 1
        fi
    else
        log_error "未找到 Python3"
        exit 1
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
    source venv/bin/activate
    pip install --upgrade pip
}

# 安装 Python 依赖
install_python_deps() {
    log_info "正在安装 Python 依赖包..."
    source venv/bin/activate
    pip install -r requirements.txt
    log_success "Python 依赖安装完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    if [[ ! -f "config.json" ]]; then
        if [[ -f "config.json.example" ]]; then
            cp config.json.example config.json
            log_info "已从 config.json.example 创建 config.json"
        else
            log_error "缺少 config.json 配置文件"
            exit 1
        fi
    fi
    log_success "配置文件检查完成"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    mkdir -p tmp template template_jianying settings drafts
    log_success "目录创建完成"
}

# 启动服务
start_service() {
    local port=${PORT:-9000}
    log_info "启动 CapCutAPI 服务... (端口: $port)"

    source venv/bin/activate
    export PYTHONPATH=$(pwd)
    export FLASK_APP=capcut_server.py
    export FLASK_ENV=production
    export PYTHONUNBUFFERED=1

    python3 capcut_server.py
}

# 主函数
main() {
    echo "========================================"
    echo "     CapCutAPI 应用部署 (专用用户)"
    echo "========================================"
    echo

    detect_os
    check_python
    create_venv
    install_python_deps
    check_config
    create_directories

    echo
    echo "========================================"
    echo "          应用部署完成！"
    echo "========================================"
    echo "项目位置: $(pwd)"
    echo "启动命令: python3 capcut_server.py"
    echo "健康检查: curl http://localhost:9000/health"
    echo

    start_service
}

main "$@"
EOF

    chmod +x "$project_dir/deploy_as_user.sh"
    chown "$username:$username" "$project_dir/deploy_as_user.sh"

    # 切换用户并运行应用部署
    su - "$username" -c "cd $project_dir && bash -c 'source ~/.bashrc && ./deploy_as_user.sh'"
}

# 主函数
main() {
    echo "========================================"
    echo "    CapCutAPI 主机部署一键启动脚本"
    echo "========================================"
    echo
    echo "此脚本将自动完成以下操作："
    echo "  1. 系统更新和基础软件安装 (root)"
    echo "  2. 创建专用用户并配置环境 (root)"
    echo "  3. 安装 Python 环境和系统依赖 (root)"
    echo "  4. 切换到专用用户部署应用 (capcut)"
    echo "  5. 启动 CapCutAPI 服务"
    echo

    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装已取消"
        exit 0
    fi

    # 检查当前用户和 sudo 权限
    check_user_and_sudo

    # 检测操作系统
    detect_os

    if [[ $EUID -eq 0 ]]; then
        # Root 用户：执行系统初始化
        log_info "=== 开始系统初始化阶段 (root) ==="

        # 系统初始化和基础软件安装
        init_system

        # 创建专用用户
        create_capcut_user

        # 设置 Python 环境配置
        setup_python_environment

        # 检查 Python 环境
        check_python

        # 安装项目特定系统依赖
        install_system_deps

        # 检查 FFmpeg
        check_ffmpeg

        # 为专用用户设置环境
        project_dir=$(setup_user_environment)

        log_success "=== 系统初始化完成，切换到专用用户 ==="

        # 切换到专用用户运行应用部署
        run_as_user

    else
        # 普通用户：直接进行应用部署
        log_info "=== 开始应用部署阶段 (普通用户) ==="

        # 检查并下载项目源码
        check_project_source

        # 检查 Python 环境
        check_python

        # 安装项目特定系统依赖
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

        # 显示部署完成信息
        echo
        echo "========================================"
        echo "          部署完成！"
        echo "========================================"
        echo "项目位置: $(pwd)"
        echo "配置文件: config.json, .env"
        echo "启动命令: python3 capcut_server.py"
        echo "健康检查: curl http://localhost:9000/health"
        echo

        # 启动服务
        start_service
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi