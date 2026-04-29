# 空车调车模块

## 功能概述

空车调车模块用于监控各区域设备平衡状态，自动/手动下发调车任务。基于本地 JSON 文件实现数据持久化，零外部依赖。

## 页面说明

### 1. 主看板 (`/dispatch`)

展示各区域设备平衡状态：

| 指标 | 说明 |
|------|------|
| 当前设备 | `currentCount.json` 中的设备数 |
| 需调度 | 需要调出/调入的设备数 |
| 方向 | 平衡/调出/调入 |
| 保留范围 | xmin ~ xmax 保留范围 |

每个区域卡片显示：
- 来区域模板及其任务数
- 离开模板及其任务数
- 操作按钮：详情、自动调车、**JSON 文件**、配置
- 启用/禁用开关（实时切换）

#### JSON 文件查看/编辑

点击区域卡片的 `[📄 JSON文件]` 按钮，在该卡片下方展开面板：
- 列出该区域所有关联的 JSON 文件（模板文件 + `currentCount.json`）
- 不存在的文件显示「未创建」，点击「创建」可新建
- **查看模式**：只读展示文件内容
- **编辑模式**：textarea 编辑 + JSON 格式校验 + 保存后自动刷新看板

> **注意**：看板每 10 秒自动刷新，采用增量更新模式（只更新数字和状态，不重新渲染 DOM），展开的 JSON 面板不会被关闭。

### 2. 配置管理 (`/dispatch/config`)

三标签页编辑模式：

#### 可视化编辑
- 区域列表：增删改区域
- 每个区域可编辑：区域标识、areaId、服务器地址、xmin/xmax、单次最大调车数
- 模板列表：增删改模板（代码、文件名、方向）

#### 源文件编辑
- 直接编辑 JSON 格式的配置内容
- 点击"应用到可视化编辑器"同步

#### 备份恢复
- Git 图形版本历史展示
- 创建备份（可带描述）
- 查看/恢复/删除备份

### 3. 区域详情 (`/dispatch/area/<id>`)

查看指定区域的详细状态。

## 数据文件

所有数据存储在 `data/dispatch/` 目录下（已加入 .gitignore）：

```
data/dispatch/
├── cache_index.json              # 主配置文件（区域、服务器、模板映射）
├── backups/                      # 备份文件目录
│   ├── dispatch_config_20260428_120000.json
│   └── ...
├── region_1_currentCount.json    # 区域1当前设备列表
├── region_1_DKCqu.json           # 区域1调空车来模板数据
└── ...
```

### cache_index.json 格式

```json
{
  "region_1": {
    "areaId": "1",
    "enabled": true,
    "max_dispatch_once": 3,
    "server": "10.68.2.31:7000",
    "xmin": 2,
    "xmax": 4,
    "templates": [
      {"name": "DKCqu",       "file": "DKCqu.json",        "direction": "in"},
      {"name": "DKCback",     "file": "DKCback.json",      "direction": "out"}
    ]
  }
}
```

- `direction: "in"` — 来区域模板（设备进入区域）
- `direction: "out"` — 离开模板（设备离开区域）
- `enabled` — 区域启用/禁用开关
- `max_dispatch_once` — 单次最大调车数（容量管控）

### currentCount.json 格式

```json
[
  {"deviceCode": "BL11637BAK00010", "deviceNum": "C185", "create_time": "2026-04-28T12:00:00"},
  {"deviceCode": "BL11637BAK00011", "deviceNum": "C186", "create_time": "2026-04-28T12:05:00"}
]
```

每条记录包含设备序列号(`deviceCode`)和设备编号(`deviceNum`)，可有多条。

## API 接口

### 权限说明

调车模块已接入系统账号体系，权限分为三级：

| 权限 | 说明 |
|------|------|
| 🔓 无需登录 | 外部设备上报接口，无需认证 |
| 🔑 登录 | 登录用户可访问（普通用户或管理员） |
| ⚙️ 管理员 | 需在首页启用管理员提权 |

