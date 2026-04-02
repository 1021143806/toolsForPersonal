# AGV日志拉取工具使用示例

本文档提供AGV日志拉取工具的典型使用示例和场景。

## 基本使用示例

### 示例1：快速拉取TPS日志
```bash
# 进入脚本目录
cd /main/app/mntc/git/toolsForPersonal/projects/agv_system/app/agv_log_fetcher/bin

# 拉取2026年4月1日10:10的TPS日志
./copy_all_log.sh tps 20260401_1010
```

### 示例2：拉取RTPS算法日志（区域4）
```bash
# 拉取区域4在2026年4月1日11:09的RTPS算法日志
./copy_all_log.sh rtps 4 20260401_1109
```

### 示例3：拉取ICS日志
```bash
# 拉取2026年4月1日09:45的ICS日志
./copy_all_log.sh ics 20260401_0945
```

### 示例4：批量拉取所有日志
```bash
# 批量拉取2026年4月1日10:24的所有类型日志（默认区域4）
./copy_all_log.sh all 20260401_1024

# 批量拉取2026年4月1日10:24的所有类型日志（指定区域6）
./copy_all_log.sh all 20260401_1024 6
```

## 常见问题排查场景

### 场景1：排查TPS任务规划问题

当TPS任务规划出现问题时，可以按以下步骤收集日志：

```bash
# 1. 定位问题发生的大致时间（如2026年4月1日10:15左右）
TIMESTAMP="20260401_1015"

# 2. 拉取TPS日志
./copy_all_log.sh tps $TIMESTAMP

# 3. 检查拉取到的日志文件
ls -lh /home/ymsk/alllog/${TIMESTAMP}_TPS.log
```

**分析要点：**
- 查看ERROR级别的日志
- 查看任务开始和结束时间
- 查看任务执行过程中的状态变化

### 场景2：排查RTPS算法异常

当AGV路径规划或避障算法出现问题时：

```bash
# 1. 确定发生问题的区域（如区域4）
AREA="4"
TIMESTAMP="20260401_1109"

# 2. 拉取RTPS算法日志
./copy_all_log.sh rtps $AREA $TIMESTAMP

# 3. 检查所有相关日志
ls -lh /home/ymsk/alllog/${TIMESTAMP}_rtps*.log*
```

**分析要点：**
- 查看TAL调度日志，了解任务分配情况
- 查看rtps算法日志，了解路径计算过程
- 查看DPL调度日志，了解执行状态

### 场景3：排查ICS通信问题

当AGV与控制系统通信中断时：

```bash
# 1. 定位通信中断的时间点（如2026年4月1日09:30）
TIMESTAMP="20260401_0930"

# 2. 拉取ICS日志
./copy_all_log.sh ics $TIMESTAMP

# 3. 查看拉取的日志
cat /home/ymsk/alllog/${TIMESTAMP}_ICS.log | grep -i "error\|timeout\|disconnect"
```

**分析要点：**
- 查看设备连接状态
- 查看心跳超时情况
- 查看重连次数和成功率

### 场景4：综合问题排查

当问题涉及多个系统时，需要同时分析多种日志：

```bash
# 1. 定义问题时间点和区域
AREA="4"
TIMESTAMP="20260401_1030"

# 2. 批量拉取所有相关日志
./copy_all_log.sh all $TIMESTAMP $AREA

# 3. 列出所有拉取的日志
ls -lh /home/ymsk/alllog/*${TIMESTAMP}*.log*
```

**日志文件可能包括：**
- `${TIMESTAMP}_TPS.log` - TPS日志
- `${TIMESTAMP}_rtpsa_*_TAL.log` - TAL调度日志
- `${TIMESTAMP}_*_rtps.log` - RTPS算法日志
- `${TIMESTAMP}_rtpsp_${AREA}_DPL.log` - DPL调度日志
- `${TIMESTAMP}_ICS.log` - ICS日志

## 脚本单独使用示例

除了使用主脚本，也可以直接调用各个专用脚本：

### 直接使用TPS日志脚本
```bash
cd /main/app/mntc/git/toolsForPersonal/projects/agv_system/app/getlog/bin

# 使用专用脚本拉取TPS日志
./copy_tps_log.sh 20260401_1024
```

### 直接使用RTPS算法脚本
```bash
# 使用专用脚本拉取RTPS算法日志
./copy_rtps_log.sh 4 20260401_1010
```

### 直接使用ICS日志脚本
```bash
# 使用专用脚本拉取ICS日志
./copy_ics_log.sh 20260401_1000
```

## 高级使用技巧

### 1. 批量处理多个时间点

