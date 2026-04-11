#!/bin/bash
# 跨环境任务模板管理系统 - 通用部署脚本
# 适用于大多数Linux环境
# 版本: 1.0

set -e

echo "========================================"
echo "跨环境任务模板管理系统 - 通用部署"
echo "========================================"
echo "系统: $(uname -s)"
echo "时间: $(date)"
echo "========================================"

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3未安装"
    echo "请安装Python 3.8+"
    exit 1
fi

python_version=$(python3 --version 2>&1)
echo "   Python版本: $python_version"

# 检查Python版本
if [[ ! "$python_version" =~ ^Python\ 3\.(8|9|10|11|12|13|14) ]]; then
    echo "警告: 建议使用Python 3.8+，当前版本可能不兼容"
    read -p "继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "2. 创建虚拟环境..."
if [ ! -d "venv" ]; then
    if python3 -m venv venv; then
        echo "   ✓ 虚拟环境创建成功"
    else
        echo "   ✗ 虚拟环境创建失败"
        echo "   可能缺少python3-venv包，尝试:"
        echo "   Ubuntu/Debian: sudo apt install python3-venv"
        echo "   CentOS/RHEL: sudo yum install python3-venv"
        echo "   或使用系统Python环境: python3 app.py"
        exit 1
    fi
else
    echo "   ⚠️  虚拟环境已存在"
    read -p "   重新创建虚拟环境? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "   ✓ 重新创建虚拟环境"
    fi
fi

echo "3. 激活虚拟环境并安装依赖..."
source venv/bin/activate
echo "   虚拟环境Python: $(python --version 2>&1)"

# 检查安装模式
echo "4. 选择安装模式..."
echo "   1) 在线安装 (需要网络)"
echo "   2) 离线安装 (需要vendor_packages目录)"
echo "   3) 使用清华源在线安装"

read -p "   选择 (1/2/3, 默认3): " install_mode
install_mode=${install_mode:-3}

case $install_mode in
    1)
        echo "   使用默认PyPI源安装..."
        pip install -r requirements.txt
        ;;
    2)
        if [ -d "vendor_packages" ] && [ "$(ls -A vendor_packages/*.whl vendor_packages/*.tar.gz 2>/dev/null | wc -l)" -gt 0 ]; then
            echo "   使用离线包安装..."
            pip install --no-index --find-links=vendor_packages -r requirements.txt
        else
            echo "   错误: 离线包目录不存在或为空"
            echo "   请在有网络环境下载离线包:"
            echo "   pip download -r requirements.txt -d vendor_packages"
            exit 1
        fi
        ;;
    3)
        echo "   使用清华PyPI源安装..."
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        ;;
    *)
        echo "   无效选择，使用清华源安装..."
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        ;;
esac

echo "5. 验证依赖..."
if [ -f "verify_offline.py" ]; then
    if python verify_offline.py; then
        echo "   ✓ 依赖验证成功"
    else
        echo "   ⚠️  依赖验证有警告"
    fi
else
    echo "   ℹ️  跳过依赖验证 (verify_offline.py不存在)"
fi

echo "6. 检查应用配置..."
if [ ! -f "config/env.toml" ] && [ ! -f ".env" ]; then
    echo "   ⚠️  未找到配置文件"
    echo "   提示: 可以复制示例配置:"
    echo "   cp config/template/env.toml.template config/env.toml"
    echo "   然后编辑配置文件设置数据库连接"
fi

echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "启动应用:"
echo "方法1 - 使用虚拟环境:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "方法2 - 直接运行:"
echo "  venv/bin/python app.py"
echo ""
echo "方法3 - 使用gunicorn (生产环境):"
echo "  source venv/bin/activate"
echo "  pip install gunicorn"
echo "  gunicorn -w 2 -b 0.0.0.0:5000 app:app"
echo ""
echo "方法4 - 使用提供的启动脚本:"
echo "  ./start_app.sh (如存在)"
echo ""
echo "访问地址: http://localhost:5000"
echo ""
echo "Supervisor配置 (可选):"
echo "如需配置Supervisor，参考以下配置示例:"
echo "------------------------"
echo "[program:cross_env_manager]"
echo "command=$SCRIPT_DIR/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app"
echo "directory=$SCRIPT_DIR"
echo "user=$(whoami)"
echo "autostart=true"
echo "autorestart=true"
echo "stdout_logfile=/var/log/cross_env_manager.log"
echo "stderr_logfile=/var/log/cross_env_manager_error.log"
echo "------------------------"
echo ""
echo "配置完成后运行:"
echo "  supervisorctl reread"
echo "  supervisorctl update"
echo "  supervisorctl start cross_env_manager"
echo ""
echo "故障排除:"
echo "- 如果应用启动失败，检查端口5000是否被占用"
echo "- 查看应用输出获取错误信息"
echo "- 检查数据库连接配置"
echo "- 验证Python依赖是否完整"
echo "========================================"

# 创建简易启动脚本
cat > "start_app.sh" << 'EOF'
#!/bin/bash
# 跨环境任务模板管理系统启动脚本

cd "$(dirname "$0")"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "启动跨环境任务模板管理系统..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止应用"
echo ""

python app.py
EOF

chmod +x start_app.sh
echo "✓ 已创建启动脚本: start_app.sh"

echo ""
echo "使用 ./start_app.sh 启动应用"
echo "========================================"