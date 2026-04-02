#!/bin/bash
# AGV日志拉取系统配置文件示例
# 注意：这是一个示例文件，实际使用时请复制为 config.sh 并修改相应参数

# ============================================
# 日志源目录配置
# ============================================

# TPS日志目录
export TPS_LOG_DIR="/main/app/tps/logs"

# ICS日志目录
export ICS_LOG_DIR="/main/app/ics/logs"

# RTPS日志根目录
export RTPS_BASE_DIR="/main/app"

# ============================================
# 目标目录配置
# ============================================

# 拉取日志的存储目录
export TARGET_LOG_DIR="/home/ymsk/alllog"

# 日志归档目录（可选的归档存储）
export ARCHIVE_DIR="/home/ymsk/log_archive"

# ============================================
# 默认参数配置
# ============================================

# 默认区域号（用于RTPS日志）
export DEFAULT_AREA="4"

# 默认时间戳格式
export TIMESTAMP_FORMAT="YYYYMMDD_HHMM"

# ============================================
# 性能配置
# ============================================

# 最大文件检查数量（防止过多文件遍历）
export MAX_FILE_SCAN=1000

# 超时时间（秒）
export TIMEOUT_SECONDS=300

# 并行处理数
export PARALLEL_JOBS=2

# ============================================
# 日志记录配置
# ============================================

# 日志级别：DEBUG, INFO, WARN, ERROR
export LOG_LEVEL="INFO"

# 日志文件路径
export SCRIPT_LOG_DIR="/var/log/agv_log_fetcher"

# ============================================
# 压缩和归档配置
# ============================================

# 是否自动压缩拉取的日志文件
export AUTO_COMPRESS="yes"

# 压缩格式：gzip, bzip2, zip
export COMPRESS_FORMAT="gzip"

# 归档保留天数
export ARCHIVE_RETENTION_DAYS=30

# ============================================
# 通知配置
# ============================================

# 邮件通知收件人（逗号分隔）
export EMAIL_RECIPIENTS="admin@example.com,user@example.com"

# 邮件通知触发条件：always, error, never
export EMAIL_NOTIFY="error"

# ============================================
# 脚本路径配置
# ============================================

# 脚本根目录
export SCRIPT_BASE_DIR="/main/app/mntc/git/toolsForPersonal/projects/agv_system/app/getlog"

# 主脚本路径
export MAIN_SCRIPT="${SCRIPT_BASE_DIR}/bin/copy_all_log.sh"

# 专用脚本目录
export BIN_DIR="${SCRIPT_BASE_DIR}/bin"

# ============================================
# 验证函数
# ============================================

validate_config() {
    # 检查必要目录是否存在
    for dir_var in "TPS_LOG_DIR" "ICS_LOG_DIR" "RTPS_BASE_DIR"; do
        if [ ! -d "${!dir_var}" ]; then
            echo "警告：目录 $dir_var=${!dir_var} 不存在"
        fi
    done
    
    # 检查目标目录是否可写
    if [ ! -w "$(dirname "$TARGET_LOG_DIR")" ]; then
        echo "错误：目标目录 $(dirname "$TARGET_LOG_DIR") 不可写"
        return 1
    fi
    
    # 验证区域号
    if ! [[ "$DEFAULT_AREA" =~ ^[0-9]+$ ]]; then
        echo "错误：默认区域号必须是数字"
        return 1
    fi
    
    return 0
}

# ============================================
# 工具函数
# ============================================

# 获取当前时间戳
get_current_timestamp() {
    date +"%Y%m%d_%H%M"
}

# 获取昨天的时间戳
get_yesterday_timestamp() {
    date -d "yesterday" +"%Y%m%d_%H%M"
}

# 获取指定天数前的时间戳
get_timestamp_days_ago() {
    local days="$1"
    date -d "$days days ago" +"%Y%m%d_%H%M"
}

# 创建目录（如果不存在）
ensure_dir() {
    local dir_path="$1"
    if [ ! -d "$dir_path" ]; then
        mkdir -p "$dir_path"
    fi
}

