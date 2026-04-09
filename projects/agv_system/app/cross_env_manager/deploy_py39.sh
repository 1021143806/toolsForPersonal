#!/bin/bash
# Python 3.9专用部署脚本
# 使用vendor_packages3.9目录和pymysql

set -e

echo "========================================"
echo "跨环境任务模板管理系统 - Python 3.9专用部署"
echo "========================================"

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 检查Python版本..."
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3未安装"
    exit 1
fi

python_version=$(python3 --version | awk '{print $2}')
echo "   Python版本: $python_version"

# 检查是否是Python 3.9
if [[ "$python_version" =~ ^3\.9\. ]]; then
    echo "   ✓ 检测到Python 3.9.x"
else
    echo "   ⚠️  当前不是Python 3.9.x (版本: $python_version)"
    echo "   此脚本专为Python 3.9设计，继续吗？"
    read -p "   继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "2. 检查Python 3.9兼容包..."
if [ -d "vendor_packages3.9" ] && [ "$(ls -A vendor_packages3.9/*.whl vendor_packages3.9/*.tar.gz 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "   ✓ 发现Python 3.9兼容包"
    PACKAGE_COUNT=$(ls -1 vendor_packages3.9/*.whl vendor_packages3.9/*.tar.gz 2>/dev/null | wc -l)
    echo "   包数量: $PACKAGE_COUNT"
    
    # 列出关键包
    echo "   关键包:"
    ls -1 vendor_packages3.9/*.whl vendor_packages3.9/*.tar.gz 2>/dev/null | xargs -I {} basename {} | grep -E "(flask|pymysql|werkzeug|jinja)" | sort
else
    echo "   ❌ 未找到Python 3.9兼容包"
    echo "   请先运行: ./create_py39_vendor.sh"
    exit 1
fi

echo ""
echo "3. 应用pymysql补丁..."
if [ -f "app_py39_patch.py" ]; then
    echo "   运行补丁脚本..."
    if python3 app_py39_patch.py; then
        echo "   ✓ pymysql补丁应用成功"
    else
        echo "   ⚠️  pymysql补丁应用失败或已应用"
    fi
else
    echo "   ⚠️  补丁脚本不存在，手动检查app.py..."
    if grep -q "pymysql" app.py && grep -q "pymysql.install_as_MySQLdb()" app.py; then
        echo "   ✓ app.py已包含pymysql配置"
    else
        echo "   ❌ app.py未配置pymysql"
        echo "   请在app.py开头添加:"
        echo "   import pymysql"
        echo "   pymysql.install_as_MySQLdb()"
        read -p "   是否自动添加? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # 在文件开头添加pymysql导入
            sed -i '1i import pymysql\npymysql.install_as_MySQLdb()' app.py
            echo "   ✓ 已添加pymysql配置"
        else
            echo "   ⚠️  需要手动配置pymysql"
        fi
    fi
fi

echo ""
echo "4. 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "   ⚠️  虚拟环境 'venv' 已存在"
    read -p "   是否重新创建虚拟环境? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   删除旧虚拟环境..."
        rm -rf venv
        echo "   创建新虚拟环境 'venv'..."
        python3 -m venv venv
    else
        echo "   使用现有虚拟环境"
    fi
else
    echo "   创建虚拟环境 'venv'..."
    python3 -m venv venv
fi

echo ""
echo "5. 激活虚拟环境并安装依赖..."
source venv/bin/activate

echo "   虚拟环境Python版本: $(python --version)"
echo "   pip版本: $(pip --version | awk '{print $2}')"

echo ""
echo "6. 使用Python 3.9兼容包安装依赖..."
echo "   安装命令: pip install --no-index --find-links=vendor_packages3.9 -r requirements.txt"

# 检查requirements.txt是否使用pymysql
if grep -q "mysql-connector-python" requirements.txt && ! grep -q "pymysql" requirements.txt; then
    echo "   ⚠️  requirements.txt仍使用mysql-connector-python"
    echo "   临时修改为pymysql..."
    cp requirements.txt requirements.txt.backup.deploy
    sed -i 's/mysql-connector-python==8.1.0/pymysql==1.1.0/' requirements.txt
    echo "   ✓ 已临时修改requirements.txt"
fi

# 安装依赖
if pip install --no-index --find-links=vendor_packages3.9 -r requirements.txt; then
    echo "   ✓ 依赖安装成功"
    
    # 恢复原requirements.txt
    if [ -f "requirements.txt.backup.deploy" ]; then
        mv requirements.txt.backup.deploy requirements.txt
        echo "   ✓ 恢复原requirements.txt"
    fi
else
    echo "   ❌ 依赖安装失败，尝试替代方案..."
    
    # 尝试逐个安装
    echo "   尝试逐个安装包..."
    INSTALL_SUCCESS=true
    
    for package in vendor_packages3.9/*.whl vendor_packages3.9/*.tar.gz; do
        if [ -f "$package" ]; then
            package_name=$(basename "$package")
            echo "   安装: $package_name"
            if pip install --no-index --find-links=vendor_packages3.9 "$package"; then
                echo "   ✓ 安装成功: $package_name"
            else
                echo "   ❌ 安装失败: $package_name"
                INSTALL_SUCCESS=false
            fi
        fi
    done
    
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo "   ❌ 部分依赖安装失败"
        echo "   建议使用在线安装:"
        echo "   pip install -r requirements.txt"
        exit 1
    else
        echo "   ⚠️  依赖安装完成（可能有警告）"
    fi
    
    # 恢复原requirements.txt
    if [ -f "requirements.txt.backup.deploy" ]; then
        mv requirements.txt.backup.deploy requirements.txt
    fi
fi

echo ""
echo "7. 验证安装..."
echo "   运行验证脚本..."
if python3 verify_offline.py; then
    echo "   ✓ 验证成功"
else
    echo "   ⚠️  验证有警告，但依赖已安装"
fi

echo ""
echo "8. 测试数据库连接..."
echo "   测试pymysql导入..."
if python3 -c "import pymysql; print('✓ pymysql导入成功')"; then
    echo "   ✓ pymysql工作正常"
else
    echo "   ❌ pymysql导入失败"
fi

echo ""
echo "========================================"
echo "Python 3.9部署完成！"
echo "========================================"
echo ""
echo "部署摘要:"
echo "- Python版本: $python_version"
echo "- 虚拟环境: $SCRIPT_DIR/venv"
echo "- 使用包目录: vendor_packages3.9/"
echo "- MySQL驱动: pymysql (替代mysql-connector-python)"
echo "- 安装包数量: $(pip list | wc -l)"
echo ""
echo "启动应用:"
echo "1. 确保虚拟环境已激活:"
echo "   source venv/bin/activate"
echo ""
echo "2. 启动应用:"
echo "   python app.py"
echo ""
echo "   或使用gunicorn:"
echo "   gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "3. 访问应用:"
echo "   http://localhost:5000"
echo "   http://localhost:5000/stats (统计页面)"
echo ""
echo "故障排除:"
echo "- 如果数据库连接失败，检查app.py中的数据库配置"
echo "- 如果页面显示异常，检查templates/stats.html布局"
echo "- 参考 DEPLOY_PY39.md 获取更多帮助"
echo "========================================"