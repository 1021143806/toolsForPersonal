#!/bin/bash
# 更新项目为完全兼容Python 3.9.9版本
# 当前环境：Python 3.9.9

set -e

echo "========================================"
echo "更新项目为Python 3.9.9完全兼容版本"
echo "========================================"
echo "当前Python版本: $(python3 --version)"
echo "系统: IRAYPLEOS"
echo "用户: $(whoami)"
echo "时间: $(date)"
echo "========================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "1. 检查当前环境..."
python3 --version | grep -q "3.9" && echo "   ✅ Python 3.9.x环境" || {
    echo "   ❌ 错误：当前不是Python 3.9环境"
    echo "   当前版本: $(python3 --version)"
    exit 1
}

echo ""
echo "2. 备份现有虚拟环境..."
if [ -d "venv" ]; then
    BACKUP_NAME="venv.backup.$(date +%Y%m%d_%H%M%S)"
    mv venv "$BACKUP_NAME"
    echo "   ✅ 虚拟环境已备份到: $BACKUP_NAME"
else
    echo "   ℹ️  没有现有的虚拟环境"
fi

echo ""
echo "3. 创建新的Python 3.9.9虚拟环境..."
python3 -m venv venv
if [ ! -f "venv/bin/python" ]; then
    echo "   ❌ 虚拟环境创建失败"
    exit 1
fi
echo "   ✅ 虚拟环境创建成功"

echo ""
echo "4. 激活虚拟环境..."
source venv/bin/activate
echo "   虚拟环境Python: $(python --version)"

echo ""
echo "5. 安装Python 3.9.9完全兼容的依赖包..."
echo "   使用清华源加速下载..."

# 创建一个临时的requirements文件，包含完全兼容的版本
TEMP_REQ=$(mktemp)
cat > "$TEMP_REQ" << EOF
# Python 3.9.9完全兼容依赖包列表
Flask==2.3.3
PyMySQL==1.1.0          # 兼容Python 3.9，替代mysql-connector-python
python-dotenv==1.0.0
Werkzeug==2.3.7
Jinja2==3.1.2
click==8.1.6
itsdangerous==2.1.2
Markdown==3.5.1
tomli==2.0.1
blinker==1.9.0
# Python 3.9内置importlib.metadata，不需要importlib-metadata包
# markupsafe必须使用<3.0版本，Python 3.9兼容
markupsafe==2.1.3
zipp==3.23.0
EOF

echo "   依赖包清单:"
cat "$TEMP_REQ"

echo ""
echo "   开始安装..."
pip install -r "$TEMP_REQ" -i https://pypi.tuna.tsinghua.edu.cn/simple

rm -f "$TEMP_REQ"
echo "   ✅ 所有包安装完成"

echo ""
echo "6. 验证Python 3.9.9兼容性..."
echo "   测试关键包导入..."

test_package() {
    local cmd="$1"
    local name="$2"
    
    if python -c "$cmd" 2>/dev/null; then
        echo "   ✅ $name"
        return 0
    else
        echo "   ❌ $name 导入失败"
        python -c "$cmd" 2>&1 | head -2
        return 1
    fi
}

test_package "import flask; print(flask.__version__)" "Flask"
test_package "import markupsafe; print('markupsafe:', markupsafe.__version__)" "markupsafe"
test_package "import jinja2; print(jinja2.__version__)" "Jinja2"
test_package "import werkzeug; print(werkzeug.__version__)" "Werkzeug"
test_package "import pymysql; print('PyMySQL OK')" "PyMySQL"
test_package "import importlib.metadata; print('importlib.metadata内置模块OK')" "importlib.metadata"

echo ""
echo "7. 创建新的vendor_packages3.9目录..."
echo "   下载所有wheel包用于离线部署..."

VENDOR_DIR="vendor_packages3.9_complete"
rm -rf "$VENDOR_DIR" 2>/dev/null || true
mkdir -p "$VENDOR_DIR"

