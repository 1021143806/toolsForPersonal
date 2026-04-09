#!/usr/bin/env python3
"""
Python 3.9兼容性补丁
将mysql.connector替换为pymysql
"""

import sys
import os

def patch_app_py():
    """修改app.py以使用pymysql"""
    app_py_path = "app.py"
    
    if not os.path.exists(app_py_path):
        print(f"错误: {app_py_path} 不存在")
        return False
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经打了补丁
    if "pymysql" in content and "pymysql.install_as_MySQLdb()" in content:
        print("app.py 已经打了pymysql补丁")
        return True
    
    # 在文件开头添加pymysql导入
    lines = content.split('\n')
    
    # 找到第一个非注释/空行之后的位置
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            insert_pos = i
            break
    
    # 插入pymysql导入
    pymysql_import = """# Python 3.9兼容性修改：使用pymysql替代mysql.connector
import pymysql
pymysql.install_as_MySQLdb()
"""
    
    lines.insert(insert_pos, pymysql_import)
    
    # 写入文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✓ app.py 已修改为使用pymysql")
    return True

if __name__ == "__main__":
    if patch_app_py():
        print("补丁应用成功")
        print("注意: 需要重新启动应用以使更改生效")
    else:
        print("补丁应用失败")
        sys.exit(1)
