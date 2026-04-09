# 离线部署指南

本文档介绍如何在无网络环境下部署跨环境任务模板管理系统。

## 问题描述

用户反馈："要部署的服务没有网络连接，安装有python3，依赖能不能防止在项目文件中直接调用"

这意味着：
1. 部署环境没有互联网连接，无法从PyPI下载Python依赖包
2. 需要一种离线安装依赖的方法

## 解决方案

我们提供了完整的离线部署方案，包括：

### 1. 离线依赖包 (`vendor_packages/`目录)
- 包含所有必需的Python依赖包（.whl文件）
- 可以在有网络的环境预先下载
- 在无网络环境直接使用

### 2. 离线部署脚本 (`deploy_offline.sh`)
- 自动检测是否使用离线模式
- 支持venv虚拟环境（不依赖conda）
- 自动配置supervisor服务

### 3. 测试脚本 (`test_offline_install.sh`)
- 验证离线安装是否正常工作
- 检查所有依赖包是否正确安装

## 使用步骤

### 步骤1：在有网络的环境准备离线包

```bash
# 进入项目目录
cd /main/app/mntc/git/toolsForPersonal/projects/agv_system/app/cross_env_manager

# 下载所有依赖包到vendor_packages目录
python3 -m pip download -r requirements.txt -d vendor_packages --no-deps

# 验证下载的包
ls -la vendor_packages/
```

应该看到以下文件：
- Flask-2.3.3-py3-none-any.whl
- mysql_connector_python-8.1.0-*.whl
- python_dotenv-1.0.0-py3-none-any.whl
- Werkzeug-2.3.7-py3-none-any.whl
- Jinja2-3.1.2-py3-none-any.whl
- click-8.1.6-py3-none-any.whl
- itsdangerous-2.1.2-py3-none-any.whl
- Markdown-3.5.1-py3-none-any.whl
- tomli-2.0.1-py3-none-any.whl

### 步骤2：将项目复制到无网络环境

将整个`cross_env_manager`目录复制到目标服务器：
- 包括`vendor_packages/`目录
- 包括所有脚本和配置文件

### 步骤3：在无网络环境部署

```bash
# 进入项目目录
cd /path/to/cross_env_manager

# 给脚本执行权限
chmod +x deploy_offline.sh

# 运行离线部署脚本
./deploy_offline.sh
```

脚本会自动：
1. 检查Python环境
2. 检测离线依赖包
3. 创建venv虚拟环境
4. 使用离线包安装依赖
5. 配置supervisor服务
6. 启动应用

### 步骤4：验证部署

```bash
# 检查服务状态
supervisorctl status cross_env_manager

# 查看日志
tail -f /main/app/log/cross_env_manager.log

# 访问应用
curl http://localhost:5000
```

## 脚本说明

### `deploy_offline.sh` - 主部署脚本

特点：
- **智能检测**：自动检测是否有离线依赖包
- **离线优先**：优先使用离线包，无网络时自动切换
- **venv支持**：使用Python内置venv，不依赖conda
- **完整部署**：一键完成所有部署步骤

### `test_offline_install.sh` - 测试脚本

用于验证离线安装是否正常工作。如果系统缺少python3-venv，可以手动测试：

```bash
# 手动测试离线安装
cd /path/to/cross_env_manager
python3 -m pip install --no-index --find-links=vendor_packages -r requirements.txt

# 验证安装
python3 -c "import flask; print(f'Flask版本: {flask.__version__}')"
python3 -c "import mysql.connector; print(f'mysql-connector版本: {mysql.connector.__version__}')"
```

## 故障排除

### 1. 虚拟环境创建失败

如果系统缺少python3-venv，部署脚本会自动使用系统Python。或者手动安装：

```bash
# Ubuntu/Debian
sudo apt install python3.10-venv

# CentOS/RHEL
sudo yum install python3-venv
```

### 2. 离线包不完整

确保在有网络的环境下载所有依赖：

```bash
# 重新下载所有依赖
rm -rf vendor_packages
python3 -m pip download -r requirements.txt -d vendor_packages
```

### 3. 数据库连接问题

如果部署环境无法访问远程数据库（47.98.244.173:53308），需要：
1. 修改`config/env.toml`使用本地数据库
2. 或者确保网络可以访问远程数据库

### 4. Supervisor配置问题

检查supervisor配置：
```bash
# 重新加载配置
supervisorctl reread
supervisorctl update

# 重启服务
supervisorctl restart cross_env_manager
```

## 文件清单

离线部署需要的文件：
```
cross_env_manager/
├── app.py                          # 主应用
├── requirements.txt                # 依赖列表
├── vendor_packages/                # 离线依赖包目录
│   ├── Flask-2.3.3-py3-none-any.whl
│   ├── mysql_connector_python-8.1.0-*.whl
│   └── ...其他依赖包
├── deploy_offline.sh              # 离线部署脚本
├── deploy.sh                      # 原始部署脚本（备用）
├── test_offline_install.sh        # 测试脚本
├── config/
│   ├── env.toml                   # 配置文件
│   └── template/                  # 配置模板
├── templates/                     # HTML模板
└── README.md                      # 项目文档
```

## 注意事项

1. **Python版本**：确保目标环境有Python 3.8+
2. **数据库**：如果使用远程数据库，确保网络可达
3. **权限**：部署脚本需要执行权限，supervisor需要相应权限
4. **端口**：默认使用5000端口，确保端口未被占用
5. **日志**：查看`/main/app/log/cross_env_manager.log`获取详细错误信息

## 总结

通过本方案，您可以在完全无网络的环境下部署跨环境任务模板管理系统。关键点是预先下载所有依赖包到`vendor_packages`目录，然后使用`deploy_offline.sh`脚本进行离线安装。

这种方案解决了"依赖能不能防止在项目文件中直接调用"的问题，因为依赖包已经包含在项目目录中，不需要从网络下载。