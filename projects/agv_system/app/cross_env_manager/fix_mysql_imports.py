#!/usr/bin/env python3
"""
修复mysql.connector导入为pymysql
"""

import sys
import os

def fix_app_py():
    """修改app.py以完全使用pymysql"""
    app_py_path = "app.py"
    
    if not os.path.exists(app_py_path):
        print(f"错误: {app_py_path} 不存在")
        return False
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换mysql.connector导入为pymysql（直接使用pymysql，不使用MySQLdb兼容层）
    new_content = content
    
    # 第1步：确保开头有pymysql导入
    if "import pymysql" not in new_content:
        # 在文件开头添加
        lines = new_content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                insert_pos = i
                break
        
        pymysql_import = "# Python 3.9兼容性修改：使用pymysql替代mysql.connector\nimport pymysql\nfrom pymysql.cursors import DictCursor\n"
        lines.insert(insert_pos, pymysql_import)
        new_content = '\n'.join(lines)
    
    # 第2步：替换mysql.connector导入
    if "import mysql.connector" in new_content:
        new_content = new_content.replace("import mysql.connector", "# import mysql.connector  # 已由pymysql替代")
    
    if "from mysql.connector import Error" in new_content:
        new_content = new_content.replace("from mysql.connector import Error", "# from MySQLdb import Error  # 使用pymysql.Error替代")
    
    # 第3步：替换mysql.connector.connect为pymysql.connect
    if "mysql.connector.connect" in new_content:
        new_content = new_content.replace("mysql.connector.connect", "pymysql.connect")
    
    # 第4步：替换Error引用为pymysql.Error
    if "except Error as e:" in new_content:
        new_content = new_content.replace("except Error as e:", "except pymysql.Error as e:")
    
    # 第5步：替换cursor(dictionary=True)为cursor(DictCursor)
    if "cursor(dictionary=True)" in new_content:
        new_content = new_content.replace("cursor(dictionary=True)", "cursor(DictCursor)")
    
    # 写入文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ app.py 已修改为使用pymysql替代mysql.connector")
    
    # 验证修改
    with open(app_py_path, 'r', encoding='utf-8') as f:
        final_content = f.read()
    
    # 检查关键修改
    checks = [
        ("mysql.connector.connect" not in final_content, "mysql.connector.connect已移除"),
        ("pymysql.connect" in final_content, "使用pymysql.connect"),
        ("DictCursor" in final_content, "使用DictCursor"),
    ]
    
    all_passed = True
    for check_passed, message in checks:
        if check_passed:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    if fix_app_py():
        print("修复成功")
        print("注意: 需要重新启动应用以使更改生效")
    else:
        print("修复失败")
        sys.exit(1)