#!/bin/bash
# 跨环境任务模板管理系统 - IRAYPLEOS专用部署脚本
# 专为IRAYPLEOS系统环境设计（仅离线安装模式）
# 该脚本仅限指定系统离线安装
# 版本: 3.0 (支持Python 3.9兼容性修复)

set -e

echo "========================================"
echo "跨环境任务模板管理系统 - IRAYPLEOS部署"
echo "========================================"
echo "系统: IRAYPLEOS"
echo "Python版本: $(python3 --version 2>&1)"
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

echo "1. 检查IRAYPLEOS系统环境..."
echo "   Python版本: $(python3 --version 2>&1)"

# IRAYPLEOS特定路径检查
echo "2. 检查IRAYPLEOS路径结构..."
if [ -d "/main/server/supervisor" ]; then
    echo "   ✓ 发现IRAYPLEOS supervisor目录"
else
    echo "   ⚠️  未找到标准IRAYPLEOS路径"
fi

# 检查IRAYPLEOS用户
IRAY_USER="ymsk"  # 修正：实际用户是ymsk，不是ymks
echo "   当前用户: $(whoami)"
echo "   Supervisor运行用户: $IRAY_USER"

echo ""
echo "3. 清理并创建虚拟环境..."
rm -rf venv 2>/dev/null || true
python3 -m venv venv

if [ ! -f "venv/bin/python" ]; then
    echo "   ❌ 虚拟环境创建失败"
    exit 1
fi
echo "   ✓ 虚拟环境创建成功"

echo ""
echo "4. 激活虚拟环境..."
source venv/bin/activate
echo "   虚拟环境Python: $(python --version 2>&1)"

echo ""
echo "5. 解决Python 3.9兼容性问题..."
echo "   已知问题:"
echo "   - markupsafe wheel为Python 3.10编译 (cp310)"
echo "   - importlib-metadata要求Python >= 3.10"
echo "   将使用兼容性修复方案..."

echo ""
echo "6. 安装markupsafe兼容版本..."
pip download markupsafe==2.1.1 --no-binary :all: 2>/dev/null
if [ -f MarkupSafe*.tar.gz ]; then
    pip install MarkupSafe*.tar.gz 2>/dev/null
    rm -f MarkupSafe*.tar.gz 2>/dev/null
    echo "   ✓ markupsafe 2.1.1源码安装成功"
else
    echo "   ❌ markupsafe下载失败"
    exit 1
fi

echo ""
echo "7. 应用pymysql补丁和修复mysql导入..."
if [ -f "fix_mysql_imports.py" ]; then
    python3 fix_mysql_imports.py
    echo "   ✓ mysql.connector导入修复完成"
else
    echo "   ⚠️  修复脚本不存在，手动修复mysql导入..."
    # 确保有pymysql导入
    if ! grep -q "import pymysql" app.py; then
        sed -i '1i# Python 3.9兼容性修改：使用pymysql替代mysql.connector\nimport pymysql\nfrom pymysql.cursors import DictCursor\n' app.py
    fi
    
    # 替换mysql.connector导入
    sed -i 's/import mysql\.connector/# import mysql.connector  # 已由pymysql替代/' app.py
    sed -i 's/from mysql\.connector import Error/# from MySQLdb import Error  # 使用pymysql.Error替代/' app.py
    sed -i 's/mysql\.connector\.connect/pymysql.connect/g' app.py
    sed -i 's/except Error as e:/except pymysql.Error as e:/g' app.py
    sed -i 's/cursor(dictionary=True)/cursor(DictCursor)/g' app.py
    
    echo "   ✓ 手动修复mysql导入完成"
fi

echo ""
echo "8. 安装关键依赖包..."
echo "   安装顺序: click -> itsdangerous -> tomli -> blinker -> python-dotenv -> Jinja2 -> Werkzeug -> PyMySQL -> Flask -> Markdown -> importlib_metadata zipp"

# 使用requirements_py39.txt安装，但先处理可能的问题
echo "   使用requirements_py39.txt安装（排除已知问题包）..."

# 创建临时requirements文件，排除有问题的包
TEMP_REQ=$(mktemp)
cp requirements_py39.txt "$TEMP_REQ"

# 如果markupsafe已在vendor中且不兼容，从requirements中移除
if find vendor_packages3.9 -iname "*markupsafe*.whl" -type f | head -1 | xargs basename 2>/dev/null | grep -q "cp310"; then
    sed -i '/[Mm]arkup[sS]afe/d' "$TEMP_REQ"
    echo "   已从requirements中移除markupsafe（已安装兼容版本）"
fi

# 安装
if pip install --no-index --find-links=vendor_packages3.9 -r "$TEMP_REQ" 2>/dev/null; then
    echo "   ✓ 批量依赖安装成功"