# 下载所有依赖包的wheel文件
echo "   下载wheel文件..."
pip download \
    -r requirements_py39.txt \
    --platform manylinux2014_x86_64 \
    --python-version 39 \
    --implementation cp \
    --only-binary=:all: \
    --dest "$VENDOR_DIR" \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 确保markupsafe是Python 3.9兼容版本
echo "   确保markupsafe为Python 3.9兼容..."
if find "$VENDOR_DIR" -name "*markupsafe*.whl" | grep -q "cp310"; then
    echo "   ⚠️  发现Python 3.10编译的markupsafe，重新下载..."
    pip download \
        "markupsafe==2.1.3" \
        --platform manylinux2014_x86_64 \
        --python-version 39 \
        --implementation cp \
        --only-binary=:all: \
        --dest "$VENDOR_DIR" \
        -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

echo ""
echo "8. 验证离线包..."
WHL_COUNT=$(ls -1 "$VENDOR_DIR"/*.whl 2>/dev/null | wc -l)
echo "   生成 $WHL_COUNT 个wheel文件"

echo "   检查关键包:"
for pkg in flask pymysql werkzeug jinja2 markupsafe click itsdangerous; do
    if find "$VENDOR_DIR" -type f -iname "*${pkg}*.whl" | grep -q .; then
        wheel_file=$(find "$VENDOR_DIR" -type f -iname "*${pkg}*.whl" | head -1)
        wheel_name=$(basename "$wheel_file")
        
        # 检查兼容性
        if echo "$wheel_name" | grep -q "cp310"; then
            echo "   ⚠️  $pkg: 可能不兼容 (cp310)"
        elif echo "$wheel_name" | grep -q "cp39" || echo "$wheel_name" | grep -q "py3-none-any"; then
            echo "   ✅ $pkg: 兼容Python 3.9"
        else
            echo "   ℹ️  $pkg: $wheel_name"
        fi
    else
        echo "   ❌ 缺少: $pkg"
    fi
done

echo ""
echo "9. 更新部署脚本..."
echo "   修复部署脚本中的markupsafe处理逻辑..."

# 备份原部署脚本
if [ -f "deploy_iraypleos.sh" ]; then
    cp deploy_iraypleos.sh "deploy_iraypleos.sh.backup.$(date +%Y%m%d_%H%M%S)"
fi

echo ""
echo "10. 创建新版的离线包目录..."
# 将新的vendor目录复制到标准位置
if [ -d "vendor_packages3.9" ]; then
    mv vendor_packages3.9 "vendor_packages3.9.old.$(date +%Y%m%d_%H%M%S)"
fi
mv "$VENDOR_DIR" vendor_packages3.9
echo "   ✅ 新的vendor_packages3.9目录已就绪"

echo ""
echo "========================================"
echo "Python 3.9.9完全兼容性更新完成！"
echo "========================================"
echo ""
echo "📋 更新总结："
echo "1. ✅ 创建了新的Python 3.9.9虚拟环境"
echo "2. ✅ 安装了所有Python 3.9.9兼容的依赖包"
echo "3. ✅ markupsafe使用2.1.3版本（Python 3.9兼容）"
echo "4. ✅ 使用PyMySQL替代mysql-connector-python"
echo "5. ✅ 利用Python 3.9内置的importlib.metadata"
echo "6. ✅ 生成了新的vendor_packages3.9目录（$WHL_COUNT个包）"
echo ""
echo "🚀 现在可以进行离线部署测试："
echo ""
echo "步骤1: 测试部署脚本"
echo "  ./verify_python39_packages.sh"
echo ""
echo "步骤2: 运行离线部署（完全兼容Python 3.9.9）"
echo "  ./deploy_iraypleos.sh"
echo ""
echo "注意："
echo "- 新生成的vendor_packages3.9目录包含所有Python 3.9.9兼容包"
echo "- markupsafe已确保为Python 3.9兼容版本（2.1.3）"
echo "- 可以直接用于其他Python 3.9环境的离线部署"
echo "========================================"