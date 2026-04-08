#!/bin/bash

# 脚本名称：copy_tps_log.sh
# 功能：根据时间参数从 TPS 日志中拉取包含该时间点的日志文件
# 用法：./copy_tps_log.sh 20260401_1010

# 导入路径辅助函数
# 更健壮的方法获取脚本目录
if [ -n "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd 2>/dev/null)"
fi

# 如果BASH_SOURCE方法失败，尝试其他方法
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd 2>/dev/null)"
fi

# 如果仍然失败，使用当前目录
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(pwd)"
fi

# 导入路径辅助函数
if [ -f "$SCRIPT_DIR/path_helpers.sh" ]; then
    source "$SCRIPT_DIR/path_helpers.sh"
else
    echo "错误：找不到 path_helpers.sh 文件"
    echo "脚本目录: $SCRIPT_DIR"
    exit 1
fi

# TPS日志目录
LOG_DIR="/main/app/tps/logs"

# 检查参数
if [ $# -ne 1 ]; then
    echo "用法: $0 时间参数 (格式: YYYYMMDD_HHMM)"
    exit 1
fi

# 解析日期和时间
param="$1"
IFS='_' read -r date_str hour_min <<< "$param"
if [ -z "$date_str" ] || [ -z "$hour_min" ]; then
    echo "错误：参数格式不正确，应为 YYYYMMDD_HHMM"
    exit 1
fi

year=${date_str:0:4}
month=${date_str:4:2}
day=${date_str:6:2}
hour=${hour_min:0:2}
minute=${hour_min:2:2}

# 构造目标时间（精确到秒）
target_time="${year}-${month}-${day} ${hour}:${minute}:00"
target_epoch=$(date -d "$target_time" +%s 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "错误：无法解析目标时间 $target_time"
    exit 1
fi

# 验证时间戳
if ! validate_timestamp "$param" "TPS"; then
    exit 1
fi

# 进入日志目录
if ! cd "$LOG_DIR" 2>/dev/null; then
    echo "错误：无法进入日志目录 $LOG_DIR"
    exit 1
fi

echo "开始拉取TPS日志，时间: $target_time"

# 函数：检查日志文件是否包含目标时间
# 参数：文件路径，返回 0 表示包含，1 表示不包含
contains_time() {
    local file="$1"
    if [ ! -f "$file" ]; then
        return 1
    fi

    # 提取第一行和最后一行的日志时间（假设时间戳在行首，格式如 "2026-04-01 10:23:45"）
    local first_line last_line
    first_line=$(head -n1 "$file" 2>/dev/null)
    last_line=$(tail -n1 "$file" 2>/dev/null)
    if [ -z "$first_line" ] || [ -z "$last_line" ]; then
        return 1
    fi

    # 提取时间戳（使用正则匹配行首的日期时间）
    local first_time last_time
    first_time=$(echo "$first_line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
    last_time=$(echo "$last_line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
    if [ -z "$first_time" ] || [ -z "$last_time" ]; then
        return 1
    fi

    # 转换为 epoch 秒
    local first_epoch last_epoch
    first_epoch=$(date -d "$first_time" +%s 2>/dev/null)
    last_epoch=$(date -d "$last_time" +%s 2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$first_epoch" ] || [ -z "$last_epoch" ]; then
        return 1
    fi

    # 确保 first_epoch <= last_epoch（如果日志顺序相反则交换）
    if [ $first_epoch -gt $last_epoch ]; then
        local tmp=$first_epoch
        first_epoch=$last_epoch
        last_epoch=$tmp
    fi

    # 判断目标时间是否在区间内
    if [ $target_epoch -ge $first_epoch ] && [ $target_epoch -le $last_epoch ]; then
        return 0
    else
        return 1
    fi
}

# 1. 先检查 TPS.log
if contains_time "TPS.log"; then
    echo "找到日志文件：TPS.log"
    if copy_to_alllog "TPS.log" "$param" "tps"; then
        echo "TPS日志拉取成功"
        exit 0
    else
        echo "TPS日志拷贝失败"
        exit 1
    fi
fi

# 2. 检查当天的分片日志文件 TPS-YYYY-MM-DD.N.log
base_name="TPS-${year}-${month}-${day}"
found=0

# 获取当天所有分片文件，并按数字后缀排序
shard_files=$(ls ${base_name}.*.log 2>/dev/null | sort -t. -k3n)
if [ -z "$shard_files" ]; then
    echo "错误：未找到当天分片日志文件"
    exit 1
fi

for file in $shard_files; do
    if contains_time "$file"; then
        echo "找到日志文件：$file"
        if copy_to_alllog "$file" "$param" "tps"; then
            echo "TPS日志拉取成功"
            found=1
            break
        else
            echo "TPS日志拷贝失败"
        fi
    fi
done

if [ $found -eq 0 ]; then
    echo "错误：未找到包含时间 $target_time 的TPS日志文件"
    
    # 显示目录内容用于调试
    echo "当前目录文件列表:"
    ls -la *.log 2>/dev/null | head -10 || echo "没有找到日志文件"
    echo ""
    echo "当天相关的分片文件:"
    ls *${year}-${month}-${day}*.log 2>/dev/null || echo "没有当天文件"
    
    exit 1
fi

# 显示alllog目录内容
show_alllog_contents "$param"
