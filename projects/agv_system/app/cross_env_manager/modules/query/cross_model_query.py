#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨环境任务模板配置查询模块
基于agv-task-query的query-cross-model.php功能
"""

import pymysql
from typing import Dict, List, Optional, Any, Union
from ..database.connection import connect_to_server
from ..database.helpers import safe_int, safe_str

def query_cross_model(identifier: str = '', model_id: str = '', 
                     model_code: str = '', model_name: str = '') -> Dict[str, Any]:
    """
    查询跨环境任务模板配置
    
    Args:
        identifier: 通用标识符
        model_id: 模板ID
        model_code: 模板编号
        model_name: 模板名称
        
    Returns:
        查询结果字典
    """
    result = {
        'success': False,
        'identifier': identifier,
        'model_id': model_id,
        'model_code': model_code,
        'model_name': model_name,
        'data': None,
        'error': None
    }
    
    # 确定使用哪个标识符
    used_identifier = None
    identifier_type = 'unknown'
    
    if model_id and model_id.isdigit():
        used_identifier = int(model_id)
        identifier_type = 'id'
    elif model_code:
        used_identifier = model_code.strip()
        identifier_type = 'code'
    elif model_name:
        used_identifier = model_name.strip()
        identifier_type = 'name'
    elif identifier:
        # 尝试自动判断类型
        if identifier.isdigit():
            used_identifier = int(identifier)
            identifier_type = 'id'
        else:
            used_identifier = identifier.strip()
            identifier_type = 'code'
    else:
        result['error'] = '缺少标识符参数'
        return result
    
    # 连接数据库（默认使用IP后缀32）
    conn = connect_to_server('32')
    if not conn:
        result['error'] = '无法连接到数据库服务器'
        return result
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询主表 fy_cross_model_process
        where_clause = ''
        if identifier_type == 'id':
            where_clause = f"id = {used_identifier}"
        elif identifier_type == 'code':
            where_clause = f"model_process_code = '{pymysql.converters.escape_string(str(used_identifier))}'"
        elif identifier_type == 'name':
            where_clause = f"model_process_name = '{pymysql.converters.escape_string(str(used_identifier))}'"
        
        sql = f"SELECT * FROM fy_cross_model_process WHERE {where_clause} LIMIT 1"
        cursor.execute(sql)
        main_record = cursor.fetchone()
        
        if not main_record:
            result['error'] = f'未找到匹配的任务模板（{identifier_type}: {used_identifier}）'
            return result
        
        model_id = main_record['id']
        model_process_code = main_record['model_process_code']
        
        # 查询子表 fy_cross_model_process_detail
        sql2 = f"SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = {model_id} ORDER BY task_seq"
        cursor.execute(sql2)
        detail_records = cursor.fetchall()
        
        # 查询正在执行的任务（来自 fy_cross_task）
        sql3 = f"""
        SELECT count(0) as cnt FROM fy_cross_task 
        WHERE model_process_code = '{pymysql.converters.escape_string(model_process_code)}' 
        AND task_status in (0,1,6,4,9,10)
        """
        cursor.execute(sql3)
        executing_count_result = cursor.fetchone()
        executing_count = executing_count_result['cnt'] if executing_count_result else 0
        
        # 查询任务列表
        sql4 = f"""
        SELECT * FROM fy_cross_task 
        WHERE model_process_code = '{pymysql.converters.escape_string(model_process_code)}' 
        AND task_status in (0,1,6,4,9,10)
        """
        cursor.execute(sql4)
        task_records = cursor.fetchall()
        
        result['success'] = True
        result['data'] = {
            'main_record': main_record,
            'detail_records': detail_records,
            'executing_count': executing_count,
            'task_records': task_records,
            'identifier_type': identifier_type,
            'used_identifier': used_identifier
        }
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result

def get_server_ips_from_cross_model(cross_model: str) -> List[str]:
    """
    根据跨环境大任务模板获取服务器IP列表
    
    Args:
        cross_model: 跨环境大任务模板
        
    Returns:
        服务器IP后缀列表
    """
    # 连接到固定服务器 10.68.2.32
    conn = connect_to_server('32')
    if not conn:
        return []
    
    ips = []
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询模板ID
        sql = """
        SELECT id FROM fy_cross_model_process 
        WHERE model_process_code = %s 
           OR model_process_name = %s
           OR id = %s
        """
        
        # 尝试按ID查询
        if cross_model.isdigit():
            cursor.execute(sql, (cross_model, cross_model, int(cross_model)))
        else:
            cursor.execute(sql, (cross_model, cross_model, 0))
        
        row = cursor.fetchone()
        if row:
            model_id = row['id']
            
            # 查询子任务
            sql2 = "SELECT task_servicec FROM fy_cross_model_process_detail WHERE model_process_id = %s"
            cursor.execute(sql2, (model_id,))
            
            rows = cursor.fetchall()
            for row in rows:
                url = row['task_servicec']
                # 从URL中提取IP，例如 http://10.68.2.27:7000
                import re
                match = re.search(r'\d+\.\d+\.\d+\.(\d+)', url)
                if match:
                    ip = match.group(1)
                    if ip not in ips:
                        ips.append(ip)
    
    except pymysql.Error:
        pass
    finally:
        conn.close()
    
    return ips

def query_cross_task_by_model(model_process_code: str, server_ip_suffix: str = '32') -> Dict[str, Any]:
    """
    根据模型代码查询跨环境任务
    
    Args:
        model_process_code: 模型处理代码
        server_ip_suffix: 服务器IP后缀
        
    Returns:
        跨环境任务查询结果
    """
    result = {
        'success': False,
        'model_process_code': model_process_code,
        'server_ip': f'10.68.2.{server_ip_suffix}',
        'data': None,
        'error': None
    }
    
    # 连接数据库
    conn = connect_to_server(server_ip_suffix)
    if not conn:
        result['error'] = f'无法连接到服务器 10.68.2.{server_ip_suffix}'
        return result
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询跨环境任务
        sql = f"""
        SELECT * FROM fy_cross_task 
        WHERE model_process_code = '{pymysql.converters.escape_string(model_process_code)}'
        ORDER BY id DESC
        """
        cursor.execute(sql)
        tasks = cursor.fetchall()
        
        # 查询任务详情
        task_data = []
        for task in tasks:
            task_info = dict(task)
            
            # 查询任务详情
            task_id = task.get('id')
            if task_id:
                detail_sql = f"""
                SELECT * FROM fy_cross_task_detail 
                WHERE cross_task_id = {task_id} 
                ORDER BY task_seq
                """
                cursor.execute(detail_sql)
                details = cursor.fetchall()
                task_info['details'] = details
            
            task_data.append(task_info)
        
        result['success'] = True
        result['data'] = task_data
        result['count'] = len(task_data)
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result