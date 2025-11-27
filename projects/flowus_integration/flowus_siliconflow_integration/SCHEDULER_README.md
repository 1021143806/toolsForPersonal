# FlowUs+SiliconFlow 定时任务调度器使用说明

## 概述

本项目已成功集成了每日定时运行的脚本功能，可以自动执行FlowUs数据获取、AI处理和内容生成流程。

## 功能特性

- ✅ **每日定时执行** - 可配置每日固定时间自动运行
- ✅ **智能重试机制** - 失败时自动重试，可配置重试次数和间隔
- ✅ **超时保护** - 防止任务无限期运行
- ✅ **周末控制** - 可选择是否在周末执行任务
- ✅ **时区支持** - 支持不同时区配置
- ✅ **详细日志** - 完整的执行日志记录
- ✅ **错误处理** - 完善的异常处理和恢复机制
- ✅ **配置灵活** - 通过配置文件轻松调整参数

## 安装依赖

```bash
pip install schedule pytz --break-system-packages
```

或者使用requirements.txt：

```bash
pip install -r requirements.txt --break-system-packages
```

## 配置说明

在 `config.toml` 文件中已添加了 `[scheduler]` 配置段：

```toml
# 定时任务配置
[scheduler]
# 是否启用定时任务
enabled = true
# 每日执行时间（24小时制）
time = "08:00"
# 时区设置
timezone = "Asia/Shanghai"
# 重试次数（失败时）
max_retries = 3
# 重试间隔（秒）
retry_interval = 300
# 是否启用周末执行
run_on_weekends = true
# 任务超时时间（秒）
timeout = 3600
```

### 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `true` | 是否启用定时任务 |
| `time` | string | `"08:00"` | 每日执行时间，格式：HH:MM |
| `timezone` | string | `"Asia/Shanghai"` | 时区设置 |
| `max_retries` | int | `3` | 失败时的最大重试次数 |
| `retry_interval` | int | `300` | 重试间隔（秒） |
| `run_on_weekends` | bool | `true` | 是否在周末执行任务 |
| `timeout` | int | `3600` | 单次任务超时时间（秒） |

## 使用方法

### 1. 启动定时调度器

```bash
# 启动调度器（持续运行）
python scheduler.py

# 或者使用后台运行
nohup python scheduler.py > scheduler.log 2>&1 &
```

### 2. 立即执行一次任务（测试用）

```bash
python scheduler.py --run-once
```

### 3. 测试配置

```bash
python scheduler.py --test-config
```

### 4. 查看帮助

```bash
python scheduler.py --help
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `--run-once` | 立即执行一次任务（用于测试） |
| `--test-config` | 测试配置文件是否正确 |
| `--help` | 显示帮助信息 |

## 日志文件

系统会生成以下日志文件：

- `scheduler.log` - 调度器主要日志
- `main_scheduler.log` - 主程序执行日志
- `fetch_diary.log` - 数据获取日志
- `process_diary.log` - AI处理日志
- `siliconflow_api_requests.log` - API请求详细日志

## 系统服务部署

### 使用Supervisor管理（推荐）

Supervisor是一个强大的进程控制系统，特别适合管理Python应用程序。

#### 1. 安装Supervisor

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install supervisor

# CentOS/RHEL
sudo yum install supervisor
# 或者在CentOS 8+使用dnf
sudo dnf install supervisor
```

#### 2. 配置Supervisor

1. 将配置文件复制到supervisor配置目录：

```bash
sudo cp flowus-scheduler.conf /etc/supervisor/conf.d/
```

2. 或者手动创建配置文件：

```bash
sudo nano /etc/supervisor/conf.d/flowus-scheduler.conf
```

3. 配置文件内容（已提供flowus-scheduler.conf）：

```ini
[program:flowus-scheduler]
command=python3 scheduler.py
directory=/main/app/www/web/php/toolsForPersonal/projects/flowus_integration/flowus_siliconflow_integration
autostart=true
autorestart=true
startsecs=10
startretries=3
user=a1
redirect_stderr=true
stdout_logfile=/var/log/flowus-scheduler.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PYTHONPATH="/main/app/www/web/php/toolsForPersonal/projects/flowus_integration/flowus_siliconflow_integration"
```

