#!/bin/bash
# 跨环境任务模板管理系统部署脚本

set -e

echo "========================================"
echo "跨环境任务模板管理系统部署脚本"
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

echo "2. 创建conda虚拟环境..."
if conda env list | grep -q "cross_env_manager"; then
    echo "   虚拟环境 'cross_env_manager' 已存在，跳过创建"
else
    echo "   创建虚拟环境 'cross_env_manager'..."
    conda create -n cross_env_manager python=3.9 -y
fi

echo "3. 激活虚拟环境并安装依赖..."
source /home/a1/miniconda3/etc/profile.d/conda.sh
conda activate cross_env_manager

echo "   安装Python依赖..."
pip install -r requirements.txt

echo "4. 检查数据库..."
echo "   数据库配置:"
echo "   - 主机: $(grep DB_HOST .env | cut -d= -f2)"
echo "   - 数据库: $(grep DB_NAME .env | cut -d= -f2)"
echo "   - 用户: $(grep DB_USER .env | cut -d= -f2)"

echo "5. 配置supervisor..."
SUPERVISOR_CONF="/main/app/supervisor/conf.d/cross_env_manager.conf"
if [ -f "$SUPERVISOR_CONF" ]; then
    echo "   supervisor配置已存在，备份原配置..."
    cp "$SUPERVISOR_CONF" "${SUPERVISOR_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
fi

echo "   复制supervisor配置文件..."
cp cross_env_manager_supervisor.conf "$SUPERVISOR_CONF"

echo "6. 更新supervisor配置..."
supervisorctl update

echo "7. 启动服务..."
supervisorctl start cross_env_manager

echo "8. 检查服务状态..."
sleep 2
supervisorctl status cross_env_manager

echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "服务信息:"
echo "- 应用URL: http://localhost:5000"
echo "- 日志文件: /main/app/log/cross_env_manager.log"
echo "- Supervisor配置: $SUPERVISOR_CONF"
echo ""
echo "常用命令:"
echo "- 查看状态: supervisorctl status cross_env_manager"
echo "- 重启服务: supervisorctl restart cross_env_manager"
echo "- 停止服务: supervisorctl stop cross_env_manager"
echo "- 查看日志: tail -f /main/app/log/cross_env_manager.log"
echo ""
echo "首次使用建议:"
echo "1. 访问 http://localhost:5000"
echo "2. 使用搜索功能测试数据库连接"
echo "3. 尝试复制一个模板测试完整功能"
echo "========================================"