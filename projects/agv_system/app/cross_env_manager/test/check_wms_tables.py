#!/usr/bin/env python3
"""
检查wms数据库的实际表结构
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_wms_tables():
    """检查wms数据库表结构"""
    print("检查wms数据库表结构")
    print("=" * 60)
    
    try:
        from modules.database.connection import get_production_db_config, execute_query
        
        config = get_production_db_config()
        
        # 获取所有表
        print("\n1. 数据库中的表:")
        print("-" * 40)
        
        tables_query = "SHOW TABLES"
        tables = execute_query(tables_query, config=config)
        
        if tables:
            table_names = [list(table.values())[0] for table in tables]
            print(f"  总表数: {len(table_names)}")
            
            # 显示前20个表
            for i, table in enumerate(table_names[:20], 1):
                print(f"  {i:2d}. {table}")
            
            if len(table_names) > 20:
                print(f"  ... 还有 {len(table_names) - 20} 个表")
        
        # 检查与任务相关的表
        print("\n2. 与任务相关的表结构:")
        print("-" * 40)
        
        task_related_tables = [
            'fy_cross_task',
            'agv_robot',
            'task_group',
            'join_qr_node_info'  # 我们之前测试的表
        ]
        
        for table in task_related_tables:
            if table in table_names:
                print(f"\n  表 {table} 的字段:")
                desc_query = f"DESCRIBE {table}"
                columns = execute_query(desc_query, config=config)
                
                if columns:
                    for col in columns[:10]:  # 只显示前10个字段
                        print(f"    {col['Field']} ({col['Type']}) - {col.get('Key', '')}")
                    if len(columns) > 10:
                        print(f"    ... 还有 {len(columns) - 10} 个字段")
                
                # 显示表记录数
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                count_result = execute_query(count_query, config=config)
                if count_result:
                    print(f"    记录数: {count_result[0]['count']}")
            else:
                print(f"\n  表 {table} 不存在")
        
        # 检查fy_cross_task表的示例数据
        print("\n3. fy_cross_task表示例数据:")
        print("-" * 40)
        
        if 'fy_cross_task' in table_names:
            sample_query = "SELECT * FROM fy_cross_task ORDER BY id DESC LIMIT 3"
            sample_data = execute_query(sample_query, config=config)
            
            if sample_data:
                for i, task in enumerate(sample_data, 1):
                    print(f"\n  示例任务 {i}:")
                    for key, value in list(task.items())[:8]:  # 只显示前8个字段
                        print(f"    {key}: {value}")
                    if len(task) > 8:
                        print(f"    ... 还有 {len(task) - 8} 个字段")
        
        print("\n" + "=" * 60)
        print("表结构检查完成!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n检查过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        success = check_wms_tables()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n检查被用户中断")
        return 1
    except Exception as e:
        print(f"\n检查过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    exit(main())