# AGV日志拉取系统

这是一个为AGV系统设计的日志拉取工具集，用于从不同的日志源中拉取特定时间点的日志文件。

## 目录结构

```
agv_log_fetcher/
├── bin/                   # 脚本目录
│   ├── copy_all_log.sh    # 主脚本 - 统一入口
│   ├── copy_tps_log.sh    # TPS日志拉取脚本
│   ├── copy_rtps_log.sh   # RTPS算法日志拉取脚本
│   ├── copy_ics_log.sh    # ICS日志拉取脚本
│   └── copy_fywds_log.sh  # FYWDS日志拉取脚本
├── alllog/                # 拉取的日志存储目录
│   └── (拉取的日志文件)
├── docs/                  # 文档目录
│   └── LOG_FORMAT.md      # 日志格式说明
├── examples/              # 使用示例目录
│   └── USAGE_EXAMPLE.md   # 使用示例文档
├── conf/                  # 配置文件目录
│   └── config.example.sh  # 配置示例文件
└── README.md              # 本文件
```

## 功能概述

### 1. 支持的日志类型

1. **TPS日志** - Task Planning System（任务规划系统）日志
2. **RTPS日志** - Real-Time Planning System（实时规划系统）算法日志
3. **ICS日志** - Inter-Control System（内部控制系统）日志
4. **FYWDS日志** - FYWDS系统日志

### 2. 脚本说明

#### 主脚本：`copy_all_log.sh`
统一的入口脚本，支持多种日志类型拉取。

**用法：**
```bash
./copy_all_log.sh <日志类型> [区域号] <时间戳>
```

**可用日志类型：**
- `tps` - 拉取TPS日志
- `rtps` - 拉取RTPS算法日志（需要区域号参数）
- `ics` - 拉取ICS日志
- `fywds` - 拉取FYWDS日志
- `all` - 批量拉取所有类型日志

**示例：**
```bash
# 拉取TPS日志
./copy_all_log.sh tps 20260401_1010

# 拉取RTPS算法日志（区域4）
./copy_all_log.sh rtps 20260401_1010 4

# 拉取ICS日志
./copy_all_log.sh ics 20260401_1010

# 拉取FYWDS日志
./copy_all_log.sh fywds 20260401_1010

# 批量拉取所有日志
./copy_all_log.sh all 20260401_1010

# 批量拉取所有日志（指定区域6）
./copy_all_log.sh all 20260401_1010 6
```

#### TPS日志脚本：`copy_tps_log.sh`
拉取TPS日志的专用脚本。

**用法：**
```bash
./copy_tps_log.sh <时间戳>
```

**示例：**
```bash
./copy_tps_log.sh 20260401_1024
```

**日志文件命名规则：**
```
YYYYMMDD_HHMM_TPS.log
```

**查找策略：**
1. 首先检查 `TPS.log` 文件
2. 如果不存在，检查分片日志文件 `TPS-YYYY-MM-DD.N.log`
3. 根据时间范围确定包含目标时间戳的文件

#### RTPS算法日志脚本：`copy_rtps_log.sh`
拉取RTPS算法日志的专用脚本，需要区域号参数。

**用法：**
```bash
./copy_rtps_log.sh <区域号> <时间戳>
```

**示例：**
```bash
./copy_rtps_log.sh 4 20260401_1010
```

**查找策略：**
1. 根据区域号查找对应的 `rtpsa-*` 和 `rtpsp-*` 文件夹
2. 在 `TAL_log` 目录中查找TAL调度日志
3. 在 `logs` 目录中查找rtps日志
4. 在 `DPL_log` 目录中查找DPL日志

#### ICS日志脚本：`copy_ics_log.sh`
拉取ICS日志的专用脚本。

**用法：**
```bash
./copy_ics_log.sh <时间戳>
```

**示例：**
```bash
./copy_ics_log.sh 20260401_1000
```

**日志文件命名规则：**
```
YYYYMMDD_HHMM_ICS.log
```

#### FYWDS日志脚本：`copy_fywds_log.sh`
拉取FYWDS日志的专用脚本。

**用法：**
```bash
./copy_fywds_log.sh <时间戳>
```

**示例：**
```bash
./copy_fywds_log.sh 20260401_1000
```

**日志文件命名规则：**
```
YYYYMMDD_HHMM_FYWDS.log
```

**查找策略：**
1. 首先检查 `FYWDS.log` 文件
2. 如果不存在，检查分片日志文件 `FYWDS-YYYY-MM-DD.N.log`
3. 根据时间范围确定包含目标时间戳的文件

