#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
货架查询模块
基于agv-task-query的query-shelf.php功能
"""

import pymysql
from typing import Dict, List, Optional, Any
from ..database.connection import connect_to_server
from ..database.helpers import parse_server_ips, safe_int, safe_str

def query_shelf(shelf_codes: str, cross_model: str = '', 
               server_ips_str: str = '') -> Dict[str, Any]:
    """
    查询货架配置信息
    
    Args:
        shelf_codes: 货架编号（单个或范围，如 HX001 或 HX001-HX010）
        cross_model: 跨环境大任务模板
        server_ips_str: 服务器IP字符串
        
    Returns:
        查询结果字典
    """
    result = {
        'success': False,
        'shelf_codes': shelf_codes,
        'cross_model': cross_model,
        'server_ips': [],
        'data': {},
        'error': None
    }
    
    if not shelf_codes:
        result['error'] = '货架编号不能为空'
        return result
    
    # 解析货架编号范围
    shelf_code_list = parse_shelf_codes(shelf_codes)
    if not shelf_code_list:
        result['error'] = '无法解析货架编号'
        return result
    
    # 确定要检查的服务器IP列表
    server_ips = []
    if server_ips_str:
        server_ips = parse_server_ips(server_ips_str)
    elif cross_model:
        # 从跨环境模板获取服务器IP
        from .cross_model_query import get_server_ips_from_cross_model
        server_ips = get_server_ips_from_cross_model(cross_model)
    else:
        # 默认使用所有已知环境IP
        server_ips = ['31', '32', '17']
    
    result['server_ips'] = server_ips
    
    # 对每个服务器IP进行查询
    for ip in server_ips:
        ip_result = query_shelf_on_server(ip, shelf_code_list, cross_model)
        result['data'][ip] = ip_result
    
    result['success'] = True
    return result

def parse_shelf_codes(shelf_codes: str) -> List[str]:
    """
    解析货架编号字符串
    
    Args:
        shelf_codes: 货架编号字符串，如'HX001'或'HX001-HX010'
        
    Returns:
        货架编号列表
    """
    if '-' in shelf_codes:
        # 处理范围，如 HX001-HX010
        try:
            start, end = shelf_codes.split('-')
            start_prefix = ''.join([c for c in start if not c.isdigit()])
            end_prefix = ''.join([c for c in end if not c.isdigit()])
            
            if start_prefix != end_prefix:
                return [shelf_codes]  # 前缀不同，返回原字符串
            
            start_num = int(''.join([c for c in start if c.isdigit()]))
            end_num = int(''.join([c for c in end if c.isdigit()]))
            
            shelf_list = []
            for i in range(start_num, end_num + 1):
                shelf_list.append(f"{start_prefix}{i:03d}")
            return shelf_list
        except (ValueError, IndexError):
            return [shelf_codes]
    else:
        # 单个货架编号
        return [shelf_codes.strip()]

def query_shelf_on_server(ip_suffix: str, shelf_codes: List[str], 
                         cross_model: str = '') -> Dict[str, Any]:
    """
    在特定服务器上查询货架信息
    
    Args:
        ip_suffix: 服务器IP后缀
        shelf_codes: 货架编号列表
        cross_model: 跨环境大任务模板
        
    Returns:
        查询结果
    """
    result = {
        'server_ip': f'10.68.2.{ip_suffix}',
        'success': False,
        'data': None,
        'error': None
    }
    
    # 连接数据库
    conn = connect_to_server(ip_suffix)
    if not conn:
        result['error'] = f'无法连接到服务器 10.68.2.{ip_suffix}'
        return result
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 构建IN条件
        in_condition = "'" + "','".join([pymysql.converters.escape_string(code) for code in shelf_codes]) + "'"
        
        # 查询货架信息
        sql = f"SELECT * FROM shelf_config WHERE shelf_code IN ({in_condition}) ORDER BY shelf_code"
        cursor.execute(sql)
        shelves = cursor.fetchall()
        
        # 查询货架类型一致性
        shelf_type_info = {}
        for shelf in shelves:
            shelf_type = shelf.get('shelf_type')
            if shelf_type:
                if shelf_type not in shelf_type_info:
                    shelf_type_info[shelf_type] = []
                shelf_type_info[shelf_type].append(shelf['shelf_code'])
        
        # 如果指定了跨环境模板，查询相关的任务信息
        task_info = None
        if cross_model:
            sql2 = f"""
            SELECT * FROM task_group 
            WHERE carrier_code IN ({in_condition}) 
            AND template_code LIKE '%{pymysql.converters.escape_string(cross_model)}%'
            LIMIT 10
            """
            cursor.execute(sql2)
            task_info = cursor.fetchall()
        
        result['success'] = True
        result['data'] = {
            'shelves': shelves,
            'shelf_count': len(shelves),
            'shelf_type_info': shelf_type_info,
            'task_info': task_info
        }
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result