```bash
# 创建一个时间点列表
TIMESTAMPS=("20260401_1000" "20260401_1015" "20260401_1030" "20260401_1045")
AREA="4"

# 循环处理每个时间点
for TIMESTAMP in "${TIMESTAMPS[@]}"; do
    echo "处理时间点: $TIMESTAMP"
    ./copy_all_log.sh all $TIMESTAMP $AREA
    echo ""
done
```

### 2. 自动化日志收集脚本

创建自动化的日志收集脚本：

```bash
#!/bin/bash
# auto_collect_logs.sh - 自动收集AGV日志

set -e

# 配置参数
AREA="${1:-4}"
TIMESTAMP="${2:-$(date +"%Y%m%d_%H%M")}"
LOG_DIR="/home/ymsk/alllog"
SCRIPT_DIR="/main/app/mntc/git/toolsForPersonal/projects/agv_system/app/getlog/bin"

echo "开始自动收集AGV日志"
echo "区域: $AREA"
echo "时间戳: $TIMESTAMP"
echo "日志目录: $LOG_DIR"
echo ""

# 创建目录
mkdir -p "$LOG_DIR"

# 执行日志拉取
cd "$SCRIPT_DIR"

echo "1. 拉取TPS日志..."
./copy_all_log.sh tps "$TIMESTAMP" 2>/dev/null || echo "TPS日志拉取失败"

echo "2. 拉取RTPS算法日志..."
./copy_all_log.sh rtps "$AREA" "$TIMESTAMP" 2>/dev/null || echo "RTPS日志拉取失败"

echo "3. 拉取ICS日志..."
./copy_all_log.sh ics "$TIMESTAMP" 2>/dev/null || echo "ICS日志拉取失败"

echo ""
echo "日志收集完成！"

# 显示收集到的文件
echo "收集到的日志文件:"
find "$LOG_DIR" -name "*${TIMESTAMP}*" -type f | sort
```

### 3. 与其他工具集成

#### 结合grep进行快速搜索
```bash
# 拉取日志后立即搜索特定关键词
TIMESTAMP="20260401_1024"
./copy_all_log.sh tps $TIMESTAMP

# 在拉取的日志中搜索错误
grep -i "error\|fail\|timeout" /home/ymsk/alllog/${TIMESTAMP}_TPS.log
```

#### 结合less进行分页查看
```bash
# 使用less分页查看大型日志文件
less /home/ymsk/alllog/20260401_1024_TPS.log

# 在less中搜索：按下 `/` 然后输入搜索词
```

### 4. 定时自动收集

可以设置cron任务定期收集日志：

```crontab
# 每天凌晨1点收集前一天的关键时间点日志
0 1 * * * /main/app/mntc/git/toolsForPersonal/projects/agv_system/app/getlog/bin/auto_collect_logs.sh 4 $(date -d "yesterday" +"%Y%m%d_1000")

# 每小时的第10分钟收集当前时间日志
10 * * * * /main/app/mntc/git/toolsForPersonal/projects/agv_system/app/getlog/bin/auto_collect_logs.sh 4 $(date +"%Y%m%d_%H00")
```

## 故障排除

### 1. 常见错误及解决方法

**错误1：参数格式错误**
```
错误：时间戳格式错误，应为YYYYMMDD_HHMM（如20260401_1010）
```
**解决：** 检查时间戳格式，确保是8位日期+下划线+4位时间

**错误2：目录不存在**
```
错误：无法进入日志目录 /main/app/tps/logs
```
**解决：** 检查日志源目录是否存在，或修改脚本中的目录路径

**错误3：权限不足**
```
错误：无法创建目录 /home/ymsk/alllog
```
**解决：** 检查目标目录的写入权限

**错误4：找不到日志文件**
```
错误：未找到包含时间 2026-04-01 10:15:00 的日志文件
```
**解决：** 检查指定的时间点是否有对应的日志文件生成

### 2. 调试模式

如果要查看详细的执行过程，可以在脚本开头添加 `set -x`：

```bash
#!/bin/bash
set -x  # 启用调试模式
# 脚本内容...
```

或者在执行时启用bash的调试：

```bash
bash -x ./copy_all_log.sh tps 20260401_1010
```

## 最佳实践

1. **时间点选择**:
   - 选择问题明确发生的时间点
   - 如果时间不明确，可以收集问题前后几个时间点的日志

2. **区域号确认**:
   - 确认问题所在的AGV区域
   - 如果不确定，可以收集多个区域的日志

3. **日志保存**:
   - 定期清理旧的拉取日志
   - 重要问题的日志应归档保存
   - 使用统一的命名规范

4. **分析策略**:
   - 先看ERROR级别的日志
   - 注意日志的时间顺序
   - 结合多种日志综合分析