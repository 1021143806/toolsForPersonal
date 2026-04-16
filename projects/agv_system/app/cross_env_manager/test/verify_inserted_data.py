#!/usr/bin/env python3
"""
验证插入的数据是否与用户提供的数据一致
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

def verify_main_table_data(connection):
    """验证主表数据"""
    print("\n验证主表数据 (fy_cross_model_process):")
    print("="*80)
    
    # 用户提供的主表数据
    expected_main_data = {
        'id': 462,
        'model_process_code': 'K_go_32JGBL2F_to_32DJBL2F_462',
        'model_process_name': '去空车_32结构备料2F_to_32点胶备料2F_462',
        'enable': 1,
        'request_url': 'http://127.0.0.1:7000/ics/taskOrder/updateTaskStatus',
        'capacity': 0,
        'target_points': None,
        'area_id': None,
        'target_points_ip': None,
        'backflow_template_code': None,
        'comeback_template_code': None,
        'change_charge_template_code': '',
        'min_power': None,
        'back_wait_time': None,
        'check_area_name': None
    }
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fy_cross_model_process WHERE id = 462")
            actual_data = cursor.fetchone()
            
            if not actual_data:
                print("✗ 未找到ID为462的主表数据")
                return False
            
            print("✓ 找到ID为462的主表数据")
            print("\n字段对比:")
            print(f"{'字段名':<30} {'期望值':<40} {'实际值':<40} {'状态':<10}")
            print("-"*120)
            
            all_match = True
            for field, expected_value in expected_main_data.items():
                actual_value = actual_data.get(field)
                
                # 处理NULL值的比较
                if expected_value is None and actual_value is None:
                    status = "✓ 匹配"
                elif expected_value == actual_value:
                    status = "✓ 匹配"
                else:
                    status = "✗ 不匹配"
                    all_match = False
                
                print(f"{field:<30} {str(expected_value):<40} {str(actual_value):<40} {status:<10}")
            
            return all_match
            
    except pymysql.Error as e:
        print(f"查询主表数据错误: {e}")
        return False

def verify_detail_table_data(connection):
    """验证子任务数据"""
    print("\n\n验证子任务数据 (fy_cross_model_process_detail):")
    print("="*80)
    
    # 用户提供的子任务数据
    expected_detail_data = [
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
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = 462 ORDER BY task_seq")
            actual_details = cursor.fetchall()
            
            if len(actual_details) != len(expected_detail_data):
                print(f"✗ 子任务数量不匹配: 期望 {len(expected_detail_data)} 个, 实际 {len(actual_details)} 个")
                return False
            
            print(f"✓ 找到 {len(actual_details)} 个子任务数据")
            
            all_details_match = True
            for i, (expected, actual) in enumerate(zip(expected_detail_data, actual_details), 1):
                print(f"\n子任务 #{i} (task_seq={expected['task_seq']}):")
                print(f"{'字段名':<25} {'期望值':<35} {'实际值':<35} {'状态':<10}")
                print("-"*105)
                
                detail_match = True
                for field, expected_value in expected.items():
                    actual_value = actual.get(field)
                    
                    # 处理NULL值的比较
                    if expected_value is None and actual_value is None:
                        status = "✓ 匹配"
                    elif expected_value == actual_value:
                        status = "✓ 匹配"
                    else:
                        status = "✗ 不匹配"
                        detail_match = False
                    
                    print(f"{field:<25} {str(expected_value):<35} {str(actual_value):<35} {status:<10}")
                
                if not detail_match:
                    all_details_match = False
                    print(f"✗ 子任务 #{i} 数据不匹配")
                else:
                    print(f"✓ 子任务 #{i} 数据完全匹配")
            
            return all_details_match
            
    except pymysql.Error as e:
        print(f"查询子任务数据错误: {e}")
        return False

def main():
    """主函数"""
    db_config = get_db_config()
    
    print("验证插入的数据是否与用户提供的数据一致")
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
        main_match = verify_main_table_data(connection)
        detail_match = verify_detail_table_data(connection)
        
        print("\n" + "="*80)
        print("验证结果汇总:")
        print("="*80)
        
        if main_match:
            print("✓ 主表数据完全匹配")
        else:
            print("✗ 主表数据不匹配")
        
        if detail_match:
            print("✓ 子任务数据完全匹配")
        else:
            print("✗ 子任务数据不匹配")
        
        if main_match and detail_match:
            print("\n🎉 所有数据验证通过！插入的数据与用户提供的数据完全一致。")
        else:
            print("\n⚠️  数据验证未通过，请检查数据差异。")
        
    finally:
        connection.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()