## 配置文件说明

所有脚本使用硬编码的目录路径，可以根据实际情况进行修改：

### 日志源目录
- **TPS日志目录**: `/main/app/tps/logs`
- **ICS日志目录**: `/main/app/ics/logs`
- **FYWDS日志目录**: `/main/app/fywds/logs`
- **RTPS日志根目录**: `/main/app/`

### 目标目录
- **所有拉取日志的存储目录**: `/home/ymsk/alllog`

### RTPS文件夹命名规则
- **rtpsa-***: RTPS算法文件夹，包含区域列表（如 `rtpsa-4,5,6,8,16,17,18`）
- **rtpsp-***: RTPS规划文件夹，包含单个区域（如 `rtpsp-4` 或 `rtpsp-16`）

## 参数格式

### 时间戳格式
所有脚本使用统一的时间戳格式：
```
YYYYMMDD_HHMM
```

**示例：**
- `20260401_1010` - 2026年4月1日 10:10
- `20260402_1430` - 2026年4月2日 14:30

### 区域号格式
- 纯数字格式
- 支持多位数字
- 示例：`4`, `16`, `18`

## 输出文件命名规则

脚本会根据日志类型和时间戳自动生成输出文件名：

### TPS日志
```
YYYYMMDD_HHMM_TPS.log
```

### ICS日志
```
YYYYMMDD_HHMM_ICS.log
```

### FYWDS日志
```
YYYYMMDD_HHMM_FYWDS.log
```

### RTPS日志
- **TAL调度日志**: `YYYYMMDD_HHMM_rtpsa_区域列表_TAL.log[.zip]`
- **rtps日志**: `YYYYMMDD_HHMM_区域列表_rtps.log[.gz]`
- **DPL日志**: `YYYYMMDD_HHMM_rtpsp_区域号_DPL.log[.gz]`

**示例：**
```
20260401_1010_rtpsa_4,5,6,8,16,17,18_TAL.log.zip
20260401_1010_4,5,6,8,16,17,18_rtps.log.gz
20260401_1010_rtpsp_4_DPL.log.gz
20260401_1010_FYWDS.log
```

## 错误处理

所有脚本都包含错误处理逻辑：
1. 参数验证失败会显示详细错误信息
2. 文件不存在或权限问题会有明确提示
3. 时间解析失败会显示具体原因
4. 在批处理模式下，单个脚本失败不会影响其他脚本执行

## 使用建议

1. **初次使用**：建议先使用 `copy_all_log.sh` 主脚本，它有更友好的用户界面和错误提示
2. **批量处理**：如果需要同时拉取多种类型的日志，使用 `all` 参数
3. **单个类型**：如果只需要特定类型的日志，直接使用对应的脚本或主脚本的类型参数
4. **调试**：如果遇到问题，可以首先检查参数格式是否正确，然后检查相关目录是否存在

## 环境要求

- **操作系统**: Linux
- **Shell**: Bash
- **系统工具**: `date`, `head`, `tail`, `grep`, `sed`, `awk`, `stat`, `basename`, `dirname`
- **权限**: 需要读取日志源目录的权限和写入目标目录的权限

## 常见问题

### 1. 为什么脚本执行失败？
可能的原因：
- 参数格式不正确（检查时间戳格式）
- 日志源目录不存在
- 目标目录没有写入权限
- 相关系统工具未安装

### 2. 如何查看更详细的错误信息？
所有脚本都包含详细的日志输出，会显示每个步骤的执行结果。

### 3. 如何修改日志目录？
直接编辑脚本文件，修改对应的 `LOG_DIR` 和类似变量。

### 4. 如何添加新的日志类型？
1. 创建新的专用脚本（参照现有脚本格式）
2. 在主脚本 `copy_all_log.sh` 中添加新的类型处理逻辑
3. 更新README文档

## 维护说明

- 本项目基于现有的日志拉取脚本进行重构和整合
- 所有原始脚本功能保持不变，只是增加了统一的入口和管理
- 建议使用主脚本进行日常操作，专用脚本用于特殊情况或调试

## 版本历史

### v1.1 (2026-04-03)
- 添加FYWDS日志支持
- 创建 `copy_fywds_log.sh` 脚本
- 更新主脚本 `copy_all_log.sh` 支持fywds类型
- 更新文档和示例

### v1.0 (2026-04-02)
- 统一现有分散的日志拉取脚本
- 创建主脚本 `copy_all_log.sh` 作为统一入口
- 整理项目目录结构
- 创建详细的使用文档
- 保持向后兼容性，原始脚本均可独立使用