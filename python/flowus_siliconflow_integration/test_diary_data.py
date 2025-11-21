#!/usr/bin/env python3
"""
测试日记数据获取和时间范围过滤功能
"""
from config.config_loader import ConfigLoader
from database.mysql_client import MySQLClient
from datetime import datetime, timedelta

def test_data_summary():
    """测试数据汇总"""
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    mysql_client = MySQLClient(config)
    
    if not mysql_client.connect():
        print("数据库连接失败")
        return
    
    try:
        print("=== 数据库中的数据汇总 ===")
        
        # 测试日记记录
        diary_records = mysql_client.get_recent_diary_records(days=365)  # 获取所有记录
        print(f"日记记录总数: {len(diary_records)}")
        
        if diary_records:
            print("\n=== 日记记录分类统计 ===")
            categories = {}
            for record in diary_records:
                category = record.get('category', '未知')
                categories[category] = categories.get(category, 0) + 1
            
            for category, count in categories.items():
                print(f"{category}: {count} 条")
        
        # 测试问题记录
        problem_records = mysql_client.get_recent_problem_records(days=365)
        print(f"\n问题记录总数: {len(problem_records)}")
        
        # 测试项目记录
        project_records = mysql_client.get_recent_project_records(days=365)
        print(f"项目记录总数: {len(project_records)}")
        
        # 测试时间范围过滤
        print("\n=== 时间范围过滤测试 ===")
        test_time_ranges = [7, 30, 90]
        
        for days in test_time_ranges:
            print(f"\n--- 最近 {days} 天的数据 ---")
            
            recent_diary = mysql_client.get_recent_diary_records(days=days)
            recent_problems = mysql_client.get_recent_problem_records(days=days)
            recent_projects = mysql_client.get_recent_project_records(days=days)
            
            print(f"日记记录: {len(recent_diary)} 条")
            print(f"问题记录: {len(recent_problems)} 条")
            print(f"项目记录: {len(recent_projects)} 条")
            
            # 显示一些示例数据
            if recent_diary:
                print(f"最新日记: {recent_diary[0].get('title', '无标题')}")
            if recent_problems:
                print(f"最新问题: {recent_problems[0].get('title', '无标题')}")
            if recent_projects:
                print(f"最新项目: {recent_projects[0].get('title', '无标题')}")
        
        # 测试数据详情
        print("\n=== 数据详情示例 ===")
        
        if diary_records:
            print("\n--- 日记记录示例 ---")
            record = diary_records[0]
            print(f"标题: {record.get('title', '无标题')}")
            print(f"分类: {record.get('category', '无分类')}")
            print(f"完成状态: {record.get('completed', False)}")
            print(f"开始时间: {record.get('start_time', '无时间')}")
            print(f"创建时间: {record.get('created_time', '无时间')}")
            
            problem_links = record.get('problem_record_links')
            project_links = record.get('project_record_links')
            
            if problem_links:
                import json
                try:
                    links = json.loads(problem_links) if isinstance(problem_links, str) else problem_links
                    print(f"关联问题记录数量: {len(links)}")
                except:
                    print(f"关联问题记录: {problem_links}")
            
            if project_links:
                import json
                try:
                    links = json.loads(project_links) if isinstance(project_links, str) else project_links
                    print(f"关联项目记录数量: {len(links)}")
                except:
                    print(f"关联项目记录: {project_links}")
        
        if problem_records:
            print("\n--- 问题记录示例 ---")
            record = problem_records[0]
            print(f"标题: {record.get('title', '无标题')}")
            print(f"创建时间: {record.get('created_time', '无时间')}")
            print(f"状态: {record.get('status', '无状态')}")
            print(f"优先级: {record.get('priority', '无优先级')}")
        
        if project_records:
            print("\n--- 项目记录示例 ---")
            record = project_records[0]
            print(f"标题: {record.get('title', '无标题')}")
            print(f"创建时间: {record.get('created_time', '无时间')}")
            print(f"状态: {record.get('status', '无状态')}")
            print(f"进度: {record.get('progress', 0)}%")
        
    finally:
        mysql_client.disconnect()

def test_content_extraction():
    """测试内容提取功能"""
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    mysql_client = MySQLClient(config)
    
    if not mysql_client.connect():
        print("数据库连接失败")
        return
    
    try:
        print("\n=== 内容提取测试 ===")
        
        # 获取最近的问题记录
        problem_records = mysql_client.get_recent_problem_records(days=30)
        if problem_records:
            print(f"测试 {len(problem_records)} 条问题记录的内容提取")
            
            for i, record in enumerate(problem_records[:3]):  # 只测试前3条
                print(f"\n--- 问题记录 {i+1} ---")
                print(f"ID: {record.get('id')}")
                print(f"标题: {record.get('title', '无标题')}")
                
                # 尝试从raw_response中提取内容
                raw_response = record.get('raw_response')
                if raw_response:
                    import json
                    try:
                        page_data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
                        
                        # 提取页面内容
                        if 'properties' in page_data:
                            properties = page_data['properties']
                            for key, value in properties.items():
                                if key != 'title':  # 跳过标题，已经显示过了
                                    print(f"{key}: {value}")
                    
                    except json.JSONDecodeError:
                        print("无法解析raw_response")
        
        # 获取最近的项目记录
        project_records = mysql_client.get_recent_project_records(days=30)
        if project_records:
            print(f"\n测试 {len(project_records)} 条项目记录的内容提取")
            
            for i, record in enumerate(project_records[:3]):  # 只测试前3条
                print(f"\n--- 项目记录 {i+1} ---")
                print(f"ID: {record.get('id')}")
                print(f"标题: {record.get('title', '无标题')}")
                
                # 尝试从raw_response中提取内容
                raw_response = record.get('raw_response')
                if raw_response:
                    import json
                    try:
                        page_data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
                        
                        # 提取页面内容
                        if 'properties' in page_data:
                            properties = page_data['properties']
                            for key, value in properties.items():
                                if key != 'title':  # 跳过标题，已经显示过了
                                    print(f"{key}: {value}")
                    
                    except json.JSONDecodeError:
                        print("无法解析raw_response")
    
    finally:
        mysql_client.disconnect()

def main():
    """主函数"""
    print("开始测试日记数据...")
    test_data_summary()
    test_content_extraction()
    print("\n测试完成！")

if __name__ == "__main__":
    main()