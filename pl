# 空车调车模块 - 配置编辑页面设计方案

## 现状分析

### 现有文件
- [`dispatch/dashboard.html`](projects/agv_system/app/cross_env_manager/templates/dispatch/dashboard.html) — 主看板（已完成）
- [`dispatch_routes.py`](projects/agv_system/app/cross_env_manager/routes/dispatch_routes.py) — 路由（模拟数据版）
- [`dispatch_module_design.md`](plans/dispatch_module_design.md) — 完整设计文档

### 参考模板
- [`addTask/config_editor.html`](projects/agv_system/app/cross_env_manager/templates/addTask/config_editor.html)（90710 字节）— 任务下发系统的配置编辑器，包含可视化编辑 + 源文件编辑双模式

## 配置编辑页面设计

### 页面结构

```
/dispatch/config
├── 区域列表（左侧或顶部）
│   ├── 区域1 [编辑] [删除]
│   ├── 区域2 [编辑] [删除]
│   └── [+ 新增区域]
│
├── 选中区域的配置表单
│   ├── 基本信息
│   │   ├── 区域名称 (text)
│   │   ├── xmin (number)
│   │   ├── xmax (number)
│   │   └── 单次最大调车数 (number)
│   │
│   ├── 服务器配置
│   │   ├── 服务器IP (text)
│   │   ├── 端口 (number)
│   │   └── 名称 (text)
│   │   [+ 新增服务器]
│   │
│   ├── 来区域模板列表
│   │   ├── 模板代码 (text)
│   │   ├── 模板名称 (text)
│   │   ├── 类型 (下拉: empty_in/load_in)
│   │   └── [删除]
│   │   [+ 新增来区域模板]
│   │
│   └── 离开模板列表
│       ├── 模板代码 (text)
│       ├── 模板名称 (text)
│       ├── 类型 (下拉: empty_out/load_out)
│       └── [删除]
│       [+ 新增离开模板]
│
└── 保存/取消按钮
```

### 复用 addTask/config_editor.html 的策略

你说得对，可以直接把 `config_editor.html` 的编辑界面拿过来改。具体改动：

| 组件 | 原 config_editor | 改为 dispatch config |
|------|-----------------|---------------------|
| 数据结构 | `{general, areas: {areaName: {tasks: {...}}}}` | `{areas: [{id, name, xmin, xmax, servers, templates}]}` |
| 可视化编辑 | 区域 → 任务 两级 | 区域列表 → 区域配置 两级 |
| 源文件编辑 | 编辑整个 JS 文件 | 编辑 JSON 配置 |
| 保存 API | `POST /addtask/config` | `POST /dispatch/config/save` |
| 备份功能 | 有 Git 图形备份 | 不需要（配置简单） |

### 推荐方案：直接复用 config_editor 的 UI 框架

1. **复制** `config_editor.html` 为 `dispatch/config.html`
2. **保留** 其可视化编辑 + 源文件编辑双模式
3. **修改** 数据结构为 dispatch 的 JSON 格式
4. **修改** API 调用地址
5. **简化** 去掉 Git 图形备份功能（dispatch 配置不需要版本管理）

### 数据格式

```json
{
  "version": 1,
  "areas": [
    {
      "id": 1,
      "name": "区域1",
      "xmin": 2,
      "xmax": 4,
      "max_dispatch_once": 3,
      "servers": [
        {"ip": "10.68.2.31", "port": 7000, "name": "ICS-31"}
      ],
      "templates": {
        "incoming": [
          {"code": "DKCqu", "name": "调空车模板1去空车", "type": "empty_in"}
        ],
        "outgoing": [
          {"code": "DKCback", "name": "调空车模板1回空车", "type": "empty_out"}
        ]
      }
    }
  ]
}
```

### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dispatch/config` | 配置页面 |
| GET | `/api/dispatch/config` | 获取配置 JSON |
| POST | `/api/dispatch/config` | 保存配置 JSON |
| GET | `/api/dispatch/config/backups` | 列出备份（可选） |

### 实施步骤

1. 复制 `config_editor.html` → `dispatch/config.html`
2. 修改数据结构为 dispatch 格式
3. 修改 API 调用路径
4. 在 `dispatch_routes.py` 添加配置读写 API
5. 配置文件存储位置：`data/dispatch/config.json`
