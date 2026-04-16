---
#名称
name: my-skill
#指导说明
description: 该cross_env_manager项目相关指导操作

#指导说明Instructions
#示例用法Example Usage
---

# Instructions

在该文件夹内编写技能相关的代码和资源文件，技能的具体实现可以根据项目需求进行设计和开发。



## Example Usage

## 离线部署相关

### 部署脚本位置
`deploy_iraypleos/deploy_iraypleos.sh` - 作为离线部署脚本,同时用于更新后续的部署测试验证。

### 重要更新（2026-04-14）
1. **依赖包修复**：添加了缺失的 `importlib_metadata==8.7.1` 依赖包
2. **代码修复**：修复了 `back_wait_time` 数据处理错误（int对象没有strip方法）
3. **部署逻辑改进**：改进了mysql.connector检测逻辑，只检测未注释的导入

### 部署流程
1. 新增依赖时，需要同时更新离线依赖包（vendor_packages3.9目录）
2. 在部署脚本中添加相应的安装步骤
3. 更新requirements.txt文件

### 配置文件验证
确认 `config/env.toml` 中内容为：
```
[database]
host = "47.98.244.173"
port = 53308
user = "root"
password = "Qq13235202993"
name = "wms"
charset = "utf8mb4"
```
时，可以进行数据库插入和编辑操作。同时这个数据也可以作为你的测试数据库，可以自由操作及创建表和数据，但请勿修改其他配置文件以确保数据安全和环境隔离。

**重要**：该地址数据库为测试用数据库，其他配置文件则不允许操作，以确保数据安全和环境隔离。

此电脑可连接上生产环境数据库，允许读取生产环境的数据库内容，并拷贝表结构和部分数据至测试环境数据库，但不允许修改生产环境数据库内容。
以下为生产环境数据库的连接信息，仅作为参考，测试时优先从生产环境中获取表结构和部分数据至测试数据库后进行测试。
```
[database]
host = "10.68.2.32"
port = 3306
user = "wms"
password = "CCshenda889"
name = "wms"
charset = "utf8mb4"
```

### 测试验证

在确认可以进行操作后，执行离线部署脚本进行测试：
```bash
cd /main/app/toolsForPersonal/projects/agv_system/app/cross_env_manager
./deploy_iraypleos/deploy_iraypleos.sh
```

验证数据库操作相关功能是否正常工作：
1. 搜索功能
2. 模板详情查看
3. 编辑功能
4. 复制模版功能
5. 添加子任务
6. 删除子任务

检查日志：/main/app/log/cross_env_manager.log，确认没有错误日志输出。

### 1.3项目功能整合

项目已成功整合1.3项目的AGV任务查询功能，新增了以下功能模块：

#### 新增功能
1. **任务单号查询** - 根据任务订单ID查询详细信息
2. **跨环境任务模板查询** - 查询当前执行中的任务
3. **跨环境任务模板详情** - 查看模板配置和子任务
4. **跨环境任务详情** - 查询所有子任务信息

#### 访问路径
- 主页导航: 点击"任务查询系统"按钮
- 直接访问: `/task_query`

#### 测试验证
整合后的功能已通过基本测试，可以正常访问和显示界面。

### 测试报告
详细的测试报告见：`test/DEPLOYMENT_TEST_REPORT.md`

### 新增功能测试 (2026-04-16)

#### 新增功能清单
1. **健康检查接口** - `/actuator/health` (返回固定值1000，用于服务器监控)
2. **AGV任务下发页面** - `/addtask` (集成原有addTask功能)
3. **配置管理系统** - `/config` (独立配置管理界面)
4. **配置管理API** - 支持配置的获取、保存、备份管理
5. **帮助文档功能** - `/addtask/help` (在线帮助文档)

#### 测试验证
所有新增功能已通过Flask测试客户端验证：
- ✓ 健康检查接口正常工作
- ✓ 主页面包含任务下发导航链接
- ✓ addtask页面正常显示
- ✓ 配置管理页面功能完整
- ✓ 配置管理API接口正常
- ✓ 帮助文档功能正常

#### 测试脚本
新增综合测试脚本：`test/test_new_features.py`
```bash
# 运行测试
cd /main/app/toolsForPersonal/projects/agv_system/app/cross_env_manager
python3 test/test_new_features.py http://127.0.0.1:5000
```

#### 测试文件夹管理
test文件夹已从.gitignore中移除，包含以下测试脚本：
- `test_new_features.py` - 新增功能综合测试
- `test_web_access.py` - Web访问测试
- `test_production_task_query.py` - 生产环境任务查询测试
- 其他功能测试脚本

#### 配置管理功能
- 支持可视化编辑和源文件编辑双模式
- 自动备份和版本管理
- 备份文件存储在`static/js/backups/`目录
- 配置文件和备份文件已添加到.gitignore

#### 健康检查接口
- 地址：`/actuator/health`
- 输入：无
- 返回：`1000` (纯文本)
- 用途：服务器监控系统健康检查

### 部署验证
部署后应验证以下功能：
1. 健康检查接口返回1000
2. 主页面导航栏显示任务下发链接
3. addtask页面功能正常
4. 配置管理系统可访问
5. 帮助文档正常加载