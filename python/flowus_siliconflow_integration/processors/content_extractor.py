"""
内容提取器
"""

from processors.database_processor import DatabaseProcessor
from processors.page_formatter import PageFormatter


class ContentExtractor:
    """内容提取器"""
    
    def __init__(self, config, flowus_client):
        self.config = config
        self.flowus_client = flowus_client
        self.database_processor = DatabaseProcessor(config, flowus_client)
        self.page_formatter = PageFormatter(config, flowus_client)
    
    def extract_content_from_blocks(self, blocks_data):
        """从块数据中提取文本内容"""
        print(f"调试 - blocks_data类型: {type(blocks_data)}, 内容: {blocks_data}")  # 调试日志
        text_content = []
        
        if not blocks_data:
            print("警告: 接收到空的blocks_data")
            return ""
            
        # 统一处理blocks_data为列表
        if isinstance(blocks_data, dict):
            if 'results' in blocks_data:
                blocks_list = blocks_data['results']
            elif 'records' in blocks_data:  # 处理数据库记录格式
                blocks_list = blocks_data['records']
            else:
                print(f"警告: 无法识别的字典格式: {blocks_data.keys()}")
                blocks_list = []
        elif isinstance(blocks_data, list):
            blocks_list = blocks_data
        else:
            print(f"错误: 不支持的blocks_data类型: {type(blocks_data)}")
            blocks_list = []
        
        # 提取普通文本内容
        text_content.extend(self._extract_basic_text({'results': blocks_list}))
        
        # 提取数据库内容（如果启用）
        if self.config.get('database', {}).get('enabled', True):
            database_content = self._extract_database_content(blocks_data)
            if database_content:
                text_content.append("\n" + "="*60)
                text_content.append("关联数据库内容:")
                text_content.append("="*60)
                text_content.append(database_content)
        
        # 提取链接内容
        links_content = self._extract_links_content({'results': blocks_list})
        if links_content:
            text_content.append("\n" + "="*60)
            text_content.append("关联链接内容:")
            text_content.append("="*60)
            text_content.append(links_content)
        
        return '\n'.join(text_content)
    
    def _extract_basic_text(self, blocks_data):
        """提取基础文本内容"""
        text_content = []
        
        if not isinstance(blocks_data.get('results'), list):
            return []
            
        for block in blocks_data['results']:
            if not isinstance(block, dict):
                continue
                
            block_type = block.get('type')
            block_data = block.get('data', {})
            
            # 处理文本类块
            if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3',
                            'bulleted_list_item', 'numbered_list_item', 'to_do',
                            'quote', 'toggle', 'callout']:
                rich_text = block_data.get('rich_text', [])
                block_text = []
                for text_item in rich_text:
                    if isinstance(text_item, dict) and text_item.get('type') == 'text' and 'plain_text' in text_item:
                        block_text.append(text_item['plain_text'])
                if block_text:
                    # 添加块类型前缀
                    prefix = {
                        'heading_1': '# ',
                        'heading_2': '## ',
                        'heading_3': '### ',
                        'bulleted_list_item': '* ',
                        'numbered_list_item': '1. ',
                        'to_do': '- [ ] ',
                        'quote': '> ',
                        'callout': '💡 '
                    }.get(block_type, '')
                    text_content.append(prefix + ''.join(block_text))
            
            # 处理代码块
            elif block_type == 'code':
                code_text = '\n'.join([
                    text_item['plain_text']
                    for text_item in block_data.get('rich_text', [])
                    if isinstance(text_item, dict) and 'plain_text' in text_item
                ])
                if code_text:
                    text_content.append(f"```{block_data.get('language', '')}\n{code_text}\n```")
            
            # 处理分割线
            elif block_type == 'divider':
                text_content.append("---")
            
            # 处理表格
            elif block_type == 'table':
                table_content = self._extract_table_content(block_data)
                if table_content:
                    text_content.append(table_content)
        
        return text_content

    def _extract_table_content(self, table_data):
        """提取表格内容"""
        if not isinstance(table_data, dict):
            return ""
            
        table_rows = []
        
        # 提取表头
        if table_data.get('has_column_header'):
            header_row = []
            for cell in table_data.get('header_cells', []):
                header_row.append(''.join([t.get('plain_text', '') for t in cell]))
            table_rows.append('| ' + ' | '.join(header_row) + ' |')
            table_rows.append('|' + '|'.join(['---'] * len(header_row)) + '|')
        
        # 提取表格内容
        for row in table_data.get('rows', []):
            row_content = []
            for cell in row.get('cells', []):
                row_content.append(''.join([t.get('plain_text', '') for t in cell]))
            table_rows.append('| ' + ' | '.join(row_content) + ' |')
        
        return '\n'.join(table_rows)
    
    def _extract_database_content(self, blocks_data):
        """提取数据库内容"""
        print(f"调试 - 数据库处理输入数据: {type(blocks_data)}, {blocks_data}")  # 新增调试日志
        database_blocks = self.database_processor.extract_database_info(blocks_data)
        print(f"调试 - 提取到的数据库块: {database_blocks}")  # 新增调试日志
        if not database_blocks:
            return ""
        
        database_content = []
        for db_info in database_blocks:
            print(f"处理数据库: {db_info['title']} (ID: {db_info['id']}, 来源: {db_info['source']})")
            db_content = self.flowus_client.get_database_content(db_info['id'])
            if db_content:
                formatted_db_content = self.database_processor.format_database_content(db_info, db_content)
                database_content.append(formatted_db_content)
            else:
                database_content.append(f"数据库 '{db_info['title']}' 内容获取失败")
        
        return '\n\n'.join(database_content)
    
    def _extract_links_content(self, blocks_data):
        """提取链接内容"""
        links_content = []
        
        if not isinstance(blocks_data, list):
            return []
            
        for block in blocks_data:
            if not isinstance(block, dict):
                continue
                
            block_type = block.get('type')
            block_data = block.get('data', {})
            
            # 处理文本块中的链接
            if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3',
                            'bulleted_list_item', 'numbered_list_item', 'to_do',
                            'quote', 'toggle', 'callout']:
                rich_text = block_data.get('rich_text', [])
                for text_item in rich_text:
                    if not isinstance(text_item, dict):
                        continue
                        
                    # 处理文本链接
                    if text_item.get('type') == 'text' and text_item.get('text', {}).get('link'):
                        link = text_item['text']['link']
                        links_content.append(f"链接: {text_item.get('plain_text', '无标题')} ({link.get('url', '无URL')})")
                    
                    # 处理页面提及
                    elif text_item.get('type') == 'mention' and text_item.get('mention', {}).get('type') == 'page':
                        page_id = text_item['mention']['page']['id']
                        page_title = self.flowus_client.get_page_title(page_id)
                        links_content.append(f"关联页面: {page_title} (ID: {page_id})")
                        
                        # 获取关联页面内容
                        linked_content = self.flowus_client.get_page_content(page_id)
                        if linked_content:
                            extracted_content = self.extract_content_from_blocks(linked_content)
                            links_content.append(f"关联页面内容:\n{extracted_content}")
            
            # 处理书签块
            elif block_type == 'bookmark' and block_data.get('url'):
                links_content.append(f"书签: {block_data.get('title', '无标题')} ({block_data.get('url')})")
            
            # 处理文件块
            elif block_type == 'file' and block_data.get('url'):
                links_content.append(f"文件: {block_data.get('name', '未命名文件')} ({block_data.get('url')})")
            
            # 处理内嵌块
            elif block_type == 'embed' and block_data.get('url'):
                links_content.append(f"内嵌内容: {block_data.get('title', '无标题')} ({block_data.get('url')})")
        
        return '\n\n'.join(links_content)