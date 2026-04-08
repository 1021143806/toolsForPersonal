#!/bin/bash

# 路径辅助函数
# 用于处理跨平台路径问题（WSL/Windows）

# 获取脚本所在目录的绝对路径
get_script_dir() {
    local script_path="$0"
    local script_dir=""
    
    # 尝试不同方法获取脚本真实路径
    if [ -L "$script_path" ]; then
        # 如果是符号链接
        script_dir="$(dirname "$(readlink -f "$script_path" 2>/dev/null || readlink "$script_path" 2>/dev/null)")"
    else
        # 更健壮的方法：先检查目录是否存在
        local dir_part="$(dirname "$script_path")"
        if [ -d "$dir_part" ]; then
            script_dir="$(cd "$dir_part" && pwd -P 2>/dev/null)"
        fi
        
        # 如果上述方法失败，尝试使用BASH_SOURCE（如果可用）
        if [ -z "$script_dir" ] && [ -n "${BASH_SOURCE[0]}" ]; then
            script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P 2>/dev/null)"
        fi
        
        # 如果仍然失败，使用当前目录
        if [ -z "$script_dir" ]; then
            script_dir="$(pwd -P)"
        fi
    fi
    
    echo "$script_dir"
}

# 获取项目根目录（所有脚本共享的alllog目录）
get_project_root() {
    local script_dir=$(get_script_dir)
    # bin目录上一层是项目根目录
    echo "$(dirname "$script_dir")"
}

# 获取alllog目录路径（相对路径）
get_alllog_dir() {
    local project_root=$(get_project_root)
    echo "$project_root/alllog"
}

# 验证和创建目录
ensure_dir() {
    local dir_path="$1"
    if [ ! -d "$dir_path" ]; then
        mkdir -p "$dir_path" || {
            echo "错误：无法创建目录 $dir_path"
            return 1
        }
        echo "创建目录: $dir_path"
    fi
    return 0
}

# 获取目标目录路径
get_target_dir() {
    local timestamp="$1"
    local alllog_dir=$(get_alllog_dir)
    echo "$alllog_dir/$timestamp"
}

# 根据日志类型和目标时间生成输出文件名
get_output_filename() {
    local timestamp="$1"
    local log_type="$2"  # tps, ics, rtps等
    local area="${3:-}"   # 区域号（可选）
    
    case "$log_type" in
        "tps")
            echo "${timestamp}_TPS.log"
            ;;
        "ics")
            echo "${timestamp}_ICS.log"
            ;;
        "rtps")
            if [ -n "$area" ]; then
                echo "${timestamp}_RTPS_${area}.log"
            else
                echo "${timestamp}_RTPS.log"
            fi
            ;;
        *)
            echo "${timestamp}_${log_type}.log"
            ;;
    esac
}

# 复制文件到alllog目录
copy_to_alllog() {
    local source_file="$1"
    local timestamp="$2"
    local log_type="$3"
    local area="${4:-}"
    
    if [ ! -f "$source_file" ]; then
        echo "错误：源文件不存在: $source_file"
        return 1
    fi
    
    # 获取目标目录和文件名
    local target_dir=$(get_target_dir "$timestamp")
    local output_filename=$(get_output_filename "$timestamp" "$log_type" "$area")
    local target_path="$target_dir/$output_filename"
    
    # 创建目录
    if ! ensure_dir "$target_dir"; then
        return 1
    fi
    
    # 复制文件
    echo "复制文件: $(basename "$source_file") -> $output_filename"
    if cp "$source_file" "$target_path"; then
        echo "文件保存到: $target_path"
        
        # 显示文件信息
        if [ -f "$target_path" ]; then
            file_size=$(ls -lh "$target_path" | awk '{print $5}')
            echo "文件大小: $file_size"
        fi
        return 0
    else
        echo "错误：文件复制失败"
        return 1
    fi
}

# 验证时间戳格式
validate_timestamp() {
    local timestamp="$1"
    local log_type="$2"
    
    if ! [[ "$timestamp" =~ ^[0-9]{8}_[0-9]{4}$ ]]; then
        echo "$log_type时间戳格式错误，应为YYYYMMDD_HHMM（如20260401_1010）"
        return 1
    fi
    
    # 解析时间戳
    local date_part=$(echo "$timestamp" | cut -d'_' -f1)
    local time_part=$(echo "$timestamp" | cut -d'_' -f2)
    
    # 验证日期有效性
    if ! date -d "${date_part:0:4}-${date_part:4:2}-${date_part:6:2}" >/dev/null 2>&1; then
        echo "$log_type无效的日期: $date_part"
        return 1
    fi
    
    # 验证时间有效性
    local hour=${time_part:0:2}
    local minute=${time_part:2:2}
    if [ "$hour" -gt 23 ] || [ "$minute" -gt 59 ]; then
        echo "$log_type无效的时间: ${hour}:${minute}"
        return 1
    fi
    
    return 0
}

# 显示alllog目录内容
show_alllog_contents() {
    local timestamp="$1"
    local alllog_dir=$(get_alllog_dir)
    local target_dir="$alllog_dir/$timestamp"
    
    echo ""
    echo "alllog目录结构:"
    find "$alllog_dir" -type f -name "*.log" -o -name "*.gz" -o -name "*.zip" | sort
    
    if [ -n "$timestamp" ]; then
        echo ""
        echo "目标目录: $target_dir"
        if [ -d "$target_dir" ]; then
            echo "目录内容:"
            ls -lh "$target_dir/" 2>/dev/null || echo "目录为空"
        fi
    fi
}