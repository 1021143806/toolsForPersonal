#!/bin/bash
# 验证Python 3.9依赖包兼容性
# 检查vendor_packages3.9目录中的包是否兼容Python 3.9

set -e

echo "========================================"
echo "Python 3.9依赖包兼容性验证"
echo "========================================"
echo "时间: $(date)"
echo "Python版本: $(python3 --version 2>&1)"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "vendor_packages3.9" ]; then
    echo "❌ vendor_packages3.9目录不存在"
    exit 1
fi

echo "1. 检查基本依赖包..."
REQUIRED_PACKAGES=(
    "click"         # Flask命令行支持
    "itsdangerous"  # Flask安全组件  
    "blinker"       # Flask信号系统
    "tomli"         # TOML解析
    "python_dotenv" # 环境变量管理
    "zipp"          # zip文件支持
    "Werkzeug"      # WSGI工具库
    "Jinja2"        # 模板引擎
    "PyMySQL"       # MySQL连接
    "Markdown"      # Markdown解析
    "Flask"         # Web框架
)

ALL_AVAILABLE=1
echo "   检查所有必需包..."
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if find vendor_packages3.9 -type f -iname "*${pkg}*.whl" | grep -q .; then
        wheel_file=$(find vendor_packages3.9 -type f -iname "*${pkg}*.whl" | head -1)
        wheel_name=$(basename "$wheel_file")
        echo "   ✓ $pkg ($wheel_name)"
    else
        echo "   ❌ 缺少: $pkg"
        ALL_AVAILABLE=0
    fi
done

if [ $ALL_AVAILABLE -eq 0 ]; then
    echo "   ⚠️  缺少一些必需包，可能需要重新下载"
fi

echo ""
echo "2. 检查Python版本兼容性..."
echo "   标记可能不兼容的包:"

# 检查markupsafe
MARKUPSAFE_WHEEL=$(find vendor_packages3.9 -type f -iname "*markupsafe*.whl" | head -1)
if [ -n "$MARKUPSAFE_WHEEL" ]; then
    wheel_name=$(basename "$MARKUPSAFE_WHEEL")
    if echo "$wheel_name" | grep -q "cp310"; then
        echo "   ⚠️  markupsafe: $wheel_name (Python 3.10编译，不适合Python 3.9)"
        echo "       解决方案: 跳过安装，Jinja2将使用纯Python实现"
    elif echo "$wheel_name" | grep -q "cp39" || echo "$wheel_name" | grep -q "py3-none-any"; then
        echo "   ✓ markupsafe: $wheel_name (Python 3.9兼容)"
    else
        echo "   ❓ markupsafe: $wheel_name (版本未知)"
    fi
fi

# 检查importlib_metadata（不应该存在）
IMPORTLIB_WHEEL=$(find vendor_packages3.9 -type f -iname "*importlib_metadata*.whl" | head -1)
if [ -n "$IMPORTLIB_WHEEL" ]; then
    wheel_name=$(basename "$IMPORTLIB_WHEEL")
    echo "   ⚠️  importlib_metadata: $wheel_name (Python 3.9内置此模块，不需要额外包)"
    echo "       建议: 可以删除此包，Python 3.9使用内置importlib.metadata"
fi

echo ""
echo "3. 测试Python 3.9兼容性..."
echo "   创建临时虚拟环境测试..."

TEMP_VENV=".temp_venv_verify"
rm -rf "$TEMP_VENV" 2>/dev/null || true
python3 -m venv "$TEMP_VENV"

if [ ! -f "$TEMP_VENV/bin/activate" ]; then
    echo "   ❌ 临时虚拟环境创建失败"
    exit 1
fi

source "$TEMP_VENV/bin/activate"

echo "   虚拟环境Python: $(python --version 2>&1)"

echo ""
echo "4. 测试包安装..."
echo "   尝试安装几个关键包:"

test_package_install() {
    local pkg="$1"
    local display="$2"
    
    wheel_file=$(find vendor_packages3.9 -type f -iname "*${pkg}*.whl" | head -1)
    if [ -f "$wheel_file" ]; then
        echo "   测试 $display..."
        if pip install --no-index --no-deps "$wheel_file" 2>/dev/null; then
            echo "   ✓ $display 安装成功"
            return 0
        else
            echo "   ❌ $display 安装失败"
            return 1
        fi
    else
        echo "   ❌ $display: wheel文件不存在"
        return 2
    fi
}

# 测试几个关键包
test_package_install "click" "click"
test_package_install "PyMySQL" "PyMySQL" 
test_package_install "Flask" "Flask"

echo ""
echo "5. 清理临时环境..."
deactivate
rm -rf "$TEMP_VENV"
echo "   ✓ 临时环境清理完成"

echo ""
echo "6. 总结报告..."
echo "   Python 3.9兼容性验证完成"
echo ""
echo "   建议操作:"
echo "   1. 如有markupsafe-cp310包，部署时会自动跳过"
echo "   2. 如有importlib_metadata包，建议删除（Python 3.9内置）"
echo "   3. 如需重新下载Python 3.9兼容包，运行:"
echo "      ./download_packages_for_offline.sh"
echo ""
echo "   当前包状态:"
WHL_COUNT=$(ls -1 vendor_packages3.9/*.whl 2>/dev/null | wc -l)
echo "   - Wheel文件数量: $WHL_COUNT"
echo "   - 必需包数量: ${#REQUIRED_PACKAGES[@]}"
echo "   - 所有必需包可用: $(if [ $ALL_AVAILABLE -eq 1 ]; then echo "是"; else echo "否"; fi)"
echo ""
echo "========================================"
echo "Python 3.9部署验证完成"
echo "========================================"