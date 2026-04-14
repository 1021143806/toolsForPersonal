#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务查询模块
基于agv-task-query的find-task.php和find-cross-task.php功能
"""

import pymysql
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..database.connection import connect_to_server
from ..database.helpers import safe_int, safe_str, sql_find_one

def find_task_by_id(task_id: str, server_ip_suffix: str) -> Dict[str, Any]:
    """
    根据任务ID查询任务信息（模仿find-task.php）
    
    Args:
        task_id: 任务ID
        server_ip_suffix: 服务器IP后缀，如'31'
        
    Returns:
        任务信息字典
    """
    result = {
        'success': False,
        'task_id': task_id,
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
        # 查询任务信息
        query = "SELECT * FROM task_group WHERE third_order_id = %s"
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, (task_id,))
        tasks = cursor.fetchall()
        
        if not tasks:
            result['error'] = f'未找到任务ID为 {task_id} 的任务'
            return result
        
        task_data = []
        for task in tasks:
            task_info = {
                'area_id': task.get('area_id'),
                'template_code': task.get('template_code'),
                'robot_num': task.get('robot_num'),
                'robot_id': task.get('robot_id'),
                'robot_type': task.get('robot_type'),
                'shelf_model': task.get('shelf_model'),
                'carrier_code': task.get('carrier_code'),
                'error_desc': task.get('error_desc'),
                'path_points': task.get('path_points'),
                'status': task.get('status'),
                'order_id': task.get('order_id'),
                'out_order_id': task.get('out_order_id'),
                'tg_id': task.get('id')
            }
            
            # 查询设备IP
            robot_id = task.get('robot_id')
            if robot_id:
                device_ip = sql_find_one(conn, 
                    f"SELECT DEVICE_IP FROM agv_robot WHERE DEVICE_CODE = '{robot_id}'", 
                    'DEVICE_IP')
                task_info['device_ip'] = device_ip
            
            # 查询货架模型名称
            shelf_model = task.get('shelf_model')
            if shelf_model:
                shelf_model_name = sql_find_one(conn,
                    f"SELECT name FROM load_config WHERE model = {shelf_model}",
                    'name')
                task_info['shelf_model_name'] = shelf_model_name
            
            # 查询任务状态名称
            status = task.get('status')
            if status is not None:
                task_status_name = sql_find_one(conn,
                    f"SELECT task_status_name FROM task_status_config WHERE task_status = {status}",
                    'task_status_name')
                task_info['task_status_name'] = task_status_name
            
            # 格式化时间
            for time_field in ['create_time', 'start_time', 'end_time']:
                if task.get(time_field):
                    try:
                        timestamp = int(task[time_field])
                        task_info[f'{time_field}_formatted'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        task_info[f'{time_field}_formatted'] = task[time_field]
            
            task_data.append(task_info)
        
        result['success'] = True
        result['data'] = task_data
        result['count'] = len(task_data)
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result

def find_cross_task_by_id(cross_task_id: str, server_ip_suffix: str = '32') -> Dict[str, Any]:
    """
    查询跨环境任务信息（模仿find-cross-task.php）
    
    Args:
        cross_task_id: 跨环境任务ID
        server_ip_suffix: 服务器IP后缀，默认'32'
        
    Returns:
        跨环境任务信息字典
    """
    result = {
        'success': False,
        'cross_task_id': cross_task_id,
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
        # 查询跨环境任务信息
        query = """
        SELECT * FROM fy_cross_task 
        WHERE model_process_code LIKE %s 
           OR model_process_name LIKE %s
           OR id = %s
        """
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 尝试按ID查询
        if cross_task_id.isdigit():
            cursor.execute(query, (f'%{cross_task_id}%', f'%{cross_task_id}%', int(cross_task_id)))
        else:
            cursor.execute(query, (f'%{cross_task_id}%', f'%{cross_task_id}%', 0))
        
        tasks = cursor.fetchall()
        
        if not tasks:
            result['error'] = f'未找到跨环境任务ID为 {cross_task_id} 的任务'
            return result
        
        # 获取任务详情
        task_data = []
        for task in tasks:
            task_info = dict(task)
            
            # 查询任务详情
            task_id = task.get('id')
            if task_id:
                detail_query = """
                SELECT * FROM fy_cross_task_detail 
                WHERE cross_task_id = %s 
                ORDER BY task_seq
                """
                cursor.execute(detail_query, (task_id,))
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

def check_cross_model(cross_model: str, server_ip_suffix: str = '32') -> Dict[str, Any]:
    """
    检查跨环境任务模板信息（模仿check-cross-model.php）
    
    Args:
        cross_model: 跨环境任务模板
        server_ip_suffix: 服务器IP后缀，默认'32'
        
    Returns:
        跨环境任务模板信息字典
    """
    result = {
        'success': False,
        'cross_model': cross_model,
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
        # 查询跨环境任务模板
        query = """
        SELECT * FROM fy_cross_model_process 
        WHERE model_process_code LIKE %s 
           OR model_process_name LIKE %s
           OR id = %s
        """
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 尝试按ID查询
        if cross_model.isdigit():
            cursor.execute(query, (f'%{cross_model}%', f'%{cross_model}%', int(cross_model)))
        else:
            cursor.execute(query, (f'%{cross_model}%', f'%{cross_model}%', 0))
        
        models = cursor.fetchall()
        
        if not models:
            result['error'] = f'未找到跨环境任务模板 {cross_model}'
            return result
        
        # 获取模板详情
        model_data = []
        for model in models:
            model_info = dict(model)
            
            # 查询子任务
            model_id = model.get('id')
            if model_id:
                detail_query = """
                SELECT * FROM fy_cross_model_process_detail 
                WHERE model_process_id = %s 
                ORDER BY task_seq
                """
                cursor.execute(detail_query, (model_id,))
                details = cursor.fetchall()
                model_info['details'] = details
            
            model_data.append(model_info)
        
        result['success'] = True
        result['data'] = model_data
        result['count'] = len(model_data)
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result