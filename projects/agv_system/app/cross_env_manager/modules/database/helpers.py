#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库帮助函数
模仿agv-task-query的SQL帮助函数，适配Python
"""

import re
from typing import Any, Optional, Union, List, Dict
import pymysql

def safe_int(value: Any, default: int = 0) -> int:
    """
    安全地将值转换为整数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的整数值
    """
    if value is None:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_str(value: Any, default: str = '') -> str:
    """
    安全地将值转换为字符串
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的字符串
    """
    if value is None:
        return default
    
    try:
        return str(value).strip()
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全地将值转换为浮点数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        转换后的浮点数值
    """
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def format_results(results: Union[List[Dict], Dict, None], 
                   format_type: str = 'html') -> str:
    """
    格式化查询结果
    
    Args:
        results: 查询结果
        format_type: 格式化类型：'html', 'json', 'text'
        
    Returns:
        格式化后的字符串
    """
    if results is None:
        return "无结果"
    
    if format_type == 'html':
        return format_results_html(results)
    elif format_type == 'json':
        import json
        return json.dumps(results, ensure_ascii=False, indent=2)
    else:  # text
        return format_results_text(results)

def format_results_html(results: Union[List[Dict], Dict]) -> str:
    """
    将结果格式化为HTML表格
    
    Args:
        results: 查询结果
        
    Returns:
        HTML表格字符串
    """
    if isinstance(results, dict):
        # 单个记录
        html = '<table class="table table-bordered table-striped">'
        html += '<tbody>'
        for key, value in results.items():
            html += f'<tr><th>{key}</th><td>{value}</td></tr>'
        html += '</tbody></table>'
        return html
    elif isinstance(results, list):
        if not results:
            return '<p>无数据</p>'
        
        # 多个记录
        html = '<table class="table table-bordered table-striped">'
        html += '<thead><tr>'
        
        # 获取表头
        headers = list(results[0].keys())
        for header in headers:
            html += f'<th>{header}</th>'
        html += '</tr></thead><tbody>'
        
        # 填充数据
        for row in results:
            html += '<tr>'
            for header in headers:
                value = row.get(header, '')
                html += f'<td>{value}</td>'
            html += '</tr>'
        
        html += '</tbody></table>'
        return html
    else:
        return str(results)

def format_results_text(results: Union[List[Dict], Dict]) -> str:
    """
    将结果格式化为文本
    
    Args:
        results: 查询结果
        
    Returns:
        文本字符串
    """
    if isinstance(results, dict):
        lines = []
        for key, value in results.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    elif isinstance(results, list):
        if not results:
            return "无数据"
        
        lines = []
        headers = list(results[0].keys())
        lines.append(" | ".join(headers))
        lines.append("-" * (len(" | ".join(headers))))
        
        for row in results:
            values = [str(row.get(header, '')) for header in headers]
            lines.append(" | ".join(values))
        
        return "\n".join(lines)
    else:
        return str(results)

def extract_id_from_code(model_process_code: str) -> Optional[int]:
    """
    从model_process_code中提取ID后缀
    
    Args:
        model_process_code: 模型处理代码，如'HJBY_test_484'
        
    Returns:
        提取的ID或None
    """
    # 匹配末尾的数字ID，如_HJBY_test_484中的484
    match = re.search(r'_(\d+)$', model_process_code)
    if match:
        return int(match.group(1))
    return None

def get_next_available_id(conn: pymysql.Connection, table: str, id_column: str = 'id') -> int:
    """
    获取下一个可用的数据库ID
    
    Args:
        conn: 数据库连接
        table: 表名
        id_column: ID列名
        
    Returns:
        下一个可用的ID
    """
    cursor = None
    try:
        cursor = conn.cursor()
        query = f"SELECT MAX({id_column}) as max_id FROM {table}"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            return result[0] + 1
        else:
            return 1
    except pymysql.Error as e:
        print(f"获取下一个ID错误: {e}")
        return 1
    finally:
        if cursor:
            cursor.close()

def sql_find_one(conn: pymysql.Connection, sql: str, column: str) -> Any:
    """
    执行SQL查询并返回单个字段值（模仿agv-task-query的sqlfindone）
    
    Args:
        conn: 数据库连接
        sql: SQL查询语句
        column: 要返回的列名
        
    Returns:
        查询结果
    """
    cursor = None
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result and column in result:
            return result[column]
        else:
            return None
    except pymysql.Error as e:
        print(f"查询错误: {e}")
        return None
    finally:
        if cursor:
            cursor.close()

def sql_find_all(conn: pymysql.Connection, sql: str) -> List[Dict]:
    """
    执行SQL查询并返回所有结果（模仿agv-task-query的sqlfindall）
    
    Args:
        conn: 数据库连接
        sql: SQL查询语句
        
    Returns:
        查询结果列表
    """
    cursor = None
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except pymysql.Error as e:
        print(f"查询错误: {e}")
        return []
    finally:
        if cursor:
            cursor.close()

def build_in_condition(values: List[str], conn: Optional[pymysql.Connection] = None) -> str:
    """
    构建IN条件语句
    
    Args:
        values: 值列表
        conn: 数据库连接（用于转义）
        
    Returns:
        IN条件字符串
    """
    if not values:
        return "''"
    
    if conn:
        # 转义值
        escaped_values = []
        for value in values:
            escaped_values.append(pymysql.converters.escape_string(value))
        values = escaped_values
    
    return "'" + "','".join(values) + "'"

def parse_device_codes(device_codes_str: str) -> List[str]:
    """
    解析设备序列号字符串
    
    Args:
        device_codes_str: 设备序列号字符串，逗号分隔
        
    Returns:
        设备序列号列表
    """
    if not device_codes_str:
        return []
    
    device_codes = [code.strip() for code in device_codes_str.split(',')]
    device_codes = [code for code in device_codes if code]
    return device_codes

def parse_server_ips(server_ips_str: str) -> List[str]:
    """
    解析服务器IP字符串
    
    Args:
        server_ips_str: 服务器IP字符串，逗号分隔
        
    Returns:
        服务器IP后缀列表
    """
    if not server_ips_str:
        return []
    
    server_ips = [ip.strip() for ip in server_ips_str.split(',')]
    server_ips = [ip for ip in server_ips if ip]
    return server_ips