#!/bin/bash
# 修复MySQL包为Python 3.9兼容版本

set -e

echo "修复MySQL包为Python 3.9兼容版本"
echo "=================================="

# 检查当前vendor_packages
if [ ! -d "vendor_packages" ]; then
    echo "❌ vendor_packages目录不存在"
    exit 1
fi

# 备份现有MySQL包
echo "备份现有MySQL包..."
MYSQL_PACKAGES=$(find vendor_packages -name "*mysql*connector*" -type f)
if [ -n "$MYSQL_PACKAGES" ]; then
    for package in $MYSQL_PACKAGES; do
        BACKUP_FILE="${package}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$package" "$BACKUP_FILE"
        echo "备份: $(basename "$package") -> $(basename "$BACKUP_FILE")"
    done
else
    echo "⚠️  未找到MySQL包"
fi

echo ""
echo "当前vendor_packages内容:"
ls -la vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | awk '{print $9}' | xargs -I {} basename {} | sort

echo ""
echo "方案1: 下载Python 3.9兼容的MySQL包"
echo "----------------------------------"
echo "如果当前环境有网络连接，可以尝试下载Python 3.9兼容的包"

# 检查网络
if curl -s --connect-timeout 5 https://pypi.org > /dev/null; then
    echo "✓ 网络连接正常"
    
    # 创建临时目录下载Python 3.9包
    TEMP_DIR=$(mktemp -d)
    echo "临时目录: $TEMP_DIR"
    
    echo "下载MySQL连接器包..."
    # 尝试下载多个可能兼容的版本
    for version in "8.1.0" "8.0.33" "8.0.32"; do
        echo "尝试版本: mysql-connector-python==$version"
        if pip download --no-deps --platform manylinux2014_x86_64 --python-version 39 --implementation cp --abi cp39 \
            "mysql-connector-python==$version" -d "$TEMP_DIR" 2>/dev/null; then
            echo "✓ 下载成功: mysql-connector-python==$version"
            break
        fi
    done
    
    # 如果上述方法失败，尝试通用方法
    if [ ! -f "$TEMP_DIR"/*mysql*connector* ]; then
        echo "尝试通用下载..."
        pip download "mysql-connector-python==8.1.0" -d "$TEMP_DIR" 2>/dev/null || true
    fi
    
    # 检查是否下载成功
    NEW_MYSQL_PACKAGE=$(find "$TEMP_DIR" -name "*mysql*connector*" -type f | head -1)
    if [ -n "$NEW_MYSQL_PACKAGE" ]; then
        echo "下载的新包: $(basename "$NEW_MYSQL_PACKAGE")"
        
        # 删除旧的MySQL包
        rm -f vendor_packages/*mysql*connector*
        
        # 复制新包
        cp "$NEW_MYSQL_PACKAGE" vendor_packages/
        echo "✓ 已替换为Python 3.9兼容包"
    else
        echo "❌ 未能下载Python 3.9兼容包"
    fi
    
    # 清理临时目录
    rm -rf "$TEMP_DIR"
else
    echo "❌ 无网络连接，无法下载"
fi

echo ""
echo "方案2: 使用pymysql替代"
echo "----------------------"
echo "如果无法获得mysql-connector-python的Python 3.9版本，可以使用pymysql作为替代"

read -p "是否使用pymysql替代? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "更新requirements.txt..."
    if grep -q "mysql-connector-python" requirements.txt; then
        # 备份原文件
        cp requirements.txt requirements.txt.backup
        
        # 替换为pymysql
        sed -i 's/mysql-connector-python==8.1.0/pymysql==1.1.0/' requirements.txt
        echo "✓ requirements.txt已更新"
        
        # 下载pymysql包
        echo "下载pymysql包..."
        if curl -s --connect-timeout 5 https://pypi.org > /dev/null; then
            pip download "pymysql==1.1.0" -d vendor_packages/ 2>/dev/null && echo "✓ pymysql包已下载"
        fi
        
        echo ""
        echo "注意: 使用pymysql需要修改app.py中的导入"
        echo "在app.py开头添加:"
        echo "import pymysql"
        echo "pymysql.install_as_MySQLdb()"
    else
        echo "❌ 未找到mysql-connector-python在requirements.txt中"
    fi
fi

echo ""
echo "方案3: 手动提供Python 3.9包"
echo "---------------------------"
echo "可以手动将Python 3.9兼容的MySQL包复制到vendor_packages目录"
echo "需要的包名应该包含 'cp39'，例如:"
echo "mysql_connector_python-8.1.0-cp39-cp39-manylinux_2_17_x86_64.whl"
echo ""
echo "操作步骤:"
echo "1. 在有Python 3.9的环境下载包:"
echo "   python3.9 -m pip download mysql-connector-python==8.1.0 -d ./"
echo "2. 将下载的包复制到 vendor_packages/ 目录"
echo "3. 删除旧的MySQL包: rm vendor_packages/*mysql*connector*cp310*"

echo ""
echo "修复完成！"
echo "=========="
echo "当前vendor_packages内容:"
ls -la vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | awk '{print $9}' | xargs -I {} basename {} | sort

echo ""
echo "验证步骤:"
echo "1. 运行: ./test_py39_compatibility.sh"
echo "2. 测试安装: ./deploy_offline.sh"
echo "3. 或参考: PYTHON39_MYSQL_FIX.md"