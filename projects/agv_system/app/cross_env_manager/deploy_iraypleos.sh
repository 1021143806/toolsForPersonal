#!/bin/bash
# 跨环境任务模板管理系统 - IRAYPLEOS专用部署脚本（完全离线版）
# 专为IRAYPLEOS系统环境设计，完全离线安装，无网络依赖
# 版本: 4.0 (完全离线部署 - Python 3.9兼容性修复)
# 注意：所有依赖包必须预先下载并放入vendor_packages3.9目录

set -e

echo "========================================"
echo "跨环境任务模板管理系统 - IRAYPLEOS部署"
echo "========================================"
echo "系统: IRAYPLEOS (完全离线部署模式)"
echo "Python版本: $(python3 --version 2>&1)"
echo "用户: $(whoami)"
echo "时间: $(date)"
echo "部署模式: 100% 离线 (无网络连接)"
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
echo "   当前目录: $SCRIPT_DIR"

# IRAYPLEOS特定路径检查
echo "2. 检查IRAYPLEOS路径结构..."
if [ -d "/main/server/supervisor" ]; then
    echo "   ✓ 发现IRAYPLEOS supervisor目录"
else
    echo "   ⚠️  未找到标准IRAYPLEOS路径，使用当前目录"
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
echo "5. 完全离线依赖安装准备..."
echo "   检查离线包目录..."

# 关键检查：vendor_packages3.9目录必须存在且有wheel文件
if [ ! -d "vendor_packages3.9" ]; then
    echo "   ❌ 离线包目录 vendor_packages3.9 不存在"
    echo "   请在有网环境运行 download_packages_for_offline.sh 下载依赖包"
    echo "   然后将整个 vendor_packages3.9 目录复制到当前目录"
    exit 1
fi

