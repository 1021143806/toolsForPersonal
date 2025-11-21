"""
数据库处理器
"""

import datetime


class DatabaseProcessor:
    """数据库处理器"""
    
    def __init__(self, config, flowus_client):
        self.config = config
        self.flowus_client = flowus_client
        self.database_config = config.get('database', {})

    @staticmethod
    def parse_iso_time(time_str):
        """解析ISO 8601时间字符串为datetime对象(带UTC时区)"""
        from datetime import datetime, timezone
        
        print(f"调试 - 解析时间字符串: {time_str}, 类型: {type(time_str)}")
        
        if not time_str:
            return None
            
        try:
            # 处理时间戳格式
            if isinstance(time_str, (int, float)):
                print(f"调试 - 处理时间戳格式: {time_str}")
                return datetime.fromtimestamp(time_str/1000, tz=timezone.utc)
                
            # 处理ISO 8601字符串格式
            if isinstance(time_str, str):
                print(f"调试 - 处理ISO字符串格式: {time_str}")
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
                        print(f"调试 - 成功解析时间: {dt}")
                        return dt
                    except ValueError:
                        continue
                        
                # 如果所有格式都失败，尝试使用fromisoformat（Python 3.7+）
                try:
                    dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    print(f"调试 - fromisoformat成功解析: {dt}")
                    return dt
                except ValueError:
                    pass
                    
        except (ValueError, TypeError) as e:
            print(f"时间解析错误: {e}, 输入: {time_str}")
            return None
            
        print(f"调试 - 无法解析时间: {time_str}")
        return None

    
    def extract_database_info(self, blocks_data):
        """从块数据中提取数据库信息"""
        database_blocks = []
        mentioned_databases = []
        
        if not blocks_data:
            return []
            
        # 统一处理blocks_data为列表
        blocks_list = blocks_data if isinstance(blocks_data, list) else blocks_data.get('results', [])
        
        print(f"调试数据库处理器 - 输入type: {type(blocks_data)}")
        if not blocks_list:
            print(f"调试数据库处理器 - blocks_list为空")
        else:
            print(f"调试数据库处理器 - blocks_list长度: {len(blocks_list)}, 第一项type: {type(blocks_list[0])}")
        
        for block in blocks_list:
            print(f"调试数据库处理器 - block类型: {type(block)}")
            if not isinstance(block, dict):
                print(f"调试数据库处理器 - 跳过非字典block: {type(block)}")
                continue
                
            # 检查直接嵌入的数据库块
            if 'type' in block and block['type'] in ['child_database', 'database']:
                database_info = {
                    'id': block.get('id'),
                    'type': block.get('type'),
                    'title': self.extract_database_title(block),
                    'created_time': block.get('created_time'),
                    'last_edited_time': block.get('last_edited_time'),
                    'source': 'embedded'
                }
                database_blocks.append(database_info)
            
            # 检查页面提及中的数据库
            elif (block.get('type') == 'paragraph' and
                  'data' in block and
                  'rich_text' in block['data']):
                    for text_item in block['data']['rich_text']:
                        if (text_item['type'] == 'mention' and 
                            'mention' in text_item and 
                            text_item['mention']['type'] == 'page'):
                            mentioned_page_id = text_item['mention']['page']['id']
                            if self.flowus_client.is_database(mentioned_page_id):
                                db_info = self.flowus_client.get_database_info(mentioned_page_id)
                                if db_info:
                                    db_info['source'] = 'mentioned'
                                    mentioned_databases.append(db_info)
        
        # 合并去重
        all_databases = database_blocks
        seen_ids = {db['id'] for db in database_blocks}
        
        for db in mentioned_databases:
            if db['id'] not in seen_ids:
                all_databases.append(db)
                seen_ids.add(db['id'])
        
        return all_databases
    
    @staticmethod
    def extract_database_title(database_block):
        """提取数据库标题"""
        if 'data' in database_block and 'title' in database_block['data']:
            title_data = database_block['data']['title']
            if isinstance(title_data, str):
                return title_data
            elif isinstance(title_data, list) and len(title_data) > 0:
                title_parts = []
                for item in title_data:
                    if isinstance(item, dict) and 'text' in item and 'content' in item['text']:
                        title_parts.append(item['text']['content'])
                    elif isinstance(item, dict) and 'plain_text' in item:
                        title_parts.append(item['plain_text'])
                return ''.join(title_parts) if title_parts else "未命名数据库"
        return "未命名数据库"
    
    @staticmethod
    def extract_database_title_from_db_object(db_object):
        """从数据库对象中提取标题"""
        if 'title' in db_object:
            title_data = db_object['title']
            if isinstance(title_data, list):
                title_parts = []
                for item in title_data:
                    if isinstance(item, dict):
                        if 'text' in item and 'content' in item['text']:
                            title_parts.append(item['text']['content'])
                        elif 'plain_text' in item:
                            title_parts.append(item['plain_text'])
                return ''.join(title_parts) if title_parts else "未命名数据库"
        return "未命名数据库"
    
    def format_database_content(self, database_info, database_content):
        """格式化数据库内容
        Args:
            database_info: 数据库信息字典
            database_content: 数据库内容
        """
        db_config = self.database_config
        page_size = db_config.get('page_size', 5)  # 默认每页5条
        stop_before = db_config.get('stop_before')  # 配置中的停止时间
        
        # 处理配置中的stop_before时间
        if stop_before:
            if isinstance(stop_before, (int, float)):
                # 处理时间戳格式
                stop_before = self.parse_iso_time(stop_before)
            else:
                stop_before = self.parse_iso_time(stop_before)
            if stop_before and stop_before.tzinfo is None:
                from datetime import timezone
                stop_before = stop_before.replace(tzinfo=timezone.utc)
        
        formatted = []
        formatted.append(f"数据库: {database_info.get('title', '无标题')}")
        formatted.append(f"每页记录数: {page_size}")
        formatted.append(f"停止时间: {stop_before.astimezone().isoformat()}" if stop_before else "无时间限制")
        formatted.append("=" * 60)
        
        from processors.page_formatter import PageFormatter
        page_formatter = PageFormatter(self.config, self.flowus_client)
        
        all_records = []
        current_content = database_content
        should_stop = False
        
        while current_content and not should_stop:
            records = current_content.get('results', [])
            if not records:
                break
                
            for record in records:
                created_time = record.get('created_time')
                if created_time:
                    record_time = self.parse_iso_time(created_time)
                    if record_time is None:
                        print(f"无法解析记录时间: {created_time}")
                        continue
                        
                    if stop_before:
                        # 确保两个时间都带有时区信息
                        from datetime import timezone
                        if record_time.tzinfo is None:
                            record_time = record_time.replace(tzinfo=timezone.utc)
                        if stop_before.tzinfo is None:
                            stop_before = stop_before.replace(tzinfo=timezone.utc)
                            
                        # 统一转换为UTC时区后再比较
                        if record_time.astimezone(timezone.utc) < stop_before.astimezone(timezone.utc):
                            should_stop = True
                            break
                
                all_records.append(record)
            
            if should_stop:
                break
                
            if not current_content.get('has_more'):
                break
                
            next_cursor = current_content.get('next_cursor')
            if not next_cursor:
                break
                
            current_content = self.flowus_client.get_database_content(
                database_info['id'],
                start_cursor=next_cursor
            )
        
        formatted.append(f"获取记录数: {len(all_records)}")
        
        for i, record in enumerate(all_records, 1):
            if not isinstance(record, dict) or 'id' not in record:
                continue
                
            record_id = record.get('id')
            
            if record_id in self.flowus_client.processed_pages:
                formatted.append(f"\n记录 {i} [已处理页面: {record_id}]")
                continue
                
            formatted.append(f"\n记录 {i} (ID: {record_id}, 创建于: {record.get('created_time', '未知时间')}):")
            self.flowus_client.processed_pages.add(record_id)
            
            try:
                record_details = self.flowus_client.get_page_details(record_id)
                if isinstance(record_details, dict) and 'properties' in record_details:
                    formatted_record = page_formatter.format_page_details(record_details)
                    formatted.append(formatted_record)
                else:
                    formatted.append(f"\n记录 {i} [无效数据格式]")
            except Exception as e:
                formatted.append(f"\n记录 {i} [处理出错: {str(e)}]")
            
            links = self.flowus_client.get_links_from_page(record_id)
            if links:
                formatted.append("\n关联链接:")
                for link in links:
                    if 'page_id' in link:
                        page_title = self.flowus_client.get_page_title(link['page_id'])
                        formatted.append(f"- {link['text']} (页面ID: {link['page_id']}, 标题: {page_title})")
                    else:
                        formatted.append(f"- {link['text']} (URL: {link['url']})")
        
        return '\n'.join(formatted)