**注意**：请根据实际系统用户修改配置文件中的`user`字段。可以使用以下命令查看当前用户：

```bash
whoami
# 或者
echo $USER
```

常见的用户名可能是：`a1`、`ubuntu`、`centos`、`ec2-user`等。

#### 3. 启动和管理服务

```bash
# 重新加载配置
sudo supervisorctl reread

# 更新配置
sudo supervisorctl update

# 启动服务
sudo supervisorctl start flowus-scheduler

# 查看服务状态
sudo supervisorctl status flowus-scheduler

# 停止服务
sudo supervisorctl stop flowus-scheduler

# 重启服务
sudo supervisorctl restart flowus-scheduler
```

#### 4. Supervisor常用命令

```bash
# 查看所有进程状态
sudo supervisorctl status

# 查看实时日志
sudo supervisorctl tail -f flowus-scheduler

# 查看进程详细信息
sudo supervisorctl info flowus-scheduler

# 重新加载配置文件
sudo supervisorctl reread && sudo supervisorctl update
```

#### 5. Supervisor Web界面（可选）

1. 编辑supervisor主配置文件：

```bash
sudo nano /etc/supervisor/supervisord.conf
```

2. 取消注释并配置Web界面：

```ini
[inet_http_server]
port=127.0.0.1:9001
username=admin
password=your_password
```

3. 重启supervisor服务：

```bash
sudo systemctl restart supervisor
```

4. 访问Web界面：`http://127.0.0.1:9001`

### 使用systemd服务

1. 创建服务文件：

```bash
sudo nano /etc/systemd/system/flowus-scheduler.service
```

2. 添加以下内容：

```ini
[Unit]
Description=FlowUs SiliconFlow Scheduler
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/main/app/www/web/php/toolsForPersonal/projects/flowus_integration/flowus_siliconflow_integration
ExecStart=/usr/bin/python3 scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. 启用和启动服务：

```bash
sudo systemctl enable flowus-scheduler
sudo systemctl start flowus-scheduler
sudo systemctl status flowus-scheduler
```

### 使用cron定时任务

1. 编辑crontab：

```bash
crontab -e
```

2. 添加定时任务（每天8:00执行）：

```bash
0 8 * * * cd /main/app/www/web/php/toolsForPersonal/projects/flowus_integration/flowus_siliconflow_integration && python scheduler.py --run-once >> /var/log/flowus-scheduler.log 2>&1
```

#### Supervisor vs systemd vs cron 对比

| 特性 | Supervisor | systemd | cron |
|------|------------|---------|------|
| 进程监控 | ✅ 优秀 | ✅ 良好 | ❌ 无 |
| 自动重启 | ✅ 支持 | ✅ 支持 | ❌ 无 |
| Web界面 | ✅ 支持 | ❌ 无 | ❌ 无 |
| 日志管理 | ✅ 内置 | ✅ 支持 | ⚠️ 基础 |
| 配置复杂度 | 🟡 中等 | 🟢 简单 | 🟢 简单 |
| 长期运行进程 | ✅ 最佳 | ✅ 良好 | ❌ 不适合 |
| 定时任务 | ⚠️ 需要额外配置 | ⚠️ 需要timer | ✅ 原生支持 |

**推荐使用Supervisor**，因为它专门为管理Python应用程序设计，提供了最好的进程控制和监控功能。

## 监控和维护

### 使用Supervisor监控

```bash
# 查看进程状态
sudo supervisorctl status flowus-scheduler

# 实时查看日志
sudo supervisorctl tail -f flowus-scheduler

# 查看进程详细信息
sudo supervisorctl info flowus-scheduler

# 查看所有进程
sudo supervisorctl status

# 重启进程
sudo supervisorctl restart flowus-scheduler

# 停止进程
sudo supervisorctl stop flowus-scheduler
```

### Supervisor日志管理

```bash
# 查看supervisor主日志
sudo tail -f /var/log/supervisor/supervisord.log

# 查看应用程序日志
sudo tail -f /var/log/flowus-scheduler.log

# 查看日志轮转配置
ls -la /var/log/flowus-scheduler.log*
```

### 查看任务状态

```bash
# 查看最近的日志
tail -f scheduler.log

