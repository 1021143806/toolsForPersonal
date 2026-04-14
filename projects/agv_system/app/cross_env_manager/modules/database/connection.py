#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理模块
基于agv-task-query的数据库连接逻辑，适配Python Flask
"""

import pymysql
from pymysql.cursors import DictCursor
import os
import sys
from typing import Optional, Dict, Any, List, Union

# 默认配置（不直接从app导入以避免循环导入）
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'wms',
    'charset': 'utf8mb4'
}

# 尝试从环境变量加载配置
import os
db_host = os.getenv('DB_HOST')
if db_host:
    DB_CONFIG['host'] = db_host
db_port = os.getenv('DB_PORT')
if db_port:
    DB_CONFIG['port'] = int(db_port)
db_user = os.getenv('DB_USER')
if db_user:
    DB_CONFIG['user'] = db_user
db_password = os.getenv('DB_PASSWORD')
if db_password:
    DB_CONFIG['password'] = db_password
db_name = os.getenv('DB_NAME')
if db_name:
    DB_CONFIG['database'] = db_name
db_charset = os.getenv('DB_CHARSET')
if db_charset:
    DB_CONFIG['charset'] = db_charset

def get_db_connection(config: Optional[Dict[str, Any]] = None) -> Optional[pymysql.Connection]:
    """
    获取数据库连接
    
    Args:
        config: 数据库配置，如果为None则使用默认配置
        
    Returns:
        pymysql.Connection对象或None
    """
    try:
        if config is None:
            config = DB_CONFIG
        
        conn = pymysql.connect(**config)
        return conn
    except pymysql.Error as e:
        print(f"数据库连接错误: {e}")
        return None

def execute_query(query: str, params: Optional[tuple] = None, 
                  fetch: bool = True, config: Optional[Dict[str, Any]] = None) -> Union[List[Dict], int, None]:
    """
    执行SQL查询
    
    Args:
        query: SQL查询语句
        params: 查询参数
        fetch: 是否获取结果（用于SELECT查询）
        config: 数据库配置
        
    Returns:
        查询结果：对于SELECT返回列表，对于INSERT/UPDATE返回影响行数，失败返回None
    """
    conn = get_db_connection(config)
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(DictCursor)
        cursor.execute(query, params or ())
        
        if fetch and query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount
        
        return result
    except pymysql.Error as e:
        print(f"查询执行错误: {e}")
        conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def connect_to_server(ip_suffix: str) -> Optional[pymysql.Connection]:
    """
    连接到指定IP后缀的服务器（模仿agv-task-query的connectMsqlAgvWmsNoINFO）
    
    Args:
        ip_suffix: IP后缀，如'31'、'32'、'17'
        
    Returns:
        数据库连接对象或None
    """
    try:
        # 构建完整的IP地址
        ip = f"10.68.2.{ip_suffix}"
        
        conn = pymysql.connect(
            host=ip,
            port=3306,
            user='wms',
            password='CCshenda889',
            database='wms',
            charset='utf8mb4'
        )
        return conn
    except pymysql.Error as e:
        print(f"连接到服务器 {ip} 失败: {e}")
        return None

def connect_to_server_full_ip(full_ip: str) -> Optional[pymysql.Connection]:
    """
    连接到完整IP地址的服务器
    
    Args:
        full_ip: 完整的IP地址，如'10.68.2.31'
        
    Returns:
        数据库连接对象或None
    """
    try:
        conn = pymysql.connect(
            host=full_ip,
            port=3306,
            user='wms',
            password='CCshenda889',
            database='wms',
            charset='utf8mb4'
        )
        return conn
    except pymysql.Error as e:
        print(f"连接到服务器 {full_ip} 失败: {e}")
        return None

def test_connection(ip_suffix: str) -> bool:
    """
    测试数据库连接
    
    Args:
        ip_suffix: IP后缀
        
    Returns:
        连接是否成功
    """
    conn = connect_to_server(ip_suffix)
    if conn:
        conn.close()
        return True
    return False

def get_server_list() -> List[str]:
    """
    获取可用的服务器列表
    
    Returns:
        服务器IP后缀列表
    """
    servers = ['31', '32', '17', '27']  # 常见服务器
    available_servers = []
    
    for server in servers:
        if test_connection(server):
            available_servers.append(server)
    
    return available_servers

def execute_query_on_server(ip_suffix: str, query: str, params: Optional[tuple] = None) -> Union[List[Dict], int, None]:
    """
    在指定服务器上执行查询
    
    Args:
        ip_suffix: IP后缀
        query: SQL查询语句
        params: 查询参数
        
    Returns:
        查询结果
    """
    conn = connect_to_server(ip_suffix)
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(DictCursor)
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
        
        return result
    except pymysql.Error as e:
        print(f"查询执行错误: {e}")
        conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def batch_execute_on_servers(servers: List[str], query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
    """
    在多个服务器上批量执行查询
    
    Args:
        servers: 服务器IP后缀列表
        query: SQL查询语句
        params: 查询参数
        
    Returns:
        包含各服务器结果的字典
    """
    results = {}
    
    for server in servers:
        result = execute_query_on_server(server, query, params)
        results[server] = {
            'success': result is not None,
            'data': result
        }
    
    return results