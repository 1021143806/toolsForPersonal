#!/usr/bin/env python3
"""
从FlowUs获取日记多维表数据并处理关联页面
"""
import logging
from typing import List, Dict, Any, Optional
from config.config_loader import ConfigLoader
from clients.flowus_client import FlowUsClient
from database.mysql_client import MySQLClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='fetch_diary.log'
)
logger = logging.getLogger(__name__)


class DiaryDataFetcher:
    """日记数据获取器"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.config = config_loader.load_config()
        self.flowus_client = FlowUsClient(config_loader)
        self.mysql_client = MySQLClient(self.config)
        
    def extract_database_reference_from_blocks(self, blocks_data: Dict[str, Any]) -> Optional[str]:
        """从页面块中提取数据库引用"""
        if not blocks_data or 'results' not in blocks_data:
            logger.warning("块数据为空或缺少results字段")
            return None
            
        logger.info(f"开始分析 {len(blocks_data.get('results', []))} 个页面块")
        
        # 统计块类型
        block_types = {}
        for block in blocks_data.get('results', []):
            block_type = block.get('type', 'unknown')
            block_types[block_type] = block_types.get(block_type, 0) + 1
        logger.info(f"发现块类型分布: {block_types}")
        
        # 1. 首先检查段落块中的页面提及
        for block in blocks_data.get('results', []):
            if block.get('type') == 'paragraph':
                rich_text = block.get('data', {}).get('rich_text', [])
                for text_item in rich_text:
                    if (text_item.get('type') == 'mention' and
                        'mention' in text_item and
                        text_item['mention'].get('type') == 'page'):
                        page_id = text_item['mention']['page']['id']
                        logger.info(f"发现页面提及: {page_id}")
                        if self.flowus_client.is_database(page_id):
                            logger.info(f"确认数据库引用: {page_id}")
                            return page_id
                        else:
                            logger.info(f"页面 {page_id} 不是数据库")
        
        # 2. 检查是否有直接的数据库块
        for block in blocks_data.get('results', []):
            if block.get('type') in ['database', 'collection_view']:
                logger.info(f"发现直接数据库块: {block.get('id')}, 类型: {block.get('type')}")
                # 尝试获取数据库ID
                block_id = block.get('id')
                if block_id and self.flowus_client.is_database(block_id):
                    logger.info(f"确认直接数据库引用: {block_id}")
                    return block_id
        
        # 3. 检查标题包含"日记"的块
        for block in blocks_data.get('results', []):
            if block.get('type') in ['child_database', 'child_page']:
                title = ""
                if 'data' in block and 'title' in block['data']:
                    title_items = block['data']['title']
                    title = ' '.join([item.get('plain_text', '') for item in title_items])
                
                if '日记' in title:
                    block_id = block.get('id')
                    logger.info(f"发现标题包含'日记'的块: {title}, ID: {block_id}")
                    if block_id and self.flowus_client.is_database(block_id):
                        logger.info(f"确认标题数据库引用: {block_id}")
                        return block_id
        
        logger.warning("未找到任何数据库引用")
        return None
    
    def process_diary_database(self, diary_db_id: str) -> bool:
        """处理日记数据库"""
        logger.info(f"开始处理日记数据库: {diary_db_id}")
        
        # 获取数据库内容
        db_content = self.flowus_client.get_database_content(diary_db_id)
        if not db_content:
            logger.error(f"无法获取日记数据库内容: {diary_db_id}")
            return False
        
        results = db_content.get('results', [])
        logger.info(f"日记数据库包含 {len(results)} 条记录")
        
        # 收集所有需要获取的关联页面
        problem_page_ids = set()
        project_page_ids = set()
        
        # 处理每条日记记录
        for record in results:
            # 存储日记记录
            if not self.mysql_client.insert_diary_record(record):
                logger.error(f"存储日记记录失败: {record.get('id')}")
                continue
            
            # 提取关联页面ID
            properties = record.get('properties', {})
            
            # 提取问题记录链接
            if '问题记录总表链接' in properties:
                problem_links = properties['问题记录总表链接'].get('relation', [])
                for link in problem_links:
                    if 'id' in link:
                        problem_page_ids.add(link['id'])
            
            # 提取项目记录链接
            if '项目总表' in properties:
                project_links = properties['项目总表'].get('relation', [])
                for link in project_links:
                    if 'id' in link:
                        project_page_ids.add(link['id'])
        
        logger.info(f"发现 {len(problem_page_ids)} 个问题记录页面")
        logger.info(f"发现 {len(project_page_ids)} 个项目记录页面")
        
        # 获取并存储问题记录页面
        for page_id in problem_page_ids:
            self.process_problem_record_page(page_id)
        
        # 获取并存储项目记录页面
        for page_id in project_page_ids:
            self.process_project_record_page(page_id)
        
        return True
    
    def process_problem_record_page(self, page_id: str) -> bool:
        """处理问题记录页面"""
        logger.info(f"处理问题记录页面: {page_id}")
        
        try:
            # 获取页面信息
            page_data = self.flowus_client.get_page_details(page_id)
            if not page_data:
                logger.error(f"无法获取问题记录页面信息: {page_id}")
                return False
            
            # 获取页面块内容
            blocks_data = self.flowus_client.get_page_content(page_id)
            if blocks_data:
                # 将块内容添加到页面数据中
                page_data['blocks'] = blocks_data
            
            # 存储问题记录
            if self.mysql_client.insert_problem_record(page_data):
                logger.info(f"成功存储问题记录: {page_id}")
                return True
            else:
                logger.error(f"存储问题记录失败: {page_id}")
                return False
                
        except Exception as e:
            logger.error(f"处理问题记录页面出错 {page_id}: {e}")
            return False
    
    def process_project_record_page(self, page_id: str) -> bool:
        """处理项目记录页面"""
        logger.info(f"处理项目记录页面: {page_id}")
        
        try:
            # 获取页面信息
            page_data = self.flowus_client.get_page_details(page_id)
            if not page_data:
                logger.error(f"无法获取项目记录页面信息: {page_id}")
                return False
            
            # 获取页面块内容
            blocks_data = self.flowus_client.get_page_content(page_id)
            if blocks_data:
                # 将块内容添加到页面数据中
                page_data['blocks'] = blocks_data
            
            # 存储项目记录
            if self.mysql_client.insert_project_record(page_data):
                logger.info(f"成功存储项目记录: {page_id}")
                return True
            else:
                logger.error(f"存储项目记录失败: {page_id}")
                return False
                
        except Exception as e:
            logger.error(f"处理项目记录页面出错 {page_id}: {e}")
            return False
    
    def fetch_all_data(self) -> bool:
        """获取所有数据的主流程"""
        logger.info("=== 开始获取日记数据 ===")
        
        # 连接数据库
        if not self.mysql_client.connect():
            logger.error("数据库连接失败")
            return False
        
        try:
            # 创建数据表
            if not self.mysql_client.create_tables():
                logger.error("创建数据表失败")
                return False
            
            # 获取配置的页面ID
            page_url = self.config['flowus']['url']
            page_id = page_url.split('/')[-1].split('?')[0]
            logger.info(f"处理主页面: {page_id}")
            
            # 获取主页面块内容
            blocks_data = self.flowus_client.get_page_content(page_id)
            if not blocks_data:
                logger.error("无法获取主页面块内容")
                return False
            
            # 提取日记数据库引用
            diary_db_id = self.extract_database_reference_from_blocks(blocks_data)
            if not diary_db_id:
                logger.error("未找到日记数据库引用")
                return False
            
            logger.info(f"找到日记数据库: {diary_db_id}")
            
            # 处理日记数据库
            if not self.process_diary_database(diary_db_id):
                logger.error("处理日记数据库失败")
                return False
            
            logger.info("=== 日记数据获取完成 ===")
            return True
            
        except Exception as e:
            logger.error(f"获取数据过程中出错: {e}")
            return False
        finally:
            # 关闭数据库连接
            self.mysql_client.disconnect()


def main():
    """主函数"""
    config_loader = ConfigLoader()
    fetcher = DiaryDataFetcher(config_loader)
    
    if fetcher.fetch_all_data():
        print("日记数据获取成功！")
    else:
        print("日记数据获取失败！")


if __name__ == "__main__":
    main()