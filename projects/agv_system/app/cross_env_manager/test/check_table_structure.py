#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from pymysql.cursors import DictCursor
import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'agv_cross_env_test',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as e:
        print(f"数据库连接错误: {e}")
        return None

def check_table_structure():
    """检查表结构"""
    conn = get_db_connection()
    if not conn:
        print("无法连接数据库")
        return
    
    cursor = None
    try:
        cursor = conn.cursor(DictCursor)
        
        # 检查fy_cross_model_process_detail表结构
        print("检查 fy_cross_model_process_detail 表结构...")
        cursor.execute("DESCRIBE fy_cross_model_process_detail")
        columns = cursor.fetchall()
        
        print("\n表字段列表:")
        print("-" * 80)
        print(f"{'字段名':<30} {'类型':<20} {'允许NULL':<10} {'默认值':<15} {'额外信息':<10}")
        print("-" * 80)
        
        for col in columns:
            print(f"{col['Field']:<30} {col['Type']:<20} {col['Null']:<10} {str(col['Default'] or ''):<15} {col['Extra']:<10}")
        
        print("\n\n检查 app.py 中的SQL语句字段匹配...")
        
        # app.py中的INSERT语句字段
        app_fields = [
            'model_process_id', 'task_seq', 'task_servicec', 'template_code',
            'template_name', 'task_path', 'backflow_template_code',
            'comeback_template_code', 'change_charge_template_code', 'back_wait_time'
        ]
        
        db_fields = [col['Field'] for col in columns]
        
        print(f"\napp.py INSERT语句字段 ({len(app_fields)}个):")
        for field in app_fields:
            if field in db_fields:
                print(f"  ✓ {field}")
            else:
                print(f"  ✗ {field} (数据库中不存在!)")
        
        print(f"\n数据库实际字段 ({len(db_fields)}个):")
        for field in db_fields:
            print(f"  - {field}")
        
        # 检查缺失的字段
        missing_in_db = [f for f in app_fields if f not in db_fields]
        missing_in_app = [f for f in db_fields if f not in app_fields]
        
        if missing_in_db:
            print(f"\n⚠️  警告: 以下字段在app.py中使用，但数据库中不存在:")
            for field in missing_in_db:
                print(f"    - {field}")
        
        if missing_in_app:
            print(f"\n⚠️  警告: 以下字段在数据库中存在，但app.py中未使用:")
            for field in missing_in_app:
                print(f"    - {field}")
        
    except pymysql.Error as e:
        print(f"查询错误: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    check_table_structure()