### 接口列表

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/dispatch` | 🔑 登录 | 主看板页面 |
| GET | `/dispatch/config` | ⚙️ 管理员 | 配置编辑页面 |
| GET | `/dispatch/area/<id>` | 🔑 登录 | 区域详情页面 |
| GET | `/api/dispatch/status` | 🔑 登录 | 获取所有区域状态（含平衡计算） |
| GET | `/api/dispatch/config` | 🔑 登录 | 获取配置 |
| POST | `/api/dispatch/config` | ⚙️ 管理员 | 保存配置 |
| GET | `/api/dispatch/config/backups` | 🔑 登录 | 列出备份 |
| POST | `/api/dispatch/config/backup` | ⚙️ 管理员 | 创建备份 |
| GET | `/api/dispatch/config/backup/<name>` | 🔑 登录 | 查看备份内容 |
| POST | `/api/dispatch/config/backup/<name>/restore` | ⚙️ 管理员 | 恢复备份 |
| DELETE | `/api/dispatch/config/backup/<name>` | ⚙️ 管理员 | 删除备份 |
| GET | `/api/dispatch/region_files/<region_key>` | 🔑 登录 | 获取区域关联的文件列表 |
| GET | `/api/dispatch/region_file/<region_key>/<filename>` | 🔑 登录 | 获取文件内容 |
| POST | `/api/dispatch/region_file/<region_key>/<filename>` | ⚙️ 管理员 | 保存文件内容 |
| POST | `/api/dispatch/execute/<region_key>` | 🔑 登录 | 执行计算并下发调车 |
| POST | `/api/dispatch/clean_simulated/<region_key>` | 🔑 登录 | 清理模拟数据 |
| GET | `/api/dispatch/dispatch_log/<region_key>` | 🔑 登录 | 获取下发记录 |
| POST | `/api/dispatch/dispatch_log/<region_key>` | ⚙️ 管理员 | 写入下发记录 |
| **POST** | **`/api/dispatch/report_status`** | **🔓 无需登录** | **任务状态上报接口（外部设备）** |

### 状态上报接口

**路径**: `POST /api/dispatch/report_status`

**请求体** (JSON):
```json
{
  "region_key": "region_1",
  "template_name": "DKCqu",
  "deviceCode": "BL11637BAK00010",
  "deviceNum": "C185",
  "status": 6,
  "order_id": "可选"
}
```

**status 说明**:

| 值 | 含义 | 处理逻辑 |
|----|------|----------|
| `6` | 任务开始 | 记录到对应模板 JSON 文件 |
| `8` | 任务完成 | 从模板 JSON 删除；来区域完成 → 写入 `currentCount.json`；离开完成 → 从 `currentCount.json` 删除 |

**响应**:
```json
{"success": true, "message": "状态上报成功"}
```

**调用示例**:
```bash
curl -X POST http://localhost:5000/api/dispatch/report_status \
  -H "Content-Type: application/json" \
  -d '{"region_key":"region_1","template_name":"DKCqu","deviceCode":"BL11637BAK00010","deviceNum":"C185","status":6}'
```

## 设备平衡计算逻辑

```
currentCount = currentCount.json 中的设备数
a = 所有来区域模板中 status=6 的任务数之和
b = 所有离开模板中 status=6 的任务数之和
expectedCount = currentCount + a - b

if expectedCount > xmax:
    need = expectedCount - xmax    # 正数，车过多，下发回空车
    direction = "out"
elif expectedCount < xmin:
    need = expectedCount - xmin    # 负数，车不够，下发调空车
    direction = "in"
else:
    need = 0                       # 平衡
    direction = "none"

# 容量管控
dispatch_count = min(abs(need), max_dispatch_once)

# 互斥逻辑
if 要下发去空车(in) 但存在未完成的回空车(out)任务 → 禁止下发
if 要下发回空车(out) 但存在未完成的去空车(in)任务 → 禁止下发
```

## 开发说明

- 所有数据文件存储在 `data/dispatch/`，不会提交到 Git
- 首次使用需在配置页面创建区域和模板配置
- 备份文件存储在 `data/dispatch/backups/`
- 看板采用增量刷新模式，展开的 JSON 面板不会被自动刷新关闭
