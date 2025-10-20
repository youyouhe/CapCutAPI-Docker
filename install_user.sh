#!/bin/bash

# CapCutAPI 应用部署脚本 (普通用户)
# 负责Python环境配置、依赖安装、服务启动等应用层操作

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
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
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

    # 确定使用的 Python 版本
    local python_cmd="python3"
    if command -v python3.11 &> /dev/null; then
        python_cmd="python3.11"
        log_info "使用 Python 3.11 创建虚拟环境"
    else
        log_info "使用系统默认 Python 创建虚拟环境"
    fi

    # 显示将要使用的 Python 版本
    local python_version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    log_info "Python 版本: $python_version"

    # 检查虚拟环境是否完整
    if [[ -d "venv" && -f "venv/bin/activate" && -f "venv/bin/python" ]]; then
        # 检查现有虚拟环境的 Python 版本
        local venv_python_version=$(venv/bin/python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "未知")
        log_info "现有虚拟环境 Python 版本: $venv_python_version"

        if [[ "$venv_python_version" == "$python_version" ]]; then
            log_info "虚拟环境已存在且版本匹配"
        else
            log_warning "虚拟环境 Python 版本 ($venv_python_version) 与系统 Python 版本 ($python_version) 不匹配"
            log_info "正在重新创建虚拟环境..."
            rm -rf venv
        fi
    fi

    # 如果虚拟环境不存在或需要重新创建
    if [[ ! -d "venv" ]]; then
        log_info "正在创建新的虚拟环境..."
        $python_cmd -m venv venv || {
            log_error "虚拟环境创建失败"
            log_info "请检查以下问题："
            log_info "1. python3-venv 包是否已安装 (对于 Python 3.11 可能需要 python3.11-venv)"
            log_info "2. 当前用户是否有创建目录的权限"
            log_info "3. $python_cmd 命令是否可用"
            exit 1
        }
        log_success "虚拟环境创建完成"
    fi

    # 激活虚拟环境
    log_info "激活虚拟环境..."
    source venv/bin/activate || {
        log_error "虚拟环境激活失败"
        exit 1
    }

    # 验证虚拟环境中的 Python 版本
    local venv_python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    log_info "虚拟环境 Python 版本: $venv_python_version"

    # 升级 pip
    log_info "升级 pip..."
    pip install --upgrade pip
    log_success "虚拟环境配置完成"
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
        REPLY="${REPLY:-}"  # 确保REPLY变量已定义
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

    # 输出环境变量信息
    log_info "=== 环境变量配置 ==="
    log_info "PYTHONPATH: $PYTHONPATH"
    log_info "FLASK_APP: $FLASK_APP"
    log_info "FLASK_ENV: $FLASK_ENV"
    log_info "PYTHONUNBUFFERED: $PYTHONUNBUFFERED"
    log_info "PORT: ${PORT:-9000}"

    # 输出配置文件信息
    if [[ -f "config.json" ]]; then
        log_info "配置文件: config.json (已加载)"
        # 提取并显示一些关键配置（如果有的话）
        if command -v jq &> /dev/null; then
            local server_port=$(jq -r '.port // "未配置"' config.json 2>/dev/null)
            log_info "配置文件端口: $server_port"
        fi
    else
        log_warning "配置文件: config.json (不存在)"
    fi

    # 输出 .env 文件信息
    if [[ -f ".env" ]]; then
        log_info "环境文件: .env (存在)"
        # 安全地显示 .env 文件中的非敏感变量
        if [[ -r ".env" ]]; then
            log_info ".env 文件中的变量:"
            while IFS='=' read -r key value; do
                # 跳过注释和空行
                [[ $key =~ ^[[:space:]]*# ]] && continue
                [[ -z $key ]] && continue

                # 只显示非敏感变量（不包含 password, secret, key, token 等词）
                if [[ ! $key =~ (password|secret|key|token|auth) ]]; then
                    log_info "  $key=${value:-空值}"
                else
                    log_info "  $key=*** (敏感信息已隐藏)"
                fi
            done < .env
        fi
    else
        log_info "环境文件: .env (不存在)"
    fi

    log_info "======================="
    log_info "启动服务中... (端口: ${PORT:-9000})"
    log_info "按 Ctrl+C 停止服务"

    # 启动服务
    python3 capcut_server.py
}

# 检查是否为一键安装模式
check_install_mode() {
    local mode="${1:-}"
    if [[ "$mode" == "--auto" || "$mode" == "-y" ]]; then
        export AUTO_INSTALL=true
        log_info "启用一键安装模式"
        return 0
    else
        export AUTO_INSTALL=false
        return 1
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "    CapCutAPI 应用部署脚本"
    echo "========================================"
    echo
    echo "使用方法:"
    echo "  bash install_user.sh         # 交互式安装"
    echo "  bash install_user.sh --auto  # 一键安装模式"
    echo
    echo "此脚本将自动完成以下操作："
    echo "  1. 检查Python环境"
    echo "  2. 创建虚拟环境"
    echo "  3. 安装Python依赖"
    echo "  4. 检查配置文件"
    echo "  5. 创建必要目录"
    echo "  6. 启动CapCutAPI服务"
    echo

    # 检查安装模式
    local install_mode="${1:-}"
    check_install_mode "$install_mode" || true

    if [[ "$AUTO_INSTALL" != "true" ]]; then
        read -p "是否继续? (y/n): " -n 1 -r
        echo
        REPLY="${REPLY:-}"  # 确保REPLY变量已定义
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "安装已取消"
            exit 0
        fi
    else
        log_info "一键安装模式已启用，30秒后自动开始安装..."
        log_info "按 Ctrl+C 可以取消安装"
        sleep 30
        log_info "开始自动安装..."
    fi

    # 确保在项目目录中
    if [[ ! -f "requirements.txt" ]]; then
        log_error "未找到 requirements.txt，请确保在项目目录中运行此脚本"
        exit 1
    fi

    log_info "当前工作目录: $(pwd)"
    log_info "当前用户: $(whoami)"

    # 检测操作系统
    detect_os

    # 检查 Python 环境
    check_python

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
    echo "          🎉 部署完成！"
    echo "========================================"
    echo "项目位置: $(pwd)"
    echo "配置文件: config.json, .env"
    echo "启动命令: python3 capcut_server.py"
    echo

    # 获取服务器 IP 地址
    local server_ip=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "localhost")
    local local_ip=$(hostname -I | awk '{print $1}')
    local port=${PORT:-9000}

    echo "🌐 访问地址:"
    echo "  本地访问: http://localhost:$port"
    echo "  局域网访问: http://$local_ip:$port"
    echo "  外网访问: http://$server_ip:$port"
    echo
    echo "🔍 健康检查:"
    echo "  curl http://localhost:$port/health"
    echo
    echo "📖 API 文档: 请参考项目 README"
    echo "⚠️  防火墙设置: 如果外网无法访问，请检查防火墙设置"
    echo "   sudo ufw allow $port"
    echo

    if [[ "$AUTO_INSTALL" == "true" ]]; then
        echo "🚀 一键安装模式：服务将自动启动..."
        echo "   使用 Ctrl+C 停止服务"
        echo
    fi

    # 启动服务
    start_service
}

# 脚本入口
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]] || [[ -z "${BASH_SOURCE[0]:-}" ]]; then
    main "$@"
fi