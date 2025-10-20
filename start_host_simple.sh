#!/bin/bash

# CapCutAPI 简化启动脚本
# 自动选择执行root安装脚本或用户安装脚本

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

# 主函数
main() {
    echo "========================================"
    echo "    CapCutAPI 简化启动脚本"
    echo "========================================"
    echo

    if [[ $EUID -eq 0 ]]; then
        # Root用户：运行系统初始化脚本
        log_info "检测到root用户，将运行系统初始化..."
        log_info "完成后会自动切换到普通用户继续部署"
        echo

        # 检查root脚本是否存在
        if [[ ! -f "install_root.sh" ]]; then
            log_error "未找到 install_root.sh 脚本"
            exit 1
        fi

        chmod +x install_root.sh
        ./install_root.sh

        # 系统初始化完成后，提示切换用户
        echo
        log_info "系统初始化完成！"
        log_info "请运行以下命令切换到普通用户继续部署："
        echo "  su - capcut"
        echo "  cd CapCutAPI-Docker"
        echo "  bash install_user.sh"
        echo

    else
        # 普通用户：运行应用部署脚本
        log_info "检测到普通用户，将运行应用部署..."
        echo

        # 检查用户脚本是否存在
        if [[ ! -f "install_user.sh" ]]; then
            log_error "未找到 install_user.sh 脚本"
            log_info "请确保在项目目录中运行此脚本"
            exit 1
        fi

        chmod +x install_user.sh

        # 传递参数给用户脚本
        ./install_user.sh "$@"
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]:-}" == "${0}" ]] || [[ ! "${BASH_SOURCE[0]:-}" ]]; then
    main "$@"
fi