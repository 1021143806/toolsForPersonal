#!/bin/bash
# 下载Python 3.9兼容的依赖包（包括markupsafe）
# 专门解决Python 3.9兼容性问题

set -e

echo "========================================"
echo "下载Python 3.9兼容依赖包"
echo "========================================"
echo "目标Python版本: 3.9"
echo "目标平台: manylinux2014_x86_64"
echo "时间: $(date)"
echo "========================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 创建目标目录
TARGET_DIR="vendor_packages3.9_py39_fixed"
rm -rf "$TARGET_DIR" 2>/dev/null || true
mkdir -p "$TARGET_DIR"

echo ""
echo "1. 创建Python 3.9专用的requirements文件..."
cat > "$TARGET_DIR/requirements_py39_fixed.txt" << EOF
# Python 3.9专用依赖包
# 所有包必须兼容Python 3.9

# Flask核心依赖
Flask==2.3.3
PyMySQL==1.1.0
python-dotenv==1.0.0
Werkzeug==2.3.7
Jinja2==3.1.2
click==8.1.6
itsdangerous==2.1.2
Markdown==3.5.1
tomli==2.0.1

# 额外依赖
blinker==1.9.0
zipp==3.23.0

# markupsafe - 必须使用Python 3.9兼容版本 (< 3.0)
markupsafe==2.1.3  # Python 3.9兼容版本
EOF

echo "   ✓ 创建requirements文件"

echo ""
echo "2. 下载Python 3.9兼容包..."
echo "   使用pip download下载所有包..."

# 创建一个批处理下载命令
echo "   下载批处理..."
pip download \
    -r "$TARGET_DIR/requirements_py39_fixed.txt" \
    --platform manylinux2014_x86_64 \
    --python-version 39 \
    --implementation cp \
    --only-binary=:all: \
    --dest "$TARGET_DIR" \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "3. 特别处理markupsafe..."
# 检查是否下载到了正确的markupsafe版本
MARKUPSAFE_FILE=$(find "$TARGET_DIR" -name "*markupsafe*.whl" -type f | head -1)
if [ -n "$MARKUPSAFE_FILE" ]; then
    FILE_NAME=$(basename "$MARKUPSAFE_FILE")
    echo "   找到markupsafe: $FILE_NAME"
    
    if echo "$FILE_NAME" | grep -q "cp39" || echo "$FILE_NAME" | grep -q "py3-none-any" || echo "$FILE_NAME" | grep -q "manylinux2014"; then
        echo "   ✓ markupsafe看起来兼容Python 3.9"
    else
        echo "   ⚠️  markupsafe可能不兼容，尝试下载源码包..."
        # 尝试下载源码包作为备份
        pip download \
            "markupsafe==2.1.3" \
            --no-binary :all: \
            --dest "$TARGET_DIR" \
            -i https://pypi.tuna.tsinghua.edu.cn/simple 2>/dev/null || \
        echo "   ⚠️  源码包下载失败"
    fi
else
    echo "   ⚠️  未找到markupsafe wheel，尝试源码包..."
    pip download \
        "markupsafe==2.1.3" \
        --no-binary :all: \
        --dest "$TARGET_DIR" \
        -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

echo ""
echo "4. 验证下载的包..."
echo "   检查关键包:"
REQUIRED_PACKAGES=("flask" "pymysql" "werkzeug" "jinja2" "click" "itsdangerous" "markupsafe")
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if find "$TARGET_DIR" -type f -iname "*${pkg}*.whl" | grep -q .; then
        echo "   ✓ $pkg (wheel文件)"
    elif find "$TARGET_DIR" -type f \( -iname "*${pkg}*.tar.gz" -o -iname "*${pkg}*.zip" \) | grep -q .; then
        echo "   ✓ $pkg (源码包)"
    else
        echo "   ❌ 缺少: $pkg"
    fi
done

echo ""
echo "5. 创建说明文件..."
cat > "$TARGET_DIR/README.md" << EOF
# Python 3.9兼容依赖包

## 生成信息
- 生成时间: $(date)
- Python版本: 3.9
- 平台: manylinux2014_x86_64

## 使用说明
1. 将此目录（$TARGET_DIR）复制到离线环境
2. 替换原有的vendor_packages3.9目录：
   \`\`\`bash
   rm -rf vendor_packages3.9
   mv $TARGET_DIR vendor_packages3.9
   \`\`\`
3. 运行部署脚本：
   \`\`\`bash
   ./deploy_iraypleos.sh
   \`\`\`

## 包清单
$(for file in "$TARGET_DIR"/*; do
  if [ -f "$file" ]; then
    echo "- $(basename "$file")"
  fi
done)

## 特别说明
- markupsafe已确保为Python 3.9兼容版本（2.1.3）
- 所有包都支持manylinux2014_x86_64平台
- 无需Python >= 3.10的包
EOF

echo "   ✓ 创建说明文件"

echo ""
echo "6. 包数量统计..."
WHL_COUNT=$(ls -1 "$TARGET_DIR"/*.whl 2>/dev/null | wc -l)
TAR_COUNT=$(ls -1 "$TARGET_DIR"/*.tar.gz "$TARGET_DIR"/*.zip 2>/dev/null | wc -l)

echo "   Wheel文件: $WHL_COUNT"
echo "   源码包: $TAR_COUNT"
echo "   总计: $((WHL_COUNT + TAR_COUNT))"

echo ""
echo "========================================"
echo "Python 3.9兼容包下载完成！"
echo "========================================"
echo ""
echo "操作总结:"
echo "- 目标目录: $TARGET_DIR/"
echo "- 包数量: $WHL_COUNT wheel文件 + $TAR_COUNT 源码包"
echo "- markupsafe兼容性: 已确保Python 3.9兼容"
echo ""
echo "注意事项:"
echo "1. 如果markupsafe是源码包（.tar.gz），部署时需要编译"
echo "2. 确保离线服务器有编译工具（gcc, python3-dev等）"
echo "3. 编译可能需要一些时间"
echo ""
echo "部署准备:"
echo "1. 将 $TARGET_DIR/ 复制到离线服务器"
echo "2. 替换原有的 vendor_packages3.9/"
echo "3. 运行部署脚本"
echo "========================================"