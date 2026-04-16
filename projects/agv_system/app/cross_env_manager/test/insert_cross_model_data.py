#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插入跨环境任务模板数据到测试数据库
根据提供的SQL数据，适配测试数据库的表结构
"""

import pymysql
import sys
import os

# 测试数据库配置
TEST_DB_CONFIG = {
    'host': '47.98.244.173',
    'port': 53308,
    'user': 'root',
    'password': 'Qq13235202993',
    'database': 'ds',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**TEST_DB_CONFIG)
        return conn
    except pymysql.Error as e:
        print(f"数据库连接错误: {e}")
        return None

def check_existing_data():
    """检查是否已存在相同ID的数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # 检查主表
        cursor.execute('SELECT id FROM fy_cross_model_process WHERE id = 462')
        existing_process = cursor.fetchone()
        
        # 检查详情表
        cursor.execute('SELECT id FROM fy_cross_model_process_detail WHERE id IN (101503607, 101503608, 101503609)')
        existing_details = cursor.fetchall()
        
        if existing_process:
            print(f"警告: fy_cross_model_process表中已存在id=462的记录")
            return True
        
        if existing_details:
            print(f"警告: fy_cross_model_process_detail表中已存在部分记录: {[d[0] for d in existing_details]}")
            return True
        
        return False
        
    except Exception as e:
        print(f"检查现有数据时出错: {e}")
        return True
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insert_cross_model_process():
    """插入主表数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # 适配测试数据库表结构（缺少create_time和update_time字段）
        sql = """
        INSERT INTO fy_cross_model_process 
        (id, model_process_code, model_process_name, enable, request_url, 
         capacity, target_points, area_id, target_points_ip, 
         backflow_template_code, comeback_template_code, change_charge_template_code, 
         min_power, back_wait_time, check_area_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # 参数值 - 注意：测试数据库没有create_time和update_time字段
        params = (
            462,  # id
            'K_go_32JGBL2F_to_32DJBL2F_462',  # model_process_code
            '去空车_32结构备料2F_to_32点胶备料2F_462',  # model_process_name
            1,  # enable
            'http://127.0.0.1:7000/ics/taskOrder/updateTaskStatus',  # request_url
            0,  # capacity
            None,  # target_points
            None,  # area_id
            None,  # target_points_ip
            None,  # backflow_template_code
            None,  # comeback_template_code
            '',  # change_charge_template_code
            None,  # min_power
            None,  # back_wait_time
            None   # check_area_name
        )
        
        cursor.execute(sql, params)
        conn.commit()
        
        print(f"成功插入主表数据: id=462, 模板代码={params[1]}")
        return True
        
    except pymysql.Error as e:
        print(f"插入主表数据时出错: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insert_cross_model_process_details():
    """插入详情表数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # 详情数据列表
        detail_data = [
            {
                'id': 101503607,
                'model_process_id': 462,
                'task_seq': 1,
                'task_servicec': 'http://10.68.2.27:7000',
                'template_code': 'moveKQDL-1',
                'template_name': 'moveKQDL-1',
                'task_path': '60000017',
                'backflow_template_code': None,
                'comeback_template_code': None,
                'back_wait_time': None
            },
            {
                'id': 101503608,
                'model_process_id': 462,
                'task_seq': 2,
                'task_servicec': 'http://10.68.2.32:7000',
                'template_code': 'moveK-3',
                'template_name': 'moveK-3',
                'task_path': '66000003',
                'backflow_template_code': None,
                'comeback_template_code': None,
                'back_wait_time': None
            },
            {
                'id': 101503609,
                'model_process_id': 462,
                'task_seq': 3,
                'task_servicec': 'http://10.68.2.32:7000',
                'template_code': 'no_stop-1',
                'template_name': 'no_stop-1',
                'task_path': '66000003',
                'backflow_template_code': None,
                'comeback_template_code': None,
                'back_wait_time': None
            }
        ]
        
        sql = """
        INSERT INTO fy_cross_model_process_detail 
        (id, model_process_id, task_seq, task_servicec, template_code, 
         template_name, task_path, backflow_template_code, 
         comeback_template_code, back_wait_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for detail in detail_data:
            params = (
                detail['id'],
                detail['model_process_id'],
                detail['task_seq'],
                detail['task_servicec'],
                detail['template_code'],
                detail['template_name'],
                detail['task_path'],
                detail['backflow_template_code'],
                detail['comeback_template_code'],
                detail['back_wait_time']
            )
            
            try:
                cursor.execute(sql, params)
                success_count += 1
                print(f"成功插入详情数据: id={detail['id']}, 任务序号={detail['task_seq']}")
            except pymysql.Error as e:
                print(f"插入详情数据id={detail['id']}时出错: {e}")
        
        conn.commit()
        print(f"详情表插入完成: 成功 {success_count}/{len(detail_data)} 条记录")
        return success_count == len(detail_data)
        
    except Exception as e:
        print(f"插入详情表数据时出错: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def verify_inserted_data():
    """验证插入的数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = None
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("\n验证插入的数据:")
        
        # 验证主表
        cursor.execute('SELECT * FROM fy_cross_model_process WHERE id = 462')
        process_data = cursor.fetchone()
        
        if process_data:
            print(f"✓ 主表数据验证成功:")
            print(f"  ID: {process_data['id']}")
            print(f"  模板代码: {process_data['model_process_code']}")
            print(f"  模板名称: {process_data['model_process_name']}")
            print(f"  启用状态: {process_data['enable']}")
        else:
            print("✗ 主表数据验证失败: 未找到id=462的记录")
            return False
        
        # 验证详情表
        cursor.execute('SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = 462 ORDER BY task_seq')
        detail_data = cursor.fetchall()
        
        if detail_data:
            print(f"✓ 详情表数据验证成功: 找到 {len(detail_data)} 条记录")
            for detail in detail_data:
                print(f"  任务序号 {detail['task_seq']}: {detail['template_code']} -> {detail['task_path']}")
        else:
            print("✗ 详情表数据验证失败: 未找到model_process_id=462的记录")
            return False
        
        return True
        
    except Exception as e:
        print(f"验证数据时出错: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """主函数"""
    print("=" * 60)
    print("插入跨环境任务模板数据到测试数据库")
    print("=" * 60)
    
    # 检查是否已存在数据
    print("\n1. 检查现有数据...")
    if check_existing_data():
        print("数据已存在，是否继续？(y/n): ", end="")
        choice = input().strip().lower()
        if choice != 'y':
            print("操作已取消")
            return
    
    # 插入主表数据
    print("\n2. 插入主表数据...")
    if not insert_cross_model_process():
        print("主表数据插入失败，终止操作")
        return
    
    # 插入详情表数据
    print("\n3. 插入详情表数据...")
    if not insert_cross_model_process_details():
        print("详情表数据插入失败，但主表数据已插入")
    
    # 验证数据
    print("\n4. 验证插入的数据...")
    if verify_inserted_data():
        print("\n✓ 所有数据插入验证成功！")
    else:
        print("\n✗ 数据验证失败")
    
    print("\n" + "=" * 60)
    print("操作完成")
    print("=" * 60)

if __name__ == '__main__':
    main()