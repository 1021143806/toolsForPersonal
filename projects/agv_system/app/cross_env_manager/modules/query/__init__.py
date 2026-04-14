#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询功能模块
包含agv-task-query的所有查询功能，适配Python Flask
"""

# 动态导入，避免循环依赖
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

# 动态导入模块
try:
    from .task_query import find_task_by_id, find_cross_task_by_id, check_cross_model
    TASK_QUERY_AVAILABLE = True
except ImportError:
    TASK_QUERY_AVAILABLE = False
    find_task_by_id = find_cross_task_by_id = check_cross_model = None

try:
    from .device_validation import validate_devices, query_devices_in_environment, get_server_ips_from_cross_model
    DEVICE_VALIDATION_AVAILABLE = True
except ImportError:
    DEVICE_VALIDATION_AVAILABLE = False
    validate_devices = query_devices_in_environment = get_server_ips_from_cross_model = None

try:
    from .cross_model_query import query_cross_model
    CROSS_MODEL_QUERY_AVAILABLE = True
except ImportError:
    CROSS_MODEL_QUERY_AVAILABLE = False
    query_cross_model = None

try:
    from .join_point_query import query_join_point
    JOIN_POINT_QUERY_AVAILABLE = True
except ImportError:
    JOIN_POINT_QUERY_AVAILABLE = False
    query_join_point = None

try:
    from .shelf_model_query import query_shelf_model
    SHELF_MODEL_QUERY_AVAILABLE = True
except ImportError:
    SHELF_MODEL_QUERY_AVAILABLE = False
    query_shelf_model = None

try:
    from .shelf_query import query_shelf
    SHELF_QUERY_AVAILABLE = True
except ImportError:
    SHELF_QUERY_AVAILABLE = False
    query_shelf = None

try:
    from .agv_status import show_agv_info_one_area, get_agv_device_detail, get_agv_alarms
    AGV_STATUS_AVAILABLE = True
except ImportError:
    AGV_STATUS_AVAILABLE = False
    show_agv_info_one_area = get_agv_device_detail = get_agv_alarms = None

__all__ = [
    'find_task_by_id',
    'find_cross_task_by_id',
    'validate_devices',
    'query_devices_in_environment',
    'query_cross_model',
    'get_server_ips_from_cross_model',
    'query_join_point',
    'query_shelf_model',
    'query_shelf',
    'show_agv_info_one_area'
]