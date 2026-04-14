#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGV状态查询模块
基于agv-task-query的agv-status.php功能
"""

import pymysql
from typing import Dict, List, Optional, Any
from ..database.connection import connect_to_server

def show_agv_info_one_area(server_ip_suffix: str, area_id: str = '2') -> Dict[str, Any]:
    """
    显示指定区域的AGV设备状态信息
    
    Args:
        server_ip_suffix: 服务器IP后缀
        area_id: 区域ID
        
    Returns:
        AGV状态信息字典
    """
    result = {
        'success': False,
        'server_ip': f'10.68.2.{server_ip_suffix}',
        'area_id': area_id,
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
        
        # 查询AGV设备信息
        sql = f"""
        SELECT 
            ar.device_code,
            ar.device_name,
            ar.devicetype,
            ar.DEVICE_IP,
            ar.area_id,
            ars.status,
            ars.battery,
            ars.position,
            ars.task_id,
            ars.update_time
        FROM agv_robot ar
        LEFT JOIN agv_state ars ON ar.device_code = ars.device_code
        WHERE ar.area_id = {pymysql.converters.escape_string(area_id)}
        ORDER BY ar.device_code
        """
        cursor.execute(sql)
        agv_devices = cursor.fetchall()
        
        # 查询区域信息
        sql2 = f"SELECT * FROM bms_area WHERE id = {pymysql.converters.escape_string(area_id)}"
        cursor.execute(sql2)
        area_info = cursor.fetchone()
        
        # 统计信息
        total_devices = len(agv_devices)
        online_devices = sum(1 for device in agv_devices if device.get('status') == 1)
        offline_devices = total_devices - online_devices
        
        # 设备状态分类
        status_categories = {
            'online': [],
            'offline': [],
            'charging': [],
            'error': []
        }
        
        for device in agv_devices:
            status = device.get('status')
            if status == 1:
                status_categories['online'].append(device)
            elif status == 0:
                status_categories['offline'].append(device)
            elif status == 2:
                status_categories['charging'].append(device)
            else:
                status_categories['error'].append(device)
        
        result['success'] = True
        result['data'] = {
            'agv_devices': agv_devices,
            'area_info': area_info,
            'statistics': {
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': offline_devices,
                'charging_devices': len(status_categories['charging']),
                'error_devices': len(status_categories['error'])
            },
            'status_categories': status_categories
        }
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result

def get_agv_device_detail(server_ip_suffix: str, device_code: str) -> Dict[str, Any]:
    """
    获取AGV设备详细信息
    
    Args:
        server_ip_suffix: 服务器IP后缀
        device_code: 设备序列号
        
    Returns:
        设备详细信息字典
    """
    result = {
        'success': False,
        'server_ip': f'10.68.2.{server_ip_suffix}',
        'device_code': device_code,
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
        
        # 查询设备基本信息
        sql = f"SELECT * FROM agv_robot WHERE device_code = '{pymysql.converters.escape_string(device_code)}'"
        cursor.execute(sql)
        device_info = cursor.fetchone()
        
        if not device_info:
            result['error'] = f'未找到设备 {device_code}'
            return result
        
        # 查询设备扩展信息
        sql2 = f"SELECT * FROM agv_robot_ext WHERE device_code = '{pymysql.converters.escape_string(device_code)}'"
        cursor.execute(sql2)
        device_ext_info = cursor.fetchone()
        
        # 查询设备状态
        sql3 = f"SELECT * FROM agv_state WHERE device_code = '{pymysql.converters.escape_string(device_code)}' ORDER BY update_time DESC LIMIT 1"
        cursor.execute(sql3)
        device_state = cursor.fetchone()
        
        # 查询设备型号信息
        device_type = device_info.get('devicetype')
        device_model_info = None
        if device_type:
            sql4 = f"SELECT * FROM agv_model WHERE SERIES_MODEL_NAME = '{pymysql.converters.escape_string(device_type)}'"
            cursor.execute(sql4)
            device_model_info = cursor.fetchone()
        
        # 查询最近的任务
        sql5 = f"""
        SELECT * FROM task_group 
        WHERE robot_id = '{pymysql.converters.escape_string(device_code)}' 
        ORDER BY create_time DESC 
        LIMIT 5
        """
        cursor.execute(sql5)
        recent_tasks = cursor.fetchall()
        
        result['success'] = True
        result['data'] = {
            'device_info': device_info,
            'device_ext_info': device_ext_info,
            'device_state': device_state,
            'device_model_info': device_model_info,
            'recent_tasks': recent_tasks
        }
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result

def get_agv_alarms(server_ip_suffix: str, limit: int = 20) -> Dict[str, Any]:
    """
    获取AGV告警信息
    
    Args:
        server_ip_suffix: 服务器IP后缀
        limit: 返回记录数限制
        
    Returns:
        告警信息字典
    """
    result = {
        'success': False,
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
        
        # 查询最近的告警信息
        sql = f"""
        SELECT 
            al.*,
            ar.device_name,
            ar.devicetype
        FROM agv_log_alarm al
        LEFT JOIN agv_robot ar ON al.device_code = ar.device_code
        ORDER BY al.create_time DESC
        LIMIT {limit}
        """
        cursor.execute(sql)
        alarms = cursor.fetchall()
        
        # 统计告警级别
        alarm_levels = {}
        for alarm in alarms:
            level = alarm.get('alarm_level', '未知')
            if level not in alarm_levels:
                alarm_levels[level] = 0
            alarm_levels[level] += 1
        
        result['success'] = True
        result['data'] = {
            'alarms': alarms,
            'alarm_levels': alarm_levels,
            'total_alarms': len(alarms)
        }
        
    except pymysql.Error as e:
        result['error'] = f'数据库查询错误: {str(e)}'
    finally:
        conn.close()
    
    return result