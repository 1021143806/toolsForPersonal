# vendor_packages3.9 目录结构说明

## 目录用途
此目录包含跨环境任务模板管理系统所需的Python 3.9.9兼容离线依赖包。

## 包兼容性说明

### ✅ 完全兼容Python 3.9.9的包
- MarkupSafe-2.1.3-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
  - Python 3.9编译版本（cp39）
  - 关键依赖：Werkzeug和Jinja2都需要此包
- 其他所有纯Python包（py3-none-any）
  - 通用兼容

### 📋 包含的包
1. **Flask及依赖**（全部兼容）
   - Flask 2.3.3
   - Werkzeug 2.3.7
   - Jinja2 3.1.2
   - click 8.1.6
   - itsdangerous 2.1.2
   - blinker 1.9.0

2. **数据库驱动**
   - PyMySQL 1.1.0（替代mysql-connector-python，Python 3.9兼容）

3. **工具包**
   - python-dotenv 1.0.0
   - Markdown 3.5.1
   - tomli 2.0.1
   - zipp 3.23.0

4. **可选包**
   - importlib_metadata 8.7.1（可选，Python 3.9已有内置）

## 部署说明

### 离线部署
```bash
# 确保在项目根目录
cd /main/app/toolsForPersonal/projects/agv_system/app/cross_env_manager

# 运行部署脚本
./deploy_iraypleos.sh
```

### 包验证
```bash
# 验证包兼容性
./verify_python39_packages.sh
```

## 文件说明
- `.whl`文件：二进制wheel包
- `.tar.gz`文件：源码包（备用）
- `requirements_py39_fixed.txt`：Python 3.9专用依赖清单

## 维护说明
1. 如需更新包版本，在有网环境重新下载
2. 确保所有包都是Python 3.9兼容版本
3. 关键检查点：markupsafe必须是cp39版本
