#!/bin/bash

# copy_all_log.sh - AGV日志统一拉取脚本
# 功能：根据输入的参数，调用相应的日志拉取脚本
# 支持多种日志类型：TPS、RTPS（算法）、ICS、FYWDS
#
# 用法：
#   1. 拉取TPS日志：./copy_all_log.sh tps <时间戳>
#   2. 拉取RTPS算法日志：./copy_all_log.sh rtps <时间戳> <区域号>
#   3. 拉取ICS日志：./copy_all_log.sh ics <时间戳>
#   4. 拉取FYWDS日志：./copy_all_log.sh fywds <时间戳>
#   5. 批量拉取所有类型日志：./copy_all_log.sh all <时间戳> [区域号 - 可选，默认为4]
#
# 示例：
#   ./copy_all_log.sh tps 20260401_1010
#   ./copy_all_log.sh rtps 20260401_1010 4
#   ./copy_all_log.sh ics 20260401_1010
#   ./copy_all_log.sh fywds 20260401_1010
#   ./copy_all_log.sh all 20260401_1010
#   ./copy_all_log.sh all 20260401_1010 6

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# 显示用法
show_usage() {
    echo "AGV日志统一拉取工具"
    echo ""
    echo "用法: $0 <日志类型> <时间戳> [区域号]"
    echo ""
    echo "可用日志类型:"
    echo "  tps     - 拉取TPS日志"
    echo "  rtps    - 拉取RTPS算法日志（需要区域号参数）"
    echo "  ics     - 拉取ICS日志"
    echo "  fywds   - 拉取FYWDS日志"
    echo "  all     - 批量拉取所有类型日志"
    echo ""
    echo "参数说明:"
    echo "  时间戳: 日志时间戳，格式为YYYYMMDD_HHMM（如20260401_1010）"
    echo "  区域号: 需要拉取日志的区域编号（如4,5,6等），仅rtps类型需要"
    echo ""
    echo "示例:"
    echo "  $0 tps 20260401_1010"
    echo "  $0 rtps 20260401_1010 4"
    echo "  $0 ics 20260401_1010"
    echo "  $0 fywds 20260401_1010"
    echo "  $0 all 20260401_1010"
    echo "  $0 all 20260401_1010 6"
    echo ""
    exit 1
}

# 验证时间戳格式
validate_timestamp() {
    local timestamp="$1"
    local type="$2"
    
    if ! [[ "$timestamp" =~ ^[0-9]{8}_[0-9]{4}$ ]]; then
        log_error "$type时间戳格式错误，应为YYYYMMDD_HHMM（如20260401_1010）"
        return 1
    fi
    
    # 解析时间戳
    local date_part=$(echo "$timestamp" | cut -d'_' -f1)
    local time_part=$(echo "$timestamp" | cut -d'_' -f2)
    
    # 验证日期有效性
    if ! date -d "${date_part:0:4}-${date_part:4:2}-${date_part:6:2}" >/dev/null 2>&1; then
        log_error "$type无效的日期: $date_part"
        return 1
    fi
    
    # 验证时间有效性
    local hour=${time_part:0:2}
    local minute=${time_part:2:2}
    if [ "$hour" -gt 23 ] || [ "$minute" -gt 59 ]; then
        log_error "$type无效的时间: ${hour}:${minute}"
        return 1
    fi
    
    return 0
}

# 拉取TPS日志
pull_tps_log() {
    local timestamp="$1"
    local script_dir="$(dirname "$0")"
    local tps_script="$script_dir/bin/copy_tps_log.sh"
    
    log_header "开始拉取TPS日志"
    log_info "时间戳: $timestamp"
    
    if [ ! -f "$tps_script" ]; then
        log_error "TPS日志拉取脚本不存在: $tps_script"
        return 1
    fi
    
    if ! validate_timestamp "$timestamp" "TPS"; then
        return 1
    fi
    
    log_info "执行TPS日志拉取..."
    if bash "$tps_script" "$timestamp"; then
        log_success "TPS日志拉取成功"
        return 0
    else
        log_error "TPS日志拉取失败"
        return 1
    fi
}

# 拉取RTPS算法日志
pull_rtps_log() {
    local area="$1"
    local timestamp="$2"
    local script_dir="$(dirname "$0")"
    local rtps_script="$script_dir/bin/copy_rtps_log.sh"
    
    log_header "开始拉取RTPS算法日志"
    log_info "区域号: $area"
    log_info "时间戳: $timestamp"
    
    if [ ! -f "$rtps_script" ]; then
        log_error "RTPS日志拉取脚本不存在: $rtps_script"
        return 1
    fi
    
    # 验证区域号
    if ! [[ "$area" =~ ^[0-9]+$ ]]; then
        log_error "区域号必须是数字"
        return 1
    fi
    
    if ! validate_timestamp "$timestamp" "RTPS"; then
        return 1
    fi
    
    log_info "执行RTPS日志拉取..."
    if bash "$rtps_script" "$timestamp" "$area"; then
        log_success "RTPS日志拉取成功"
        return 0
    else
        log_error "RTPS日志拉取失败"
        return 1
    fi
}

