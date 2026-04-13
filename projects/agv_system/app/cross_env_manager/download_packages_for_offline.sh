#!/bin/bash
# 在有网环境下载所有依赖包
# 用于准备离线部署的包

set -e

echo "========================================"
echo "下载离线部署依赖包"
echo "========================================"
echo "目标Python版本: 3.9"
echo "目标平台: Linux"
echo "时间: $(date)"
echo "========================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "临时目录: $TEMP_DIR"

# 目标目录（vendor_packages3.9）
TARGET_DIR="vendor_packages3.9"
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
    echo "创建目标目录: $TARGET_DIR"
fi

# Python版本和平台信息
PYTHON_VERSION="3.9"
PLATFORM="linux"
ARCH="x86_64"

echo ""
echo "1. 下载requirements_py39.txt中的包..."
if [ -f "requirements_py39.txt" ]; then
    echo "   从requirements_py39.txt下载包..."
    
    # 下载所有包到临时目录
    echo "   下载到临时目录: $TEMP_DIR"
    pip download \
        -r requirements_py39.txt \
        --platform manylinux2014_x86_64 \
        --python-version 39 \
        --implementation cp \
        --only-binary=:all: \
        --dest "$TEMP_DIR" \
        -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    # 检查是否有纯Python包需要额外下载
    echo "   补充下载可能需要的纯Python包..."
    
    # 额外需要的包（Flask的依赖）
    EXTRA_PACKAGES="blinker importlib-metadata zipp typing-extensions"
    
    for pkg in $EXTRA_PACKAGES; do
        echo "   下载额外包: $pkg"
        pip download \
            "$pkg" \
            --platform manylinux2014_x86_64 \
            --python-version 39 \
            --implementation cp \
            --only-binary=:all: \
            --dest "$TEMP_DIR" \
            -i https://pypi.tuna.tsinghua.edu.cn/simple 2>/dev/null || \
        echo "   ⚠️  $pkg 下载失败，尝试纯Python版本..."
    done
else
    echo "   ❌ requirements_py39.txt不存在"
    exit 1
fi

echo ""
echo "2. 确保有Python 3.9兼容的markupsafe..."
# 检查是否已下载markupsafe
MARKUPSAFE_FILE=$(find "$TEMP_DIR" -name "*markupsafe*.whl" -type f | head -1)

if [ -n "$MARKUPSAFE_FILE" ]; then
    FILE_NAME=$(basename "$MARKUPSAFE_FILE")
    echo "   找到markupsafe: $FILE_NAME"
    
    # 检查是否为Python 3.9兼容（cp39或py3-none-any）
    if echo "$FILE_NAME" | grep -q "cp39" || echo "$FILE_NAME" | grep -q "py3-none-any"; then
        echo "   ✓ markupsafe兼容Python 3.9"
    else
        echo "   ⚠️  markupsafe可能不兼容Python 3.9"
        echo "   下载Python 3.9兼容的markupsafe..."
        
        # 尝试下载Python 3.9兼容的markupsafe
        pip download \
            "markupsafe<3.0" \
            --platform manylinux2014_x86_64 \
            --python-version 39 \
            --implementation cp \
            --only-binary=:all: \
            --dest "$TEMP_DIR" \
            -i https://pypi.tuna.tsinghua.edu.cn/simple 2>/dev/null || \
        echo "   ⚠️  无法下载兼容版本，尝试其他方案..."
    fi
else
    echo "   ⚠️  未找到markupsafe，下载兼容版本..."
    pip download \
        "markupsafe<3.0" \
        --platform manylinux2014_x86_64 \
        --python-version 39 \
        --implementation cp \
        --only-binary=:all: \
        --dest "$TEMP_DIR" \
        -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

echo ""
echo "3. 确保有Python 3.9兼容的importlib-metadata..."
# importlib-metadata在Python 3.9中可能需要特定版本
IMPORTLIB_FILE=$(find "$TEMP_DIR" -name "*importlib_metadata*.whl" -type f | head -1)

