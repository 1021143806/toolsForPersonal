"""
从数据库读取数据发送给硅基AI处理并生成页面
"""
import os
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='process.log'
)
logger = logging.getLogger(__name__)
from config.config_loader import ConfigLoader
from clients.siliconflow_client import SiliconFlowClient
from clients.flowus_client import FlowUsClient
from processors.page_formatter import PageFormatter
from outputs.flowus_writer import FlowUsWriter
from database.mysql_client import MySQLClient

def main():
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    flowus_client = FlowUsClient(config_loader)
    ai_client = SiliconFlowClient(config)
    formatter = PageFormatter(config, flowus_client)
    writer = FlowUsWriter(config, flowus_client)
    mysql_client = MySQLClient(config)
    
    # 连接数据库
    if not mysql_client.connect():
        logger.error("数据库连接失败，程序退出")
        return
    
    # 从数据库读取数据
    page_url = config['flowus']['url']
    page_id = page_url.split('/')[-1].split('?')[0]
    logger.info(f"开始从数据库读取页面数据: {page_id}")
    
    content = mysql_client.get_page_content(page_id)
    if not content:
        logger.error("从数据库读取内容失败")
        mysql_client.disconnect()
        return
    
    logger.info(f"读取文本内容长度: {len(content)}")
    
    # 简单预处理：去除空行和多余空格
    content = '\n'.join([line.strip() for line in content.split('\n') if line.strip()])
    logger.info(f"预处理后的内容长度: {len(content)}")
    
    # 发送给AI处理
    logger.info("发送内容给AI处理...")
    ai_response = ai_client.send_content(content)
    logger.info(f"AI响应类型: {type(ai_response)}")
    logger.debug(f"AI响应内容: {ai_response}")
    
    # 格式化页面内容
    logger.info("格式化AI响应内容...")
    formatted = formatter.format_page_details(ai_response)
    logger.info(f"格式化后内容: {formatted}")
    
    # 保存本地副本并记录日志
    output_dir = config.get('output', {}).get('output_dir', 'outputs')
    local_filename = config.get('output', {}).get('filename', 'local.md')
    
    # 确保输出目录存在
    output_path = os.path.join(os.path.dirname(__file__), output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    local_path = os.path.join(output_path, local_filename)
    try:
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
        logger.info(f"成功生成本地文件: {local_path}")
        logger.debug(f"文件内容预览:\n{formatted[:200]}...")  # 记录前200字符
    except Exception as e:
        logger.error(f"生成本地文件失败: {str(e)}")
        raise
    
    # 创建FlowUs页面
    writer.create_page_with_content(formatted, ai_response)
    print("新页面创建流程已完成")
    
    # 关闭数据库连接
    mysql_client.disconnect()

if __name__ == "__main__":
    main()