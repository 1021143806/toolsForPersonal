#!/bin/bash

# 用法：./copy_ics_log.sh 20260401_1000
# 此脚本支持多种ICS日志格式：
# 1. 标准格式：ICS.log 或 ICS-YYYY-MM-DD.N.log
# 2. 业务格式：ICS-BUSINESS.log 或 ICS-BUSINESS-YYYY-MM-DD.N.log
# 3. 其他变体格式

# 导入路径辅助函数
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/path_helpers.sh"

# 检测日志目录
detect_log_dir() {
    # 如果设置了环境变量，直接使用
    if [ -n "$ICS_LOG_DIR" ] && [ -d "$ICS_LOG_DIR" ]; then
        echo "$ICS_LOG_DIR"
        return 0
    fi
    
    # 尝试查找常见目录
    local possible_dirs=(
        "/main/app/ics/logs"
        "/main/app/ics-business/logs"
        "/main/app/ics/log"
        "./logs"
        "."
    )
    
    for dir in "${possible_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo "$dir"
            return 0
        fi
    done
    
    echo ""
    return 1
}

# 检查参数
if [ $# -ne 1 ]; then
    echo "用法: $0 时间参数 (格式: YYYYMMDD_HHMM)"
    echo ""
    echo "可选步骤："
    echo "1. 设置环境变量 ICS_LOG_DIR 指定日志目录"
    echo "2. 脚本会自动检测常见目录"
    exit 1
fi

param="$1"

# 验证时间戳
if ! validate_timestamp "$param" "ICS"; then
    exit 1
fi

# 解析日期和时间
IFS='_' read -r date_str hour_min <<< "$param"
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

# 检测日志目录
LOG_DIR=$(detect_log_dir)
if [ -z "$LOG_DIR" ]; then
    echo "错误：未找到ICS日志目录"
    echo "请检查以下目录是否存在："
    echo "- /main/app/ics/logs"
    echo "- /main/app/ics-business/logs"
    echo "- 或设置环境变量 ICS_LOG_DIR"
    exit 1
fi

echo "找到ICS日志目录: $LOG_DIR"

# 进入日志目录，如果失败则退出
echo "进入日志目录: $LOG_DIR"
if ! cd "$LOG_DIR" 2>/dev/null; then
    echo "错误：无法进入日志目录 $LOG_DIR，请检查路径权限"
    exit 1
fi

echo "开始搜索包含时间 $target_time 的ICS日志文件..."
echo "支持的日志格式："
echo "1. 标准格式: ICS.log 或 ICS-YYYY-MM-DD.N.log"
echo "2. 业务格式: ICS-BUSINESS.log 或 ICS-BUSINESS-YYYY-MM-DD.N.log"
echo "3. 其他变体: ICS-APP, ICS-SERVICE等"
echo ""

# 函数：检查日志文件是否包含目标时间
contains_time() {
    local file="$1"
    local max_lines_to_scan="${ICS_MAX_SCAN_LINES:-1000}"
    
    if [ ! -f "$file" ]; then
        return 1
    fi

    # 提取第一行和最后一行的日志时间
    local first_line last_line
    first_line=$(head -n1 "$file" 2>/dev/null)
    last_line=$(tail -n1 "$file" 2>/dev/null)
    if [ -z "$first_line" ] || [ -z "$last_line" ]; then
        return 1
    fi

    # 提取时间戳 - 支持多种格式：
    # 1. 标准格式: "2026-04-01 10:23:45"
    # 2. 带毫秒格式: "2026-04-01 10:23:45.123"
    # 3. 方括号格式: "[2026-04-01 10:23:45]"
    local first_time last_time
    first_time=$(echo "$first_line" | grep -oE '(^|\[|^[^ ]* )([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?)' | head -1 | sed 's/^\[//;s/\]$//')
    last_time=$(echo "$last_line" | grep -oE '(^|\[|^[^ ]* )([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?)' | head -1 | sed 's/^\[//;s/\]$//')
    
    if [ -z "$first_time" ] || [ -z "$last_time" ]; then
        # 如果在行首找不到，尝试在整个文件中查找更多样本
        local sample_lines=$(head -n "$max_lines_to_scan" "$file" 2>/dev/null | tail -10)
        first_time=$(echo "$sample_lines" | grep -oE '(^|\[|^[^ ]* )([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?)' | head -1 | sed 's/^\[//;s/\]$//')
        if [ -z "$first_time" ]; then
            return 1
        fi
    fi

    # 去掉毫秒部分
    first_time=$(echo "$first_time" | cut -d. -f1)
    last_time=$(echo "$last_time" | cut -d. -f1)

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

# 按顺序尝试不同的ICS日志格式
found=0

# 格式列表：基本格式在前，业务格式在后
ics_formats=("ICS" "ICS-BUSINESS" "ICS-APP" "ICS-SERVICE")

for format in "${ics_formats[@]}"; do
    echo "尝试查找格式: $format"
    
    # 检查单一文件
    if [ -f "${format}.log" ]; then
        echo "找到单一文件: ${format}.log"
        if contains_time "${format}.log"; then
            echo "文件包含目标时间 $target_time"
            if copy_to_alllog "${format}.log" "$param" "ics"; then
                echo "ICS日志拉取成功"
                found=1
                break
            else
                echo "ICS日志拷贝失败"
            fi
        else
            echo "文件 ${format}.log 不包含目标时间 $target_time"
        fi
    fi
    
    # 检查分片文件
    base_name="$format-${year}-${month}-${day}"
    # 获取当天所有分片文件字符串
    shard_files_str=$(ls ${base_name}.*.log 2>/dev/null | sort -t. -k3n 2>/dev/null | grep -E "^${base_name}\.[0-9]+\.log$" 2>/dev/null || echo "")
    
    if [ -n "$shard_files_str" ]; then
        echo "找到分片文件"
        found_in_shards=0
        
        # 将字符串拆分为单独文件处理
        while IFS= read -r file; do
            if [ -n "$file" ]; then
                echo "检查分片文件: $(basename "$file")"
                if contains_time "$file"; then
                    echo "找到合适的日志文件：$(basename "$file")"
                    if copy_to_alllog "$file" "$param" "ics"; then
                        echo "ICS日志拉取成功"
                        found=1
                        found_in_shards=1
                        break
                    else
                        echo "ICS日志拷贝失败"
                    fi
                fi
            fi
        done <<< "$shard_files_str"
        
        if [ $found_in_shards -eq 1 ]; then
            break
        else
            echo "所有分片文件都不包含目标时间"
        fi
    else
        echo "未找到 ${format} 的分片文件"
    fi
    
    echo ""
done

echo ""
if [ $found -eq 0 ]; then
    echo "错误：未找到包含时间 $target_time 的ICS日志文件"
    echo "已检查以下格式: ${ics_formats[*]}"
    
    # 显示目录中的实际文件，帮助调试
    echo ""
    echo "当前目录文件列表:"
    ls -la *.log 2>/dev/null | head -20 || echo "没有找到日志文件"
    echo ""
    echo "当天相关的分片文件:"
    ls *${year}-${month}-${day}*.log 2>/dev/null || echo "没有当天文件"
    
    exit 1
fi

echo "ICS日志拉取成功完成"

# 显示alllog目录内容
show_alllog_contents "$param"