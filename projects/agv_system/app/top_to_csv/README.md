# Top日志解析工具

这是一个用于解析top命令输出日志的Python脚本，将日志转换为CSV格式，便于分析和可视化。

## 功能特性

- 解析多设备top日志文件
- 提取关键系统指标：
  - CPU使用率（100 - idle）
  - 内存使用率（used/total）
  - 交换空间使用率
  - 系统负载（1min, 5min, 15min）
  - I/O等待时间
  - 任务统计
- 自动识别连接成功和失败的设备
- 生成结构化的CSV文件
- 提供统计摘要

## 文件结构

```
top_to_csv/
├── top_to_csv.py          # 主解析脚本
├── README.md              # 本文档
├── top_out/               # 输入日志目录（示例）
│   └── top_20260403_140256.log
└── csv_out/               # 输出CSV目录（自动创建）
    └── top_20260403_140256.csv
```

## 安装要求

- Python 3.6+
- 无需额外依赖包

## 使用方法

### 基本用法

```bash
python3 top_to_csv.py <输入日志文件> [输出CSV文件]
```

### 示例

```bash
# 使用默认输出路径
python3 top_to_csv.py top_out/top_20260403_140256.log

# 指定输出文件
python3 top_to_csv.py top_out/top_20260403_140256.log my_analysis.csv

# 使用相对路径
python3 top_to_csv.py ../other_logs/top.log
```

### 输出示例

```
开始解析文件: top_out/top_20260403_140256.log
解析完成: 共 27 个设备
  - 成功: 10 个
  - 失败: 17 个
CSV文件已保存: csv_out/top_20260403_140256.csv
共处理 27 条记录

成功设备的统计信息:
  - 平均CPU使用率: 23.6%
  - 平均内存使用率: 55.4%
  - 最高CPU使用率: 99.0% (IP: 10.68.2.3)
  - 最高内存使用率: 85.6% (IP: 10.68.2.40)
```

## CSV字段说明

| 字段名 | 说明 | 示例 |
|--------|------|------|
| timestamp | 采集时间戳 | Fri Apr  3 14:02:56 CST 2026 |
| ip | 设备IP地址 | 10.68.2.3 |
| status | 连接状态（success/failed） | success |
| cpu_usage | CPU使用率百分比 | 99.0 |
| mem_usage | 内存使用率百分比 | 84.2 |
| swap_usage | 交换空间使用率百分比 | 100.0 |
| mem_total_mb | 内存总量（MB） | 31951.05 |
| mem_used_mb | 已用内存（MB） | 26901.85 |
| mem_free_mb | 空闲内存（MB） | 1889.36 |
| swap_total_mb | 交换空间总量（MB） | 8192.0 |
| swap_used_mb | 已用交换空间（MB） | 8192.0 |
| load_1min | 1分钟系统负载 | 16.48 |
| load_5min | 5分钟系统负载 | 10.68 |
| load_15min | 15分钟系统负载 | 9.02 |
| io_wait | I/O等待百分比 | 2.5 |
| tasks_total | 总任务数 | 286 |
| tasks_running | 运行中任务数 | 1 |
| tasks_sleeping | 睡眠任务数 | 283 |
| uptime | 系统运行时间 | 1213 days |
| users | 登录用户数 | 0 |
| error_message | 错误信息（仅失败时） | Permission denied... |

## 输入日志格式

脚本支持以下格式的日志文件：

### 设备分隔格式
```
========== 10.68.2.1 at Fri Apr  3 14:02:56 CST 2026 ==========
Permission denied, please try again.
错误：连接超时（1秒）或认证失败，已跳过

========== 10.68.2.3 at Fri Apr  3 14:02:56 CST 2026 ==========
top - 14:13:03 up 1213 days,  2:50,  0 users,  load average: 16.48, 10.68, 9.02
Tasks: 286 total,   1 running, 283 sleeping,   1 stopped,   1 zombie
%Cpu(s): 90.8 us,  5.7 sy,  0.0 ni,  1.0 id,  2.5 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem : 32717872 total,  1934708 free, 27547496 used,  3235668 buff/cache
KiB Swap:  8388604 total,        0 free,  8388604 used.  3085868 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
25462 ymsk      20   0   11.8g   2.4g   4716 S 705.9  7.6  44193,21 java
```

### 支持的内存单位
- KiB（自动转换为MB）
- MiB（直接使用）
- GiB（自动转换为MB）

## 算法说明

### CPU使用率计算
```
CPU使用率 = 100 - idle百分比
```
其中idle从`%Cpu(s): ... id, ...`字段提取

### 内存使用率计算
```
内存使用率 = (used / total) × 100%
```
自动处理不同单位（KiB/MiB/GiB）的转换

### 状态判断
- **success**: 包含完整的top输出
- **failed**: 包含"Permission denied"或"连接超时"等错误信息

## 使用场景

### 1. 批量设备监控分析
解析从多台设备采集的top日志，快速了解整体系统状态。

### 2. 性能问题排查
通过CSV数据筛选高CPU/内存使用率的设备，定位性能瓶颈。

### 3. 历史数据对比
将不同时间点的日志解析为CSV，进行趋势分析。

### 4. 自动化报告生成
结合其他工具（如pandas, Excel）生成可视化报告。

## 扩展功能

### 自定义输出字段
修改`TopLogParser.save_to_csv()`方法中的`fieldnames`列表，调整输出字段。

### 添加进程信息
如需提取进程级别的信息，可扩展`parse_section()`方法，解析进程列表。

### 批量处理
创建批处理脚本，自动处理多个日志文件：

```bash
#!/bin/bash
for log_file in top_out/*.log; do
    python3 top_to_csv.py "$log_file"
done
```

## 故障排除

### 常见问题

1. **文件不存在错误**
   ```
   错误：输入文件不存在 - top_out/missing.log
   ```
   检查文件路径是否正确。

2. **解析失败**
   ```
   警告：没有解析到任何数据
   ```
   检查日志文件格式是否符合要求。

3. **编码问题**
   脚本使用UTF-8编码，如遇编码错误可尝试：
   ```python
   with open(file_path, 'r', encoding='gbk') as f:  # 或其他编码
   ```

### 调试模式
如需查看详细解析过程，可在脚本中添加调试输出：

```python
import pprint
pprint.pprint(result)  # 在parse_section()末尾添加
```

## 版本历史

### v1.0 (2026-04-03)
- 初始版本
- 支持基本top日志解析
- 生成包含CPU、内存、负载等指标的CSV

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request改进本工具。