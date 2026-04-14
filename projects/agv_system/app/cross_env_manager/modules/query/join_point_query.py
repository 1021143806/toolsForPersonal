#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交接点查询模块
基于agv-task-query的query-join-point.php功能
"""

import pymysql
from typing import Dict, List, Optional, Any
from ..database.connection import connect_to_server, execute_query_on_server
from ..database.helpers import parse_server_ips, safe_int, safe_str

def query_join_point(join_point_id: str = '', qr_content: str = '', 
                    cross_model: str = '', server_ips_str: str = '') -> Dict[str, Any]:
    """
    查询交接点配置信息
    
    Args:
        join_point_id: 交接点ID
        qr_content: 二维码内容
        cross_model: 跨环境大任务模板
        server_ips_str: 服务器IP字符串
        
    Returns:
        查询结果字典
    """
    result = {
        'success': False,
        'join_point_id': join_point_id,
        'qr_content': qr_content,
        'cross_model': cross_model,
        'server_ips': [],
        'data': {},
        'error': None
    }
    
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
        ip_result = query_join_point_on_server(ip, join_point_id, qr_content, cross_model)
        result['data'][ip] = ip_result
    
    result['success'] = True
    return result

def query_join_point_on_server(ip_suffix: str, join_point_id: str = '', 
                              qr_content: str = '', cross_model: str = '') -> Dict[str, Any]:
    """
    在特定服务器上查询交接点信息
    
    Args:
        ip_suffix: 服务器IP后缀
        join_point_id: 交接点ID
        qr_content: 二维码内容
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
        
        # 构建查询条件
        conditions = []
        if join_point_id:
            conditions.append(f"id = {safe_int(join_point_id)}")
        if qr_content:
            conditions.append(f"qr_content LIKE '%{pymysql.converters.escape_string(qr_content)}%'")
        if cross_model:
            conditions.append(f"cross_model LIKE '%{pymysql.converters.escape_string(cross_model)}%'")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询交接点信息
        sql = f"SELECT * FROM join_qr_node_info WHERE {where_clause} ORDER BY id"
        cursor.execute(sql)
        join_points = cursor.fetchall()
        
        result['success'] = True
        result['data'] = join_points
        result['count'] = len(join_points)
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result