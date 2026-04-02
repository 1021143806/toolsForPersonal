#!/bin/bash

# copy_rtps_log.sh - 拉取算法日志脚本
# 用法: copy_rtps_log.sh <区域号> <时间戳>
# 示例: copy_rtps_log.sh 4 20260401_1010

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示用法
show_usage() {
    echo "用法: $0 <区域号> <时间戳>"
    echo "示例: $0 4 20260401_1010"
    echo ""
    echo "参数说明:"
    echo "  区域号: 需要拉取日志的区域编号（如4,5,6等）"
    echo "  时间戳: 日志时间戳，格式为YYYYMMDD_HHMM（如20260401_1010）"
    exit 1
}

# 验证参数
validate_parameters() {
    if [ $# -ne 2 ]; then
        log_error "参数数量错误，需要2个参数"
        show_usage
    fi
    
    AREA="$1"
    TIMESTAMP="$2"
    
    # 验证区域号
    if ! [[ "$AREA" =~ ^[0-9]+$ ]]; then
        log_error "区域号必须是数字"
        exit 1
    fi
    
    # 验证时间戳格式
    if ! [[ "$TIMESTAMP" =~ ^[0-9]{8}_[0-9]{4}$ ]]; then
        log_error "时间戳格式错误，应为YYYYMMDD_HHMM（如20260401_1010）"
        exit 1
    fi
    
    # 解析时间戳
    DATE_PART=$(echo "$TIMESTAMP" | cut -d'_' -f1)
    TIME_PART=$(echo "$TIMESTAMP" | cut -d'_' -f2)
    
    # 验证日期有效性
    if ! date -d "${DATE_PART:0:4}-${DATE_PART:4:2}-${DATE_PART:6:2}" >/dev/null 2>&1; then
        log_error "无效的日期: $DATE_PART"
        exit 1
    fi
    
    log_info "参数验证通过: 区域=$AREA, 时间戳=$TIMESTAMP"
}

# 查找包含指定区域的rtpsa文件夹
find_rtpsa_folders() {
    local area="$1"
    local found_folders=()
    
    log_info "查找包含区域 $area 的rtpsa文件夹..."
    
    if [ ! -d "/main/app" ]; then
        log_error "/main/app 目录不存在"
        echo ""
        return 1
    fi
    
    # 查找所有rtpsa-开头的文件夹
    for folder in /main/app/rtpsa-*; do
        if [ -d "$folder" ]; then
            # 提取文件夹名中的区域列表
            folder_name=$(basename "$folder")
            # 格式如: rtpsa-4,5,6,8,16,17,18
            areas_list=$(echo "$folder_name" | sed 's/rtpsa-//')
            
            # 检查区域是否在列表中
            if echo ",$areas_list," | grep -q ",$area,"; then
                log_info "找到rtpsa文件夹: $folder_name (包含区域 $area)"
                found_folders+=("$folder")
            fi
        fi
    done
    
    if [ ${#found_folders[@]} -eq 0 ]; then
        log_warning "未找到包含区域 $area 的rtpsa文件夹"
    fi
    
    echo "${found_folders[@]}"
}

# 查找包含指定区域的rtpsp文件夹
find_rtpsp_folders() {
    local area="$1"
    local found_folders=()
    
    log_info "查找包含区域 $area 的rtpsp文件夹..."
    
    if [ ! -d "/main/app" ]; then
        log_error "/main/app 目录不存在"
        echo ""
        return 1
    fi
    
    # 查找所有rtpsp-开头的文件夹
    for folder in /main/app/rtpsp-*; do
        if [ -d "$folder" ]; then
            # 提取文件夹名中的区域号
            folder_name=$(basename "$folder")
            # 格式如: rtpsp-4 或 rtpsp-16
            folder_area=$(echo "$folder_name" | sed 's/rtpsp-//')
            
            # 检查区域是否匹配
            if [ "$folder_area" = "$area" ]; then
                log_info "找到rtpsp文件夹: $folder_name (区域 $area)"
                found_folders+=("$folder")
            fi
        fi
    done
    
    if [ ${#found_folders[@]} -eq 0 ]; then
        log_warning "未找到区域 $area 的rtpsp文件夹"
    fi
    
    echo "${found_folders[@]}"
}

# 从时间戳转换为可比较的时间格式
convert_timestamp_to_seconds() {
    local timestamp="$1"
    local date_part=$(echo "$timestamp" | cut -d'_' -f1)
    local time_part=$(echo "$timestamp" | cut -d'_' -f2)
    
    # 格式: YYYYMMDD HHMM
    local datetime="${date_part:0:4}-${date_part:4:2}-${date_part:6:2} ${time_part:0:2}:${time_part:2:2}:00"
    
    # 转换为秒
    date -d "$datetime" +%s 2>/dev/null || echo "0"
}

# 从日志文件名提取时间范围
extract_time_from_logfile() {
    local logfile="$1"
    local log_type="$2"  # "tal", "rtps", "dpl"
    
    case "$log_type" in
        "tal")
            # tal_log_202604011111_977.zip 格式
            if [[ "$logfile" =~ tal_log_([0-9]{8})([0-9]{4})_[0-9]+\.zip ]]; then
                local date_part="${BASH_REMATCH[1]}"
                local time_part="${BASH_REMATCH[2]}"
                echo "${date_part}_${time_part}"
            fi
            ;;
        "rtps")
            # rtps.log.20260219125337121.gz 格式
            if [[ "$logfile" =~ rtps\.log\.([0-9]{8})([0-9]{6})[0-9]+\.gz ]]; then
                local date_part="${BASH_REMATCH[1]}"
                local time_part="${BASH_REMATCH[2]:0:4}"  # 取前4位作为HHMM
                echo "${date_part}_${time_part}"
            fi
            ;;
        "dpl")
            # dis_log_202603042220_821.gz 格式
            if [[ "$logfile" =~ dis_log_([0-9]{8})([0-9]{4})_[0-9]+\.gz ]]; then
                local date_part="${BASH_REMATCH[1]}"
                local time_part="${BASH_REMATCH[2]}"
                echo "${date_part}_${time_part}"
            fi
            ;;
    esac
}

# 从日志行中提取时间戳
extract_timestamp_from_logline() {
    local line="$1"
    # 尝试匹配常见的时间格式，如: 2026-04-01 11:09:49
    if [[ "$line" =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}) ]]; then
        local datetime="${BASH_REMATCH[1]}"
        # 转换为YYYYMMDD_HHMM格式
        echo "$datetime" | sed 's/[-:]//g' | sed 's/ /_/' | cut -c1-13
    # 尝试匹配其他格式，如: 20260401 11:09:49
    elif [[ "$line" =~ ([0-9]{8}\ [0-9]{2}:[0-9]{2}:[0-9]{2}) ]]; then
        local datetime="${BASH_REMATCH[1]}"
        echo "$datetime" | sed 's/ /_/' | sed 's/://g' | cut -c1-13
    else
        echo ""
    fi
}

