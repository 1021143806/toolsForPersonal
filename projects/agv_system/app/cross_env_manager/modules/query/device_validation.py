#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备验证模块
基于agv-task-query的validate-device.php功能
"""

import pymysql
import re
from typing import Dict, List, Optional, Any
from ..database.connection import connect_to_server
from ..database.helpers import parse_device_codes, parse_server_ips, build_in_condition

def validate_devices(device_codes_str: str, cross_model: str = '', 
                    server_ips_str: str = '', strict: bool = False) -> Dict[str, Any]:
    """
    验证设备序列号配置（模仿validate-device.php）
    
    Args:
        device_codes_str: 设备序列号字符串，逗号分隔
        cross_model: 跨环境大任务模板
        server_ips_str: 服务器IP字符串，逗号分隔
        strict: 严格模式
        
    Returns:
        验证结果字典
    """
    # 解析设备序列号
    device_codes = parse_device_codes(device_codes_str)
    if not device_codes:
        return {
            'success': False,
            'error': '设备序列号列表为空',
            'device_codes': [],
            'overall_status': 'incomplete'
        }
    
    # 确定要检查的服务器IP列表
    server_ips = []
    if server_ips_str:
        server_ips = parse_server_ips(server_ips_str)
    elif cross_model:
        server_ips = get_server_ips_from_cross_model(cross_model)
    else:
        # 默认使用所有已知环境IP
        server_ips = ['31', '32', '17']
    
    # 查询报告
    report = {
        'device_codes': device_codes,
        'cross_model': cross_model,
        'server_ips': server_ips,
        'strict_mode': strict,
        'overall_status': 'complete',
        'environment_checks': {},
        'missing_configs': [],
        'suggestions': []
    }
    
    # 对每个服务器IP进行检查
    for ip in server_ips:
        env_report = query_devices_in_environment(ip, device_codes, strict)
        report['environment_checks'][ip] = env_report
        if env_report['status'] == 'incomplete':
            report['overall_status'] = 'incomplete'
            report['missing_configs'].extend(env_report['missing'])
    
    # 生成建议
    if report['overall_status'] == 'incomplete':
        report['suggestions'].append('部分设备配置缺失，请根据缺失项补充相应配置。')
    else:
        report['suggestions'].append('所有设备配置完整，跨环境一致性良好。')
    
    report['success'] = True
    return report

def query_devices_in_environment(ip_suffix: str, device_codes: List[str], 
                                strict: bool) -> Dict[str, Any]:
    """
    在特定环境中查询设备配置详情
    
    Args:
        ip_suffix: 服务器IP后缀
        device_codes: 设备序列号列表
        strict: 严格模式
        
    Returns:
        环境检查结果
    """
    # 连接数据库
    conn = connect_to_server(ip_suffix)
    if not conn:
        return {
            'status': 'incomplete',
            'message': '无法连接数据库',
            'missing': ['数据库连接失败'],
            'details': [],
            'tables_summary': {}
        }
    
    details = []
    missing = []
    status = 'complete'
    tables_summary = {}
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1. 查询 agv_robot 表
        in_condition = build_in_condition(device_codes, conn)
        sql = f"SELECT * FROM agv_robot WHERE device_code IN ({in_condition})"
        cursor.execute(sql)
        found_in_robot = []
        
        rows = cursor.fetchall()
        for row in rows:
            found_in_robot.append(row['device_code'])
            details.append({
                'device': row['device_code'],
                'table': 'agv_robot',
                'status': 'found',
                'data': row
            })
        
        tables_summary['agv_robot'] = f'{len(found_in_robot)} 条记录'
        
        # 检查缺失的设备
        for code in device_codes:
            if code not in found_in_robot:
                missing.append(f"设备 {code} 在 agv_robot 表中不存在")
                details.append({
                    'device': code,
                    'table': 'agv_robot',
                    'status': 'missing',
                    'data': None
                })
                status = 'incomplete'
        
        # 2. 查询 agv_robot_ext 表
        sql = f"SELECT * FROM agv_robot_ext WHERE device_code IN ({in_condition})"
        cursor.execute(sql)
        found_in_ext = []
        
        rows = cursor.fetchall()
        for row in rows:
            found_in_ext.append(row['device_code'])
            details.append({
                'device': row['device_code'],
                'table': 'agv_robot_ext',
                'status': 'found',
                'data': row
            })
        
        tables_summary['agv_robot_ext'] = f'{len(found_in_ext)} 条记录'
        
        # 检查缺失的设备（在ext中）- 严格模式
        if strict:
            for code in device_codes:
                if code not in found_in_ext:
                    missing.append(f"设备 {code} 在 agv_robot_ext 表中不存在")
                    details.append({
                        'device': code,
                        'table': 'agv_robot_ext',
                        'status': 'missing',
                        'data': None
                    })
                    status = 'incomplete'
        
        # 3. 查询 agv_model 表（根据设备型号）
        device_types = []
        if found_in_robot:
            # 获取设备型号列表
            sql = f"SELECT DISTINCT devicetype FROM agv_robot WHERE device_code IN ({in_condition})"
            cursor.execute(sql)
            device_types = [row['devicetype'] for row in cursor.fetchall() if row['devicetype']]
            
            if device_types:
                type_condition = build_in_condition(device_types, conn)
                sql = f"SELECT * FROM agv_model WHERE SERIES_MODEL_NAME IN ({type_condition})"
                cursor.execute(sql)
                found_models = []
                
                rows = cursor.fetchall()
                for row in rows:
                    found_models.append(row['SERIES_MODEL_NAME'])
                    details.append({
                        'device': f'型号 {row["SERIES_MODEL_NAME"]}',
                        'table': 'agv_model',
                        'status': 'found',
                        'data': row
                    })
                
                tables_summary['agv_model'] = f'{len(found_models)} 条记录'
                
                # 检查缺失的型号
                for device_type in device_types:
                    if device_type not in found_models:
                        missing.append(f"设备型号 {device_type} 在 agv_model 表中不存在")
                        details.append({
                            'device': device_type,
                            'table': 'agv_model',
                            'status': 'missing',
                            'data': None
                        })
                        status = 'incomplete'
        
        # 4. 查询 agv_model_init 表（根据设备型号）
        if found_in_robot and device_types:
            type_condition = build_in_condition(device_types, conn)
            sql = f"SELECT * FROM agv_model_init WHERE SERIES_MODEL_NAME IN ({type_condition})"
            
            try:
                cursor.execute(sql)
                found_model_inits = []
                
                rows = cursor.fetchall()
                for row in rows:
                    found_model_inits.append(row['SERIES_MODEL_NAME'])
                    details.append({
                        'device': f'型号 {row["SERIES_MODEL_NAME"]}',
                        'table': 'agv_model_init',
                        'status': 'found',
                        'data': row
                    })
                
                tables_summary['agv_model_init'] = f'{len(found_model_inits)} 条记录'
                
                # 检查缺失的型号
                for device_type in device_types:
                    if device_type not in found_model_inits:
                        missing.append(f"设备型号 {device_type} 在 agv_model_init 表中不存在")
                        details.append({
                            'device': device_type,
                            'table': 'agv_model_init',
                            'status': 'missing',
                            'data': None
                        })
                        status = 'incomplete'
            except pymysql.Error:
                # 表可能不存在，忽略
                tables_summary['agv_model_init'] = '表不存在或查询失败'
    
    except pymysql.Error as e:
        missing.append(f"数据库查询错误: {str(e)}")
        status = 'incomplete'
    finally:
        conn.close()
    
    return {
        'status': status,
        'message': '设备配置查询完成' if status == 'complete' else '设备配置存在缺失',
        'missing': missing,
        'details': details,
        'tables_summary': tables_summary
    }

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