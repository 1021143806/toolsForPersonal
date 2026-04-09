#!/bin/bash
# 下载Python 3.9兼容的离线依赖包

set -e

echo "下载Python 3.9兼容的离线依赖包"
echo "================================="

# 检查Python 3.9是否可用
if command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
    echo "✓ 找到python3.9: $(python3.9 --version)"
elif python3 --version | grep -q "3\.9"; then
    PYTHON_CMD="python3"
    echo "✓ 当前python3是3.9版本: $(python3 --version)"
else
    echo "❌ 未找到Python 3.9"
    echo "请先安装Python 3.9，或使用以下方法："
    echo "1. 安装Python 3.9: sudo apt-get install python3.9"
    echo "2. 或使用conda创建Python 3.9环境"
    echo "3. 或在有Python 3.9的机器上下载包"
    exit 1
fi

# 备份现有包
if [ -d "vendor_packages" ]; then
    BACKUP_DIR="vendor_packages_backup_$(date +%Y%m%d_%H%M%S)"
    echo "备份现有包到: $BACKUP_DIR"
    mv vendor_packages "$BACKUP_DIR"
fi

# 创建新目录
mkdir -p vendor_packages

echo ""
echo "使用 $PYTHON_CMD 下载依赖包..."
echo "下载命令: $PYTHON_CMD -m pip download -r requirements.txt -d vendor_packages"

# 下载包
if $PYTHON_CMD -m pip download -r requirements.txt -d vendor_packages; then
    echo "✓ 依赖包下载成功"
else
    echo "❌ 依赖包下载失败"
    echo "尝试使用pip3下载..."
    if pip3 download -r requirements.txt -d vendor_packages; then
        echo "✓ 使用pip3下载成功"
    else
        echo "❌ 下载失败，请检查网络连接和pip配置"
        exit 1
    fi
fi

# 检查下载的包
echo ""
echo "检查下载的包..."
PACKAGE_COUNT=$(ls -1 vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | wc -l)
echo "下载包数量: $PACKAGE_COUNT"

if [ $PACKAGE_COUNT -eq 0 ]; then
    echo "❌ 未下载任何包"
    exit 1
fi

# 检查MySQL包
MYSQL_PACKAGE=$(find vendor_packages -name "*mysql*connector*" -type f | head -1)
if [ -n "$MYSQL_PACKAGE" ]; then
    PACKAGE_NAME=$(basename "$MYSQL_PACKAGE")
    echo "MySQL包: $PACKAGE_NAME"
    
    if [[ "$PACKAGE_NAME" =~ cp39 ]]; then
        echo "✓ MySQL包针对Python 3.9编译"
    elif [[ "$PACKAGE_NAME" =~ cp310 ]]; then
        echo "⚠️  MySQL包针对Python 3.10编译"
        echo "   这可能不是使用Python 3.9下载的"
    else
        echo "ℹ️  MySQL包版本未知"
    fi
else
    echo "⚠️  未找到MySQL连接器包"
fi

# 列出所有包
echo ""
echo "下载的包列表:"
ls -1 vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | xargs -I {} basename {} | sort

# 测试安装
echo ""
echo "测试安装兼容性..."
if [ -f "deploy_offline.sh" ]; then
    echo "可以运行以下命令测试安装:"
    echo "./deploy_offline.sh"
else
    echo "创建测试安装脚本..."
    cat > test_install_py39.sh << 'EOF'
#!/bin/bash
# 测试Python 3.9包安装

set -e

echo "测试Python 3.9包安装..."
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate

echo "Python版本: $(python --version)"
echo "pip版本: $(pip --version | awk '{print $2}')"

echo "尝试安装..."
if pip install --no-index --find-links=vendor_packages -r requirements.txt; then
    echo "✓ 安装成功"
else
    echo "❌ 安装失败"
    echo "尝试逐个安装..."
    
    for package in vendor_packages/*.whl vendor_packages/*.tar.gz; do
        if [ -f "$package" ]; then
            echo "安装: $(basename "$package")"
            pip install --no-index --find-links=vendor_packages "$package" || true
        fi
    done
fi

echo "验证安装..."
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import mysql.connector; print('MySQL连接器: 已安装')" 2>/dev/null || echo "MySQL连接器: 未安装"
EOF
    
    chmod +x test_install_py39.sh
    echo "创建测试脚本: test_install_py39.sh"
fi

echo ""
echo "下载完成！"
echo "=========="
echo "下一步操作:"
echo "1. 将 vendor_packages/ 目录复制到目标环境"
echo "2. 在目标环境运行: ./deploy_offline.sh"
echo "3. 或运行测试: ./test_install_py39.sh"
echo ""
echo "注意: 确保目标环境也是Python 3.9.x"