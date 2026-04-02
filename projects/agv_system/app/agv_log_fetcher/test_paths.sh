#!/bin/bash

# 测试脚本：验证所有日志拉取脚本的路径配置

echo "=== AGV日志拉取系统路径测试 ==="
echo "测试时间: $(date)"
echo ""

# 切换到脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "脚本目录: $SCRIPT_DIR"
cd "$SCRIPT_DIR"

echo ""

# 测试路径辅助函数
echo "1. 测试路径辅助函数..."
if [ -f "bin/path_helpers.sh" ]; then
    echo "  ✓ 找到 path_helpers.sh"
    
    # 导入函数
    source "bin/path_helpers.sh"
    
    # 测试各个函数
    script_dir=$(get_script_dir)
    echo "  ✓ get_script_dir: $script_dir"
    
    project_root=$(get_project_root)
    echo "  ✓ get_project_root: $project_root"
    
    alllog_dir=$(get_alllog_dir)
    echo "  ✓ get_alllog_dir: $alllog_dir"
    
    # 测试目录创建
    if ensure_dir "$alllog_dir"; then
        echo "  ✓ alllog目录创建/验证成功: $alllog_dir"
    else
        echo "  ✗ alllog目录创建失败"
    fi
    
    # 测试目标目录函数
    target_dir=$(get_target_dir "20260401_1010")
    echo "  ✓ get_target_dir: $target_dir"
    
    # 测试输出文件名函数
    filename1=$(get_output_filename "20260401_1010" "tps")
    echo "  ✓ TPS输出文件名: $filename1"
    
    filename2=$(get_output_filename "20260401_1010" "ics")
    echo "  ✓ ICS输出文件名: $filename2"
    
    filename3=$(get_output_filename "20260401_1010" "rtps" "4")
    echo "  ✓ RTPS区域4输出文件名: $filename3"
    
else
    echo "  ✗ 未找到 path_helpers.sh"
fi

echo ""

# 测试各个脚本是否存在
echo "2. 测试所有脚本文件..."
scripts=("copy_tps_log.sh" "copy_ics_log.sh" "copy_rtps_log.sh" "copy_all_log.sh")
missing_scripts=()

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "  ✓ 找到主脚本: $script"
    elif [ -f "bin/$script" ]; then
        echo "  ✓ 找到脚本: bin/$script"
        # 检查脚本权限
        if [ -x "bin/$script" ]; then
            echo "    ✓ 脚本有执行权限"
        else
            echo "    ⚠ 脚本缺少执行权限，尝试添加..."
            chmod +x "bin/$script" 2>/dev/null
            if [ -x "bin/$script" ]; then
                echo "    ✓ 执行权限已添加"
            else
                echo "    ✗ 无法添加执行权限"
            fi
        fi
    else
        echo "  ✗ 未找到脚本: $script"
        missing_scripts+=("$script")
    fi
done

echo ""

# 测试配置文件
echo "3. 测试配置文件..."
if [ -f "conf/config.example.sh" ]; then
    echo "  ✓ 找到配置文件示例: conf/config.example.sh"
    
    # 检查是否有实际的配置文件
    if [ -f "conf/config.sh" ]; then
        echo "  ✓ 找到实际配置文件: conf/config.sh"
    else
        echo "  ⚠ 没有找到实际配置文件config.sh，可以从示例复制"
        echo "    运行: cp conf/config.example.sh conf/config.sh"
    fi
else
    echo "  ✗ 未找到配置文件示例"
fi

echo ""

# 测试alllog目录结构
echo "4. 测试alllog目录..."
if [ -d "alllog" ]; then
    echo "  ✓ alllog目录存在"
    
    # 列出目录内容
    file_count=$(find "alllog" -type f 2>/dev/null | wc -l)
    dir_count=$(find "alllog" -type d 2>/dev/null | wc -l)
    
    echo "  ✓ 目录数: $((dir_count - 1)) (不包括alllog本身)"
    echo "  ✓ 文件数: $file_count"
    
    if [ $file_count -gt 0 ]; then
        echo "  ✓ 最近修改的文件:"
        find "alllog" -type f -printf '%TY-%Tm-%Td %TT %p\n' 2>/dev/null | sort -r | head -5 | while read -r line; do
            echo "    - $line"
        done
    fi
else
    echo "  ⚠ alllog目录不存在，将自动创建"
    mkdir -p "alllog" 2>/dev/null
    if [ -d "alllog" ]; then
        echo "  ✓ alllog目录创建成功"
    else
        echo "  ✗ alllog目录创建失败"
    fi
fi

echo ""

# 测试示例命令
echo "5. 测试示例命令结构..."
echo "  示例命令:"
echo "  ./copy_all_log.sh tps 20260401_1010"
echo "  ./copy_all_log.sh rtps 4 20260401_1010"
echo "  ./copy_all_log.sh ics 20260401_1010"
echo "  ./copy_all_log.sh all 20260401_1010"
echo "  ./copy_all_log.sh all 20260401_1010 6"

echo ""

# 系统兼容性检查
echo "6. 系统兼容性检查..."
echo "  当前系统: $(uname -s)"
echo "  Bash版本: $(bash --version | head -1)"
echo "  当前用户: $(whoami)"
echo "  工作目录: $(pwd)"

# 检查所需的命令
echo ""
echo "7. 检查所需命令..."
required_commands=("bash" "date" "ls" "find" "cp" "mkdir" "chmod" "head" "tail" "grep" "sed")
missing_commands=()

for cmd in "${required_commands[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  ✓ $cmd 可用"
    else
        echo "  ✗ $cmd 不可用"
        missing_commands+=("$cmd")
    fi
done

echo ""

# 测试结果总结
echo "=== 测试结果总结 ==="
if [ ${#missing_scripts[@]} -eq 0 ] && [ ${#missing_commands[@]} -eq 0 ]; then
    echo "✓ 所有测试通过！系统已准备好使用。"
    echo ""
    echo "快速开始:"
    echo "1. 确保已登录到正确的服务器环境"
    echo "2. 可选：编辑 conf/config.sh 配置文件"
    echo "3. 使用示例命令拉取日志"
    echo "4. 日志将保存到 alllog/YYYYMMDD_HHMM/ 目录"
else
    echo "⚠ 发现一些问题："
    if [ ${#missing_scripts[@]} -gt 0 ]; then
        echo "  - 缺少脚本: ${missing_scripts[*]}"
    fi
    if [ ${#missing_commands[@]} -gt 0 ]; then
        echo "  - 缺少命令: ${missing_commands[*]}"
        echo "    请确保这些命令已安装在系统中"
    fi
fi

echo ""
echo "测试完成于: $(date)"