# 记录日志
log_message() {
    local level="$1"
    local message="$2"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    
    # 根据日志级别决定是否输出
    case "$LOG_LEVEL" in
        "DEBUG")
            echo "[$timestamp] [$level] $message"
            ;;
        "INFO")
            if [[ "$level" != "DEBUG" ]]; then
                echo "[$timestamp] [$level] $message"
            fi
            ;;
        "WARN")
            if [[ "$level" != "DEBUG" && "$level" != "INFO" ]]; then
                echo "[$timestamp] [$level] $message"
            fi
            ;;
        "ERROR")
            if [[ "$level" == "ERROR" ]]; then
                echo "[$timestamp] [$level] $message"
            fi
            ;;
    esac
    
    # 记录到日志文件
    ensure_dir "$SCRIPT_LOG_DIR"
    echo "[$timestamp] [$level] $message" >> "${SCRIPT_LOG_DIR}/agv_log_fetcher.log"
}

# ============================================
# 使用说明
# ============================================

# 要使用此配置文件，请执行以下步骤：
# 1. 复制此文件为 config.sh：cp config.example.sh config.sh
# 2. 编辑 config.sh，根据实际情况修改配置参数
# 3. 在脚本中导入配置：source /path/to/config.sh
# 4. 调用 validate_config 函数验证配置

# 示例脚本使用配置文件：
#
# #!/bin/bash
# # 导入配置文件
# source /path/to/config.sh
# 
# # 验证配置
# if ! validate_config; then
#     exit 1
# fi
# 
# # 使用配置参数
# TIMESTAMP="20260401_1010"
# $MAIN_SCRIPT tps "$TIMESTAMP"

# ============================================
# 预设配置方案
# ============================================

# 生产环境配置
setup_production_config() {
    export LOG_LEVEL="INFO"
    export EMAIL_NOTIFY="error"
    export ARCHIVE_RETENTION_DAYS=90
    export AUTO_COMPRESS="yes"
}

# 开发/测试环境配置
setup_dev_config() {
    export LOG_LEVEL="DEBUG"
    export EMAIL_NOTIFY="never"
    export ARCHIVE_RETENTION_DAYS=7
    export AUTO_COMPRESS="no"
}

# 调试环境配置
setup_debug_config() {
    export LOG_LEVEL="DEBUG"
    export EMAIL_NOTIFY="never"
    export ARCHIVE_RETENTION_DAYS=1
    export AUTO_COMPRESS="no"
    export MAX_FILE_SCAN=100
}

# 根据环境设置配置
setup_config_by_env() {
    local env="$1"
    
    case "$env" in
        "production")
            setup_production_config
            ;;
        "development"|"dev")
            setup_dev_config
            ;;
        "debug")
            setup_debug_config
            ;;
        *)
            echo "未知环境: $env，使用默认配置"
            ;;
    esac
}

# ============================================
# 初始化脚本
# ============================================

# 自动初始化目录
init_directories() {
    ensure_dir "$TARGET_LOG_DIR"
    ensure_dir "$ARCHIVE_DIR"
    ensure_dir "$SCRIPT_LOG_DIR"
    ensure_dir "$BIN_DIR"
    
    log_message "INFO" "目录初始化完成"
}

# 默认初始化
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 配置文件直接执行时的行为
    echo "AGV日志拉取系统配置文件示例"
    echo "使用方法："
    echo "1. cp config.example.sh config.sh"
    echo "2. 编辑config.sh文件"
    echo "3. 在脚本中使用: source /path/to/config.sh"
    echo ""
    echo "当前配置预览："
    echo "TPS日志目录: $TPS_LOG_DIR"
    echo "ICS日志目录: $ICS_LOG_DIR"
    echo "RTPS根目录: $RTPS_BASE_DIR"
    echo "目标目录: $TARGET_LOG_DIR"
    echo "默认区域号: $DEFAULT_AREA"
fi