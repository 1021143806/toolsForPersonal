"""
整合执行数据获取、导出和AI处理流程
按照用户要求：
1. 先完成信息获取
2. 根据配置文件中的时间要求从数据库获取指定时间内的信息
3. 保存到outputs/data.log
4. 然后发送给硅基API生成内容
"""
from fetch_diary_data import main as fetch_main
from process_diary_with_ai import main as process_main

def main():
    print("=== 步骤1: 从FlowUs获取多维表数据 ===")
    fetch_main()
    
    print("\n=== 步骤2: 处理数据并生成AI内容 ===")
    print("流程说明：")
    print("- 根据配置文件中的时间要求从数据库获取指定时间内的信息")
    print("- 保存到outputs/data.log")
    print("- 然后发送给硅基API生成内容")
    process_main()
    
    print("\n=== 处理完成 ===")
    print("数据流程：")
    print("FlowUs数据 → MySQL数据库 → data.log → 硅基API → FlowUs新页面")

if __name__ == "__main__":
    main()