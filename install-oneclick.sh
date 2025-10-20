#!/bin/bash

# CapCutAPI 一键安装脚本
# 这是 start_host.sh 的简化版本，专为快速安装设计

set -euo pipefail

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示安装信息
echo "========================================"
echo "    CapCutAPI 一键安装脚本"
echo "========================================"
echo "此脚本将自动完成以下操作："
echo "  ✓ 系统更新和依赖安装"
echo "  ✓ 安装 Python 3.11"
echo "  ✓ 下载并配置 CapCutAPI"
echo "  ✓ 创建虚拟环境并安装依赖"
echo "  ✓ 启动服务"
echo
echo "安装完成后，服务将运行在端口 9000"
echo

# 检查权限
if [[ $EUID -eq 0 ]]; then
    log_info "检测到 root 权限，将进行完整安装..."
else
    log_warning "建议使用 root 权限运行以确保完整安装"
    log_info "使用 sudo bash install-oneclick.sh 重新运行"
    read -p "是否继续以普通用户安装? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 获取当前脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查主安装脚本是否存在
if [[ ! -f "start_host.sh" ]]; then
    log_error "未找到 start_host.sh 脚本"
    exit 1
fi

# 确保脚本有执行权限
chmod +x start_host.sh

log_info "开始一键安装..."
log_info "如需中断安装，请按 Ctrl+C"

# 执行主安装脚本（自动模式）
exec bash start_host.sh --auto