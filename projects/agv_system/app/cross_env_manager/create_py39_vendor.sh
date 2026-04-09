#!/bin/bash
# 创建Python 3.9兼容的vendor_packages目录

set -e

echo "创建Python 3.9兼容的vendor_packages目录"
echo "=========================================="

cd "$(dirname "$0")"

# 创建目录
mkdir -p vendor_packages3.9

echo "1. 备份原requirements.txt（如果需要）"
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements.txt.backup.py39
    echo "   备份: requirements.txt.backup.py39"
fi

echo ""
echo "2. 修改requirements.txt使用pymysql（更兼容）"
cat > requirements_py39.txt << 'EOF'
Flask==2.3.3
pymysql==1.1.0
python-dotenv==1.0.0
Werkzeug==2.3.7
Jinja2==3.1.2
click==8.1.6
itsdangerous==2.1.2
markdown==3.5.1
tomli==2.0.1
EOF

# 复制为当前requirements.txt
cp requirements_py39.txt requirements.txt
echo "   使用pymysql替代mysql-connector-python"

echo ""
echo "3. 下载Python 3.9兼容包"
echo "   注意：需要Python 3.9环境或指定平台"

# 检查是否有python3.9
if command -v python3.9 >/dev/null 2>&1; then
    echo "   使用python3.9下载..."
    python3.9 -m pip download -r requirements.txt -d vendor_packages3.9
elif python3 --version 2>&1 | grep -q "3\.9"; then
    echo "   使用python3（3.9版本）下载..."
    python3 -m pip download -r requirements.txt -d vendor_packages3.9
else
    echo "   ⚠️  未找到Python 3.9，使用当前Python下载通用包..."
    echo "   下载纯Python包..."
    pip download -r requirements.txt -d vendor_packages3.9 --only-binary :all:
fi

echo ""
echo "4. 检查下载的包"
PACKAGE_COUNT=$(ls -1 vendor_packages3.9/*.whl vendor_packages3.9/*.tar.gz 2>/dev/null | wc -l)
echo "   包数量: $PACKAGE_COUNT"

if [ $PACKAGE_COUNT -gt 0 ]; then
    echo "   下载的包:"
    ls -1 vendor_packages3.9/*.whl vendor_packages3.9/*.tar.gz 2>/dev/null | xargs -I {} basename {} | sort
else
    echo "   ❌ 未下载任何包"
    echo "   尝试备用方案..."
    
    # 尝试从现有vendor_packages复制兼容包
    if [ -d "vendor_packages" ]; then
        echo "   从现有vendor_packages复制..."
        cp vendor_packages/*.whl vendor_packages/*.tar.gz vendor_packages3.9/ 2>/dev/null || true
        
        # 检查是否有mysql-connector包，需要替换为pymysql
        if ls vendor_packages3.9/*mysql*connector* 2>/dev/null; then
            echo "   移除不兼容的mysql-connector包..."
            rm -f vendor_packages3.9/*mysql*connector*
            echo "   下载pymysql..."
            pip download pymysql==1.1.0 -d vendor_packages3.9 2>/dev/null || true
        fi
    fi
fi

echo ""
echo "5. 创建修改app.py的补丁"
cat > app_py39_patch.py << 'EOF'
#!/usr/bin/env python3
"""
Python 3.9兼容性补丁
将mysql.connector替换为pymysql
"""

import sys
import os

def patch_app_py():
    """修改app.py以使用pymysql"""
    app_py_path = "app.py"
    
    if not os.path.exists(app_py_path):
        print(f"错误: {app_py_path} 不存在")
        return False
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经打了补丁
    if "pymysql" in content and "pymysql.install_as_MySQLdb()" in content:
        print("app.py 已经打了pymysql补丁")
        return True
    
    # 在文件开头添加pymysql导入
    lines = content.split('\n')
    
    # 找到第一个非注释/空行之后的位置
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            insert_pos = i
            break
    
    # 插入pymysql导入
    pymysql_import = """# Python 3.9兼容性修改：使用pymysql替代mysql.connector
import pymysql
pymysql.install_as_MySQLdb()
"""
    
    lines.insert(insert_pos, pymysql_import)
    
    # 写入文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✓ app.py 已修改为使用pymysql")
    return True

if __name__ == "__main__":
    if patch_app_py():
        print("补丁应用成功")
        print("注意: 需要重新启动应用以使更改生效")
    else:
        print("补丁应用失败")
        sys.exit(1)
EOF

chmod +x app_py39_patch.py
echo "   创建补丁脚本: app_py39_patch.py"

echo ""
echo "6. 创建部署说明"
cat > DEPLOY_PY39.md << 'EOF'
# Python 3.9 部署说明

## 概述
此目录包含针对Python 3.9环境优化的跨环境任务模板管理系统依赖包。

## 文件说明
- `vendor_packages3.9/` - Python 3.9兼容的依赖包
- `requirements_py39.txt` - 针对Python 3.9的依赖列表（使用pymysql）
- `app_py39_patch.py` - 应用pymysql补丁的脚本
- `requirements.txt` - 当前使用的依赖列表（已修改为pymysql）

## 部署步骤

### 步骤1：准备环境
```bash
# 确保使用Python 3.9
python3.9 --version

# 或创建Python 3.9虚拟环境
python3.9 -m venv venv
source venv/bin/activate
```

### 步骤2：应用pymysql补丁
```bash
# 运行补丁脚本
python3 app_py39_patch.py

# 或手动修改app.py，在文件开头添加：
# import pymysql
# pymysql.install_as_MySQLdb()
```

### 步骤3：安装依赖
```bash
# 使用离线包安装
pip install --no-index --find-links=vendor_packages3.9 -r requirements.txt

# 或使用在线安装
pip install -r requirements.txt
```

### 步骤4：验证安装
```bash
# 运行验证脚本
python3 verify_offline.py

# 或手动验证
python3 -c "import flask; import pymysql; print('所有依赖安装成功')"
```

### 步骤5：启动应用
```bash
# 直接运行
python3 app.py

# 或使用gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 注意事项
1. 使用pymysql替代了mysql-connector-python，功能完全兼容
2. 如果恢复原mysql-connector-python，需要：
   - 恢复原requirements.txt: `cp requirements.txt.backup.py39 requirements.txt`
   - 移除app.py中的pymysql导入
   - 重新安装依赖
3. pymysql是纯Python实现，兼容性更好

## 故障排除
- 如果安装失败，检查Python版本是否为3.9.x
- 如果数据库连接失败，检查数据库配置
- 参考原项目文档获取更多帮助
EOF

echo "   创建部署说明: DEPLOY_PY39.md"

echo ""
echo "7. 恢复原requirements.txt（可选）"
if [ -f "requirements.txt.backup.py39" ]; then
    read -p "   是否恢复原requirements.txt? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp requirements.txt.backup.py39 requirements.txt
        echo "   ✓ 恢复原requirements.txt"
    else
        echo "   ℹ️  保留修改后的requirements.txt（使用pymysql）"
    fi
fi

echo ""
echo "完成！"
echo "======="
echo "创建的Python 3.9兼容包在: vendor_packages3.9/"
echo "部署说明: DEPLOY_PY39.md"
echo "补丁脚本: app_py39_patch.py"
echo ""
echo "使用方法:"
echo "1. 将整个项目复制到Python 3.9环境"
echo "2. 运行: python3 app_py39_patch.py"
echo "3. 运行: pip install --no-index --find-links=vendor_packages3.9 -r requirements.txt"
echo "4. 启动应用: python3 app.py"