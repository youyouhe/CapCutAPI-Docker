#!/bin/bash

# UFW防火墙配置脚本
# 确保SSH访问后再启用防火墙，避免断开连接

echo "=== UFW防火墙配置脚本 ==="
echo "检查当前UFW状态..."

# 检查UFW当前状态
ufw_status=$(sudo ufw status | head -1)
echo "当前状态: $ufw_status"

# 如果已经激活，询问是否重新配置
if [[ "$ufw_status" == "Status: active" ]]; then
    echo "UFW已经激活。"
    read -p "是否要重新配置防火墙规则? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "配置取消。"
        exit 0
    fi

    # 重置UFW规则
    echo "重置现有UFW规则..."
    sudo ufw --force reset
fi

echo "开始配置UFW防火墙规则..."

# 1. 首先允许SSH端口（避免断开连接）
echo "1. 允许SSH端口22/tcp..."
sudo ufw allow 22/tcp comment "SSH access"

# 2. 允许HTTP和HTTPS（如果运行web服务）
echo "2. 允许HTTP和HTTPS端口..."
sudo ufw allow 80/tcp comment "HTTP"
sudo ufw allow 443/tcp comment "HTTPS"

# 3. 允许CapCutAPI默认端口9000
echo "3. 允许CapCutAPI端口9000..."
sudo ufw allow 9000/tcp comment "CapCutAPI"

# 4. 允许端口9001（从netstat看到有服务在运行）
echo "4. 允许端口9001..."
sudo ufw allow 9001/tcp comment "Service on port 9001"

# 5. 允许DNS（如果需要）
echo "5. 允许DNS查询..."
sudo ufw allow 53 comment "DNS"

# 6. 设置默认策略
echo "6. 设置默认防火墙策略..."
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 7. 显示配置的规则
echo ""
echo "=== 配置的防火墙规则 ==="
sudo ufw status numbered

# 确认是否启用UFW
echo ""
read -p "确认要启用UFW防火墙吗? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在启用UFW防火墙..."
    sudo ufw --force enable

    echo ""
    echo "=== UFW防火墙已激活 ==="
    sudo ufw status verbose

    echo ""
    echo "防火墙配置完成！"
    echo "允许的端口："
    echo "  - 22/tcp (SSH)"
    echo "  - 80/tcp (HTTP)"
    echo "  - 443/tcp (HTTPS)"
    echo "  - 9000/tcp (CapCutAPI)"
    echo "  - 9001/tcp (Custom Service)"
    echo "  - 53 (DNS)"
    echo ""
    echo "如果需要添加其他端口，请使用："
    echo "  sudo ufw allow <port>/<protocol>"
    echo ""
    echo "查看防火墙状态："
    echo "  sudo ufw status"

else
    echo "UFW启用已取消。"
    echo "规则已配置但未激活。"
    echo "如需手动启用，请运行："
    echo "  sudo ufw enable"
fi

echo ""
echo "脚本执行完成。"