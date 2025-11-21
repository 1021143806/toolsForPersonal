"""
测试数据库连接和表创建
"""
from config.config_loader import ConfigLoader
from database.mysql_client import MySQLClient
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    mysql_client = MySQLClient(config)
    
    # 测试数据库连接
    logger.info("测试数据库连接...")
    if mysql_client.connect():
        logger.info("数据库连接成功")
        
        # 测试表创建
        logger.info("测试创建数据表...")
        if mysql_client.create_tables():
            logger.info("数据表创建成功")
        else:
            logger.error("数据表创建失败")
        
        # 关闭连接
        mysql_client.disconnect()
        logger.info("数据库连接已关闭")
    else:
        logger.error("数据库连接失败")

if __name__ == "__main__":
    main()