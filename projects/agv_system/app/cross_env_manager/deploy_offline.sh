#!/bin/bash
# 跨环境任务模板管理系统离线部署脚本
# 支持无网络环境部署

set -e

echo "========================================"
echo "跨环境任务模板管理系统离线部署脚本"
echo "========================================"

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3未安装"
    exit 1
fi

python_version=$(python3 --version | awk '{print $2}')
echo "   Python版本: $python_version"

echo "2. 检查离线依赖包..."
if [ -d "vendor_packages" ] && [ "$(ls -A vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "   发现离线依赖包，使用离线安装模式"
    OFFLINE_MODE=true
else
    echo "   未找到离线依赖包，使用在线安装模式"
    OFFLINE_MODE=false
    
    # 检查网络连接
    if ! curl -s --connect-timeout 5 https://pypi.org > /dev/null; then
        echo "   警告: 无法连接到PyPI，离线依赖包不存在，安装可能失败"
        echo "   请在有网络的环境下运行以下命令准备离线包:"
        echo "   python3 -m pip download -r requirements.txt -d vendor_packages"
    fi
fi

echo "3. 创建虚拟环境..."
# 使用venv而不是conda，因为conda可能不可用
if [ -d "venv" ]; then
    echo "   虚拟环境 'venv' 已存在，跳过创建"
else
    echo "   创建虚拟环境 'venv'..."
    python3 -m venv venv
fi

echo "4. 激活虚拟环境并安装依赖..."
source venv/bin/activate

if [ "$OFFLINE_MODE" = true ]; then
    echo "   使用离线依赖包安装..."
    # 安装所有下载的包
    pip install --no-index --find-links=vendor_packages -r requirements.txt
else
    echo "   使用在线安装..."
    pip install -r requirements.txt
    
    # 可选：下载依赖包供以后离线使用
    echo "   下载依赖包供离线使用..."
    mkdir -p vendor_packages
    pip download -r requirements.txt -d vendor_packages
fi

# echo "5. 检查数据库配置..."
# if [ -f "config/env.toml" ]; then
#     echo "   使用现有配置文件: config/env.toml"
#     echo "   数据库配置:"
#     grep -A 5 "\[database\]" config/env.toml | grep -v "^\[" || echo "   未找到数据库配置"
# else
#     echo "   警告: 配置文件 config/env.toml 不存在"
#     echo "   请创建配置文件或使用模板: cp config/template/env.toml config/env.toml"
#     echo "   然后编辑配置文件设置正确的数据库连接"
# fi

# echo "6. 配置supervisor..."
# SUPERVISOR_CONF="/main/app/supervisor/conf.d/cross_env_manager.conf"
# if [ -f "$SUPERVISOR_CONF" ]; then
#     echo "   supervisor配置已存在，备份原配置..."
#     cp "$SUPERVISOR_CONF" "${SUPERVISOR_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
# fi

# echo "   生成supervisor配置文件..."
# # 创建supervisor配置
# cat > cross_env_manager_supervisor_offline.conf << EOF
# [program:cross_env_manager]
# command=$SCRIPT_DIR/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
# directory=$SCRIPT_DIR
# user=a1
# autostart=true
# autorestart=true
# startsecs=10
# startretries=3
# redirect_stderr=true
# stdout_logfile=/main/app/log/cross_env_manager.log
# stdout_logfile_maxbytes=10MB
# stdout_logfile_backups=5
# stderr_logfile=/main/app/log/cross_env_manager_error.log
# stderr_logfile_maxbytes=10MB
# stderr_logfile_backups=5
# environment=PYTHONPATH="$SCRIPT_DIR",PATH="$SCRIPT_DIR/venv/bin:%(ENV_PATH)s"
# EOF

# echo "   复制supervisor配置文件..."
# cp cross_env_manager_supervisor_offline.conf "$SUPERVISOR_CONF"

# echo "7. 更新supervisor配置..."
# supervisorctl update

# echo "8. 启动服务..."
# supervisorctl start cross_env_manager

# echo "9. 检查服务状态..."
# sleep 2
# supervisorctl status cross_env_manager

echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "服务信息:"
echo "- 应用URL: http://localhost:5000"
echo "- 日志文件: /main/app/log/cross_env_manager.log"
echo "- Supervisor配置: $SUPERVISOR_CONF"
echo "- 虚拟环境: $SCRIPT_DIR/venv"
echo "- 部署模式: $(if [ "$OFFLINE_MODE" = true ]; then echo "离线"; else echo "在线"; fi)"
echo ""
echo "常用命令:"
echo "- 查看状态: supervisorctl status cross_env_manager"
echo "- 重启服务: supervisorctl restart cross_env_manager"
echo "- 停止服务: supervisorctl stop cross_env_manager"
echo "- 查看日志: tail -f /main/app/log/cross_env_manager.log"
echo ""
echo "离线部署说明:"
echo "1. 在有网络的环境准备离线包:"
echo "   python3 -m pip download -r requirements.txt -d vendor_packages"
echo "2. 将整个项目目录复制到无网络环境"
echo "3. 运行此脚本进行离线部署"
echo "========================================"