if [ -n "$IMPORTLIB_FILE" ]; then
    FILE_NAME=$(basename "$IMPORTLIB_FILE")
    echo "   找到importlib-metadata: $FILE_NAME"
    
    # 检查是否要求Python >= 3.10
    if echo "$FILE_NAME" | grep -q "importlib_metadata" && python3 -c "
import pkg_resources
spec = pkg_resources.Requirement.parse('importlib-metadata')
# 检查是否有Python版本要求
" 2>/dev/null; then
        echo "   检查版本兼容性..."
    fi
else
    echo "   下载importlib-metadata..."
    pip download \
        "importlib-metadata<5.0" \
        --platform manylinux2014_x86_64 \
        --python-version 39 \
        --implementation cp \
        --only-binary=:all: \
        --dest "$TEMP_DIR" \
        -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

echo ""
echo "4. 复制文件到vendor_packages3.9目录..."
# 清空目标目录
rm -f "$TARGET_DIR"/*.whl "$TARGET_DIR"/*.tar.gz

# 复制所有wheel文件
WHL_COUNT=0
for whl_file in "$TEMP_DIR"/*.whl; do
    if [ -f "$whl_file" ]; then
        cp "$whl_file" "$TARGET_DIR/"
        WHL_COUNT=$((WHL_COUNT + 1))
    fi
done

echo "   复制了 $WHL_COUNT 个wheel文件"

# 复制所有源码包（如果需要）
TAR_COUNT=0
for tar_file in "$TEMP_DIR"/*.tar.gz "$TEMP_DIR"/*.zip; do
    if [ -f "$tar_file" ]; then
        cp "$tar_file" "$TARGET_DIR/"
        TAR_COUNT=$((TAR_COUNT + 1))
    fi
done

if [ $TAR_COUNT -gt 0 ]; then
    echo "   复制了 $TAR_COUNT 个源码包"
fi

echo ""
echo "5. 验证下载的包..."
echo "   目标目录内容 ($TARGET_DIR):"
ls -la "$TARGET_DIR/" | head -20

echo ""
echo "   关键包检查:"
REQUIRED_PACKAGES="flask pymysql werkzeug jinja2 click itsdangerous markupsafe"
for pkg in $REQUIRED_PACKAGES; do
    if find "$TARGET_DIR" -type f -iname "*${pkg}*.whl" | grep -q .; then
        echo "   ✓ $pkg"
    else
        echo "   ❌ 缺少: $pkg"
    fi
done

echo ""
echo "6. 创建包清单..."
cat > "$TARGET_DIR/PACKAGES.md" << EOF
# 离线依赖包清单

## 基本信息
- 生成时间: $(date)
- Python版本: $PYTHON_VERSION
- 目标平台: $PLATFORM-$ARCH
- 包数量: $WHL_COUNT wheel文件 + $TAR_COUNT 源码包

## 包含的包
EOF

# 列出所有包
for whl_file in "$TARGET_DIR"/*.whl; do
    if [ -f "$whl_file" ]; then
        echo "- $(basename "$whl_file")" >> "$TARGET_DIR/PACKAGES.md"
    fi
done

# 清理临时目录
rm -rf "$TEMP_DIR"
echo "   清理临时目录"

echo ""
echo "========================================"
echo "下载完成！"
echo "========================================"
echo ""
echo "操作总结:"
echo "- 下载包数量: $WHL_COUNT wheel文件"
echo "- 目标目录: $TARGET_DIR/"
echo "- 包清单: $TARGET_DIR/PACKAGES.md"
echo ""
echo "下一步:"
echo "1. 将 $TARGET_DIR/ 目录复制到离线环境"
echo "2. 在离线环境运行 deploy_iraypleos.sh"
echo "3. 部署脚本将使用这些包进行离线安装"
echo ""
echo "注意:"
echo "- 确保离线环境Python版本为 3.9.x"
echo "- 确保离线环境为Linux系统"
echo "========================================"