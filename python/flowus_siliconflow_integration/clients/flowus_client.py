"""
FlowUs API 客户端
"""

import http.client
import json
import logging
import os
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class FlowUsClient:
    """FlowUs API 客户端"""
    
    def __init__(self, config_loader):
        self.config_loader = config_loader
        self.config = config_loader.config
        self.flowus_token = self.config['flowus']['token']
        self.page_id = self._extract_page_id(self.config['flowus']['url'])
        self.processed_pages = set()
        self.page_details_cache = {}
    
    def _extract_page_id(self, url):
        """从URL中提取页面ID"""
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        if len(path_parts) >= 2:
            return path_parts[-1]
        else:
            raise ValueError("无法从URL中提取页面ID")
    
    def _make_request(self, method, endpoint, payload='', headers=None, max_retries=3):
        """发送HTTP请求到FlowUs API"""
        if headers is None:
            headers = {}
        
        default_headers = {
            'Authorization': self.flowus_token,
            'Content-Type': 'application/json'
        }
        default_headers.update(headers)
        
        last_error = None
        for attempt in range(max_retries):
            try:
                conn = http.client.HTTPSConnection("api.flowus.cn")
                conn.request(method, endpoint, payload, default_headers)
                res = conn.getresponse()
                data = res.read()
                
                if res.status == 200:
                    return json.loads(data.decode("utf-8"))
                elif res.status in [403, 404]:
                    return None
                elif res.status == 503 and attempt < max_retries - 1:
                    import time
                    time.sleep(1 * (attempt + 1))  # 指数退避
                    continue
                else:
                    print(f"FlowUs API请求失败，状态码: {res.status}")
                    print(f"响应内容: {data.decode('utf-8')}")
                    return None
                    
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    print(f"FlowUs API请求时出错: {e}")
                    return None
                import time
                time.sleep(1 * (attempt + 1))
        
        print(f"FlowUs API请求最终失败: {last_error}")
        return None
    
    def get_page_content(self, page_id=None):
        """获取页面子块内容
        调用API: /v1/blocks/{page_id}/children
        """
        if page_id is None:
            page_id = self.page_id
            
        if page_id in self.processed_pages:
            print(f"跳过已处理的页面: {page_id}")
            return None
            
        endpoint = f"/v1/blocks/{page_id}/children"
        result = self._make_request("GET", endpoint)
        
        if result:
            self.processed_pages.add(page_id)
            return result
            
        print(f"获取子块内容失败: {page_id}")
        return None

    def get_page_full_info(self, page_id=None):
        """获取页面完整信息(包含页面详情和子块信息)
        调用两个API:
        1. /v1/pages/{page_id} - 获取页面详情
        2. /v1/blocks/{page_id}/children - 获取子块内容
        """
        if page_id is None:
            page_id = self.page_id
            
        if page_id in self.processed_pages:
            print(f"跳过已处理的页面: {page_id}")
            return None

        result = {}
        
        # 获取页面详情
        page_details = self.get_page_details(page_id)
        if not page_details:
            print(f"获取页面详情失败: {page_id}")
            return None
        result["details"] = page_details
        
        # 获取子块内容
        page_content = self.get_page_content(page_id)
        if not page_content:
            print(f"获取子块内容失败: {page_id}")
            return None
        result["content"] = page_content
        
        self.processed_pages.add(page_id)
        return result
    
    def get_page_details(self, page_id):
        """获取页面详细信息"""
        if page_id in self.page_details_cache:
            return self.page_details_cache[page_id]
            
        endpoint = f"/v1/pages/{page_id}"
        page_data = self._make_request("GET", endpoint)
        
        if page_data:
            self.page_details_cache[page_id] = page_data
            
        return page_data
    
    def get_page_title(self, page_id):
        """获取页面标题"""
        if page_id in self.processed_pages:
            return f"[已处理页面: {page_id}]"
            
        page_data = self.get_page_details(page_id)
        if not page_data:
            return "未知页面"
        
        # 提取页面标题
        if 'properties' in page_data and 'title' in page_data['properties']:
            title_prop = page_data['properties']['title']
            if 'title' in title_prop:
                titles = title_prop['title']
                if titles and len(titles) > 0:
                    return titles[0].get('plain_text', '无标题')
        return "无标题"
    
    def is_database(self, page_id):
        """检查页面是否是数据库"""
        endpoint = f"/v1/databases/{page_id}"
        result = self._make_request("GET", endpoint)
        return result is not None
    
    def get_database_info(self, database_id):
        """获取数据库信息"""
        from processors.database_processor import DatabaseProcessor
        
        endpoint = f"/v1/databases/{database_id}"
        db_data = self._make_request("GET", endpoint)
        
        if db_data:
            return {
                'id': database_id,
                'type': 'database',
                'title': DatabaseProcessor.extract_database_title_from_db_object(db_data),
                'created_time': db_data.get('created_time'),
                'last_edited_time': db_data.get('last_edited_time'),
                'source': 'mentioned'
            }
        return None
    
    def check_config_update(self):
        """检查配置是否更新"""
        if os.path.getmtime(self.config_loader.config_file) > self.config_loader.last_modified:
            self.config = self.config_loader.load_config()
            self.flowus_token = self.config['flowus']['token']
            return True
        return False

    def get_database_content(self, database_id, start_cursor=None, start_date=None, end_date=None):
        """获取数据库内容(支持配置参数)
        Args:
            database_id: 数据库ID
            start_cursor: 分页游标
            start_date: 开始日期(用于时间过滤)
            end_date: 结束日期(用于时间过滤)
        """
        self.check_config_update()
        import json
        from datetime import datetime, timezone, timedelta
        
        # 从配置中读取参数
        db_config = self.config.get('database', {})
        page_size = db_config.get('page_size', 100)
        recent_days = db_config.get('recent_days', 30)
        include_properties = db_config.get('include_properties', True)
        include_mentioned = db_config.get('include_mentioned', True)
        fetch_relations = db_config.get('fetch_relations', True)
        
        logger.info(f"使用配置参数: page_size={page_size}, recent_days={recent_days}, include_properties={include_properties}")
        
        # 构建基础查询参数
        query_params = {
            "page_size": page_size,  # 使用配置的分页大小
            "sorts": [{
                "property": "Created Time",
                "direction": "descending"
            }]
        }
        
        # 添加时间过滤
        if start_date or end_date:
            filter_conditions = []
            if start_date:
                filter_conditions.append({
                    "property": "Created Time",
                    "date": {
                        "on_or_after": start_date.isoformat() if hasattr(start_date, 'isoformat') else start_date
                    }
                })
            if end_date:
                filter_conditions.append({
                    "property": "Created Time",
                    "date": {
                        "on_or_before": end_date.isoformat() if hasattr(end_date, 'isoformat') else end_date
                    }
                })
            
            if filter_conditions:
                if len(filter_conditions) == 1:
                    query_params["filter"] = filter_conditions[0]
                else:
                    query_params["filter"] = {
                        "and": filter_conditions
                    }
                logger.info(f"添加时间过滤: {filter_conditions}")
        elif recent_days:
            # 如果没有指定具体日期，使用recent_days配置
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=recent_days)
            
            query_params["filter"] = {
                "property": "Created Time",
                "date": {
                    "on_or_after": start_date.isoformat()
                }
            }
            logger.info(f"使用recent_days配置过滤最近{recent_days}天的数据")
        
        # 添加分页游标
        if start_cursor:
            query_params["start_cursor"] = start_cursor
        
        # 根据配置决定是否包含属性和关联信息
        if include_properties:
            # 这里可以添加属性过滤逻辑
            pass
        
        if include_mentioned:
            # 这里可以添加提及数据库的逻辑
            pass
        
        payload = json.dumps(query_params)
        endpoint = f"/v1/databases/{database_id}/query"
        
        logger.info(f"查询数据库 {database_id}, 参数: {query_params}")
        result = self._make_request("POST", endpoint, payload)
        
        if result:
            logger.info(f"获取到 {len(result.get('results', []))} 条记录")
            if fetch_relations:
                logger.info("fetch_relations配置为True，将处理关联关系")
                # 这里可以添加关联关系处理逻辑
        
        return result
    
    def get_all_database_records(self, database_id):
        """获取数据库所有符合条件的记录(按时间分页)"""
        all_records = []
        start_cursor = None
        has_more = True
        
        while has_more:
            result = self.get_database_content(database_id, start_cursor)
            if not result or 'results' not in result:
                break
                
            all_records.extend(result['results'])
            has_more = result.get('has_more', False)
            start_cursor = result.get('next_cursor')
            
            # 防止无限循环
            if not start_cursor:
                break
        
        return {'results': all_records}

    def process_database_links(self, database_id):
        """处理数据库中的链接(先获取所有记录再处理链接)"""
        import datetime
        
        # 1. 先获取所有数据库记录
        db_records = self.get_all_database_records(database_id)
        
        # 2. 提取所有链接
        links = []
        for record in db_records.get('results', []):
            if 'properties' in record:
                for prop_name, prop_value in record['properties'].items():
                    if prop_value.get('type') == 'url':
                        links.append(prop_value.get('url'))
                    elif prop_value.get('type') == 'page':
                        links.append(prop_value.get('page_id'))
        
        # 3. 处理链接
        processed_pages = set()
        for link in links:
            if link in processed_pages:
                continue
                
            if isinstance(link, str) and link.startswith('http'):
                # 处理外部链接
                print(f"处理外部链接: {link}")
            else:
                # 处理FlowUs页面链接
                page_data = self.get_page_full_info(link)
                if page_data:
                    processed_pages.add(link)
        
        # 4. 可选：按时间范围分批获取记录
        db_config = self.config.get('database', {})
        time_page_size = db_config.get('time_page_size', 1)
        max_time_range = db_config.get('max_time_range', 3)
        
        if time_page_size and max_time_range:
            all_records = []
            end_date = datetime.datetime.now(datetime.timezone.utc)
            start_date = end_date - datetime.timedelta(days=max_time_range)
            
            print(f"开始获取数据库记录，时间范围: {start_date.date()} 至 {end_date.date()}")
            print(f"时间分页大小: {time_page_size}天")
            
            while start_date < end_date:
                batch_end = min(start_date + datetime.timedelta(days=time_page_size), end_date)
                
                print(f"获取时间段: {start_date.date()} 至 {batch_end.date()}")
                records = self.get_database_content(
                    database_id,
                    start_date=start_date,
                    end_date=batch_end
                )
                
                if records and 'results' in records:
                    all_records.extend(records['results'])
                    print(f"获取到 {len(records['results'])} 条记录")
                
                start_date = batch_end
            
            print(f"总共获取到 {len(all_records)} 条记录")
            return {'results': all_records}
        
        return db_records
    
    def get_links_from_page(self, page_id):
        """获取页面中的所有链接"""
        page_content = self.get_page_content(page_id)
        if not page_content:
            return []
            
        links = []
        
        for block in page_content.get('results', []):
            if block['type'] == 'paragraph' and 'data' in block:
                rich_text = block['data'].get('rich_text', [])
                for text_item in rich_text:
                    if text_item['type'] == 'text' and 'text' in text_item and 'link' in text_item['text']:
                        links.append({
                            'text': text_item['plain_text'],
                            'url': text_item['text']['link']['url']
                        })
                    elif text_item['type'] == 'mention' and 'mention' in text_item:
                        if text_item['mention']['type'] == 'page':
                            links.append({
                                'text': text_item['plain_text'],
                                'page_id': text_item['mention']['page']['id']
                            })
        
        return links
    
    def create_page(self, title, parent_page_id=None):
        """创建新页面"""
        if parent_page_id is None:
            parent_page_id = self.config['flowus']['parent_page_id']
            
        new_page_config = self.config['new_page']
        
        payload = json.dumps({
            "parent": {
                "page_id": parent_page_id
            },
            "properties": {
                "title": {
                    "type": "title",
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            },
            "icon": {
                "emoji": new_page_config['icon_emoji']
            }
        })
        
        result = self._make_request("POST", "/v1/pages", payload)
        if result:
            print(f"成功创建新页面: {title}")
            print(f"页面URL: {result.get('url', 'N/A')}")
        return result
    
    def append_blocks(self, page_id, blocks_data):
        """向页面追加块内容"""
        payload = json.dumps({
            "children": blocks_data
        })
        
        endpoint = f"/v1/blocks/{page_id}/children"
        result = self._make_request("PATCH", endpoint, payload)
        
        if result:
            print(f"成功向页面添加 {len(blocks_data)} 个内容块")
        return result