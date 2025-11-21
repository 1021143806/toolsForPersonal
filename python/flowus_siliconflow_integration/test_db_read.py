#!/usr/bin/env python3
"""
测试从数据库读取内容
"""
from config.config_loader import ConfigLoader
from database.mysql_client import MySQLClient

def main():
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    mysql_client = MySQLClient(config)
    
    # 连接数据库
    if not mysql_client.connect():
        print("数据库连接失败")
        return
    
    # 测试页面ID（从配置中获取）
    page_url = config['flowus']['url']
    page_id = page_url.split('/')[-1].split('?')[0]
    
    print(f"测试读取页面内容: {page_id}")
    
    # 获取页面内容
    content = mysql_client.get_page_content(page_id)
    
    if content:
        print(f"成功获取页面内容，长度: {len(content)} 字符")
        print("\n=== 页面内容预览 ===")
        print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print("获取页面内容失败")
    
    # 关闭数据库连接
    mysql_client.disconnect()

if __name__ == "__main__":
    main()