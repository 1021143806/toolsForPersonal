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
