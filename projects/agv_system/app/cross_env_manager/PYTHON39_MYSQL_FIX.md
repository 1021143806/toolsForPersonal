# Python 3.9.9 环境下 mysql-connector-python 安装解决方案

## 问题描述
在Python 3.9.9环境下使用离线包安装时，出现以下错误：
```
ERROR: Could not find a version that satisfies the requirement mysql-connector-python==8.1.0
ERROR: No matching distribution found for mysql-connector-python==8.1.0
```

## 原因分析
当前 `vendor_packages/` 目录中的MySQL连接器包是针对Python 3.10编译的：
- `mysql_connector_python-8.1.0-cp310-cp310-manylinux_2_17_x86_64.whl`
  - `cp310` 表示针对Python 3.10
  - 无法在Python 3.9.9环境中安装

## 解决方案

### 方案1：重新下载适合Python 3.9的离线包（推荐）
在有网络的环境下，使用Python 3.9重新下载依赖包：

```bash
# 确保使用Python 3.9
python3.9 --version  # 应该显示 3.9.9

# 下载适合Python 3.9的依赖包
python3.9 -m pip download -r requirements.txt -d vendor_packages_py39

# 将下载的包复制到vendor_packages目录
rm -rf vendor_packages
mv vendor_packages_py39 vendor_packages
```

### 方案2：使用在线安装模式
如果目标环境有网络连接，可以直接使用在线安装：

```bash
# 运行部署脚本，它会自动检测并使用在线安装
./deploy_offline.sh
```

脚本会自动：
1. 检测到离线包不兼容
2. 使用在线安装模式
3. 下载适合当前Python版本的依赖包

### 方案3：使用替代的MySQL驱动
修改 `requirements.txt`，使用兼容性更好的MySQL驱动：

```bash
# 编辑requirements.txt
# 将 mysql-connector-python==8.1.0 替换为：
# pymysql==1.1.0

# 然后重新下载依赖包
python3.9 -m pip download -r requirements.txt -d vendor_packages
```

### 方案4：手动安装MySQL连接器
如果其他方案都不可行，可以手动安装：

```bash
# 激活虚拟环境
source venv/bin/activate

# 尝试安装通用版本
pip install mysql-connector-python

# 或者安装pymysql作为替代
pip install pymysql
```

然后修改 `app.py` 中的数据库连接代码：
```python
# 使用pymysql替代mysql-connector
import pymysql
pymysql.install_as_MySQLdb()

# 然后使用原来的mysql.connector代码
```

## 步骤指南

### 步骤1：检查当前环境
```bash
# 检查Python版本
python3 --version

# 检查现有离线包
ls -la vendor_packages/
```

### 步骤2：根据环境选择合适的方案
- **如果是有网络的环境**：使用方案2（在线安装）
- **如果是无网络环境，但有Python 3.9**：使用方案1（重新下载）
- **如果无法解决版本兼容问题**：使用方案3（替代驱动）

### 步骤3：执行解决方案
以方案1为例：
```bash
# 1. 备份现有离线包
mv vendor_packages vendor_packages_backup

# 2. 使用Python 3.9下载新包
python3.9 -m pip download -r requirements.txt -d vendor_packages

# 3. 验证下载的包
ls -la vendor_packages/ | grep mysql
# 应该看到类似: mysql_connector_python-8.1.0-cp39-cp39-manylinux_2_17_x86_64.whl

# 4. 运行部署脚本
./deploy_offline.sh
```

### 步骤4：验证安装
```bash
# 激活虚拟环境
source venv/bin/activate

# 验证MySQL连接器安装
python3 -c "import mysql.connector; print('MySQL连接器安装成功')"

# 运行验证脚本
python3 verify_offline.py
```

## 常见问题

### Q1: 如何确定需要哪个版本的MySQL连接器包？
查看Python版本和系统架构：
```bash
python3 -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
python3 -c "import platform; print(f'Platform: {platform.platform()}')"
```

对于Python 3.9.9，需要寻找包含 `cp39` 的包。

### Q2: 如果找不到适合的预编译包怎么办？
可以尝试：
1. 安装编译依赖：`sudo apt-get install python3-dev libmysqlclient-dev`
2. 使用源码安装：`pip install mysql-connector-python --no-binary mysql-connector-python`
3. 使用pymysql替代

### Q3: 部署脚本报错如何处理？
查看详细错误信息：
```bash
# 运行脚本并保存日志
./deploy_offline.sh 2>&1 | tee install.log

# 查看错误详情
tail -50 install.log
```

## 预防措施

### 1. 标准化Python版本
建议在所有环境中使用相同的Python版本（如3.9.9）。

### 2. 创建版本特定的离线包
为不同Python版本创建不同的离线包目录：
```
vendor_packages_py39/   # Python 3.9
vendor_packages_py310/  # Python 3.10
vendor_packages_py311/  # Python 3.11
```

### 3. 更新部署脚本
部署脚本已更新，可以：
- 检测Python版本不兼容问题
- 提供详细的错误信息和解决方案
- 尝试替代安装方案

## 联系支持
如果以上方案都无法解决问题，请联系系统管理员获取进一步帮助。

---
**最后更新**: 2026-04-09  
**适用环境**: Python 3.9.9, Linux x86_64  
**相关文件**: `deploy_offline.sh`, `requirements.txt`, `vendor_packages/`