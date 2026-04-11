#!/bin/bash
# IRAYPLEOS环境检查脚本
# 部署前的快速检查

echo "IRAYPLEOS环境检查"
echo "===================="

cd /main/app/toolsForPersonal/projects/agv_system/app/cross_env_manager

echo "1. 系统环境检查:"
echo "   当前目录: $(pwd)"
echo "   Python版本: $(python3 --version 2>&1)"
echo "   IRAYPLEOS用户: ymks"
echo "   Supervisor目录: $(ls -d /main/server/supervisor 2>/dev/null || echo '未找到')"

echo ""
echo "2. 项目文件检查:"
for file in app.py requirements_py39.txt app_py39_patch.py; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ❌ $file (缺失)"
    fi
done

echo ""
echo "3. 离线包检查 (vendor_packages3.9):"
if [ -d "vendor_packages3.9" ]; then
    echo "   ✓ 离线包目录存在"
    COUNT=$(ls vendor_packages3.9/*.whl 2>/dev/null | wc -l)
    echo "   wheel文件数量: $COUNT"
    
    echo "   关键包检查:"
    for pkg in flask pymysql werkzeug jinja2; do
        if find vendor_packages3.9 -iname "*${pkg}*.whl" -type f | grep -q .; then
            echo "   ✓ $pkg"
        else
            echo "   ❌ $pkg (缺失)"
        fi
    done
    
    # 检查markupsafe兼容性问题
    MARKUPSAFE_WHEEL=$(find vendor_packages3.9 -name "*markupsafe*.whl" -type f | head -1)
    if [ -n "$MARKUPSAFE_WHEEL" ] && echo "$MARKUPSAFE_WHEEL" | grep -q "cp310"; then
        echo "   ⚠️  markupsafe wheel为Python 3.10编译 (将自动修复)"
    fi
else
    echo "   ❌ 离线包目录不存在"
fi

echo ""
echo "4. Supervisor模板检查:"
if [ -f "config/template/cross_env_manager_supervisor_iraypleos.conf" ]; then
    echo "   ✓ Supervisor配置模板存在"
    if grep -q "user=" config/template/cross_env_manager_supervisor_iraypleos.conf; then
        USER=$(grep "user=" config/template/cross_env_manager_supervisor_iraypleos.conf | cut -d= -f2)
        echo "   模板中用户: $USER"
        if [ "$USER" = "ymks" ]; then
            echo "   ✓ 用户配置正确 (ymks)"
        else
            echo "   ⚠️  用户配置应为 'ymks'，当前为 '$USER'"
        fi
    fi
else
    echo "   ⚠️  Supervisor配置模板不存在 (将自动创建)"
fi

echo ""
echo "5. 端口检查 (端口5000):"
if netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
    echo "   ⚠️  端口5000已被占用"
    netstat -tlnp 2>/dev/null | grep ":5000 " | head -1
else
    echo "   ✓ 端口5000可用"
fi

echo ""
echo "6. 数据库兼容性检查:"
python3 -c "
import sys
print('   测试pymysql兼容性...')
try:
    # 检查是否可以导入pymysql
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb
    print('   ✓ pymysql可作为MySQLdb替代')
except ImportError as e:
    print(f'   ⚠️  数据库兼容性检查失败: {e}')
" 2>/dev/null

echo ""
echo "===================="
echo "检查完成！"
echo ""
echo "下一步建议:"
if [ -f "deploy_iraypleos.sh" ]; then
    echo "1. 运行部署脚本: ./deploy_iraypleos.sh"
else
    echo "1. 部署脚本不存在，请确保 deploy_iraypleos.sh 存在"
fi
echo "2. 部署后检查: supervisorctl status cross_env_manager"
echo "3. 访问应用: http://localhost:5000"
echo "===================="