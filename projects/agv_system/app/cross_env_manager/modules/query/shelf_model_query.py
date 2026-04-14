#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
货架模型查询模块
基于agv-task-query的query-shelf-model.php功能
"""

import pymysql
from typing import Dict, List, Optional, Any
from ..database.connection import connect_to_server
from ..database.helpers import parse_server_ips, safe_int, safe_str

def query_shelf_model(shelf_model_id: str, cross_model: str = '', 
                     server_ips_str: str = '') -> Dict[str, Any]:
    """
    查询货架模型配置信息
    
    Args:
        shelf_model_id: 货架模型ID
        cross_model: 跨环境大任务模板
        server_ips_str: 服务器IP字符串
        
    Returns:
        查询结果字典
    """
    result = {
        'success': False,
        'shelf_model_id': shelf_model_id,
        'cross_model': cross_model,
        'server_ips': [],
        'data': {},
        'error': None
    }
    
    if not shelf_model_id:
        result['error'] = '货架模型ID不能为空'
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
        ip_result = query_shelf_model_on_server(ip, shelf_model_id, cross_model)
        result['data'][ip] = ip_result
    
    result['success'] = True
    return result

def query_shelf_model_on_server(ip_suffix: str, shelf_model_id: str, 
                               cross_model: str = '') -> Dict[str, Any]:
    """
    在特定服务器上查询货架模型信息
    
    Args:
        ip_suffix: 服务器IP后缀
        shelf_model_id: 货架模型ID
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
        
        # 查询货架模型信息
        sql = f"SELECT * FROM load_config WHERE model = {safe_int(shelf_model_id)}"
        cursor.execute(sql)
        shelf_model = cursor.fetchone()
        
        if not shelf_model:
            result['error'] = f'未找到货架模型ID为 {shelf_model_id} 的记录'
            return result
        
        # 查询相关的货架信息
        sql2 = f"SELECT * FROM shelf_config WHERE shelf_model = {safe_int(shelf_model_id)}"
        cursor.execute(sql2)
        shelves = cursor.fetchall()
        
        # 如果指定了跨环境模板，查询相关的任务信息
        task_info = None
        if cross_model:
            sql3 = f"""
            SELECT * FROM task_group 
            WHERE shelf_model = {safe_int(shelf_model_id)} 
            AND template_code LIKE '%{pymysql.converters.escape_string(cross_model)}%'
            LIMIT 10
            """
            cursor.execute(sql3)
            task_info = cursor.fetchall()
        
        result['success'] = True
        result['data'] = {
            'shelf_model': shelf_model,
            'shelves': shelves,
            'shelf_count': len(shelves),
            'task_info': task_info
        }
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result