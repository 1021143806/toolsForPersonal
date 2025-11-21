"""
文件输出器
"""

import os
import datetime


class FileWriter:
    """文件输出器"""
    
    def __init__(self, config):
        self.config = config
        self.output_config = config['output']
    
    def save_log_file(self, content, filename=None):
        """保存内容到日志文件"""
        if filename is None:
            filename = self.output_config.get('log_file', 'data.log')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"原始内容已保存到 {os.path.abspath(filename)}")
        except Exception as e:
            print(f"保存日志文件时出错: {e}")
    
    def save_markdown_file(self, extracted_text, reply_content, silicon_response, filename=None):
        """保存内容到Markdown文件"""
        if filename is None:
            filename = self.output_config['filename']
        
        markdown_content = (
            "# 硅基流动API回复\n\n"
            "## 原始输入内容\n"
            f"```\n{extracted_text}\n```\n\n"
            "## AI回复\n"
            f"{reply_content}\n\n"
            "## 响应信息\n"
            f"- 模型: {silicon_response.get('model', 'N/A')}\n"
            f"- 响应ID: {silicon_response.get('id', 'N/A')}\n"
            f"- 创建时间: {silicon_response.get('created', 'N/A')}\n"
        )
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"内容已保存到 {os.path.abspath(filename)}")
        except Exception as e:
            print(f"保存文件时出错: {e}")