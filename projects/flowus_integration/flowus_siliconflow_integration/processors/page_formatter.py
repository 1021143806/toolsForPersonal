"""
页面格式化器
"""
import logging
import json

import datetime


class PageFormatter:
    """页面格式化器"""
    
    def __init__(self, config, flowus_client):
        self.config = config
        self.flowus_client = flowus_client
        self.database_config = config.get('database', {})
    
    def format_page_details(self, page_data):
        """格式化页面详细信息"""
        if not page_data:
            return "无内容"
            
        logger = logging.getLogger(__name__)
        logger.info(f"格式化输入数据类型: {type(page_data)}")
        
        # 处理AI返回的字典响应
        if isinstance(page_data, dict):
            if 'choices' in page_data and len(page_data['choices']) > 0:
                content = page_data['choices'][0].get('message', {}).get('content', '')
                logger.info(f"从AI响应中提取内容，长度: {len(content)}")
                return content
            return json.dumps(page_data, ensure_ascii=False, indent=2)
            
        # 处理字符串内容
        if isinstance(page_data, str):
            logger.info(f"直接返回字符串内容，长度: {len(page_data)}")
            return page_data
            
        logger.warning(f"未知数据类型: {type(page_data)}")
        return str(page_data)
            
        # 如果是字典类型且包含properties字段，按原逻辑处理
        if isinstance(page_data, dict) and 'properties' in page_data:
            formatted_content = [f"页面ID: {page_data['id']}"]
            if 'created_time' in page_data:
                formatted_content.append(f"创建时间: {page_data['created_time']}")
            if 'last_edited_time' in page_data:
                formatted_content.append(f"最后编辑时间: {page_data['last_edited_time']}")
            return '\n'.join(formatted_content)
            
        # 如果是字符串类型，直接返回
        if isinstance(page_data, str):
            return page_data
            
        return str(page_data)
        
        formatted_content = [f"页面ID: {page_data['id']}"]
        
        # 添加页面基本信息
        if 'created_time' in page_data:
            formatted_content.append(f"创建时间: {page_data['created_time']}")
        if 'last_edited_time' in page_data:
            formatted_content.append(f"最后编辑时间: {page_data['last_edited_time']}")
        
        # 处理所有属性
        for prop_name, prop_value in page_data['properties'].items():
            prop_text = self.format_property_value(prop_value)
            if prop_text:
                formatted_content.append(f"{prop_name}: {prop_text}")
        
        return '\n'.join(formatted_content)
    
    def format_property_value(self, property_value):
        """格式化属性值为文本"""
        if not property_value:
            return ""
        
        prop_type = property_value.get('type')
        
        # 处理不同类型的属性
        type_handlers = {
            'title': self._format_title_property,
            'rich_text': self._format_rich_text_property,
            'number': self._format_number_property,
            'select': self._format_select_property,
            'multi_select': self._format_multi_select_property,
            'date': self._format_date_property,
            'checkbox': self._format_checkbox_property,
            'url': self._format_url_property,
            'email': self._format_email_property,
            'phone_number': self._format_phone_number_property,
            'people': self._format_people_property,
            'files': self._format_files_property,
            'status': self._format_status_property,
            'relation': self._format_relation_property,
            'formula': self._format_formula_property,
            'rollup': self._format_rollup_property,
            'created_time': self._format_created_time_property,
            'last_edited_time': self._format_last_edited_time_property,
            'created_by': self._format_created_by_property,
            'last_edited_by': self._format_last_edited_by_property
        }
        
        handler = type_handlers.get(prop_type)
        if handler:
            return handler(property_value)
        else:
            return f"[{prop_type}类型属性]"
    
    def _format_title_property(self, prop):
        titles = prop.get('title', [])
        if titles:
            return ' '.join([item.get('plain_text', '') for item in titles if item.get('plain_text')])
        return ""
    
    def _format_rich_text_property(self, prop):
        rich_texts = prop.get('rich_text', [])
        if rich_texts:
            return ' '.join([item.get('plain_text', '') for item in rich_texts if item.get('plain_text')])
        return ""
    
    def _format_number_property(self, prop):
        return str(prop.get('number', ''))
    
    def _format_select_property(self, prop):
        select_value = prop.get('select')
        if select_value and 'name' in select_value:
            return select_value['name']
        return ""
    
    def _format_multi_select_property(self, prop):
        multi_selects = prop.get('multi_select', [])
        if multi_selects:
            return ', '.join([item.get('name', '') for item in multi_selects if item.get('name')])
        return ""
    
    def _format_date_property(self, prop):
        date_value = prop.get('date')
        if date_value:
            start = date_value.get('start', '')
            end = date_value.get('end', '')
            if end:
                return f"{start} 到 {end}"
            else:
                return start
        return ""
    
    def _format_checkbox_property(self, prop):
        return "是" if prop.get('checkbox') else "否"
    
    def _format_url_property(self, prop):
        return prop.get('url', '')
    
    def _format_email_property(self, prop):
        return prop.get('email', '')
    
    def _format_phone_number_property(self, prop):
        return prop.get('phone_number', '')
    
    def _format_people_property(self, prop):
        people = prop.get('people', [])
        if people:
            return ', '.join([person.get('id', '') for person in people])
        return ""
    
    def _format_files_property(self, prop):
        files = prop.get('files', [])
        if files:
            return ', '.join([file.get('name', '') for file in files])
        return ""
    
    def _format_status_property(self, prop):
        status_value = prop.get('status')
        if status_value and 'name' in status_value:
            return status_value['name']
        return ""
    
    def _format_relation_property(self, prop):
        if not prop or 'relation' not in prop:
            return ""
        
        relation_items = prop['relation']
        if not relation_items:
            return ""
        
        if not self.database_config.get('fetch_relations', True):
            relation_count = len(relation_items)
            return f"[{relation_count}个关联页面]"
        
        relation_content = []
        for relation_item in relation_items[:3]:  # 限制最多3个
            page_id = relation_item.get('id')
            if page_id:
                if page_id in self.flowus_client.processed_pages:
                    relation_content.append(f"关联页面: [已处理页面: {page_id}]")
                    continue
                    
                page_title = self.flowus_client.get_page_title(page_id)
                
                if page_title.startswith("[已处理页面:"):
                    relation_content.append(f"关联页面: {page_title}")
                    continue
                
                page_details = self.flowus_client.get_page_details(page_id)
                if page_details:
                    self.flowus_client.processed_pages.add(page_id)
                    formatted_page = self.format_page_details(page_details)
                    relation_content.append(f"关联页面: {page_title} (ID: {page_id})\n{formatted_page}")
                else:
                    relation_content.append(f"关联页面: {page_title} (ID: {page_id}) (无法获取内容)")
        
        return '\n\n'.join(relation_content) if relation_content else ""
    
    def _format_formula_property(self, prop):
        formula_value = prop.get('formula')
        if formula_value:
            formula_type = formula_value.get('type')
            if formula_type == 'string':
                return formula_value.get('string', '')
            elif formula_type == 'number':
                return str(formula_value.get('number', ''))
            elif formula_type == 'boolean':
                return "是" if formula_value.get('boolean') else "否"
            elif formula_type == 'date':
                date_value = formula_value.get('date')
                if date_value:
                    start = date_value.get('start', '')
                    end = date_value.get('end', '')
                    if end:
                        return f"{start} 到 {end}"
                    else:
                        return start
        return ""
    
    def _format_rollup_property(self, prop):
        rollup_value = prop.get('rollup')
        if rollup_value:
            rollup_type = rollup_value.get('type')
            if rollup_type == 'array':
                array_items = rollup_value.get('array', [])
                if array_items:
                    return f"[汇总: {len(array_items)} 项]"
            elif rollup_type == 'number':
                return str(rollup_value.get('number', ''))
            elif rollup_type == 'date':
                date_value = rollup_value.get('date')
                if date_value:
                    start = date_value.get('start', '')
                    end = date_value.get('end', '')
                    if end:
                        return f"{start} 到 {end}"
                    else:
                        return start
        return ""
    
    def _format_created_time_property(self, prop):
        return prop.get('created_time', '')
    
    def _format_last_edited_time_property(self, prop):
        return prop.get('last_edited_time', '')
    
    def _format_created_by_property(self, prop):
        created_by = prop.get('created_by')
        if created_by and 'id' in created_by:
            return created_by['id']
        return ""
    
    def _format_last_edited_by_property(self, prop):
        last_edited_by = prop.get('last_edited_by')
        if last_edited_by and 'id' in last_edited_by:
            return last_edited_by['id']
        return ""