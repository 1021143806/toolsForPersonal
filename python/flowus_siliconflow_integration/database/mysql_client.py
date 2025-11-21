"""
MySQL数据库客户端
"""
import pymysql
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def parse_iso_time(time_str):
    """解析ISO 8601时间字符串为datetime对象"""
    if not time_str:
        return None
        
    try:
        # 处理时间戳格式
        if isinstance(time_str, (int, float)):
            return datetime.fromtimestamp(time_str/1000, tz=timezone.utc)
            
        # 处理ISO 8601字符串格式
        if isinstance(time_str, str):
            # 尝试不同的ISO格式
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",      # 2025-11-17T12:48:01.036Z
                "%Y-%m-%dT%H:%M:%SZ",         # 2025-11-17T12:48:01Z
                "%Y-%m-%dT%H:%M:%S.%f%z",     # 2025-11-17T12:48:01.036+00:00
                "%Y-%m-%dT%H:%M:%S%z",        # 2025-11-17T12:48:01+00:00
                "%Y-%m-%dT%H:%M:%S"           # 2025-11-17T12:48:01
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    # 如果没有时区信息，添加UTC时区
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except ValueError:
                    continue
                    
            # 如果所有格式都失败，尝试使用fromisoformat（Python 3.7+）
            try:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                pass
                
    except (ValueError, TypeError) as e:
        logger.error(f"时间解析错误: {e}, 输入: {time_str}")
        return None
        
    return None


