#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理模块
支持多服务器连接，模仿agv-task-query的数据库连接方式
"""

import pymysql
from pymysql.cursors import DictCursor
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def get_db_config():
    """
    获取数据库配置
    从config/env.toml或环境变量读取配置
    """
    try:
        # 尝试导入tomli（Python 3.11+内置tomllib，低版本使用tomli）
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'env.toml')
        
        with open(config_path, 'rb') as f:
            config = tomllib.load(f)
        
        db_config = config.get('database', {})
        
        return {
            'host': db_config.get('host') or os.getenv('DB_HOST') or 'localhost',
            'port': int(db_config.get('port') or os.getenv('DB_PORT') or 3306),
            'user': db_config.get('user') or os.getenv('DB_USER') or 'root',
            'password': db_config.get('password') or os.getenv('DB_PASSWORD') or '',
            'database': db_config.get('name') or os.getenv('DB_NAME') or 'agv_cross_env_test',
            'charset': db_config.get('charset') or os.getenv('DB_CHARSET') or 'utf8mb4'
        }
    except Exception as e:
        print(f"读取数据库配置错误: {e}")
        # 返回默认配置
        return {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'agv_cross_env_test',
            'charset': 'utf8mb4'
        }

def get_db_connection(config=None):
    """
    获取数据库连接
    :param config: 可选的数据库配置，如果为None则使用默认配置
    :return: 数据库连接对象或None
    """
    try:
        if config is None:
            config = get_db_config()
        
        conn = pymysql.connect(**config, cursorclass=DictCursor)
        return conn
    except pymysql.Error as e:
        print(f"数据库连接错误: {e}")
        return None

def execute_query(query, params=None, fetch=True, config=None):
    """
    执行SQL查询
    :param query: SQL查询语句
    :param params: 查询参数
    :param fetch: 是否获取结果（用于SELECT查询）
    :param config: 可选的数据库配置
    :return: 查询结果或None
    """
    conn = get_db_connection(config)
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(DictCursor)
        cursor.execute(query, params or ())
        
        if fetch:
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                # 对于非SELECT查询但需要fetch的情况，返回空列表
                result = []
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

def get_production_db_config():
    """
    获取生产环境数据库配置
    用于连接生产环境数据库（只读）
    """
    return {
        'host': '10.68.2.32',
        'port': 3306,
        'user': 'wms',
        'password': 'CCshenda889',
        'database': 'wms',
        'charset': 'utf8mb4'
    }

def get_test_db_config():
    """
    获取测试环境数据库配置
    """
    return {
        'host': '47.98.244.173',
        'port': 53308,
        'user': 'root',
        'password': 'Qq13235202993',
        'database': 'ds',
        'charset': 'utf8mb4'
    }