#!/bin/bash
# 跨环境任务模板管理系统离线依赖安装脚本
# 仅用于安装Python依赖，支持无网络环境

set -e

echo "========================================"
echo "跨环境任务模板管理系统 - 离线依赖安装脚本"
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

# 检查Python版本兼容性
if [[ "$python_version" =~ ^3\.(9|10|11|12) ]]; then
    echo "   ✓ Python版本兼容"
else
    echo "   ⚠️  Python版本 $python_version，建议使用Python 3.9+"
fi

echo "2. 检查离线依赖包..."
if [ -d "vendor_packages" ] && [ "$(ls -A vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "   ✓ 发现离线依赖包，使用离线安装模式"
    OFFLINE_MODE=true
    echo "   离线包数量: $(ls -1 vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | wc -l)"
else
    echo "   ⚠️  未找到离线依赖包，使用在线安装模式"
    OFFLINE_MODE=false
    
    # 检查网络连接
    if ! curl -s --connect-timeout 5 https://pypi.org > /dev/null; then
        echo "   ❌ 无法连接到PyPI，且离线依赖包不存在"
        echo "   请在有网络的环境下运行以下命令准备离线包:"
        echo "   python3 -m pip download -r requirements.txt -d vendor_packages"
        echo "   或手动下载以下依赖包到 vendor_packages/ 目录:"
        cat requirements.txt
        exit 1
    else
        echo "   ✓ 网络连接正常，可以使用在线安装"
    fi
fi

echo "3. 创建虚拟环境..."
# 使用venv而不是conda，因为conda可能不可用
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

echo "4. 激活虚拟环境并安装依赖..."
source venv/bin/activate

echo "   虚拟环境Python版本: $(python --version)"
echo "   pip版本: $(pip --version | awk '{print $2}')"

if [ "$OFFLINE_MODE" = true ]; then
    echo "   使用离线依赖包安装..."
    echo "   安装命令: pip install --no-index --find-links=vendor_packages -r requirements.txt"
    
    # 先检查是否有平台特定的mysql-connector包
    MYSQL_PACKAGE=$(find vendor_packages -name "*mysql*connector*" -type f | head -1)
    if [ -n "$MYSQL_PACKAGE" ]; then
        echo "   发现MySQL连接器包: $(basename "$MYSQL_PACKAGE")"
        
        # 检查包是否与当前Python版本兼容
        if [[ "$MYSQL_PACKAGE" =~ cp310 ]] && [[ ! "$python_version" =~ ^3\.10 ]]; then
            echo "   ⚠️  MySQL包针对Python 3.10编译，当前版本: $python_version"
            echo "   尝试安装通用版本或使用在线安装..."
        fi
    fi
    
    # 尝试安装所有下载的包
    echo "   尝试离线安装..."
    if pip install --no-index --find-links=vendor_packages -r requirements.txt; then
        echo "   ✓ 离线依赖安装成功"
    else
        echo "   ⚠️  离线依赖安装失败，尝试替代方案..."
        
        # 尝试逐个安装包
        echo "   尝试逐个安装依赖包..."
        INSTALL_SUCCESS=true
        
        # 先安装不依赖特定平台的包
        for package in vendor_packages/*.whl vendor_packages/*.tar.gz; do
            if [ -f "$package" ]; then
                package_name=$(basename "$package")
                # 跳过可能不兼容的mysql包
                if [[ "$package_name" =~ mysql.*connector ]] && [[ "$package_name" =~ cp310 ]] && [[ ! "$python_version" =~ ^3\.10 ]]; then
                    echo "   跳过可能不兼容的包: $package_name"
                    continue
                fi
                
                echo "   安装: $package_name"
                if pip install --no-index --find-links=vendor_packages "$package"; then
                    echo "   ✓ 安装成功: $package_name"
                else
                    echo "   ❌ 安装失败: $package_name"
                    INSTALL_SUCCESS=false
                fi
            fi
        done
        
        # 检查mysql-connector是否安装成功
        if python -c "import mysql.connector" 2>/dev/null; then
            echo "   ✓ MySQL连接器已安装"
        else
            echo "   ⚠️  MySQL连接器未安装，尝试使用在线安装或替代方案"
            echo "   可以尝试:"
            echo "   1. 使用 pip install mysql-connector-python 在线安装"
            echo "   2. 使用 pip install pymysql 作为替代"
            echo "   3. 下载适合Python $python_version 的mysql-connector包"
            INSTALL_SUCCESS=false
        fi
        
        if [ "$INSTALL_SUCCESS" = false ]; then
            echo "   ❌ 部分依赖安装失败"
            echo "   建议:"
            echo "   1. 在有网络的环境重新下载适合Python $python_version 的依赖包"
            echo "   2. 或使用在线安装模式"
            echo "   3. 或手动安装缺失的依赖"
            exit 1
        else
            echo "   ⚠️  依赖安装完成（可能有警告）"
        fi
    fi
else
    echo "   使用在线安装..."
    echo "   安装命令: pip install -r requirements.txt"
    
    if pip install -r requirements.txt; then
        echo "   ✓ 在线依赖安装成功"
        
        # 可选：下载依赖包供以后离线使用
        echo "   下载依赖包供离线使用..."
        mkdir -p vendor_packages
        if pip download -r requirements.txt -d vendor_packages; then
            echo "   ✓ 离线依赖包下载成功"
            echo "   离线包保存到: $SCRIPT_DIR/vendor_packages/"
        else
            echo "   ⚠️  离线依赖包下载失败，但依赖已安装"
        fi
    else
        echo "   ❌ 在线依赖安装失败"
        echo "   可能的原因:"
        echo "   1. 网络连接问题"
        echo "   2. PyPI服务器不可用"
        echo "   3. 依赖包版本冲突"
        exit 1
    fi
fi

echo "5. 验证依赖安装..."
echo "   验证命令: python3 verify_offline.py"
if python3 verify_offline.py; then
    echo "   ✓ 依赖验证成功"
else
    echo "   ⚠️  依赖验证有警告，但依赖已安装"
fi

echo "========================================"
echo "依赖安装完成！"
echo "========================================"
echo ""
echo "安装摘要:"
echo "- Python版本: $python_version"
echo "- 虚拟环境: $SCRIPT_DIR/venv"
echo "- 安装模式: $(if [ "$OFFLINE_MODE" = true ]; then echo "离线安装"; else echo "在线安装"; fi)"
echo "- 依赖包数量: $(pip list | wc -l)"
echo ""
echo "下一步操作:"
echo "1. 启动应用:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2. 或使用gunicorn启动:"
echo "   source venv/bin/activate"
echo "   gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "3. 配置supervisor (可选):"
echo "   参考 cross_env_manager_supervisor.conf 配置文件"
echo "   复制到 /main/app/supervisor/conf.d/"
echo "   运行 supervisorctl update"
echo ""
echo "离线部署说明:"
echo "1. 在有网络的环境准备离线包:"
echo "   python3 -m pip download -r requirements.txt -d vendor_packages"
echo "2. 将整个项目目录复制到无网络环境"
echo "3. 运行此脚本进行离线依赖安装"
echo "4. 手动配置supervisor或使用其他方式启动服务"
echo "========================================"