# 查找最接近时间戳的TAL日志文件
find_tal_log() {
    local tal_dir="$1"
    local target_timestamp="$2"
    local target_seconds=$(convert_timestamp_to_seconds "$target_timestamp")
    
    if [ ! -d "$tal_dir" ]; then
        log_error "TAL日志目录不存在: $tal_dir"
        return 1
    fi
    
    log_info "在 $tal_dir 中查找TAL日志..."
    
    # 首先检查dispatchTAL.log
    local dispatch_log="$tal_dir/dispatchTAL.log"
    if [ -f "$dispatch_log" ]; then
        # 检查文件大小
        local file_size=$(stat -c%s "$dispatch_log" 2>/dev/null || echo "0")
        if [ "$file_size" -gt 100 ]; then
            # 获取第一行和最后一行的时间
            local first_line=$(head -1 "$dispatch_log" 2>/dev/null)
            local last_line=$(tail -1 "$dispatch_log" 2>/dev/null)
            
            # 提取时间戳
            local first_timestamp=$(extract_timestamp_from_logline "$first_line")
            local last_timestamp=$(extract_timestamp_from_logline "$last_line")
            
            if [ -n "$first_timestamp" ] && [ -n "$last_timestamp" ]; then
                local first_seconds=$(convert_timestamp_to_seconds "$first_timestamp")
                local last_seconds=$(convert_timestamp_to_seconds "$last_timestamp")
                
                log_info "dispatchTAL.log 时间范围: $first_timestamp 到 $last_timestamp"
                log_info "目标时间: $target_timestamp (${target_seconds}秒)"
                
                # 检查目标时间是否在范围内
                if [ "$target_seconds" -ge "$first_seconds" ] && [ "$target_seconds" -le "$last_seconds" ]; then
                    log_info "目标时间在dispatchTAL.log时间范围内，使用该文件"
                    echo "$dispatch_log"
                    return 0
                else
                    log_info "目标时间不在dispatchTAL.log时间范围内，继续查找压缩文件"
                fi
            else
                log_warning "无法解析dispatchTAL.log的时间戳，继续查找压缩文件"
            fi
        else
            log_warning "dispatchTAL.log文件太小 (${file_size}字节)，跳过"
        fi
    fi
    
    # 查找压缩的TAL日志文件
    local closest_file=""
    local min_diff=9999999999
    
    for logfile in "$tal_dir"/tal_log_*.zip; do
        if [ -f "$logfile" ]; then
            local log_timestamp=$(extract_time_from_logfile "$(basename "$logfile")" "tal")
            if [ -n "$log_timestamp" ]; then
                local log_seconds=$(convert_timestamp_to_seconds "$log_timestamp")
                local diff=$((target_seconds - log_seconds))
                
                # 取绝对值
                if [ $diff -lt 0 ]; then
                    diff=$(( -diff ))
                fi
                
                if [ $diff -lt $min_diff ]; then
                    min_diff=$diff
                    closest_file="$logfile"
                fi
            fi
        fi
    done
    
    # 如果没有找到.zip文件，尝试查找其他格式
    if [ -z "$closest_file" ]; then
        for logfile in "$tal_dir"/tal_log_*; do
            if [ -f "$logfile" ] && [[ "$logfile" != *.zip ]]; then
                local filename=$(basename "$logfile")
                # 尝试解析格式: tal_log_202604011111_977
                if [[ "$filename" =~ tal_log_([0-9]{8})([0-9]{4})_[0-9]+ ]]; then
                    local date_part="${BASH_REMATCH[1]}"
                    local time_part="${BASH_REMATCH[2]}"
                    local log_timestamp="${date_part}_${time_part}"
                    local log_seconds=$(convert_timestamp_to_seconds "$log_timestamp")
                    local diff=$((target_seconds - log_seconds))
                    
                    if [ $diff -lt 0 ]; then
                        diff=$(( -diff ))
                    fi
                    
                    if [ $diff -lt $min_diff ]; then
                        min_diff=$diff
                        closest_file="$logfile"
                    fi
                fi
            fi
        done
    fi
    
    if [ -n "$closest_file" ]; then
        log_info "找到最接近的TAL日志: $(basename "$closest_file") (时间差: ${min_diff}秒)"
        echo "$closest_file"
    else
        log_warning "未找到TAL日志文件"
        echo ""
    fi
}

