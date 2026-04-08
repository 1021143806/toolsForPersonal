# 跨环境任务模板管理系统

基于Python Flask的Web应用，用于管理AGV跨环境任务模板。支持查询、修改、复制跨环境任务模板及其子任务。

## 功能特性

- 🔍 **智能搜索**: 支持模糊搜索任务模板代码和名称
- 📋 **模板详情查看**: 显示模板完整信息及子任务列表
- ✏️ **模板编辑**: 修改模板配置信息
- 📝 **子任务管理**: 编辑子任务详细信息
- 📋 **模板复制**: 基于现有模板创建新模板，自动生成ID后缀
- 🎨 **用户友好界面**: 响应式设计，操作直观
- 📊 **数据可视化**: 清晰的表格和卡片展示

## 系统要求

- Python 3.8+
- MySQL 5.7+
- 现代浏览器 (Chrome, Firefox, Edge等)

## 安装部署

### 1. 克隆项目

```bash
cd /main/app/mntc/git/toolsForPersonal/projects/agv_system/app
git clone [项目地址] cross_env_manager
cd cross_env_manager
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 数据库配置

#### 创建测试数据库

```sql
CREATE DATABASE agv_cross_env_test;
USE agv_cross_env_test;

-- 创建表结构 (表结构已包含在app.py的初始化中)
-- 运行应用时会自动创建表
```

#### 修改数据库配置

编辑 `app.py` 中的 `DB_CONFIG` 部分：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',  # 修改为你的MySQL用户名
    'password': 'your_password',  # 修改为你的MySQL密码
    'database': 'agv_cross_env_test',
    'charset': 'utf8mb4'
}
```

### 5. 运行应用

```bash
python app.py
```

应用将在 `http://0.0.0.0:5000` 启动。

## 使用说明

### 1. 搜索模板

在首页搜索框中输入任务模板代码或名称：
- 输入 `HJBY` 查找所有包含HJBY的任务模板
- 输入完整代码如 `HJBY_back_32A3DJ2F_to_31A3QD4B3F_446`
- 支持模糊搜索，输入部分关键词即可

### 2. 查看模板详情

点击搜索结果中的"查看详情"按钮，显示：
- 模板基本信息
- 服务器配置
- 回流配置
- 子任务列表

### 3. 编辑模板

在模板详情页面点击"编辑模板"按钮：
- 修改模板名称、状态、容量管控等
- 更新服务器配置
- 修改回流参数
- 保存前需要确认

### 4. 复制模板

在模板详情页面点击"复制模板"按钮：
- 输入新模板的基础名称（不要包含ID后缀）
- 系统自动生成新ID（如：输入`HJBY_test`，最后ID为484，则生成`HJBY_test_485`）
- 继承原模板的所有配置和子任务

### 5. 编辑子任务

在模板详情页面点击子任务的编辑按钮：
- 修改任务顺序、模板代码、名称等
- 更新服务器地址和目标点
- 单独保存每个子任务

## 数据库表结构

### fy_cross_model_process (跨环境任务模板主表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| model_process_code | VARCHAR(100) | 模板代码 (如 HJBY_back_32A3DJ2F_to_31A3QD4B3F_446) |
| model_process_name | VARCHAR(255) | 模板名称 |
| enable | TINYINT | 是否启用 (0=禁用/跨环境任务, 1=启用) |
| request_url | VARCHAR(500) | 回调URL |
| capacity | INT | 容量管控值 (-1表示不限制) |
| target_points | VARCHAR(100) | 目标点位 |
| area_id | INT | 区域ID |
| target_points_ip | VARCHAR(100) | 目标服务器IP |
| backflow_template_code | VARCHAR(100) | 货架回流任务模板 |
| comeback_template_code | VARCHAR(100) | 空车回流任务模板 |
| change_charge_template_code | VARCHAR(100) | 换电新车出发的任务模板 |
| min_power | INT | 换电任务触发电量 (%) |
| back_wait_time | INT | 空车回流触发等待时长 (秒) |
| check_area_name | VARCHAR(100) | 检查回流的片区域编号 |

### fy_cross_model_process_detail (跨环境子任务模板明细表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| model_process_id | INT | 关联的跨环境主任务模板ID |
| task_seq | INT | 子任务执行顺序 (从1开始递增) |
| task_servicec | VARCHAR(255) | 该子任务需要下发到的服务器地址 |
| template_code | VARCHAR(100) | 子任务模板编号 |
| template_name | VARCHAR(255) | 子任务名称 |
| task_path | VARCHAR(100) | 目标点标识 |
| backflow_template_code | VARCHAR(100) | 空托回流任务模板 |
| comeback_template_code | VARCHAR(100) | 空车回初始环境任务模板 |
| back_wait_time | INT | 空车回流等待时长 (秒) |

## 开发说明

### 项目结构

```
cross_env_manager/
├── app.py              # 主应用文件
├── requirements.txt    # Python依赖
├── README.md          # 项目文档
├── templates/         # HTML模板
│   ├── base.html      # 基础模板
│   ├── index.html     # 首页
│   ├── search_results.html  # 搜索结果页
│   ├── template_detail.html # 模板详情页
│   ├── edit_template.html   # 编辑模板页
│   └── copy_template.html   # 复制模板页
└── static/            # 静态文件 (可选)
```

### 主要功能模块

1. **数据库连接**: `get_db_connection()`, `execute_query()`
2. **搜索功能**: `search()` 路由，支持模糊搜索
3. **模板管理**: `view_template()`, `edit_template()`
4. **子任务管理**: `edit_detail()`
5. **复制功能**: `copy_template()`，自动ID生成

### 扩展功能建议

1. **批量操作**: 批量导入/导出模板
2. **版本控制**: 模板修改历史记录
3. **权限管理**: 用户登录和操作权限
4. **API接口**: RESTful API供其他系统调用
5. **数据验证**: 更严格的输入验证

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否运行
   - 验证数据库配置信息
   - 确保用户有足够的权限

2. **模板搜索无结果**
   - 检查数据库是否有数据
   - 确认搜索关键词正确
   - 检查数据库字符集设置

3. **页面样式异常**
   - 检查网络连接，CDN资源可能加载失败
   - 清除浏览器缓存

4. **复制模板失败**
   - 检查新模板名称是否合法
   - 确认数据库插入权限
   - 查看应用日志获取详细错误信息

### 日志查看

应用运行时会在控制台输出日志，包含：
- 数据库操作日志
- 请求处理日志
- 错误信息

## 部署到生产环境

### 使用Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用Supervisor

创建配置文件 `/main/app/supervisor/conf.d/cross_env_manager.conf`:

```ini
[program:cross_env_manager]
command=/main/app/mntc/git/toolsForPersonal/projects/agv_system/app/cross_env_manager/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
directory=/main/app/mntc/git/toolsForPersonal/projects/agv_system/app/cross_env_manager
user=a1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/main/app/log/cross_env_manager.log
```

### Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 许可证

本项目基于MIT许可证开源。

## 联系方式

如有问题或建议，请联系系统管理员。

---
**版本**: 1.0  
**最后更新**: 2026-04-03  
**基于文档**: 《跨环境配置及实施说明书》