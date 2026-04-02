# AGV 系统数据库同步脚本

本目录包含用于 AGV 系统数据库同步的 Python 脚本集合，主要用于在不同数据库服务器之间同步设备信息。

## 项目结构

```
python快捷处理sql脚本/
├── 自动同步同一型号设备.py          # 主脚本：同步指定型号的 AGV 设备
├── 自动同步设备脚本.py              # 统一配置脚本：集中配置并调用其他脚本
├── function/                       # 功能模块目录
│   ├── copy_robot.py              # 可配置的设备同步脚本（支持命令行参数）
│   ├── add_device_ext.py          # 设备扩展表同步工具
│   └── quick.sh                   # 快速使用示例脚本
└── readme.md                      # 本文档
```

## 功能概述

### 1. 自动同步同一型号设备 (`自动同步同一型号设备.py`)
**功能**：从源数据库查询指定设备类型（如 `RTA-C060-Q-2L-410`）的所有记录，去除 ID 字段后插入到目标数据库。

**特点**：
- 使用 `INSERT IGNORE` 避免主键/唯一键冲突
- 自动跳过重复记录
- 输出成功插入和跳过的记录数

**配置方式**：直接修改脚本中的数据库连接配置

### 2. 自动同步设备脚本 (`自动同步设备脚本.py`)
**功能**：统一配置参数，自动调用 `copy_robot.py` 和 `add_device_ext.py` 完成完整的设备同步流程。

**特点**：
- 集中配置所有参数，避免重复输入
- 支持选择性启用/禁用不同同步任务
- 交互式确认执行，提高安全性
- 详细的执行日志和错误处理

**配置方式**：修改脚本顶部的配置变量

### 3. 可配置设备同步脚本 (`function/copy_robot.py`)
**功能**：功能与主脚本相同，但支持完整的命令行参数配置。

**特点**：
- 支持命令行参数指定源/目标数据库
- 可自定义设备类型、表名等参数
- 模块化设计，便于集成

**使用方法**：
```bash
python copy_robot.py --source-host 10.68.2.32 --source-password CCshenda889 \
                     --target-host 10.68.2.40 --target-password CCshenda889 \
                     --device-type "RTA-C060-Q-2L-410" --table agv_robot
```

### 4. 设备扩展表同步工具 (`function/add_device_ext.py`)
**功能**：根据设备组名称同步设备扩展信息，并可修改目标区域。

**特点**：
- 基于设备组进行批量同步
- 可修改 `DEVICE_AREA` 为目标区域值
- 支持复杂的数据库查询（涉及多个表关联）

**使用方法**：
```bash
python add_device_ext.py --source-host 10.68.2.27 --source-password CCshenda889 \
                         --target-host 10.68.2.40 --target-password CCshenda889 \
                         --group-name "所有四代车脚本用" --target-area 3
```

### 5. 快速使用脚本 (`function/quick.sh`)
**功能**：提供常用命令的快速执行示例。

## 环境要求

- Python 3.6+
- 依赖包：
  - `pymysql` (MySQL 数据库连接)

安装依赖：
```bash
pip install pymysql
```

## 数据库配置

### 默认配置
脚本中使用的默认数据库配置：
- **用户名**：`wms`
- **密码**：`CCshenda889`
- **数据库**：`wms`
- **字符集**：`utf8mb4`
- **端口**：`3306`

### 涉及的表结构

#### agv_robot 表（设备主表）
包含设备基本信息，如：
- `DEVICE_CODE` (设备编码)
- `DEVICE_IP` (设备IP)
- `DEVICETYPE` (设备类型)
- `CAPACITIES` (容量)
- 等18个字段（不含自增ID）

#### agv_robot_ext 表（设备扩展表）
包含设备扩展信息，如：
- `DEVICE_CODE` (设备编码)
- `DEVICE_AREA` (设备区域)
- `DEVICE_NUMBER` (设备编号)
- `DEVICE_STATUS` (设备状态)
- 等7个字段（不含自增ID）

#### agv_robot_group 表（设备组表）
- `id` (组ID)
- `group_name` (组名称)

#### agv_robot_group_detail 表（设备组详情表）
- `group_id` (组ID)
- `device_code` (设备编码)
- `device_number` (设备编号)

## 使用示例

### 示例1：使用统一配置脚本（推荐）
```bash
# 1. 修改 自动同步设备脚本.py 顶部的配置参数
# 2. 运行脚本
python 自动同步设备脚本.py

# 脚本会显示当前配置并询问是否继续
# 输入 y 确认执行，将自动调用 copy_robot.py 和 add_device_ext.py
```

### 示例2：同步特定型号设备
```bash
# 使用主脚本（需先修改配置）
python 自动同步同一型号设备.py

# 使用可配置脚本
python function/copy_robot.py \
  --source-host 10.68.2.32 \
  --source-password CCshenda889 \
  --target-host 10.68.2.40 \
  --target-password CCshenda889 \
  --device-type "RTA-C060-Q-2L-410"
```

