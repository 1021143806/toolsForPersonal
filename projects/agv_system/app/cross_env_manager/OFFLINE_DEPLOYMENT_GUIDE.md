# 跨环境任务模板管理系统 - 完全离线部署指南

## 概述

本文档描述了如何在离线环境（无网络连接）中部署跨环境任务模板管理系统。该部署方案专门为IRAYPLEOS系统设计，适用于现场服务器等需要完全离线安装的环境。

## 系统要求

### 硬件要求
- CPU: 1核以上
- 内存: 1GB以上
- 磁盘空间: 至少2GB可用空间

### 软件要求
- 操作系统: Linux (Ubuntu/CentOS/RHEL等)
- Python版本: 3.9.x (必须)
- Supervisor: 用于进程管理（可选，但推荐）
- MySQL客户端/服务器: 用于数据库连接

### IRAYPLEOS环境要求
- 用户: ymsk
- Supervisor目录: `/main/server/supervisor/`
- 应用目录: `/main/app/cross_env_manager/`
- 日志目录: `/main/app/log/`

## 部署流程

### 第一步：准备阶段（在有网环境执行）

1. **下载所有依赖包**
   ```bash
   # 在有网环境中运行
   ./download_packages_for_offline.sh
   ```
   该脚本会：
   - 下载所有Python 3.9兼容的wheel包
   - 保存到 `vendor_packages3.9/` 目录
   - 生成包清单 `PACKAGES.md`

2. **检查下载的包**
   ```bash
   ls -la vendor_packages3.9/
   ```
   应有13个wheel文件

### 第二步：传输到离线环境

1. **打包项目目录**
   ```bash
   # 在有网环境
   tar -czvf cross_env_manager_offline.tar.gz \
       deploy_iraypleos.sh \
       app.py \
       requirements_py39.txt \
       requirements.txt \
       vendor_packages3.9/ \
       templates/ \
       config/ \
       *.sh \
       README.md
   ```

2. **传输到离线服务器**
   ```bash
   # 通过U盘、内网传输等方式
   scp cross_env_manager_offline.tar.gz user@offline-server:/tmp/
   ```

3. **在离线服务器解压**
   ```bash
   # 在离线服务器执行
   cd /main/app
   tar -xzvf /tmp/cross_env_manager_offline.tar.gz
   mv cross_env_manager_offline cross_env_manager
   cd cross_env_manager
   ```

### 第三步：离线部署（在离线环境执行）

1. **设置脚本权限**
   ```bash
   chmod +x deploy_iraypleos.sh
   chmod +x test_offline_deployment.sh
   ```

2. **测试部署环境**
   ```bash
   ./test_offline_deployment.sh
   ```
   输出应为所有检查通过

3. **执行部署**
   ```bash
   ./deploy_iraypleos.sh
   ```

### 第四步：验证部署

1. **检查服务状态**
   ```bash
   # 方法1：通过Supervisor
   supervisorctl status cross_env_manager
   
   # 方法2：直接检查进程
   pgrep -f "python.*app.py"
   
   # 方法3：查看日志
   tail -f /main/app/log/cross_env_manager.log
   ```

2. **测试Web接口**
   ```bash
   # 测试健康检查
   curl -s http://localhost:5000/health
   
   # 测试主页面
   curl -s http://localhost:5000/
   ```

3. **验证数据库连接**
   - 访问 http://localhost:5000/
   - 使用搜索功能测试数据库连接
   - 检查是否能正常显示任务模板

## 关键特性说明

### 完全离线安装
- 部署脚本已完全移除网络下载尝试
- 所有依赖包从 `vendor_packages3.9/` 目录离线安装
- 使用 `pip install --no-index` 确保不联网

### Python 3.9兼容性处理
1. **mysql.connector替代方案**
   - 使用`PyMySQL`替代`mysql-connector-python`
   - 自动修复应用代码中的导入问题
   - 修复脚本：`fix_mysql_imports.py`

2. **markupsafe兼容性**
   - 当前wheel文件为Python 3.10编译(`cp310`)
   - 部署脚本会自动检测并跳过安装
   - Jinja2会自动使用纯Python实现

3. **依赖包安装顺序**
   - 按依赖关系分阶段安装
   - 使用`--no-deps`避免依赖解析问题
   - 确保离线安装的可靠性

### Supervisor配置
- 符合IRAYPLEOS标准
- 自动检测Supervisor路径
- 日志自动保存到`/main/app/log/`
- 支持自动重启和进程监控

## 故障排除

### 常见问题

#### 1. 虚拟环境创建失败
```bash
# 检查Python版本
python3 --version  # 必须为3.9.x

# 检查venv模块
python3 -m venv --help

# 手动创建虚拟环境
python3 -m venv venv
```

#### 2. 依赖包安装失败
```bash
# 检查wheel文件是否存在
ls -la vendor_packages3.9/*.whl

# 手动安装单个包
source venv/bin/activate
pip install --no-index vendor_packages3.9/click-8.1.6-py3-none-any.whl
```

#### 3. markupsafe兼容性问题
```bash
# 检查Jinja2是否正常工作
python -c "import jinja2; print('Jinja2版本:', jinja2.__version__)"

# 如果Jinja2导入失败，可能需要强制安装其他方式
```

#### 4. 服务启动失败
```bash
# 检查Supervisor配置
cat /main/server/supervisor/cross_env_manager.conf

# 检查日志
tail -100 /main/app/log/cross_env_manager_error.log

# 检查端口占用
netstat -tlnp | grep :5000

# 直接运行应用
source venv/bin/activate
python app.py
```

### 日志文件
- 应用日志: `/main/app/log/cross_env_manager.log`
- 错误日志: `/main/app/log/cross_env_manager_error.log`
- 直接启动日志: `/main/app/log/cross_env_manager_direct.log`

## 维护和更新

### 更新应用代码
```bash
# 在有网环境更新代码
cd /main/app/toolsForPersonal/projects/agv_system/app/cross_env_manager
git pull origin main

# 重新下载依赖包（仅当requirements.txt变化）
./download_packages_for_offline.sh

# 重新打包传输到离线环境
```

### 更新依赖包
```bash
# 在有网环境更新依赖
# 修改requirements_py39.txt
# 重新下载包
./download_packages_for_offline.sh
# 重新打包传输
```

## 安全注意事项

1. **数据库连接信息**
   - 应用代码中包含数据库连接字符串
   - 传输和存储时确保安全

2. **防火墙设置**
   - 应用监听5000端口
   - 根据需要配置防火墙规则
   - 如仅本地访问，可限制为127.0.0.1

3. **Supervisor权限**
   - 确保Supervisor配置正确
   - 避免以root用户运行应用
   - 使用专用用户ymsk

## 性能优化建议

1. **资源限制**
   - 在Supervisor配置中设置内存限制
   - 调整日志轮转策略避免磁盘满

2. **数据库连接池**
   - 应用中已实现连接池复用
   - 可根据需要调整连接数

3. **缓存策略**
   - 考虑增加模板缓存
   - 对于频繁访问的数据可增加缓存层

## 联系支持

遇到问题请检查：
1. 所有日志文件
2. 部署脚本错误信息
3. Python版本兼容性
4. 离线包完整性

如需远程支持，请提供：
- 系统Python版本
- 部署脚本输出
- 错误日志内容
- vendor_packages3.9目录列表