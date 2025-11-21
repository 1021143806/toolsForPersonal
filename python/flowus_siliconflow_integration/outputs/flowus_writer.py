"""
FlowUs 输出器
"""

import datetime
import json


class FlowUsWriter:
    """FlowUs 输出器"""
    
    def __init__(self, config, flowus_client):
        self.config = config
        self.flowus_client = flowus_client
        self.new_page_config = config['new_page']
        self.block_settings = config.get('block_settings', {})
    
    def create_page_with_content(self, ai_response, silicon_response):
        """创建FlowUs页面并添加内容"""
        print(f"\n在父页面 {self.config['flowus']['parent_page_id']} 下创建新页面...")
        
        # 生成页面标题
        page_title = f"{self.new_page_config['title']} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 创建页面
        page_response = self.flowus_client.create_page(page_title)
        if not page_response:
            print("新页面创建失败")
            return
        
        new_page_id = page_response.get('id')
        print(f"新页面创建成功，ID: {new_page_id}")
        
        # 向页面追加内容块
        print("向新页面添加块内容...")
        blocks_data = self._prepare_blocks_data(ai_response, silicon_response)
        blocks_response = self.flowus_client.append_blocks(new_page_id, blocks_data)
        
        if blocks_response:
            print("内容块添加成功！")
        else:
            print("内容块添加失败")
    
    def _prepare_blocks_data(self, ai_response, silicon_response):
        """准备要添加到页面的块数据"""
        children = []
        
        # 1. 添加AI回复标题
        children.append({
            "type": "heading_2",
            "data": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "AI回复内容",
                            "link": None
                        },
                        "annotations": {
                            "bold": True,
                            "color": "green"
                        }
                    }
                ],
                "text_color": "green",
                "background_color": "default"
            }
        })
        
        # 2. 添加AI回复内容（按段落分割）
        ai_paragraphs = ai_response.split('\n\n')
        for paragraph in ai_paragraphs:
            if paragraph.strip():
                children.append({
                    "type": "paragraph",
                    "data": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": paragraph.strip(),
                                    "link": None
                                }
                            }
                        ],
                        "text_color": self.block_settings.get('text_color', 'default'),
                        "background_color": self.block_settings.get('background_color', 'default')
                    }
                })
        
        # 3. 添加元数据
        if self.block_settings.get('include_metadata', True):
            children.append({
                "type": "divider",
                "data": {}
            })
            
            children.append({
                "type": "callout",
                "data": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "生成信息",
                                "link": None
                            },
                            "annotations": {
                                "bold": True
                            }
                        },
                        {
                            "type": "text",
                            "text": {
                                "content": f"\n模型: {silicon_response.get('model', 'N/A')}\n响应ID: {silicon_response.get('id', 'N/A')}\n生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                "link": None
                            }
                        }
                    ],
                    "icon": {
                        "emoji": "ℹ️"
                    },
                    "text_color": "default",
                    "background_color": "gray"
                }
            })
        
        return children