# 查看任务执行历史
grep "任务执行" scheduler.log

# 查看错误信息
grep "ERROR" scheduler.log

# 查看Supervisor管理的进程日志
sudo tail -f /var/log/flowus-scheduler.log
```

### 常见问题排查

1. **任务不执行**
   - 检查配置文件中的 `enabled = true`
   - 确认时间格式正确（HH:MM）
   - 查看日志文件中的错误信息

2. **任务执行失败**
   - 检查网络连接
   - 确认API密钥有效
   - 查看重试机制是否工作

3. **性能问题**
   - 调整超时时间
   - 考虑数据量大小
   - 监控系统资源使用

4. **Supervisor相关问题**
   - **进程无法启动**
     ```bash
     # 检查配置文件语法
     sudo supervisorctl reread
     
     # 查看详细错误信息
     sudo supervisorctl status flowus-scheduler
     sudo tail -f /var/log/supervisor/supervisord.log
     ```
   
   - **进程频繁重启**
     ```bash
     # 检查进程状态和重启历史
     sudo supervisorctl status flowus-scheduler
     
     # 查看应用程序日志
     sudo tail -f /var/log/flowus-scheduler.log
     
     # 检查配置中的启动参数
     sudo supervisorctl info flowus-scheduler
     ```
   
   - **权限问题**
     ```bash
     # 检查当前用户
     whoami
     echo $USER
     
     # 检查文件权限
     ls -la /main/app/www/web/php/toolsForPersonal/projects/flowus_integration/flowus_siliconflow_integration/
     
     # 检查用户权限
     sudo supervisorctl status flowus-scheduler | grep -E "(user|group)"
     
     # 修改配置文件中的用户设置
     sudo nano /etc/supervisor/conf.d/flowus-scheduler.conf
     
     # 验证用户是否存在
     id a1  # 替换为实际用户名
     ```
   
   - **日志文件问题**
     ```bash
     # 检查日志目录权限
     ls -la /var/log/flowus-scheduler.log*
     
     # 手动创建日志文件
     sudo touch /var/log/flowus-scheduler.log
     sudo chown www-data:www-data /var/log/flowus-scheduler.log
     ```

## 更新和维护

### 更新配置

修改 `config.toml` 文件后，需要重启调度器：

```bash
# 如果使用Supervisor（推荐）
sudo supervisorctl restart flowus-scheduler

# 如果使用systemd
sudo systemctl restart flowus-scheduler

# 如果手动运行
# 停止当前进程（Ctrl+C）然后重新启动
python scheduler.py
```

### 更新代码

更新代码后建议先测试：

```bash
# 测试配置
python scheduler.py --test-config

# 测试单次执行
python scheduler.py --run-once

# 确认无误后重启服务
# 使用Supervisor
sudo supervisorctl restart flowus-scheduler

# 或使用systemd
sudo systemctl restart flowus-scheduler
```

### Supervisor配置更新

如果修改了supervisor配置文件：

```bash
# 重新加载配置
sudo supervisorctl reread

# 应用新配置
sudo supervisorctl update

# 重启受影响的进程
sudo supervisorctl restart flowus-scheduler
```

## 故障恢复

### 手动恢复

如果自动重试失败，可以手动执行：

```bash
python scheduler.py --run-once
```

### 数据备份

重要数据会自动备份到：
- `outputs/data.log` - 导出的原始数据
- `outputs/local.md` - AI生成内容的本地备份

## 性能优化建议

1. **调整执行时间** - 避开系统高峰期
2. **优化数据范围** - 适当减少 `recent_days` 配置
3. **监控资源使用** - 定期检查内存和CPU使用情况
4. **日志轮转** - 设置日志文件大小限制和轮转策略

## 安全注意事项

1. **保护配置文件** - config.toml包含API密钥，确保文件权限正确
2. **网络安全** - 确保服务器防火墙配置正确
3. **定期更新** - 保持依赖库和系统更新

## 联系支持

如果遇到问题，请检查：
1. 日志文件中的错误信息
2. 配置文件格式是否正确
3. 网络连接是否正常
4. API密钥是否有效

---

**版本信息**: v1.0  
**最后更新**: 2025-11-25  
**兼容性**: Python 3.7+