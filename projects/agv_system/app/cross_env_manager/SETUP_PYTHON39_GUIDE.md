# Python 3.9环境设置和离线包准备指南

## 概述
本指南帮助您设置Python 3.9环境并准备跨环境任务模板管理系统所需的离线依赖包。

## 步骤1：检查当前环境

### 1.1 检查已安装的Python版本
```bash
# 检查所有可用的Python版本
ls /usr/bin/python* 2>/dev/null
ls /usr/local/bin/python* 2>/dev/null

# 检查特定版本
python3 --version
python3.9 --version 2>/dev/null || echo "Python 3.9未安装"
```

### 1.2 检查conda（如果使用）
```bash
# 检查conda是否安装
which conda || echo "conda未安装"

# 或检查miniconda
ls /home/a1/miniconda3/ 2>/dev/null && echo "miniconda已安装"
```

## 步骤2：安装Python 3.9（如果需要）

### 方案A：使用apt安装（Ubuntu/Debian）
```bash
# 更新包列表
sudo apt-get update

# 安装Python 3.9
sudo apt-get install python3.9 python3.9-venv python3.9-dev

# 验证安装
python3.9 --version
```

### 方案B：使用源码编译安装
```bash
# 安装编译依赖
sudo apt-get install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev

# 下载Python 3.9源码
wget https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tgz
tar -xf Python-3.9.9.tgz
cd Python-3.9.9

# 编译安装
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall

# 验证安装
python3.9 --version
```

### 方案C：使用conda安装（如果conda可用）
```bash
# 激活conda
source /home/a1/miniconda3/etc/profile.d/conda.sh

# 创建Python 3.9环境
conda create -n cross_env_manager_py39 python=3.9 -y

# 激活环境
conda activate cross_env_manager_py39

# 验证
python --version  # 应该显示3.9.x
```

## 步骤3：准备Python 3.9兼容的离线包

### 3.1 使用提供的脚本（推荐）
```bash
# 确保在项目目录
cd /home/a1/app/mntc/git/toolsForPersonal/projects/agv_system/app/cross_env_manager

# 给脚本执行权限
chmod +x download_py39_packages.sh fix_mysql_py39.sh

# 运行下载脚本（需要有Python 3.9）
./download_py39_packages.sh

# 如果下载失败，运行修复脚本
./fix_mysql_py39.sh
```

### 3.2 手动下载（如果脚本不可用）
```bash
# 激活Python 3.9环境
# 如果是系统安装的Python 3.9
python3.9 -m venv py39_temp
source py39_temp/bin/activate

# 或如果是conda环境
conda activate cross_env_manager_py39

# 下载所有依赖包
mkdir -p vendor_packages
pip download -r requirements.txt -d vendor_packages

# 验证下载的包
ls -la vendor_packages/ | grep mysql
# 应该看到类似: mysql_connector_python-8.1.0-cp39-cp39-manylinux_2_17_x86_64.whl
```

### 3.3 替代方案：使用pymysql
如果无法获得mysql-connector-python的Python 3.9版本：
```bash
# 修改requirements.txt
cp requirements.txt requirements.txt.backup
sed -i 's/mysql-connector-python==8.1.0/pymysql==1.1.0/' requirements.txt

# 使用Python 3.9下载包
python3.9 -m pip download -r requirements.txt -d vendor_packages

# 恢复原文件（可选）
mv requirements.txt.backup requirements.txt
```

## 步骤4：验证离线包

### 4.1 运行兼容性测试
```bash
# 运行测试脚本
chmod +x test_py39_compatibility.sh
./test_py39_compatibility.sh
```

### 4.2 检查关键包
确保以下包存在且针对Python 3.9编译：
- `mysql_connector_python-8.1.0-cp39-cp39-*.whl` 或 `pymysql-*.whl`
- `flask-2.3.3-py3-none-any.whl`
- 其他依赖包

### 4.3 测试安装
```bash
# 创建测试虚拟环境
python3.9 -m venv test_venv
source test_venv/bin/activate

# 测试离线安装
pip install --no-index --find-links=vendor_packages -r requirements.txt

# 验证安装
python -c "import flask; import mysql.connector; print('所有依赖安装成功')"
```

## 步骤5：部署到目标环境

### 5.1 准备部署包
```bash
# 创建完整的部署包
DEPLOY_PACKAGE="cross_env_manager_py39_$(date +%Y%m%d).tar.gz"
tar -czf "$DEPLOY_PACKAGE" \
  app.py \
  requirements.txt \
  vendor_packages/ \
  templates/ \
  config/ \
  deploy_offline.sh \
  verify_offline.py \
  *.md

echo "部署包已创建: $DEPLOY_PACKAGE"
```

### 5.2 在目标环境部署
```bash
# 解压部署包
tar -xzf cross_env_manager_py39_*.tar.gz
cd cross_env_manager

# 运行部署脚本
./deploy_offline.sh

# 或手动部署
python3.9 -m venv venv
source venv/bin/activate
pip install --no-index --find-links=vendor_packages -r requirements.txt
```

## 故障排除

### 问题1：找不到Python 3.9
**解决方案**：
- 按照步骤2安装Python 3.9
- 或使用Docker容器：`docker run -it python:3.9-slim bash`

### 问题2：mysql-connector-python下载失败
**解决方案**：
1. 使用pymysql替代（见3.3）
2. 下载通用版本：`pip download mysql-connector-python==8.1.0 --platform manylinux2014_x86_64 --python-version 39 -d vendor_packages`
3. 从其他来源获取预编译包

### 问题3：包版本不兼容
**解决方案**：
```bash
# 查看当前Python版本
python --version

# 查看包要求的Python版本
for pkg in vendor_packages/*.whl; do
  echo "$(basename "$pkg")"
done | grep -E "cp[0-9]+"
```

### 问题4：部署脚本失败
**解决方案**：
1. 查看详细错误：`./deploy_offline.sh 2>&1 | tee deploy.log`
2. 检查Python版本：确保目标环境也是Python 3.9.x
3. 检查网络连接：如果需要在线安装

## 快速参考

### 常用命令
```bash
# 检查环境
python3.9 --version

# 准备离线包
python3.9 -m pip download -r requirements.txt -d vendor_packages

# 验证包
./test_py39_compatibility.sh

# 部署
./deploy_offline.sh
```

### 文件说明
- `download_py39_packages.sh` - 下载Python 3.9兼容包
- `fix_mysql_py39.sh` - 修复MySQL包兼容性问题
- `test_py39_compatibility.sh` - 测试Python 3.9兼容性
- `PYTHON39_MYSQL_FIX.md` - MySQL兼容性问题解决方案
- `deploy_offline.sh` - 离线部署脚本（已更新支持Python 3.9）

### 联系支持
如果遇到无法解决的问题：
1. 检查所有错误日志
2. 参考相关文档
3. 联系系统管理员

---
**最后更新**: 2026-04-09  
**适用版本**: Python 3.9.9  
**项目**: 跨环境任务模板管理系统