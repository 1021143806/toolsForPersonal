#!/bin/bash

# 用法：./copy_log2.sh 20260401_1000
# 日志目录（可修改为实际路径，或保持当前目录）
LOG_DIR="/main/app/ics/logs"

# 检查参数
if [ $# -ne 1 ]; then
    echo "用法: $0 时间参数 (格式: YYYYMMDD_HHMM)"
    exit 1
fi

param="$1"

# 解析日期和时间
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

# 目标目录和输出文件名
dest_dir="/home/ymsk/alllog"
output_file="${dest_dir}/${param}_ICS.log"

mkdir -p "$dest_dir" || { echo "无法创建目录 $dest_dir"; exit 1; }

# 进入日志目录，如果失败则退出
if ! cd "$LOG_DIR" 2>/dev/null; then
    echo "错误：无法进入日志目录 $LOG_DIR，请检查路径"
    exit 1
fi

# 函数：检查日志文件是否包含目标时间
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

# 1. 先检查 ICS.log
if contains_time "ICS.log"; then
    echo "找到日志文件：ICS.log"
    cp "ICS.log" "$output_file" && echo "已拷贝并重命名为 $output_file"
    exit 0
fi

# 2. 检查当天的分片日志文件 ICS-YYYY-MM-DD.N.log
base_name="ICS-${year}-${month}-${day}"
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
        cp "$file" "$output_file" && echo "已拷贝并重命名为 $output_file"
        found=1
        break
    fi
done

if [ $found -eq 0 ]; then
    echo "错误：未找到包含时间 $target_time 的日志文件"
    exit 1
fi
