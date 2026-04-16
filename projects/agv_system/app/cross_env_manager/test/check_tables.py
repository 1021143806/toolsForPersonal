#!/usr/bin/env python3
"""
检查数据库表结构
"""

import pymysql
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_config():
    """获取数据库配置"""
    import tomli
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'env.toml')
    
    with open(config_path, 'rb') as f:
        config = tomli.load(f)
    
    return config['database']

def connect_to_db(db_config):
    """连接到数据库"""
    try:
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['name'],
            charset=db_config.get('charset', 'utf8mb4'),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"数据库连接错误: {e}")
        return None

def check_table_structure(connection, table_name):
    """检查表结构"""
    print(f"\n检查表 {table_name} 结构:")
    print("="*80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print(f"{'字段名':<25} {'类型':<20} {'允许NULL':<10} {'默认值':<15} {'额外信息':<10}")
            print("-"*80)
            
            for col in columns:
                print(f"{col['Field']:<25} {col['Type']:<20} {col['Null']:<10} {str(col['Default'] or ''):<15} {col['Extra']:<10}")
            
            return columns
    except pymysql.Error as e:
        print(f"查询表结构错误: {e}")
        return None

def check_table_exists(connection, table_name):
    """检查表是否存在"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            return cursor.fetchone() is not None
    except pymysql.Error as e:
        print(f"检查表存在错误: {e}")
        return False

def main():
    """主函数"""
    db_config = get_db_config()
    
    print("数据库配置:")
    print(f"  主机: {db_config['host']}")
    print(f"  端口: {db_config['port']}")
    print(f"  数据库: {db_config['name']}")
    print(f"  用户: {db_config['user']}")
    
    connection = connect_to_db(db_config)
    if not connection:
        print("无法连接到数据库")
        return
    
    try:
        # 检查表是否存在
        tables_to_check = ['fy_cross_model_process', 'fy_cross_model_process_detail']
        
        for table in tables_to_check:
            if check_table_exists(connection, table):
                print(f"\n✓ 表 {table} 存在")
                check_table_structure(connection, table)
            else:
                print(f"\n✗ 表 {table} 不存在")
        
        # 查看现有数据
        print("\n\n现有数据统计:")
        print("="*80)
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM fy_cross_model_process")
            main_count = cursor.fetchone()
            print(f"fy_cross_model_process 表记录数: {main_count['count'] if main_count else 0}")
            
            cursor.execute("SELECT COUNT(*) as count FROM fy_cross_model_process_detail")
            detail_count = cursor.fetchone()
            print(f"fy_cross_model_process_detail 表记录数: {detail_count['count'] if detail_count else 0}")
            
            # 查看前几条记录
            if main_count and main_count['count'] > 0:
                print("\nfy_cross_model_process 表前5条记录:")
                cursor.execute("SELECT id, model_process_code, model_process_name, enable FROM fy_cross_model_process ORDER BY id LIMIT 5")
                records = cursor.fetchall()
                for record in records:
                    print(f"  ID: {record['id']}, 代码: {record['model_process_code']}, 名称: {record['model_process_name']}, 启用: {record['enable']}")
        
    finally:
        connection.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()