else
    echo "   ⚠️  批量安装失败，尝试逐个安装关键包..."
    
    # 逐个安装关键包
    for pkg in click itsdangerous tomli blinker python_dotenv Jinja2 Werkzeug PyMySQL Flask Markdown; do
        echo "   安装 $pkg..."
        wheel_file=$(find vendor_packages3.9 -iname "*${pkg}*.whl" -type f | head -1)
        if [ -f "$wheel_file" ]; then
            pip install "$wheel_file" 2>/dev/null && echo "   ✓ $pkg 安装成功" || echo "   ⚠️  $pkg 安装失败"
        else
            echo "   ⚠️  未找到 $pkg wheel文件"
        fi
    done
fi

rm -f "$TEMP_REQ"

# 特别处理markupsafe（已安装）和可能的importlib_metadata版本问题
echo "   检查importlib_metadata版本兼容性..."
if find vendor_packages3.9 -iname "*importlib_metadata*.whl" -type f | head -1 | xargs basename | grep -q "importlib_metadata"; then
    echo "   ⚠️  importlib_metadata可能需要特定版本，尝试安装..."
    # 尝试安装但允许失败
    IMP_WHEEL=$(find vendor_packages3.9 -iname "*importlib_metadata*.whl" -type f | head -1)
    if [ -f "$IMP_WHEEL" ]; then
        pip install "$IMP_WHEEL" 2>/dev/null || echo "   ⚠️  importlib_metadata安装失败（可能版本不兼容）"
    fi
fi

echo ""
echo "9. 验证安装..."
echo "   测试关键包导入:"
source venv/bin/activate  # 确保在虚拟环境中
for pkg in flask pymysql werkzeug jinja2 markupsafe; do
    if python -c "import $pkg; print('  ✓ $pkg')" 2>/dev/null; then
        echo "   ✓ $pkg导入成功"
    else
        echo "   ❌ $pkg导入失败"
        # 显示具体错误
        python -c "import $pkg" 2>&1 | head -2
        exit 1
    fi
done

echo ""
echo "10. 配置IRAYPLEOS Supervisor..."
SUPERVISOR_CONF="/main/server/supervisor/cross_env_manager.conf"

if [ -f "$SUPERVISOR_CONF" ]; then
    echo "   Supervisor配置已存在，备份..."
    cp "$SUPERVISOR_CONF" "${SUPERVISOR_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
fi

echo "   创建Supervisor配置..."

# 创建Supervisor配置
cat > "$SUPERVISOR_CONF" << EOF
[program:cross_env_manager]
command=$SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/app.py
directory=$SCRIPT_DIR
user=$IRAY_USER
autostart=true
autorestart=true
startsecs=10
startretries=3
redirect_stderr=true
stdout_logfile=/main/app/log/cross_env_manager.log
stdout_logfile_maxbytes=5MB
stdout_logfile_backups=0
stderr_logfile=/main/app/log/cross_env_manager_error.log
stderr_logfile_maxbytes=5MB
stderr_logfile_backups=0
environment=PYTHONPATH="$SCRIPT_DIR"
EOF

echo "11. 更新Supervisor配置..."
supervisorctl reread 2>/dev/null || echo "   ⚠️  配置重读失败"
supervisorctl update 2>/dev/null || echo "   ⚠️  配置更新失败"

echo "12. 启动服务..."
supervisorctl start cross_env_manager 2>/dev/null || supervisorctl restart cross_env_manager 2>/dev/null
sleep 2

echo ""
echo "13. 检查服务状态..."
if supervisorctl status cross_env_manager 2>/dev/null; then
    echo "   ✓ 服务运行中"
else
    echo "   ❌ 服务启动失败"
    echo "   检查日志: /main/app/log/cross_env_manager_error.log"
fi

echo ""
echo "========================================"
echo "IRAYPLEOS部署完成！"
echo "========================================"
echo ""
echo "服务信息:"
echo "- 应用URL: http://localhost:5000"
echo "- Supervisor配置: $SUPERVISOR_CONF"
echo "- 应用日志: /main/app/log/cross_env_manager.log"
echo "- 错误日志: /main/app/log/cross_env_manager_error.log"
echo ""
echo "常用命令:"
echo "- 查看状态: supervisorctl status cross_env_manager"
echo "- 重启服务: supervisorctl restart cross_env_manager"
echo "- 停止服务: supervisorctl stop cross_env_manager"
echo "- 查看日志: tail -f /main/app/log/cross_env_manager.log"
echo ""
echo "首次使用:"
echo "1. 访问 http://localhost:5000"
echo "2. 使用搜索功能测试数据库连接"
echo "3. 测试模板查看和编辑功能"
echo ""
echo "端口配置:"
echo "如需修改端口，请编辑 $SUPERVISOR_CONF 中的端口号"
echo "========================================"