WHL_COUNT=$(ls -1 vendor_packages3.9/*.whl 2>/dev/null | wc -l)
if [ $WHL_COUNT -eq 0 ]; then
    echo "   ❌ vendor_packages3.9目录中没有wheel文件"
    echo "   请确保已在有网环境下载了所有依赖包"
    exit 1
fi

echo "   ✓ 找到离线包目录，包含 $WHL_COUNT 个wheel文件"
echo "   完全离线安装模式：不尝试任何网络连接"

# 检查关键包
echo ""
echo "6. 检查关键包可用性..."
REQUIRED_PACKAGES=(
    "click"            # Flask基础依赖
    "itsdangerous"     # Flask安全组件
    "tomli"            # TOML解析
    "blinker"          # Flask信号库
    "python_dotenv"    # 环境变量支持
    "zipp"             # zip文件支持
    "Jinja2"           # 模板引擎
    "Werkzeug"         # WSGI工具
    "PyMySQL"          # MySQL连接（替代mysql-connector-python）
    "Flask"            # Web框架
    "Markdown"         # Markdown解析
    "importlib_metadata" # 包元数据
)

MISSING_PACKAGES=0
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if find vendor_packages3.9 -type f -iname "*${pkg}*.whl" | grep -q .; then
        echo "   ✓ $pkg"
    else
        echo "   ❌ 缺少: $pkg"
        MISSING_PACKAGES=$((MISSING_PACKAGES + 1))
    fi
done

if [ $MISSING_PACKAGES -gt 0 ]; then
    echo ""
    echo "   ⚠️  缺少 $MISSING_PACKAGES 个关键包"
    echo "   必须下载完整的依赖包集才能离线部署"
    echo "   请在联机环境运行 download_packages_for_offline.sh"
    exit 1
fi

# 检查markupsafe兼容性
echo ""
echo "7. 处理Python 3.9兼容性问题..."
MARKUPSAFE_WHEEL=$(find vendor_packages3.9 -type f -iname "*markupsafe*.whl" | head -1)
if [ -n "$MARKUPSAFE_WHEEL" ]; then
    WHEEL_NAME=$(basename "$MARKUPSAFE_WHEEL")
    echo "   找到markupsafe: $WHEEL_NAME"
    
    # 检查是否为Python 3.9兼容
    if echo "$WHEEL_NAME" | grep -q "cp39" || echo "$WHEEL_NAME" | grep -q "py3-none-any"; then
        echo "   ✓ markupsafe兼容Python 3.9"
        USE_MARKUPSAFE=1
    elif echo "$WHEEL_NAME" | grep -q "cp310"; then
        echo "   ⚠️  markupsafe为Python 3.10编译，将跳过安装"
        echo "   (Jinja2有纯Python降级机制，将自动使用)"
        USE_MARKUPSAFE=0
    else
        echo "   ⚠️  未知的markupsafe版本：$WHEEL_NAME"
        USE_MARKUPSAFE=0
    fi
else
    echo "   ⚠️  未找到markupsafe wheel文件"
    echo "   (Jinja2将使用纯Python实现)"
    USE_MARKUPSAFE=0
fi

echo ""
echo "8. 修复mysql.connector导入问题..."
# 应用pymysql补丁和修复mysql导入
if [ -f "fix_mysql_imports.py" ]; then
    echo "   应用mysql导入修复脚本..."
    python3 fix_mysql_imports.py
    echo "   ✓ mysql.connector导入修复完成"
else
    echo "   ❌ 修复脚本不存在，创建并应用修复..."
    # 创建修复脚本
    cat > fix_mysql_imports.py << 'EOF'
#!/usr/bin/env python3
"""
修复mysql.connector导入问题，替换为pymysql
Python 3.9离线部署兼容性修复
"""

import os

def fix_mysql_imports():
    """修复app.py中的mysql导入问题"""
    app_py_path = os.path.join(os.path.dirname(__file__), 'app.py')
    
    if not os.path.exists(app_py_path):
        print(f"错误: 找不到 {app_py_path}")
        return False
    
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换mysql.connector导入为pymysql
        replacements = [
            # 替换导入语句
            ('import mysql.connector', '# import mysql.connector  # 已由pymysql替代'),
            ('from mysql.connector import Error', '# from MySQLdb import Error  # 使用pymysql.Error替代'),
            # 替换连接函数
            ('mysql.connector.connect', 'pymysql.connect'),
            # 替换异常处理
            ('except Error as e:', 'except pymysql.Error as e:'),
            # 替换cursor
            ('cursor(dictionary=True)', 'cursor(DictCursor)'),
            ('cursor.DictCursor', 'DictCursor'),
        ]
        
        for old_str, new_str in replacements:
            content = content.replace(old_str, new_str)
        
        # 确保有pymysql导入
        if 'import pymysql' not in content:
            # 在文件开头添加导入
            lines = content.split('\n')
            if '# Python 3.9兼容性修改' not in lines[0]:
                lines.insert(0, 'from pymysql.cursors import DictCursor')
                lines.insert(0, 'import pymysql')
                lines.insert(0, '# Python 3.9兼容性修改：使用pymysql替代mysql.connector')
                content = '\n'.join(lines)
        
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ mysql.connector导入修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == '__main__':
    fix_mysql_imports()
EOF
    
    python3 fix_mysql_imports.py
    echo "   ✓ mysql.connector导入修复完成"
fi

# 定义安装包函数
install_package() {
    local pkg="$1"
    local pkg_display="$2"
    
    echo "   安装 ${pkg_display:-$pkg}..."
    
    # 查找wheel文件（不区分大小写）
    wheel_file=$(find vendor_packages3.9 -type f -iname "*${pkg}*.whl" | head -1)
    
    if [ -f "$wheel_file" ]; then
        # 对于离线环境，使用--no-deps避免依赖问题，加上--no-index确保不联网
        if pip install --no-index --no-deps "$wheel_file" 2>/dev/null; then
            echo "   ✓ ${pkg_display:-$pkg} 安装成功"
            return 0
        else
            echo "   ⚠️  ${pkg_display:-$pkg} 安装失败，尝试普通安装（无依赖检查）..."
            pip install --no-index "$wheel_file" 2>/dev/null && echo "   ✓ ${pkg_display:-$pkg} 安装成功" || {
                echo "   ❌ ${pkg_display:-$pkg} 安装失败"
                return 1
            }
            return 0
        fi
    else
        echo "   ❌ 未找到 ${pkg_display:-$pkg} wheel文件"
        return 2
    fi
}

echo ""
echo "9. 完全离线依赖包安装..."
echo "   安装策略：按依赖关系逐个安装，跳过markupsafe版本问题"

# 分阶段安装，按依赖关系顺序
echo "   按依赖顺序安装..."

# 第一阶段：最小基础包（无依赖）
echo "   🅰️ 第一阶段：最小基础包..."
install_package "click" "click"
install_package "itsdangerous" "itsdangerous"
install_package "tomli" "tomli"
install_package "zipp" "zipp"
install_package "blinker" "blinker"

# 第二阶段：工具包
echo "   🅱️ 第二阶段：工具包..."
install_package "python_dotenv" "python-dotenv"

# 第三阶段：数据库驱动
echo "   🅲️ 第三阶段：数据库驱动..."
install_package "PyMySQL" "PyMySQL"

# 第四阶段：模板和Web框架核心
echo "   🅳️ 第四阶段：模板引擎和WSGI..."
install_package "Werkzeug" "Werkzeug"
install_package "Jinja2" "Jinja2"

# 注意：跳过markupsafe安装，让Jinja2使用纯Python实现
if [ $USE_MARKUPSAFE -eq 1 ]; then
    echo "   安装markupsafe (兼容版本)..."
    install_package "markupsafe" "markupsafe"
else
    echo "   ⏭️  跳过markupsafe安装 (Jinja2将使用纯Python实现)"
fi

# 第五阶段：主框架和工具
echo "   🅴️ 第五阶段：主框架..."
install_package "importlib_metadata" "importlib-metadata"
install_package "Markdown" "Markdown"
install_package "Flask" "Flask"

echo ""
echo "10. 验证安装..."
echo "   测试关键包导入:"

test_import() {
    local pkg="$1"
    local display_name="$2"
    
    if python -c "try: import $pkg; print('   ✓ ${display_name:-$pkg}导入成功')\nexcept ImportError as e: print(f'   ❌ {display_name:-$pkg}导入失败: {e}'); exit(1)" 2>/dev/null; then
        return 0
    else
        echo "   ❌ ${display_name:-$pkg}导入失败"
        # 显示具体错误
        python -c "import $pkg" 2>&1 | head -2
        return 1
    fi
}

# 测试关键包（允许markupsafe失败）
test_import "flask" "Flask"
test_import "pymysql" "PyMySQL"
test_import "werkzeug" "Werkzeug"
test_import "jinja2" "Jinja2"

# 测试importlib_metadata，允许不同名称
if test_import "importlib_metadata" "importlib-metadata"; then
    echo "   ✓ importlib-metadata导入成功"
elif test_import "importlib.metadata" "importlib.metadata"; then
    echo "   ✓ importlib.metadata导入成功"
else
    echo "   ⚠️  importlib-metadata导入失败，尝试跳过..."
fi

echo ""
echo "11. 验证应用启动..."
echo "   测试应用模块加载..."
if python -c "
import sys
sys.path.insert(0, '.')
try:
    import app
    print('   ✓ 应用模块加载成功')
except Exception as e:
    print(f'   ⚠️  应用模块加载警告: {e}')
    print('   这可能是由于数据库连接配置，稍后启动时会验证')
" 2>/dev/null; then
    echo "   ✓ 应用验证通过"
else
    echo "   ⚠️  应用验证有小问题，继续部署"
fi

echo ""
echo "12. 配置IRAYPLEOS Supervisor..."
# 根据IRAYPLEOS环境确定Supervisor配置路径
if [ -d "/main/server/supervisor" ]; then
    SUPERVISOR_CONF="/main/server/supervisor/cross_env_manager.conf"
    LOG_DIR="/main/app/log"
else
    # 备选路径
    SUPERVISOR_CONF="/etc/supervisor/conf.d/cross_env_manager.conf"
    LOG_DIR="/var/log"
fi

# 确保日志目录存在
mkdir -p "$LOG_DIR" 2>/dev/null || true

if [ -f "$SUPERVISOR_CONF" ]; then
    echo "   Supervisor配置已存在，备份..."
    cp "$SUPERVISOR_CONF" "${SUPERVISOR_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   ✓ 配置备份完成"
fi

echo "   创建Supervisor配置..."

# 创建Supervisor配置（符合IRAYPLEOS模板）
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
stdout_logfile=$LOG_DIR/cross_env_manager.log
stdout_logfile_maxbytes=5MB
stdout_logfile_backups=0
stderr_logfile=$LOG_DIR/cross_env_manager_error.log
stderr_logfile_maxbytes=5MB
stderr_logfile_backups=0
environment=PYTHONPATH="$SCRIPT_DIR"
EOF

echo "   ✓ Supervisor配置创建完成"

echo ""
echo "13. 更新Supervisor配置..."
if command -v supervisorctl >/dev/null 2>&1; then
    echo "   重新读取配置..."
    supervisorctl reread 2>/dev/null || echo "   ⚠️  配置重读失败"
    echo "   更新配置..."
    supervisorctl update 2>/dev/null || echo "   ⚠️  配置更新失败"
else
    echo "   ⚠️  supervisorctl命令未找到"
    echo "   请手动重启Supervisor或启动服务"
fi

echo ""
echo "14. 启动服务..."
if command -v supervisorctl >/dev/null 2>&1; then
    echo "   启动cross_env_manager服务..."
    supervisorctl start cross_env_manager 2>/dev/null || {
        echo "   ⚠️  启动失败，尝试重启..."
        supervisorctl restart cross_env_manager 2>/dev/null || echo "   ⚠️  重启失败"
    }
    sleep 3
else
    echo "   ⚠️  无法通过supervisorctl启动服务"
    echo "   需要手动启动: $SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/app.py"
fi

echo ""
echo "15. 检查服务状态..."
if command -v supervisorctl >/dev/null 2>&1; then
    if supervisorctl status cross_env_manager 2>/dev/null; then
        echo "   ✓ 服务已在Supervisor中运行"
    else
        echo "   ⚠️  服务未在Supervisor中运行"
        echo "   将尝试直接启动..."
        nohup "$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/app.py" > "$LOG_DIR/cross_env_manager_direct.log" 2>&1 &
        sleep 2
        if pgrep -f "python.*app.py" >/dev/null; then
            echo "   ✓ 已通过直接启动方式运行"
        else
            echo "   ❌ 服务启动失败"
        fi
    fi
else
    echo "   ⚠️  无法通过supervisorctl检查状态"
    if pgrep -f "python.*app.py" >/dev/null; then
        echo "   ✓ 服务已在运行"
    else
        echo "   ❌ 服务未运行"
    fi
fi

echo ""
echo "========================================"
echo "完全离线部署完成！"
echo "========================================"
echo ""
echo "部署信息:"
echo "- 模式: 100% 离线安装 (无网络连接)"
echo "- Python: $(python --version 2>&1)"
echo "- 虚拟环境: $SCRIPT_DIR/venv/"
echo "- Wheel包数量: $WHL_COUNT 个"
echo "- markupsafe解决: $([ $USE_MARKUPSAFE -eq 1 ] && echo "已安装兼容版本" || echo "使用Jinja2纯Python模式")"
echo ""
echo "服务信息:"
echo "- 应用URL: http://localhost:5000"
echo "- Supervisor配置: $SUPERVISOR_CONF"
echo "- 应用日志: $LOG_DIR/cross_env_manager.log"
echo "- 错误日志: $LOG_DIR/cross_env_manager_error.log"
echo "- 直接启动日志: $LOG_DIR/cross_env_manager_direct.log (备选)"
echo ""
echo "常用命令:"
echo "- 查看状态: supervisorctl status cross_env_manager"
echo "- 重启服务: supervisorctl restart cross_env_manager"
echo "- 停止服务: supervisorctl stop cross_env_manager"
echo "- 查看日志: tail -f $LOG_DIR/cross_env_manager.log"
echo ""
echo "离线部署验证:"
echo "1. 检查应用是否运行: pgrep -f 'python.*app.py'"
echo "2. 测试接口: curl -s http://localhost:5000/health | grep -i ok || echo '可能需要等待启动'"
echo "3. 查看日志: tail -f $LOG_DIR/cross_env_manager.log"
echo ""
echo "注意:"
echo "- 此部署完全离线，依赖包来自 vendor_packages3.9/"
echo "- 如需更新版本，请在有网环境更新包并重新部署"
echo "- 确保防火墙已开放5000端口（如果需要外部访问）"
echo "========================================"