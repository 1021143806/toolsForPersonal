#!/usr/bin/env python3
"""
插入测试数据到数据库 - 将所有数据插入到ds测试数据库
根据skill.md说明，当前配置只能操作ds测试数据库
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
    
    with open(config_path, 'rb') as f:  # tomli需要二进制模式
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

def check_data_exists(connection, table_name, id_value):
    """检查数据是否已存在"""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id FROM {table_name} WHERE id = %s", (id_value,))
        return cursor.fetchone() is not None

def insert_all_data(connection):
    """插入所有数据到ds数据库"""
    print("\n开始插入所有数据到ds数据库...")
    
    # 所有需要插入的SQL语句 - 根据实际表结构调整
    sql_statements = [
        # 主表数据 - 根据实际表结构调整字段
        """
        INSERT INTO `fy_cross_model_process` 
        (`id`, `model_process_code`, `model_process_name`, `enable`, `request_url`, `capacity`, `target_points`, `area_id`, `target_points_ip`, `backflow_template_code`, `comeback_template_code`, `change_charge_template_code`, `min_power`, `back_wait_time`, `check_area_name`) 
        VALUES 
        (462, 'K_go_32JGBL2F_to_32DJBL2F_462', '去空车_32结构备料2F_to_32点胶备料2F_462', 1, 'http://127.0.0.1:7000/ics/taskOrder/updateTaskStatus', 0, NULL, NULL, NULL, NULL, NULL, '', NULL, NULL, NULL)
        """,
        # 子任务数据1（原ds数据库的数据）
        """
        INSERT INTO `fy_cross_model_process_detail` 
        (`id`, `model_process_id`, `task_seq`, `task_servicec`, `template_code`, `template_name`, `task_path`, `backflow_template_code`, `comeback_template_code`, `back_wait_time`) 
        VALUES 
        (101503607, 462, 1, 'http://10.68.2.27:7000', 'moveKQDL-1', 'moveKQDL-1', '60000017', NULL, NULL, NULL)
        """,
        # 子任务数据2（原wms数据库的数据）
        """
        INSERT INTO `fy_cross_model_process_detail` 
        (`id`, `model_process_id`, `task_seq`, `task_servicec`, `template_code`, `template_name`, `task_path`, `backflow_template_code`, `comeback_template_code`, `back_wait_time`) 
        VALUES 
        (101503608, 462, 2, 'http://10.68.2.32:7000', 'moveK-3', 'moveK-3', '66000003', NULL, NULL, NULL)
        """,
        # 子任务数据3（原wms数据库的数据）
        """
        INSERT INTO `fy_cross_model_process_detail` 
        (`id`, `model_process_id`, `task_seq`, `task_servicec`, `template_code`, `template_name`, `task_path`, `backflow_template_code`, `comeback_template_code`, `back_wait_time`) 
        VALUES 
        (101503609, 462, 3, 'http://10.68.2.32:7000', 'no_stop-1', 'no_stop-1', '66000003', NULL, NULL, NULL)
        """
    ]
    
    success_count = 0
    try:
        with connection.cursor() as cursor:
            for i, sql in enumerate(sql_statements, 1):
                try:
                    cursor.execute(sql)
                    success_count += 1
                    if i == 1:
                        print(f"  主表数据插入成功")
                    else:
                        print(f"  子任务数据{i-1}插入成功")
                except pymysql.Error as e:
                    if "Duplicate entry" in str(e):
                        print(f"  数据已存在，跳过插入: {e}")
                        success_count += 1  # 视为成功
                    else:
                        print(f"  数据插入失败: {e}")
                        raise
        
        connection.commit()
        print(f"\n数据插入完成: {success_count}/{len(sql_statements)} 条成功")
        return success_count == len(sql_statements)
    except pymysql.Error as e:
        print(f"  数据插入过程中出错: {e}")
        connection.rollback()
        return False

def verify_data(connection):
    """验证插入的数据"""
    print("\n验证插入的数据:")
    
    try:
        with connection.cursor() as cursor:
            # 验证主表数据
            cursor.execute("SELECT * FROM fy_cross_model_process WHERE id = 462")
            main_data = cursor.fetchone()
            if main_data:
                print(f"  主表数据: ID={main_data['id']}, 代码={main_data['model_process_code']}, 名称={main_data['model_process_name']}")
            else:
                print("  主表数据未找到")
            
            # 验证子任务数据
            cursor.execute("SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = 462 ORDER BY task_seq")
            details = cursor.fetchall()
            print(f"  子任务数量: {len(details)}")
            for detail in details:
                print(f"    子任务#{detail['task_seq']}: {detail['template_name']} ({detail['template_code']}) - 服务: {detail['task_servicec']}")
        
        return True
    except pymysql.Error as e:
        print(f"  验证数据时出错: {e}")
        return False

def insert_data():
    """插入测试数据到ds数据库"""
    
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
        # 检查主表数据是否已存在
        if check_data_exists(connection, 'fy_cross_model_process', 462):
            print("\n主表数据已存在，ID: 462")
            print("将检查并插入缺失的子任务数据...")
        
        # 插入所有数据
        if insert_all_data(connection):
            print("\n数据插入操作成功完成!")
        else:
            print("\n数据插入操作部分失败")
        
        # 验证数据
        verify_data(connection)
        
    finally:
        connection.close()
        print("\n数据库连接已关闭")
    
    print("\n" + "="*60)
    print("数据插入操作完成!")
    print("="*60)

if __name__ == "__main__":
    insert_data()