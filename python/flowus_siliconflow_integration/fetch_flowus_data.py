"""
从FlowUs获取数据并保存到数据库
"""
import logging
from config.config_loader import ConfigLoader
from clients.flowus_client import FlowUsClient
from processors.database_processor import DatabaseProcessor
from database.mysql_client import MySQLClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='fetch.log'
)
logger = logging.getLogger(__name__)

def main():
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    flowus_client = FlowUsClient(config_loader)
    db_processor = DatabaseProcessor(config, flowus_client)
    mysql_client = MySQLClient(config)
    
    # 连接数据库并创建表
    if not mysql_client.connect():
        logger.error("数据库连接失败，程序退出")
        return
    
    if not mysql_client.create_tables():
        logger.error("创建数据表失败，程序退出")
        mysql_client.disconnect()
        return
    
    # 获取页面数据
    page_url = config['flowus']['url']
    page_id = page_url.split('/')[-1].split('?')[0]
    logger.info(f"开始获取页面数据: {page_id}")
    
    # 获取页面详细信息
    page_data = flowus_client.get_page_details(page_id)
    if page_data:
        logger.info(f"成功获取页面数据: {page_data.get('id')}")
        
        # 将页面信息存储到数据库
        if mysql_client.insert_page(page_data):
            logger.info("页面信息已存储到数据库")
        else:
            logger.error("存储页面信息失败")
        
        # 获取页面的块内容
        blocks_data = flowus_client.get_page_content(page_id)
        if blocks_data:
            logger.info(f"成功获取页面块数据: {len(blocks_data.get('results', []))} 个块")
            
            # 将块内容存储到数据库
            if mysql_client.insert_blocks(page_id, blocks_data):
                logger.info("页面块内容已存储到数据库")
            else:
                logger.error("存储页面块内容失败")
        else:
            logger.error("获取页面块数据失败")
        
        # 数据已存储到数据库，无需额外处理
        logger.info("数据已成功存储到数据库")
        
    else:
        logger.error("获取页面数据失败")
    
    # 关闭数据库连接
    mysql_client.disconnect()
    logger.info("数据获取完成")

if __name__ == "__main__":
    main()