# 查找最接近时间戳的rtps日志文件
find_rtps_log() {
    local logs_dir="$1"
    local target_timestamp="$2"
    local target_seconds=$(convert_timestamp_to_seconds "$target_timestamp")
    
    if [ ! -d "$logs_dir" ]; then
        log_error "rtps日志目录不存在: $logs_dir"
        return 1
    fi
    
    log_info "在 $logs_dir 中查找rtps日志..."
    
    # 首先检查rtps.log（当前日志）
    local current_log="$logs_dir/rtps.log"
    if [ -f "$current_log" ]; then
        # 检查文件大小，如果太小可能没有内容
        local file_size=$(stat -c%s "$current_log" 2>/dev/null || echo "0")
        if [ "$file_size" -gt 100 ]; then
            log_info "找到当前rtps.log文件 (大小: ${file_size}字节)"
            echo "$current_log"
            return 0
        else
            log_warning "当前rtps.log文件太小 (${file_size}字节)，跳过"
        fi
    fi
    
    # 查找压缩的rtps日志文件
    local closest_file=""
    local min_diff=9999999999
    
    # 查找所有rtps.log.*.gz文件
    for logfile in "$logs_dir"/rtps.log.*.gz; do
        if [ -f "$logfile" ]; then
            local log_timestamp=$(extract_time_from_logfile "$(basename "$logfile")" "rtps")
            if [ -n "$log_timestamp" ]; then
                local log_seconds=$(convert_timestamp_to_seconds "$log_timestamp")
                local diff=$((target_seconds - log_seconds))
                
                # 取绝对值
                if [ $diff -lt 0 ]; then
                    diff=$(( -diff ))
                fi
                
                if [ $diff -lt $min_diff ]; then
                    min_diff=$diff
                    closest_file="$logfile"
                fi
            fi
        fi
    done
    
    # 如果没有找到.gz文件，尝试查找其他格式
    if [ -z "$closest_file" ]; then
        for logfile in "$logs_dir"/rtps.log.*; do
            if [ -f "$logfile" ] && [[ "$logfile" != *.gz ]]; then
                local filename=$(basename "$logfile")
                # 尝试解析格式: rtps.log.20260219125337121
                if [[ "$filename" =~ rtps\.log\.([0-9]{8})([0-9]{6})[0-9]* ]]; then
                    local date_part="${BASH_REMATCH[1]}"
                    local time_part="${BASH_REMATCH[2]:0:4}"  # 取前4位作为HHMM
                    local log_timestamp="${date_part}_${time_part}"
                    local log_seconds=$(convert_timestamp_to_seconds "$log_timestamp")
                    local diff=$((target_seconds - log_seconds))
                    
                    if [ $diff -lt 0 ]; then
                        diff=$(( -diff ))
                    fi
                    
                    if [ $diff -lt $min_diff ]; then
                        min_diff=$diff
                        closest_file="$logfile"
                    fi
                fi
            fi
        done
    fi
    
    if [ -n "$closest_file" ]; then
        log_info "找到最接近的rtps日志: $(basename "$closest_file") (时间差: ${min_diff}秒)"
        echo "$closest_file"
    else
        log_warning "未找到rtps日志文件"
        echo ""
    fi
}

