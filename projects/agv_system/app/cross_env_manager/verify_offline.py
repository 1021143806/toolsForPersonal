#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证离线依赖安装
"""

import sys
import os

def check_package(package_name, import_name=None):
    """检查包是否可导入"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        module = sys.modules[import_name]
        
        # 尝试获取版本
        version = "未知"
        if hasattr(module, '__version__'):
            version = module.__version__
        elif hasattr(module, 'version'):
            version = module.version
        elif package_name == "mysql.connector":
            # mysql.connector的特殊处理
            import mysql.connector
            version = mysql.connector.__version__
        
        print(f"✓ {package_name}: 版本 {version}")
        return True
    except ImportError as e:
        print(f"✗ {package_name}: 导入失败 - {e}")
        return False
    except Exception as e:
        print(f"✗ {package_name}: 错误 - {e}")
        return False

def main():
    print("=" * 60)
    print("验证离线依赖安装")
    print("=" * 60)
    
    # 检查关键依赖包
    packages = [
        ("Flask", "flask"),
        ("mysql-connector-python", "mysql.connector"),
        ("python-dotenv", "dotenv"),
        ("Werkzeug", "werkzeug"),
        ("Jinja2", "jinja2"),
        ("click", "click"),
        ("itsdangerous", "itsdangerous"),
        ("markdown", "markdown"),
    ]
    
    # 检查tomli/tomllib
    try:
        import tomllib
        print("✓ tomllib: Python内置")
    except ImportError:
        check_package("tomli", "tomli")
    
    success_count = 0
    total_count = len(packages) + 1  # +1 for tomli/tomllib
    
    for package_name, import_name in packages:
        if check_package(package_name, import_name):
            success_count += 1
    
    print("\n" + "=" * 60)
    print("依赖检查结果:")
    print(f"  成功: {success_count}/{total_count}")
    print(f"  失败: {total_count - success_count}/{total_count}")
    
    # 检查应用是否可以导入
    print("\n" + "=" * 60)
    print("检查应用导入...")
    try:
        # 添加当前目录到Python路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 尝试导入应用
        from app import app, DB_CONFIG
        
        print("✓ 应用导入成功!")
        print(f"  数据库配置: {DB_CONFIG.get('host', '未设置')}:{DB_CONFIG.get('port', '未设置')}")
        print(f"  数据库名: {DB_CONFIG.get('database', '未设置')}")
        
        # 检查Flask应用
        if hasattr(app, 'name'):
            print(f"  应用名称: {app.name}")
        else:
            print(f"  Flask应用: {type(app).__name__}")
            
        success_count += 1
        total_count += 1
        
    except Exception as e:
        print(f"✗ 应用导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("最终结果:")
    print(f"  总检查项: {total_count}")
    print(f"  成功项: {success_count}")
    print(f"  失败项: {total_count - success_count}")
    
    if success_count == total_count:
        print("✅ 所有依赖检查通过!")
        return 0
    else:
        print("⚠️  部分依赖检查失败，请检查离线安装")
        return 1

if __name__ == "__main__":
    sys.exit(main())