class MySQLClient:
    """MySQL数据库客户端"""
    
    def __init__(self, config):
        self.config = config
        self.mysql_config = config.get('mysql', {})
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.mysql_config.get('host', 'localhost'),
                port=int(self.mysql_config.get('port', 3306)),
                user=self.mysql_config.get('username', 'root'),
                password=self.mysql_config.get('password', ''),
                database=self.mysql_config.get('database', 'flowus'),
                charset=self.mysql_config.get('charset', 'utf8mb4'),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def create_tables(self):
        """创建数据表"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                # 创建页面信息表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flowus_pages (
                        id VARCHAR(50) PRIMARY KEY,
                        parent_id VARCHAR(50),
                        created_time DATETIME,
                        created_by VARCHAR(50),
                        last_edited_time DATETIME,
                        last_edited_by VARCHAR(50),
                        archived BOOLEAN DEFAULT FALSE,
                        properties JSON,
                        title TEXT,
                        raw_response JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_parent_id (parent_id),
                        INDEX idx_created_time (created_time),
                        INDEX idx_last_edited_time (last_edited_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 创建页面块内容表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flowus_blocks (
                        id VARCHAR(50) PRIMARY KEY,
                        parent_id VARCHAR(50),
                        parent_table_id VARCHAR(50),
                        created_time DATETIME,
                        created_by VARCHAR(50),
                        last_edited_time DATETIME,
                        last_edited_by VARCHAR(50),
                        archived BOOLEAN DEFAULT FALSE,
                        has_children BOOLEAN DEFAULT FALSE,
                        type VARCHAR(50),
                        data JSON,
                        raw_response JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_parent_id (parent_id),
                        INDEX idx_parent_table_id (parent_table_id),
                        INDEX idx_type (type),
                        INDEX idx_created_time (created_time),
                        FOREIGN KEY (parent_table_id) REFERENCES flowus_pages(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 创建日记记录表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flowus_diary (
                        id VARCHAR(50) PRIMARY KEY,
                        title TEXT,
                        category VARCHAR(50),
                        completed BOOLEAN DEFAULT FALSE,
                        start_time DATETIME,
                        last_edited_time DATETIME,
                        created_time DATETIME,
                        problem_record_links JSON,
                        project_record_links JSON,
                        properties JSON,
                        raw_response JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_category (category),
                        INDEX idx_start_time (start_time),
                        INDEX idx_last_edited_time (last_edited_time),
                        INDEX idx_created_time (created_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 创建问题记录表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flowus_problem_records (
                        id VARCHAR(50) PRIMARY KEY,
                        title TEXT,
                        content TEXT,
                        priority VARCHAR(20),
                        status VARCHAR(20),
                        created_time DATETIME,
                        last_edited_time DATETIME,
                        created_by VARCHAR(50),
                        assigned_to VARCHAR(50),
                        tags JSON,
                        properties JSON,
                        raw_response JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_priority (priority),
                        INDEX idx_status (status),
                        INDEX idx_created_time (created_time),
                        INDEX idx_last_edited_time (last_edited_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 创建项目记录表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS flowus_project_records (
                        id VARCHAR(50) PRIMARY KEY,
                        title TEXT,
                        description TEXT,
                        status VARCHAR(20),
                        progress INT DEFAULT 0,
                        start_date DATETIME,
                        end_date DATETIME,
                        created_time DATETIME,
                        last_edited_time DATETIME,
                        created_by VARCHAR(50),
                        team_members JSON,
                        milestones JSON,
                        properties JSON,
                        raw_response JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_status (status),
                        INDEX idx_progress (progress),
                        INDEX idx_start_date (start_date),
                        INDEX idx_end_date (end_date),
                        INDEX idx_created_time (created_time)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                logger.info("数据表创建成功")
                return True
                
        except Exception as e:
            logger.error(f"创建数据表失败: {e}")
            return False
    
    def insert_page(self, page_data: Dict[str, Any]) -> bool:
        """插入页面信息"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                # 提取标题
                title = ""
                if 'properties' in page_data and 'title' in page_data['properties']:
                    title_items = page_data['properties']['title'].get('title', [])
                    title = ' '.join([item.get('plain_text', '') for item in title_items])
                
                sql = """
                    INSERT INTO flowus_pages 
                    (id, parent_id, created_time, created_by, last_edited_time, last_edited_by, 
                     archived, properties, title, raw_response)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    parent_id = VALUES(parent_id),
                    created_time = VALUES(created_time),
                    created_by = VALUES(created_by),
                    last_edited_time = VALUES(last_edited_time),
                    last_edited_by = VALUES(last_edited_by),
                    archived = VALUES(archived),
                    properties = VALUES(properties),
                    title = VALUES(title),
                    raw_response = VALUES(raw_response),
                    updated_at = CURRENT_TIMESTAMP
                """
                
                cursor.execute(sql, (
                    page_data.get('id'),
                    page_data.get('parent_id'),
                    parse_iso_time(page_data.get('created_time')),
                    page_data.get('created_by', {}).get('id') if page_data.get('created_by') else None,
                    parse_iso_time(page_data.get('last_edited_time')),
                    page_data.get('last_edited_by', {}).get('id') if page_data.get('last_edited_by') else None,
                    page_data.get('archived', False),
                    json.dumps(page_data.get('properties', {}), ensure_ascii=False),
                    title,
                    json.dumps(page_data, ensure_ascii=False)
                ))
                
                logger.debug(f"插入页面信息: {page_data.get('id')} - {title}")
                return True
                
        except Exception as e:
            logger.error(f"插入页面信息失败: {e}")
            return False
    
    def insert_blocks(self, page_id: str, blocks_data: Dict[str, Any]) -> bool:
        """插入页面块内容"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                results = blocks_data.get('results', [])
                
                for block in results:
                    sql = """
                        INSERT INTO flowus_blocks 
                        (id, parent_id, parent_table_id, created_time, created_by, last_edited_time, 
                         last_edited_by, archived, has_children, type, data, raw_response)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        parent_id = VALUES(parent_id),
                        created_time = VALUES(created_time),
                        created_by = VALUES(created_by),
                        last_edited_time = VALUES(last_edited_time),
                        last_edited_by = VALUES(last_edited_by),
                        archived = VALUES(archived),
                        has_children = VALUES(has_children),
                        type = VALUES(type),
                        data = VALUES(data),
                        raw_response = VALUES(raw_response),
                        updated_at = CURRENT_TIMESTAMP
                    """
                    
                    cursor.execute(sql, (
                        block.get('id'),
                        block.get('parent', {}).get('block_id') if block.get('parent') else None,
                        page_id,
                        parse_iso_time(block.get('created_time')),
                        block.get('created_by', {}).get('id') if block.get('created_by') else None,
                        parse_iso_time(block.get('last_edited_time')),
                        block.get('last_edited_by', {}).get('id') if block.get('last_edited_by') else None,
                        block.get('archived', False),
                        block.get('has_children', False),
                        block.get('type'),
                        json.dumps(block.get('data', {}), ensure_ascii=False),
                        json.dumps(block, ensure_ascii=False)
                    ))
                
                logger.debug(f"插入页面块内容: {page_id} - {len(results)} 个块")
                return True
                
        except Exception as e:
            logger.error(f"插入页面块内容失败: {e}")
            return False
    
    def get_page_content(self, page_id: str) -> Optional[str]:
        """获取页面内容用于AI处理"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            with self.connection.cursor() as cursor:
                # 获取页面信息
                cursor.execute("SELECT * FROM flowus_pages WHERE id = %s", (page_id,))
                page = cursor.fetchone()
                
                if not page:
                    logger.warning(f"页面不存在: {page_id}")
                    return None
                
                # 获取页面的所有块
                cursor.execute("SELECT * FROM flowus_blocks WHERE parent_table_id = %s ORDER BY created_time", (page_id,))
                blocks = cursor.fetchall()
                
                # 构建内容
                content_parts = []
                
                # 添加页面标题和属性
                if page['title']:
                    content_parts.append(f"# {page['title']}")
                
                # 添加块内容
                for block in blocks:
                    block_type = block['type']
                    block_data = json.loads(block['data']) if block['data'] else {}
                    
                    if block_type == 'paragraph':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(text)
                    
                    elif block_type == 'heading_1':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(f"# {text}")
                    
                    elif block_type == 'heading_2':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(f"## {text}")
                    
                    elif block_type == 'heading_3':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(f"### {text}")
                    
                    elif block_type == 'bulleted_list_item':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(f"- {text}")
                    
                    elif block_type == 'numbered_list_item':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(f"1. {text}")
                    
                    elif block_type == 'code':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(f"```\n{text}\n```")
                    
                    elif block_type == 'quote':
                        rich_text = block_data.get('rich_text', [])
                        text = ' '.join([item.get('plain_text', '') for item in rich_text])
                        if text:
                            content_parts.append(f"> {text}")
                    
                    # 可以根据需要添加更多块类型的处理
                
                content = '\n\n'.join(content_parts)
                logger.info(f"获取页面内容: {page_id} - {len(content)} 字符")
                return content
                
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return None
    
    def get_recent_pages(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取最近N天的页面"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM flowus_pages 
                    WHERE created_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY created_time DESC
                """, (days,))
                pages = cursor.fetchall()
                logger.info(f"获取最近 {days} 天的页面: {len(pages)} 个")
                return pages
                
        except Exception as e:
            logger.error(f"获取最近页面失败: {e}")
            return []
    
    def insert_diary_record(self, record_data: Dict[str, Any]) -> bool:
        """插入日记记录"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                # 提取标题
                title = ""
                if 'title' in record_data and 'title' in record_data['title']:
                    title_items = record_data['title']['title']
                    title = ' '.join([item.get('plain_text', '') for item in title_items])
                
                # 提取分类
                category = None
                if 'properties' in record_data and '分类' in record_data['properties']:
                    category_data = record_data['properties']['分类']
                    if 'select' in category_data:
                        category = category_data['select'].get('name')
                
                # 提取完成状态
                completed = False
                if 'properties' in record_data and '完成' in record_data['properties']:
                    completed = record_data['properties']['完成'].get('checkbox', False)
                
                # 提取时间
                start_time = None
                last_edited_time = None
                if 'properties' in record_data:
                    if '开始时间' in record_data['properties']:
                        start_time = record_data['properties']['开始时间'].get('date', {}).get('start')
                    if '最近编辑时间' in record_data['properties']:
                        last_edited_time = record_data['properties']['最近编辑时间'].get('date', {}).get('start')
                
                # 提取关联链接
                problem_links = None
                project_links = None
                if 'properties' in record_data:
                    if '问题记录总表链接' in record_data['properties']:
                        problem_links = record_data['properties']['问题记录总表链接'].get('relation', [])
                    if '项目总表' in record_data['properties']:
                        project_links = record_data['properties']['项目总表'].get('relation', [])
                
                sql = """
                    INSERT INTO flowus_diary
                    (id, title, category, completed, start_time, last_edited_time, created_time,
                     problem_record_links, project_record_links, properties, raw_response)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    category = VALUES(category),
                    completed = VALUES(completed),
                    start_time = VALUES(start_time),
                    last_edited_time = VALUES(last_edited_time),
                    problem_record_links = VALUES(problem_record_links),
                    project_record_links = VALUES(project_record_links),
                    properties = VALUES(properties),
                    raw_response = VALUES(raw_response),
                    updated_at = CURRENT_TIMESTAMP
                """
                
                cursor.execute(sql, (
                    record_data.get('id'),
                    title,
                    category,
                    completed,
                    parse_iso_time(start_time),
                    parse_iso_time(last_edited_time),
                    parse_iso_time(record_data.get('created_time')),
                    json.dumps(problem_links, ensure_ascii=False) if problem_links else None,
                    json.dumps(project_links, ensure_ascii=False) if project_links else None,
                    json.dumps(record_data.get('properties', {}), ensure_ascii=False),
                    json.dumps(record_data, ensure_ascii=False)
                ))
                
                logger.debug(f"插入日记记录: {record_data.get('id')} - {title}")
                return True
                
        except Exception as e:
            logger.error(f"插入日记记录失败: {e}")
            return False
    
    def insert_problem_record(self, page_data: Dict[str, Any]) -> bool:
        """插入问题记录"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                # 提取标题
                title = ""
                if 'properties' in page_data and 'title' in page_data['properties']:
                    title_items = page_data['properties']['title'].get('title', [])
                    title = ' '.join([item.get('plain_text', '') for item in title_items])
                
                # 提取内容（从页面块中获取）
                content = ""
                blocks_content = []
                
                # 检查是否有块内容
                if 'blocks' in page_data:
                    logger.info(f"处理问题记录 {page_data.get('id')} 的块内容")
                    blocks_data = page_data['blocks']
                    if 'results' in blocks_data:
                        for block in blocks_data['results']:
                            block_type = block.get('type', '')
                            block_data = block.get('data', {})
                            
                            if block_type == 'paragraph':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(text)
                            elif block_type == 'heading_1':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(f"# {text}")
                            elif block_type == 'heading_2':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(f"## {text}")
                            elif block_type == 'bulleted_list_item':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(f"- {text}")
                        
                        content = '\n\n'.join(blocks_content)
                        logger.info(f"从 {len(blocks_data['results'])} 个块中提取了 {len(content)} 字符的内容")
                    else:
                        logger.warning(f"问题记录 {page_data.get('id')} 的blocks中没有results字段")
                else:
                    logger.warning(f"问题记录 {page_data.get('id')} 没有blocks内容")
                
                # 保存块内容到单独的表
                if 'blocks' in page_data and 'results' in page_data['blocks']:
                    blocks_saved = self.insert_blocks(page_data.get('id'), page_data['blocks'])
                    if blocks_saved:
                        logger.info(f"成功保存问题记录 {page_data.get('id')} 的 {len(page_data['blocks']['results'])} 个块")
                    else:
                        logger.error(f"保存问题记录 {page_data.get('id')} 的块内容失败")
                
                sql = """
                    INSERT INTO flowus_problem_records
                    (id, title, content, created_time, last_edited_time, created_by,
                     properties, raw_response)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    content = VALUES(content),
                    created_time = VALUES(created_time),
                    last_edited_time = VALUES(last_edited_time),
                    created_by = VALUES(created_by),
                    properties = VALUES(properties),
                    raw_response = VALUES(raw_response),
                    updated_at = CURRENT_TIMESTAMP
                """
                
                cursor.execute(sql, (
                    page_data.get('id'),
                    title,
                    content,
                    parse_iso_time(page_data.get('created_time')),
                    parse_iso_time(page_data.get('last_edited_time')),
                    page_data.get('created_by', {}).get('id') if page_data.get('created_by') else None,
                    json.dumps(page_data.get('properties', {}), ensure_ascii=False),
                    json.dumps(page_data, ensure_ascii=False)
                ))
                
                logger.info(f"插入问题记录: {page_data.get('id')} - {title}, 内容长度: {len(content)}")
                return True
                
        except Exception as e:
            logger.error(f"插入问题记录失败: {e}")
            return False
    
    def insert_project_record(self, page_data: Dict[str, Any]) -> bool:
        """插入项目记录"""
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            with self.connection.cursor() as cursor:
                # 提取标题
                title = ""
                if 'properties' in page_data and 'title' in page_data['properties']:
                    title_items = page_data['properties']['title'].get('title', [])
                    title = ' '.join([item.get('plain_text', '') for item in title_items])
                
                # 提取描述（从页面块中获取）
                description = ""
                blocks_content = []
                
                # 检查是否有块内容
                if 'blocks' in page_data:
                    logger.info(f"处理项目记录 {page_data.get('id')} 的块内容")
                    blocks_data = page_data['blocks']
                    if 'results' in blocks_data:
                        for block in blocks_data['results']:
                            block_type = block.get('type', '')
                            block_data = block.get('data', {})
                            
                            if block_type == 'paragraph':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(text)
                            elif block_type == 'heading_1':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(f"# {text}")
                            elif block_type == 'heading_2':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(f"## {text}")
                            elif block_type == 'bulleted_list_item':
                                rich_text = block_data.get('rich_text', [])
                                text = ' '.join([item.get('plain_text', '') for item in rich_text])
                                if text:
                                    blocks_content.append(f"- {text}")
                        
                        description = '\n\n'.join(blocks_content)
                        logger.info(f"从 {len(blocks_data['results'])} 个块中提取了 {len(description)} 字符的描述")
                    else:
                        logger.warning(f"项目记录 {page_data.get('id')} 的blocks中没有results字段")
                else:
                    logger.warning(f"项目记录 {page_data.get('id')} 没有blocks内容")
                
                # 保存块内容到单独的表
                if 'blocks' in page_data and 'results' in page_data['blocks']:
                    blocks_saved = self.insert_blocks(page_data.get('id'), page_data['blocks'])
                    if blocks_saved:
                        logger.info(f"成功保存项目记录 {page_data.get('id')} 的 {len(page_data['blocks']['results'])} 个块")
                    else:
                        logger.error(f"保存项目记录 {page_data.get('id')} 的块内容失败")
                
                sql = """
                    INSERT INTO flowus_project_records
                    (id, title, description, created_time, last_edited_time, created_by,
                     properties, raw_response)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    description = VALUES(description),
                    created_time = VALUES(created_time),
                    last_edited_time = VALUES(last_edited_time),
                    created_by = VALUES(created_by),
                    properties = VALUES(properties),
                    raw_response = VALUES(raw_response),
                    updated_at = CURRENT_TIMESTAMP
                """
                
                cursor.execute(sql, (
                    page_data.get('id'),
                    title,
                    description,
                    parse_iso_time(page_data.get('created_time')),
                    parse_iso_time(page_data.get('last_edited_time')),
                    page_data.get('created_by', {}).get('id') if page_data.get('created_by') else None,
                    json.dumps(page_data.get('properties', {}), ensure_ascii=False),
                    json.dumps(page_data, ensure_ascii=False)
                ))
                
                logger.info(f"插入项目记录: {page_data.get('id')} - {title}, 描述长度: {len(description)}")
                return True
                
        except Exception as e:
            logger.error(f"插入项目记录失败: {e}")
            return False
    
    def get_recent_diary_records(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取最近N天的日记记录"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM flowus_diary
                    WHERE created_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY created_time DESC
                """, (days,))
                records = cursor.fetchall()
                logger.info(f"获取最近 {days} 天的日记记录: {len(records)} 个")
                return records
                
        except Exception as e:
            logger.error(f"获取最近日记记录失败: {e}")
            return []
    
    def get_recent_problem_records(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取最近N天的问题记录"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM flowus_problem_records
                    WHERE created_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY created_time DESC
                """, (days,))
                records = cursor.fetchall()
                logger.info(f"获取最近 {days} 天的问题记录: {len(records)} 个")
                return records
                
        except Exception as e:
            logger.error(f"获取最近问题记录失败: {e}")
            return []
    
    def get_recent_project_records(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取最近N天的项目记录"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM flowus_project_records
                    WHERE created_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    ORDER BY created_time DESC
                """, (days,))
                records = cursor.fetchall()
                logger.info(f"获取最近 {days} 天的项目记录: {len(records)} 个")
                return records
                
        except Exception as e:
            logger.error(f"获取最近项目记录失败: {e}")
            return []