# 查找最接近时间戳的DPL日志文件
find_dpl_log() {
    local dpl_dir="$1"
    local target_timestamp="$2"
    local target_seconds=$(convert_timestamp_to_seconds "$target_timestamp")
    
    if [ ! -d "$dpl_dir" ]; then
        log_error "DPL日志目录不存在: $dpl_dir"
        return 1
    fi
    
    log_info "在 $dpl_dir 中查找DPL日志..."
    
    # 首先检查dispatchX.log（X是区域号）
    local dispatch_log="$dpl_dir/dispatch${AREA}.log"
    if [ -f "$dispatch_log" ]; then
        # 检查文件大小
        local file_size=$(stat -c%s "$dispatch_log" 2>/dev/null || echo "0")
        if [ "$file_size" -gt 100 ]; then
            log_info "找到dispatch日志: $(basename "$dispatch_log") (大小: ${file_size}字节)"
            echo "$dispatch_log"
            return 0
        else
            log_warning "dispatch日志文件太小 (${file_size}字节)，跳过"
        fi
    fi
    
    # 查找压缩的DPL日志文件
    local closest_file=""
    local min_diff=9999999999
    
    # 查找dis_log_*.gz文件
    for logfile in "$dpl_dir"/dis_log_*.gz; do
        if [ -f "$logfile" ]; then
            local log_timestamp=$(extract_time_from_logfile "$(basename "$logfile")" "dpl")
            if [ -n "$log_timestamp" ]; then
                local log_seconds=$(convert_timestamp_to_seconds "$log_timestamp")
                local diff=$((target_seconds - log_seconds))
                
                # 取绝对值
                if [ $diff -lt 0 ]; then
                    diff=$(( -diff ))
                fi
                
                if [ $diff -lt $min_diff ]; then
                    min_diff=$diff
                    closest_file="$logfile"
                fi
            fi
        fi
    done
    
    # 如果没有找到.gz文件，尝试查找其他格式
    if [ -z "$closest_file" ]; then
        for logfile in "$dpl_dir"/dis_log_*; do
            if [ -f "$logfile" ] && [[ "$logfile" != *.gz ]]; then
                local filename=$(basename "$logfile")
                # 尝试解析格式: dis_log_202603042220_821
                if [[ "$filename" =~ dis_log_([0-9]{8})([0-9]{4})_[0-9]+ ]]; then
                    local date_part="${BASH_REMATCH[1]}"
                    local time_part="${BASH_REMATCH[2]}"
                    local log_timestamp="${date_part}_${time_part}"
                    local log_seconds=$(convert_timestamp_to_seconds "$log_timestamp")
                    local diff=$((target_seconds - log_seconds))
                    
                    if [ $diff -lt 0 ]; then
                        diff=$(( -diff ))
                    fi
                    
                    if [ $diff -lt $min_diff ]; then
                        min_diff=$diff
                        closest_file="$logfile"
                    fi
                fi
            fi
        done
    fi
    
    # 如果还没有找到，尝试查找其他可能的日志文件
    if [ -z "$closest_file" ]; then
        # 查找dispatch.log（不带区域号）
        local dispatch_log_general="$dpl_dir/dispatch.log"
        if [ -f "$dispatch_log_general" ]; then
            local file_size=$(stat -c%s "$dispatch_log_general" 2>/dev/null || echo "0")
            if [ "$file_size" -gt 100 ]; then
                log_info "找到通用dispatch日志: $(basename "$dispatch_log_general")"
                echo "$dispatch_log_general"
                return 0
            fi
        fi
        
        # 查找其他可能的日志文件
        for logfile in "$dpl_dir"/*.log; do
            if [ -f "$logfile" ] && [ "$logfile" != "$dispatch_log" ] && [ "$logfile" != "$dispatch_log_general" ]; then
                local file_size=$(stat -c%s "$logfile" 2>/dev/null || echo "0")
                if [ "$file_size" -gt 100 ]; then
                    log_info "找到其他日志文件: $(basename "$logfile")"
                    echo "$logfile"
                    return 0
                fi
            fi
        done
    fi
    
    if [ -n "$closest_file" ]; then
        log_info "找到最接近的DPL日志: $(basename "$closest_file") (时间差: ${min_diff}秒)"
        echo "$closest_file"
    else
        log_warning "未找到DPL日志文件"
        echo ""
    fi
}

# 复制文件到目标目录
copy_log_file() {
    local source_file="$1"
    local target_dir="$2"
    local new_filename="$3"
    
    if [ -z "$source_file" ] || [ ! -f "$source_file" ]; then
        log_warning "源文件不存在: $source_file"
        return 1
    fi
    
    # 创建目标目录
    mkdir -p "$target_dir"
    
    local target_path="$target_dir/$new_filename"
    
    log_info "复制文件: $(basename "$source_file") -> $new_filename"
    
    if cp "$source_file" "$target_path"; then
        log_success "文件复制成功: $target_path"
        echo "$target_path"
    else
        log_error "文件复制失败: $source_file -> $target_path"
        return 1
    fi
}

# 主函数
main() {
    log_info "开始拉取算法日志..."
    
    # 验证参数
    validate_parameters "$@"
    
    # 目标目录
    BASE_TARGET_DIR="/main/app/mntc/git/toolsForPersonal/projects/agv_system/app/agv_log_fetcher/alllog"
    TARGET_DIR="$BASE_TARGET_DIR/$TIMESTAMP"
    
    # 查找rtpsa文件夹
    rtpsa_folders=($(find_rtpsa_folders "$AREA"))
    
    # 查找rtpsp文件夹
    rtpsp_folders=($(find_rtpsp_folders "$AREA"))
    
    # 统计找到的文件夹数量
    rtpsa_count=0
    rtpsp_count=0
    
    for folder in "${rtpsa_folders[@]}"; do
        if [ -n "$folder" ] && [ -d "$folder" ]; then
            rtpsa_count=$((rtpsa_count + 1))
        fi
    done
    
    for folder in "${rtpsp_folders[@]}"; do
        if [ -n "$folder" ] && [ -d "$folder" ]; then
            rtpsp_count=$((rtpsp_count + 1))
        fi
    done
    
    log_info "找到 $rtpsa_count 个rtpsa文件夹，$rtpsp_count 个rtpsp文件夹"
    
    # 处理每个rtpsa文件夹
    if [ $rtpsa_count -gt 0 ]; then
        for rtpsa_folder in "${rtpsa_folders[@]}"; do
            if [ -z "$rtpsa_folder" ] || [ ! -d "$rtpsa_folder" ]; then
                continue
            fi
            
            log_info "处理rtpsa文件夹: $rtpsa_folder"
            
            # 提取文件夹名中的区域列表
            folder_name=$(basename "$rtpsa_folder")
            areas_list=$(echo "$folder_name" | sed 's/rtpsa-//')
            
            # 1. 处理TAL日志
            tal_dir="$rtpsa_folder/TAL_log"
            tal_log=$(find_tal_log "$tal_dir" "$TIMESTAMP")
            
            if [ -n "$tal_log" ]; then
                # 生成目标文件名
                new_filename="${TIMESTAMP}_rtpsa_${areas_list}_TAL.log"
                if [[ "$tal_log" == *.zip ]]; then
                    new_filename="${new_filename}.zip"
                fi
                
                copy_log_file "$tal_log" "$TARGET_DIR" "$new_filename"
            fi
            
            # 2. 处理rtps日志
            logs_dir="$rtpsa_folder/logs"
            rtps_log=$(find_rtps_log "$logs_dir" "$TIMESTAMP")
            
            if [ -n "$rtps_log" ]; then
                # 生成目标文件名
                new_filename="${TIMESTAMP}_${areas_list}_rtps.log"
                if [[ "$rtps_log" == *.gz ]]; then
                    new_filename="${new_filename}.gz"
                fi
                
                copy_log_file "$rtps_log" "$TARGET_DIR" "$new_filename"
            fi
        done
    else
        log_warning "没有找到rtpsa文件夹，跳过TAL和rtps日志拉取"
    fi
    
    # 处理每个rtpsp文件夹
    if [ $rtpsp_count -gt 0 ]; then
        for rtpsp_folder in "${rtpsp_folders[@]}"; do
            if [ -z "$rtpsp_folder" ] || [ ! -d "$rtpsp_folder" ]; then
                continue
            fi
            
            log_info "处理rtpsp文件夹: $rtpsp_folder"
            
            # 3. 处理DPL日志
            dpl_dir="$rtpsp_folder/DPL_log"
            dpl_log=$(find_dpl_log "$dpl_dir" "$TIMESTAMP")
            
            if [ -n "$dpl_log" ]; then
                # 生成目标文件名
                new_filename="${TIMESTAMP}_rtpsp_${AREA}_DPL.log"
                if [[ "$dpl_log" == *.gz ]]; then
                    new_filename="${new_filename}.gz"
                fi
                
                copy_log_file "$dpl_log" "$TARGET_DIR" "$new_filename"
            fi
        done
    else
        log_warning "没有找到rtpsp文件夹，跳过DPL日志拉取"
    fi
    
    log_success "日志拉取完成！"
    log_info "日志保存到: $TARGET_DIR"
}

# 执行主函数
main "$@"