### 示例3：同步设备组扩展信息
```bash
python function/add_device_ext.py \
  --source-host 10.68.2.27 \
  --source-password CCshenda889 \
  --target-host 10.68.2.40 \
  --target-password CCshenda889 \
  --group-name "点胶4代车" \
  --target-area 3
```

### 示例4：查看帮助信息
```bash
python function/copy_robot.py -h
python function/add_device_ext.py -h
```

## 脚本执行流程

### 统一配置脚本流程（自动同步设备脚本.py）
1. 读取顶部配置参数
2. 显示当前配置供用户确认
3. 检查脚本文件是否存在
4. 询问用户是否继续执行
5. 按顺序调用 `copy_robot.py` 和 `add_device_ext.py`
6. 输出执行结果汇总

### 设备同步流程（copy_robot.py）
1. 连接源数据库
2. 查询指定设备类型的记录
3. 连接目标数据库
4. 构造 `INSERT IGNORE` 语句
5. 逐条插入数据（跳过重复记录）
6. 输出统计结果

### 设备扩展同步流程（add_device_ext.py）
1. 根据组名查询组ID
2. 查询组内所有设备编码
3. 查询设备扩展信息
4. 修改 `DEVICE_AREA` 为目标区域
5. 插入到目标数据库（跳过重复记录）

## 错误处理

- **数据库连接失败**：脚本会捕获异常并输出错误信息
- **重复记录**：使用 `INSERT IGNORE` 自动跳过，不会中断执行
- **数据格式错误**：捕获异常，回滚当前事务，继续处理下一条记录
- **参数错误**：命令行参数解析失败时会显示帮助信息
- **脚本文件不存在**：统一配置脚本会检查子脚本是否存在
- **用户取消**：统一配置脚本支持交互式确认，用户可随时取消

## 注意事项

1. **权限要求**：执行脚本的用户需要对源数据库有 SELECT 权限，对目标数据库有 INSERT 权限
2. **网络连通性**：确保可以访问源和目标数据库服务器
3. **数据一致性**：同步过程中不会删除或修改现有数据，只进行增量添加
4. **ID 字段处理**：所有同步操作都会去除自增 ID 字段，由目标数据库自动生成新 ID
5. **字符集**：确保源和目标数据库使用相同的字符集（默认 `utf8mb4`）
6. **配置验证**：使用统一配置脚本前，请仔细检查顶部配置参数

## 常见问题

### Q1: 执行时出现 "ModuleNotFoundError: No module named 'pymysql'"
**解决**：安装 pymysql 模块：`pip install pymysql`

### Q2: 数据库连接失败
**解决**：
1. 检查网络连通性
2. 验证数据库连接参数（主机、端口、用户名、密码）
3. 确认防火墙设置

### Q3: 同步后数据重复
**解决**：脚本使用 `INSERT IGNORE`，重复记录会自动跳过。如需强制更新，需要先手动删除目标表中的重复记录。

### Q4: 如何同步其他设备类型？
**解决**：修改 `--device-type` 参数或脚本中的 `DEVICE_TYPE` 常量

### Q5: 统一配置脚本如何只执行一个任务？
**解决**：在 `自动同步设备脚本.py` 中设置 `COPY_ROBOT_ENABLED = False` 或 `ADD_DEVICE_EXT_ENABLED = False` 来禁用不需要的任务

## 扩展与定制

### 添加新的同步功能
1. 参考现有脚本结构创建新脚本
2. 使用 `argparse` 模块支持命令行参数
3. 遵循统一的错误处理模式
4. 在 `quick.sh` 中添加使用示例
5. 在 `自动同步设备脚本.py` 中添加对应的调用函数

### 修改字段映射
如需同步不同的表或字段，需要修改：
1. `TARGET_FIELDS` 列表（定义目标字段顺序）
2. 查询 SQL 语句
3. 插入 SQL 语句

### 自定义统一配置脚本
`自动同步设备脚本.py` 采用模块化设计，可以：
1. 添加新的配置参数
2. 添加新的任务调用函数
3. 修改执行顺序
4. 增强错误处理和日志记录

## 版本历史

- **v1.0**：基础设备同步功能
- **v1.1**：增加命令行参数支持
- **v1.2**：增加设备扩展表同步功能
- **v1.3**：优化错误处理和日志输出
- **v1.4**：新增统一配置脚本 `自动同步设备脚本.py`

## 维护者

- AGV 系统开发团队
- 如有问题，请联系相关开发人员

---

**重要提示**：执行数据库操作前，建议先在测试环境验证脚本功能，确保数据安全。

**推荐使用流程**：
1. 首次使用建议先阅读本文档
2. 使用 `自动同步设备脚本.py` 进行统一配置和管理
3. 执行前仔细检查配置参数
4. 先在测试环境验证，再在生产环境使用