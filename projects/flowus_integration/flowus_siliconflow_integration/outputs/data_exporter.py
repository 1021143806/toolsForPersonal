#!/usr/bin/env python3
"""
数据导出器 - 从数据库导出指定时间范围内的数据并保存到日志文件
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import ConfigLoader
from database.mysql_client import MySQLClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataExporter:
    """数据导出器"""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.config = config_loader.load_config()
        self.mysql_client = MySQLClient(self.config)
        self.output_dir = self.config['output']['output_dir']
        self.log_file = self.config['output']['log_file']
        self.recent_days = self.config['database']['recent_days']
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    def export_recent_data_to_log(self) -> bool:
        """导出最近指定天数的数据到日志文件"""
        logger.info(f"开始导出最近 {self.recent_days} 天的数据...")
        
        # 连接数据库
        if not self.mysql_client.connect():
            logger.error("数据库连接失败")
            return False
        
        try:
            # 获取最近的数据
            diary_records = self.mysql_client.get_recent_diary_records(days=self.recent_days)
            problem_records = self.mysql_client.get_recent_problem_records(days=self.recent_days)
            project_records = self.mysql_client.get_recent_project_records(days=self.recent_days)
            
            logger.info(f"获取到数据: 日记{len(diary_records)}条, 问题{len(problem_records)}条, 项目{len(project_records)}条")
            
            # 格式化数据
            formatted_data = self.format_data_for_export(diary_records, problem_records, project_records)
            
            # 保存到日志文件
            log_file_path = os.path.join(self.output_dir, self.log_file)
            success = self.save_to_log_file(formatted_data, log_file_path)
            
            if success:
                logger.info(f"数据已成功导出到: {log_file_path}")
                return True
            else:
                logger.error("数据导出失败")
                return False
                
        except Exception as e:
            logger.error(f"导出数据过程中出错: {e}")
            return False
        finally:
            # 关闭数据库连接
            self.mysql_client.disconnect()
    
    def format_data_for_export(self, diary_records: List[Dict[str, Any]], 
                              problem_records: List[Dict[str, Any]], 
                              project_records: List[Dict[str, Any]]) -> str:
        """格式化数据用于导出"""
        content_parts = []
        
        # 添加导出时间信息
        export_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content_parts.append(f"数据导出时间: {export_time}")
        content_parts.append(f"时间范围: 最近 {self.recent_days} 天")
        content_parts.append("=" * 60)
        content_parts.append("")
        
        # 添加日记分类统计
        if diary_records:
            diary_categories = {}
            for record in diary_records:
                category = record.get('category', '未分类')
                diary_categories[category] = diary_categories.get(category, 0) + 1
            
            content_parts.append("=== 日记分类统计 ===")
            for category, count in diary_categories.items():
                content_parts.append(f"- {category}: {count} 条")
            content_parts.append("")
        
        # 添加日记记录
        if diary_records:
            content_parts.append("=== 日记记录 ===")
            for record in diary_records:
                title = record.get('title', '').strip()
                category = record.get('category', '未分类')
                created_time = record.get('created_time', '')
                completed = '已完成' if record.get('completed', False) else '未完成'
                
                content_parts.append(f"- {title}")
                content_parts.append(f"  分类: {category}")
                content_parts.append(f"  时间: {created_time}")
                content_parts.append(f"  状态: {completed}")
                
                # 添加详细信息
                raw_response = record.get('raw_response')
                if raw_response:
                    try:
                        page_data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
                        if 'properties' in page_data:
                            properties = page_data['properties']
                            
                            # 提取关键信息
                            key_fields = ['开始时间', '最近编辑时间', '问题记录总表链接', '项目总表']
                            for field in key_fields:
                                if field in properties:
                                    field_data = properties[field]
                                    if isinstance(field_data, dict):
                                        if 'date' in field_data:
                                            date_info = field_data['date']
                                            if isinstance(date_info, dict):
                                                start_date = date_info.get('start', '')
                                                if start_date:
                                                    content_parts.append(f"  {field}: {start_date}")
                                        elif 'relation' in field_data:
                                            relation = field_data['relation']
                                            if relation:
                                                content_parts.append(f"  {field}: 关联了 {len(relation)} 个项目")
                        
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析记录 {record.get('id')} 的raw_response")
                
                content_parts.append("")
        
        # 添加问题记录
        if problem_records:
            content_parts.append("=== 问题记录 ===")
            for record in problem_records:
                title = record.get('title', '').strip()
                created_time = record.get('created_time', '')
                
                content_parts.append(f"- {title}")
                content_parts.append(f"  时间: {created_time}")
                
                # 添加详细信息
                raw_response = record.get('raw_response')
                if raw_response:
                    try:
                        page_data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
                        if 'properties' in page_data:
                            properties = page_data['properties']
                            
                            # 提取问题关键信息
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
                                        elif 'checkbox' in field_data:
                                            checkbox_value = field_data['checkbox']
                                            content_parts.append(f"  {field}: {'是' if checkbox_value else '否'}")
                    
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析问题记录 {record.get('id')} 的raw_response")
                
                content_parts.append("")
        
        # 添加项目记录
        if project_records:
            content_parts.append("=== 项目记录 ===")
            for record in project_records:
                title = record.get('title', '').strip()
                created_time = record.get('created_time', '')
                
                content_parts.append(f"- {title}")
                content_parts.append(f"  时间: {created_time}")
                
                # 添加详细信息
                raw_response = record.get('raw_response')
                if raw_response:
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
                    
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析项目记录 {record.get('id')} 的raw_response")
                
                content_parts.append("")
        
        return '\n'.join(content_parts)
    
    def save_to_log_file(self, data: str, file_path: str) -> bool:
        """保存数据到日志文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            logger.info(f"数据已保存到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            return False
    
    def get_exported_data(self) -> Optional[str]:
        """获取已导出的数据"""
        log_file_path = os.path.join(self.output_dir, self.log_file)
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                logger.info(f"从 {log_file_path} 读取了 {len(data)} 字符的数据")
                return data
            else:
                logger.warning(f"导出文件不存在: {log_file_path}")
                return None
        except Exception as e:
            logger.error(f"读取导出文件失败: {e}")
            return None


def main():
    """主函数"""
    config_loader = ConfigLoader()
    exporter = DataExporter(config_loader)
    
    if exporter.export_recent_data_to_log():
        print("数据导出成功！")
    else:
        print("数据导出失败！")


if __name__ == "__main__":
    main()