#!/bin/bash
# 跨环境任务模板管理系统部署脚本
# 主部署入口，根据环境选择部署方式

set -e

echo "========================================"
echo "跨环境任务模板管理系统 - 部署入口"
echo "========================================"
echo "检测系统环境..."
echo "系统: $(uname -s)"
echo "用户: $(whoami)"
echo "时间: $(date)"
echo "========================================"

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo ""
echo "请选择部署方式:"
echo "1) IRAYPLEOS系统专用部署"
echo "2) 通用Linux环境部署"
echo "3) 离线部署模式"
echo "4) Python 3.9专用部署"
echo ""
read -p "选择 (1/2/3/4, 默认2): " deploy_choice
deploy_choice=${deploy_choice:-2}

case $deploy_choice in
    1)
        echo "运行IRAYPLEOS专用部署..."
        if [ -f "deploy_iraypleos.sh" ]; then
            bash deploy_iraypleos.sh
        else
            echo "错误: deploy_iraypleos.sh不存在"
            exit 1
        fi
        ;;
    2)
        echo "运行通用部署..."
        if [ -f "deploy_generic.sh" ]; then
            bash deploy_generic.sh
        else
            echo "错误: deploy_generic.sh不存在"
            exit 1
        fi
        ;;
    3)
        echo "运行离线部署..."
        if [ -f "deploy_offline.sh" ]; then
            bash deploy_offline.sh
        else
            echo "错误: deploy_offline.sh不存在"
            exit 1
        fi
        ;;
    4)
        echo "运行Python 3.9专用部署..."
        if [ -f "deploy_py39.sh" ]; then
            bash deploy_py39.sh
        else
            echo "错误: deploy_py39.sh不存在"
            exit 1
        fi
        ;;
    *)
        echo "无效选择，使用通用部署..."
        if [ -f "deploy_generic.sh" ]; then
            bash deploy_generic.sh
        else
            echo "错误: deploy_generic.sh不存在"
            exit 1
        fi
        ;;
esac

echo ""
echo "========================================"
echo "部署向导完成！"
echo "========================================"
echo ""
echo "可用脚本列表:"
echo "- deploy.sh                 # 部署入口 (本脚本)"
echo "- deploy_iraypleos.sh       # IRAYPLEOS系统专用"
echo "- deploy_generic.sh         # 通用Linux环境"
echo "- deploy_offline.sh         # 离线部署模式"
echo "- deploy_py39.sh            # Python 3.9专用"
echo "- start_app.sh              # 启动应用"
echo ""
echo "快速启动:"
echo "  ./start_app.sh"
echo ""
echo "查看详细文档请参考 README.md"
echo "========================================"