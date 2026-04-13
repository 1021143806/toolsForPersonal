#!/bin/bash
# 验证IRAYPLEOS部署状态

echo "IRAYPLEOS部署验证"
echo "=================="

cd /main/app/toolsForPersonal/projects/agv_system/app/cross_env_manager

echo "1. 服务状态检查..."
if supervisorctl status cross_env_manager 2>/dev/null | grep -q "RUNNING"; then
    PID=$(supervisorctl status cross_env_manager | awk '{print $4}' | cut -d, -f1)
    echo "   ✓ 服务运行中 (PID: $PID)"
else
    echo "   ❌ 服务未运行"
    supervisorctl status cross_env_manager 2>/dev/null
fi

echo ""
echo "2. 端口检查..."
if netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
    echo "   ✓ 端口5000正在监听"
    netstat -tlnp 2>/dev/null | grep ":5000 " | head -1
else
    echo "   ❌ 端口5000未监听"
fi

echo ""
echo "3. 应用访问测试..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "^2"; then
    echo "   ✓ 应用可访问 (HTTP 200)"
    echo "   访问地址: http://localhost:5000"
else
    echo "   ❌ 应用无法访问"
    echo "   尝试访问: curl -I http://localhost:5000"
fi

echo ""
echo "4. 日志检查..."
if [ -f "/main/app/log/cross_env_manager.log" ]; then
    echo "   ✓ 应用日志文件存在"
    echo "   最后5行日志:"
    tail -5 /main/app/log/cross_env_manager.log
else
    echo "   ❌ 应用日志文件不存在"
fi

echo ""
echo "5. Supervisor配置检查..."
if [ -f "/main/server/supervisor/cross_env_manager.conf" ]; then
    echo "   ✓ Supervisor配置文件存在"
    echo "   关键配置:"
    grep -E "^(user=|command=|directory=|stdout_logfile=)" /main/server/supervisor/cross_env_manager.conf
else
    echo "   ❌ Supervisor配置文件不存在"
fi

echo ""
echo "6. Python依赖检查..."
source venv/bin/activate 2>/dev/null
echo "   检查关键包:"
for pkg in flask pymysql werkzeug jinja2 markupsafe; do
    if python -c "import $pkg; print('  ✓ $pkg')" 2>/dev/null; then
        echo "   ✓ $pkg已安装"
    else
        echo "   ❌ $pkg未安装"
    fi
done

echo ""
echo "7. 应用数据库连接检查..."
echo "   测试app.py导入..."
if python -c "
import sys
sys.path.insert(0, '.')
from app import app
print('  ✓ Flask应用导入成功')
print(f'   应用名称: {app.name}')
print(f'   URL映射: {len(app.url_map._rules)}个路由')
" 2>/dev/null; then
    echo "   ✓ 应用代码可正常运行"
else
    echo "   ❌ 应用代码运行失败"
    python -c "from app import app" 2>&1 | head -5
fi

echo ""
echo "=================="
echo "验证完成！"
echo ""
echo "总结:"
echo "- 服务状态: $(supervisorctl status cross_env_manager 2>/dev/null | awk '{print $2}' || echo '未知')"
echo "- 应用访问: http://localhost:5000"
echo "- 查看日志: tail -f /main/app/log/cross_env_manager.log"
echo "- 管理服务: supervisorctl [start|stop|restart|status] cross_env_manager"
echo "=================="