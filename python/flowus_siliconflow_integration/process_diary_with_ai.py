#!/usr/bin/env python3
"""
处理日记数据并生成AI内容
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config.config_loader import ConfigLoader
from clients.siliconflow_client import SiliconFlowClient
from database.mysql_client import MySQLClient
from outputs.flowus_writer import FlowUsWriter
from outputs.data_exporter import DataExporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='process_diary.log'
)
logger = logging.getLogger(__name__)

# 添加硅基API请求日志记录器
api_logger = logging.getLogger('siliconflow_api')
api_handler = logging.FileHandler('siliconflow_api_requests.log')
api_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
api_logger.addHandler(api_handler)
api_logger.setLevel(logging.INFO)


class DiaryAIProcessor:
    """日记AI处理器"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.config = config_loader.load_config()
        self.silicon_client = SiliconFlowClient(self.config)
        self.mysql_client = MySQLClient(self.config)
        # 创建FlowUs客户端
        from clients.flowus_client import FlowUsClient
        flowus_client = FlowUsClient(config_loader)
        self.flowus_writer = FlowUsWriter(self.config, flowus_client)
        # 创建数据导出器
        self.data_exporter = DataExporter(config_loader)
        
    def extract_content_from_records(self, records: List[Dict[str, Any]]) -> str:
        """从记录中提取内容"""
        content_parts = []
        
        for record in records:
            title = record.get('title', '').strip()
            if not title:
                continue
                
            content_parts.append(f"- {title}")
            
            # 提取详细信息
            raw_response = record.get('raw_response')
            if raw_response:
                import json
                try:
                    page_data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
                    
                    if 'properties' in page_data:
                        properties = page_data['properties']
                        
                        # 提取关键信息
                        key_fields = [
                            '原因及解决方法', '位置：服务器ip+车间名称', '是否解决', 
                            '记录详细过程（案例）', '服务器相关模块', '归属'
                        ]
                        
                        for field in key_fields:
                            if field in properties:
                                field_data = properties[field]
                                if isinstance(field_data, dict):
                                    if 'rich_text' in field_data:
                                        rich_text = field_data['rich_text']
                                        text_parts = []
                                        for text_item in rich_text:
                                            if isinstance(text_item, dict) and 'plain_text' in text_item:
                                                text_parts.append(text_item['plain_text'])
                                        if text_parts:
                                            content_parts.append(f"  {field}: {' '.join(text_parts)}")
                                    elif 'select' in field_data:
                                        select_data = field_data['select']
                                        if select_data and 'name' in select_data:
                                            content_parts.append(f"  {field}: {select_data['name']}")
                                    elif 'multi_select' in field_data:
                                        multi_select = field_data['multi_select']
                                        if multi_select:
                                            names = [item.get('name', '') for item in multi_select]
                                            content_parts.append(f"  {field}: {', '.join(names)}")
                                    elif 'checkbox' in field_data:
                                        checkbox_value = field_data['checkbox']
                                        content_parts.append(f"  {field}: {'是' if checkbox_value else '否'}")
                        
                        content_parts.append("")  # 空行分隔
                
                except json.JSONDecodeError:
                    logger.warning(f"无法解析记录 {record.get('id')} 的raw_response")
        
        return '\n'.join(content_parts)
    
    def extract_project_content(self, records: List[Dict[str, Any]]) -> str:
        """从项目记录中提取内容"""
        content_parts = []
        
        for record in records:
            title = record.get('title', '').strip()
            if not title:
                continue
                
            content_parts.append(f"- {title}")
            
            # 提取详细信息
            raw_response = record.get('raw_response')
            if raw_response:
                import json
                try:
                    page_data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
                    
                    if 'properties' in page_data:
                        properties = page_data['properties']
                        
                        # 提取项目关键信息
                        key_fields = [
                            '是否完成', '同步父项目', '同步日记', '项目状态', '进度'
                        ]
                        
                        for field in key_fields:
                            if field in properties:
                                field_data = properties[field]
                                if isinstance(field_data, dict):
                                    if 'checkbox' in field_data:
                                        checkbox_value = field_data['checkbox']
                                        content_parts.append(f"  {field}: {'是' if checkbox_value else '否'}")
                                    elif 'select' in field_data:
                                        select_data = field_data['select']
                                        if select_data and 'name' in select_data:
                                            content_parts.append(f"  {field}: {select_data['name']}")
                                    elif 'relation' in field_data:
                                        relation = field_data['relation']
                                        if relation:
                                            content_parts.append(f"  {field}: 关联了 {len(relation)} 个项目")
                        
                        content_parts.append("")  # 空行分隔
                
                except json.JSONDecodeError:
                    logger.warning(f"无法解析项目记录 {record.get('id')} 的raw_response")
        
        return '\n'.join(content_parts)
    
    def format_diary_summary(self, diary_records: List[Dict[str, Any]], 
                           problem_records: List[Dict[str, Any]], 
                           project_records: List[Dict[str, Any]]) -> str:
        """格式化日记摘要"""
        content_parts = []
        
        # 添加时间范围信息
        if diary_records:
            latest_date = diary_records[0].get('created_time')
            earliest_date = diary_records[-1].get('created_time')
            content_parts.append(f"数据时间范围: {earliest_date} 至 {latest_date}")
            content_parts.append("")
        
        # 添加日记分类统计
        diary_categories = {}
        for record in diary_records:
            category = record.get('category', '未分类')
            diary_categories[category] = diary_categories.get(category, 0) + 1
        
        content_parts.append("=== 日记分类统计 ===")
        for category, count in diary_categories.items():
            content_parts.append(f"- {category}: {count} 条")
        content_parts.append("")
        
        # 添加问题记录
        if problem_records:
            content_parts.append("=== 问题记录 ===")
            problem_content = self.extract_content_from_records(problem_records)
            content_parts.append(problem_content)
            content_parts.append("")
        
        # 添加项目记录
        if project_records:
            content_parts.append("=== 项目记录 ===")
            project_content = self.extract_project_content(project_records)
            content_parts.append(project_content)
            content_parts.append("")
        
        return '\n'.join(content_parts)
    
    def get_prompt_from_main_page(self) -> Optional[str]:
        """从主页面获取提示词"""
        try:
            # 获取配置的页面ID
            page_url = self.config['flowus']['url']
            page_id = page_url.split('/')[-1].split('?')[0]
            
            # 创建FlowUs客户端来获取页面内容
            from clients.flowus_client import FlowUsClient
            flowus_client = FlowUsClient(self.config_loader)
            
            # 获取页面块内容
            blocks_data = flowus_client.get_page_content(page_id)
            if not blocks_data:
                return None
            
            # 查找代码块（提示词通常在代码块中）
            for block in blocks_data.get('results', []):
                if block.get('type') == 'code':
                    rich_text = block.get('data', {}).get('rich_text', [])
                    for text_item in rich_text:
                        if 'plain_text' in text_item:
                            return text_item['plain_text']
            
            return None
            
        except Exception as e:
            logger.error(f"获取提示词失败: {e}")
            return None
    
    def process_with_ai(self, days: int = 30) -> bool:
        """使用AI处理日记数据"""
        logger.info(f"=== 开始处理最近 {days} 天的日记数据 ===")
        
        # 连接数据库
        if not self.mysql_client.connect():
            logger.error("数据库连接失败")
            return False
        
        try:
            # 先导出数据到日志文件
            logger.info("步骤1: 导出数据到日志文件...")
            if not self.data_exporter.export_recent_data_to_log():
                logger.error("数据导出失败")
                return False
            
            # 从日志文件读取数据
            logger.info("步骤2: 从日志文件读取数据...")
            formatted_content = self.data_exporter.get_exported_data()
            
            if not formatted_content:
                logger.warning("没有找到导出的数据")
                return False
            
            logger.info(f"从日志文件读取了 {len(formatted_content)} 字符的数据")
            
            # 获取提示词
            prompt = self.get_prompt_from_main_page()
            if not prompt:
                logger.warning("无法获取提示词，使用默认提示词")
                prompt = "请根据以下日记数据生成月报和周报，包括项目进展总结和问题记录整理。"
            
            # 构建完整的AI输入
            ai_input = f"{prompt}\n\n{formatted_content}"
            
            logger.info(f"发送给AI的内容长度: {len(ai_input)} 字符")
            
            # 详细记录发送给硅基API的内容
            api_logger.info("=" * 80)
            api_logger.info("发送给硅基API的请求内容:")
            api_logger.info("=" * 80)
            api_logger.info(f"提示词长度: {len(prompt)} 字符")
            api_logger.info(f"数据内容长度: {len(formatted_content)} 字符")
            api_logger.info(f"总内容长度: {len(ai_input)} 字符")
            api_logger.info("--- 提示词内容 ---")
            api_logger.info(prompt)
            api_logger.info("--- 数据内容 ---")
            api_logger.info(formatted_content)
            api_logger.info("=" * 80)
            
            # 调用AI处理
            logger.info("开始调用硅基API...")
            ai_response_json = self.silicon_client.send_content(ai_input)
            
            if not ai_response_json:
                logger.error("AI处理失败")
                api_logger.error("硅基API调用失败，返回空响应")
                return False
            
            # 提取AI响应内容
            ai_response = ""
            if 'choices' in ai_response_json and len(ai_response_json['choices']) > 0:
                ai_response = ai_response_json['choices'][0].get('message', {}).get('content', '')
            
            if not ai_response:
                logger.error("AI响应内容为空")
                api_logger.error("硅基API响应内容为空")
                return False
            
            logger.info(f"AI响应内容长度: {len(ai_response)} 字符")
            logger.info(f"AI响应前200字符: {ai_response[:200]}")
            
            # 详细记录AI响应内容
            api_logger.info("=" * 80)
            api_logger.info("硅基API响应内容:")
            api_logger.info("=" * 80)
            api_logger.info(f"响应长度: {len(ai_response)} 字符")
            api_logger.info("--- 完整响应内容 ---")
            api_logger.info(ai_response)
            api_logger.info("=" * 80)
            
            # 保存到FlowUs
            try:
                self.flowus_writer.create_page_with_content(ai_response, ai_response_json)
                logger.info("内容已成功保存到FlowUs")
                
                # 同时保存到本地文件
                local_backup_success = self.save_to_local_backup(ai_response, ai_response_json)
                if local_backup_success:
                    logger.info("内容已成功保存到本地备份")
                else:
                    logger.warning("本地备份保存失败，但FlowUs保存成功")
                
                return True
            except Exception as e:
                logger.error(f"保存到FlowUs失败: {e}")
                # 即使FlowUs保存失败，也尝试本地备份
                try:
                    self.save_to_local_backup(ai_response, ai_response_json)
                    logger.info("FlowUs保存失败，但本地备份成功")
                except Exception as backup_e:
                    logger.error(f"本地备份也失败: {backup_e}")
                return False
                
        except Exception as e:
            logger.error(f"处理过程中出错: {e}")
            return False
        finally:
            # 关闭数据库连接
            self.mysql_client.disconnect()
    
    def save_to_local_backup(self, ai_response: str, ai_response_json: Dict[str, Any]) -> bool:
        """保存AI生成内容到本地备份文件"""
        try:
            # 确保输出目录存在
            output_dir = self.config['output']['output_dir']
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            # 构建本地文件路径
            local_file_path = os.path.join(output_dir, self.config['output']['filename'])
            
            # 构建完整的Markdown内容
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            markdown_content = f"""# AI生成内容 - {current_time}

## AI回复

{ai_response}

---

## 生成信息

- 模型: {ai_response_json.get('model', 'N/A')}
- 响应ID: {ai_response_json.get('id', 'N/A')}
- 生成时间: {current_time}
- 内容长度: {len(ai_response)} 字符

---

*此文件由FlowUs+SiliconFlow集成系统自动生成*
"""
            
            # 写入本地文件
            with open(local_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"本地备份已保存到: {local_file_path}")
            logger.info(f"备份文件大小: {len(markdown_content)} 字符")
            return True
            
        except Exception as e:
            logger.error(f"保存本地备份失败: {e}")
            return False


def main():
    """主函数"""
    config_loader = ConfigLoader()
    processor = DiaryAIProcessor(config_loader)
    
    # 从配置中获取时间范围
    # 这里可以添加配置项来指定时间范围
    days = 30  # 默认30天
    
    if processor.process_with_ai(days=days):
        print("日记数据AI处理成功！")
    else:
        print("日记数据AI处理失败！")


if __name__ == "__main__":
    main()