# 拉取ICS日志
pull_ics_log() {
    local timestamp="$1"
    local script_dir="$(dirname "$0")"
    local ics_script="$script_dir/bin/copy_ics_log.sh"
    
    log_header "开始拉取ICS日志"
    log_info "时间戳: $timestamp"
    
    if [ ! -f "$ics_script" ]; then
        log_error "ICS日志拉取脚本不存在: $ics_script"
        return 1
    fi
    
    if ! validate_timestamp "$timestamp" "ICS"; then
        return 1
    fi
    
    log_info "执行ICS日志拉取..."
    if bash "$ics_script" "$timestamp"; then
        log_success "ICS日志拉取成功"
        return 0
    else
        log_error "ICS日志拉取失败"
        return 1
    fi
}

# 拉取FYWDS日志
pull_fywds_log() {
    local timestamp="$1"
    local script_dir="$(dirname "$0")"
    local fywds_script="$script_dir/bin/copy_fywds_log.sh"
    
    log_header "开始拉取FYWDS日志"
    log_info "时间戳: $timestamp"
    
    if [ ! -f "$fywds_script" ]; then
        log_error "FYWDS日志拉取脚本不存在: $fywds_script"
        return 1
    fi
    
    if ! validate_timestamp "$timestamp" "FYWDS"; then
        return 1
    fi
    
    log_info "执行FYWDS日志拉取..."
    if bash "$fywds_script" "$timestamp"; then
        log_success "FYWDS日志拉取成功"
        return 0
    else
        log_error "FYWDS日志拉取失败"
        return 1
    fi
}

# 批量拉取所有日志
pull_all_logs() {
    local timestamp="$1"
    local area="${2:-4}"  # 默认区域号为4
    
    log_header "开始批量拉取所有AGV日志"
    log_info "时间戳: $timestamp"
    log_info "区域号: $area (用于RTPS)"
    
    echo ""
    
    # 拉取TPS日志
    if ! pull_tps_log "$timestamp"; then
        log_warning "TPS日志拉取失败，继续处理其他日志..."
    fi
    
    echo ""
    
    # 拉取RTPS日志
    if ! pull_rtps_log "$area" "$timestamp"; then
        log_warning "RTPS日志拉取失败，继续处理其他日志..."
    fi
    
    echo ""
    
    # 拉取ICS日志
    if ! pull_ics_log "$timestamp"; then
        log_warning "ICS日志拉取失败，继续处理其他日志..."
    fi

    echo ""

    # 拉取FYWDS日志
    if ! pull_fywds_log "$timestamp"; then
        log_warning "FYWDS日志拉取失败，继续处理其他日志..."
    fi

    echo ""
    log_header "批量拉取完成"
    
# 展示拉取的日志文件 - 使用相对路径
    local script_dir="$(cd "$(dirname "$0")" && pwd)"
    local base_target_dir="$script_dir/alllog"
    local target_dir="$base_target_dir/$timestamp"
    log_info "拉取的日志文件保存到: $target_dir"
    
    if [ -d "$target_dir" ]; then
        log_info "目录内容:"
        ls -lh "$target_dir"/ 2>/dev/null || log_info "目录为空"
        
        # 显示文件数量统计
        local file_count=$(find "$target_dir" -type f -name "*.log" -o -name "*.gz" -o -name "*.zip" 2>/dev/null | wc -l)
        log_info "共拉取 $file_count 个日志文件"
        
        # 显示文件详细信息
        echo ""
        log_info "拉取的日志文件："
        find "$target_dir" -type f -name "*.log" -o -name "*.gz" -o -name "*.zip" 2>/dev/null | xargs -I {} sh -c 'echo "  - {} ($(ls -lh "{}" | awk "{print \$5}"))"' || log_info "没有找到文件"
    fi
}

# 主函数
main() {
    if [ $# -lt 2 ]; then
        show_usage
    fi
    
    local log_type="$1"
    
    case "$log_type" in
        tps)
            if [ $# -ne 2 ]; then
                log_error "tps日志需要一个参数：时间戳"
                show_usage
            fi
            pull_tps_log "$2"
            ;;
            
        rtps)
            if [ $# -ne 3 ]; then
                log_error "rtps日志需要两个参数：时间戳 区域号"
                show_usage
            fi
            pull_rtps_log "$3" "$2"  # 注意：现在第2个参数是时间戳，第3个是区域号
            ;;
            
        ics)
            if [ $# -ne 2 ]; then
                log_error "ics日志需要一个参数：时间戳"
                show_usage
            fi
            pull_ics_log "$2"
            ;;
            
        fywds)
            if [ $# -ne 2 ]; then
                log_error "fywds日志需要一个参数：时间戳"
                show_usage
            fi
            pull_fywds_log "$2"
            ;;
            
        all)
            local timestamp="$2"
            local area="${3:-4}"
            
            if [ -z "$timestamp" ]; then
                log_error "all日志需要时间戳参数"
                show_usage
            fi
            
            if ! validate_timestamp "$timestamp" "批量"; then
                exit 1
            fi
            
            pull_all_logs "$timestamp" "$area"
            ;;
            
        *)
            log_error "未知的日志类型: $log_type"
            show_usage
            ;;
    esac
}

# 执行主函数
main "$@"