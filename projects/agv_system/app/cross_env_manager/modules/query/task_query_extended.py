#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务查询扩展模块
基于1.3项目的FindTheTask.php功能移植
"""

import pymysql
from datetime import datetime
from modules.database.connection import get_db_connection

def get_task_info_by_order_id(order_id, server_ip=None):
    """
    根据任务订单ID查询任务详细信息
    对应FindTheTask.php功能
    """
    if server_ip:
        # 如果指定了服务器IP，使用生产环境连接
        conn = connect_to_production_db(server_ip)
    else:
        # 使用默认配置的数据库连接
        conn = get_db_connection()
    
    if conn is None:
        return {"error": "数据库连接失败"}
    
    try:
        with conn.cursor() as cursor:
            # 查询任务组信息
            sql = "SELECT * FROM task_group WHERE third_order_id = %s"
            cursor.execute(sql, (order_id,))
            task_group = cursor.fetchone()
            
            if not task_group:
                return {"error": "未找到对应的任务信息"}
            
            # 获取设备IP
            device_ip = get_device_ip_by_code(conn, task_group['robot_id'])
            
            # 获取货架模型名称
            shelf_model_name = get_shelf_model_name(conn, task_group['shelf_model'])
            
            # 获取任务状态名称
            task_status_name = get_task_status_name(conn, task_group['status'])
            
            # 格式化时间
            create_time = format_timestamp(task_group['create_time'])
            start_time = format_timestamp(task_group['start_time'])
            end_time = format_timestamp(task_group['end_time'])
            
            result = {
                "area_id": task_group['area_id'],
                "template_code": task_group['template_code'],
                "robot_num": task_group['robot_num'],
                "robot_id": task_group['robot_id'],
                "device_ip": device_ip,
                "path_points": task_group['path_points'],
                "robot_type": task_group['robot_type'],
                "shelf_model": task_group['shelf_model'],
                "shelf_model_name": shelf_model_name,
                "carrier_code": task_group['carrier_code'],
                "error_desc": task_group['error_desc'],
                "create_time": create_time,
                "start_time": start_time,
                "end_time": end_time,
                "status": task_group['status'],
                "task_status_name": task_status_name,
                "order_id": task_group['order_id'],
                "out_order_id": task_group['out_order_id'],
                "tg_id": task_group['id']
            }
            
            return result
            
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}
    finally:
        conn.close()

def get_task_group_by_order_id(order_id, server_ip=None):
    """
    根据订单ID获取task_group和task_group_detail信息
    支持本地数据库和远程服务器查询
    按照FindTheTask.php的逻辑完善查询
    """
    from modules.database.connection import get_db_connection
    
    # 首先尝试查询本地数据库
    conn = get_db_connection()
    if conn is None:
        return {"error": "数据库连接失败"}
    
    try:
        with conn.cursor() as cursor:
            # 查询task_group信息（按照PHP文件的逻辑）
            sql = "SELECT * FROM task_group WHERE third_order_id = %s OR order_id = %s OR out_order_id = %s"
            cursor.execute(sql, (order_id, order_id, order_id))
            task_group = cursor.fetchone()
            
            if task_group:
                # 关联查询其他信息（按照PHP文件的逻辑）
                # 1. 查询设备IP
                device_ip = None
                if task_group.get('robot_id'):
                    try:
                        sql = "SELECT DEVICE_IP FROM agv_robot WHERE DEVICE_CODE = %s"
                        cursor.execute(sql, (task_group['robot_id'],))
                        device_ip_result = cursor.fetchone()
                        if device_ip_result:
                            device_ip = device_ip_result['DEVICE_IP']
                    except Exception as e:
                        print(f"查询设备IP失败: {e}")
                
                # 2. 查询货架模型名称
                shelf_model_name = None
                if task_group.get('shelf_model'):
                    try:
                        sql = "SELECT name FROM load_config WHERE model = %s"
                        cursor.execute(sql, (task_group['shelf_model'],))
                        shelf_model_result = cursor.fetchone()
                        if shelf_model_result:
                            shelf_model_name = shelf_model_result['name']
                    except Exception as e:
                        print(f"查询货架模型名称失败: {e}")
                
                # 3. 查询任务状态名称
                task_status_name = None
                if task_group.get('status') is not None:
                    try:
                        sql = "SELECT task_status_name FROM task_status_config WHERE task_status = %s"
                        cursor.execute(sql, (task_group['status'],))
                        status_result = cursor.fetchone()
                        if status_result:
                            task_status_name = status_result['task_status_name']
                    except Exception as e:
                        print(f"查询任务状态名称失败: {e}")
                
                # 添加关联查询结果到task_group
                task_group['device_ip'] = device_ip
                task_group['shelf_model_name'] = shelf_model_name
                task_group['task_status_name'] = task_status_name
                
                # 查询task_group_detail信息
                task_group_details = []
                try:
                    sql = """
                    SELECT 
                        id, tg_id, task_seq, start_point, end_point, 
                        x, y, action, angel, shelf_num, robot_id,
                        robot_num, start_time, end_time, status,
                        area_id, task_type, point_type, need_trigger,
                        notify_third, shelf_model
                    FROM task_group_detail 
                    WHERE tg_id = %s 
                    ORDER BY task_seq
                    """
                    cursor.execute(sql, (task_group['id'],))
                    task_group_details = cursor.fetchall()
                    
                    # 为每个子任务查询关联信息
                    for detail in task_group_details:
                        # 查询子任务设备IP
                        if detail.get('robot_id'):
                            try:
                                sql = "SELECT DEVICE_IP FROM agv_robot WHERE DEVICE_CODE = %s"
                                cursor.execute(sql, (detail['robot_id'],))
                                detail_device_ip = cursor.fetchone()
                                if detail_device_ip:
                                    detail['device_ip'] = detail_device_ip['DEVICE_IP']
                            except Exception as e:
                                print(f"查询子任务设备IP失败: {e}")
                        
                        # 查询子任务状态名称
                        if detail.get('status') is not None:
                            try:
                                sql = "SELECT task_status_name FROM task_status_config WHERE task_status = %s"
                                cursor.execute(sql, (detail['status'],))
                                detail_status = cursor.fetchone()
                                if detail_status:
                                    detail['task_status_name'] = detail_status['task_status_name']
                            except Exception as e:
                                print(f"查询子任务状态名称失败: {e}")
                                
                except Exception as detail_error:
                    # 如果查询失败，尝试简单查询
                    try:
                        sql = "SELECT * FROM task_group_detail WHERE tg_id = %s ORDER BY task_seq"
                        cursor.execute(sql, (task_group['id'],))
                        task_group_details = cursor.fetchall()
                    except Exception as e2:
                        print(f"注意: task_group_detail表查询失败: {e2}")
                        task_group_details = []
                
                return {
                    "taskGroup": task_group,
                    "details": task_group_details,
                    "source": "local"
                }
            
    except Exception as e:
        print(f"本地数据库查询失败: {e}")
    finally:
        conn.close()
    
    # 如果本地没有找到，尝试查询远程服务器（跨环境任务）
    try:
        if not server_ip:
            server_ip = "10.68.2.32"
        
        # 连接到生产环境数据库
        prod_conn = connect_to_production_db(server_ip)
        
        with prod_conn.cursor() as cursor:
            # 查询fy_cross_task表
            sql = "SELECT * FROM fy_cross_task WHERE orderId = %s"
            cursor.execute(sql, (order_id,))
            cross_task = cursor.fetchone()
            
            if cross_task:
                # 查询子任务详情
                sql = "SELECT * FROM fy_cross_task_detail WHERE order_id = %s"
                cursor.execute(sql, (order_id,))
                cross_task_details = cursor.fetchall()
                
                # 转换为task_group格式（兼容前端显示）
                task_group = {
                    "id": cross_task.get('id'),
                    "third_order_id": cross_task.get('orderId'),
                    "order_id": cross_task.get('orderId'),
                    "model_process_code": cross_task.get('model_process_code'),
                    "status": cross_task.get('task_status'),
                    "create_time": cross_task.get('create_time'),
                    "start_time": cross_task.get('start_time'),
                    "end_time": cross_task.get('end_time'),
                    "source": "cross_task"
                }
                
                # 转换子任务格式
                details = []
                for detail in cross_task_details:
                    details.append({
                        "id": detail.get('id'),
                        "sub_order_id": detail.get('sub_order_id'),
                        "service_url": detail.get('service_url'),
                        "create_time": detail.get('create_time'),
                        "source": "cross_task_detail"
                    })
                
                return {
                    "taskGroup": task_group,
                    "details": details,
                    "source": "remote"
                }
            else:
                return {"error": "未找到对应的任务记录（本地和远程）"}
                
    except Exception as e:
        print(f"远程服务器查询失败: {e}")
        return {"error": f"远程服务器查询失败: {str(e)}"}
    
    return {"error": "未找到对应的任务记录"}

def get_cross_task_info(order_id, server_ip=None):
    """
    查询跨环境任务信息
    对应FindTheTaskKua.php功能
    """
    if server_ip:
        conn = connect_to_production_db(server_ip)
    else:
        from modules.database.connection import get_db_connection
        conn = get_db_connection()
    
    if conn is None:
        return {"error": "数据库连接失败"}
    
    try:
        with conn.cursor() as cursor:
            # 查询跨环境任务详情
            sql = "SELECT * FROM fy_cross_task_detail WHERE order_id = %s"
            cursor.execute(sql, (order_id,))
            cross_task_details = cursor.fetchall()
            
            # 查询跨环境任务模板信息
            sql = "SELECT model_process_code FROM fy_cross_task WHERE orderId = %s"
            cursor.execute(sql, (order_id,))
            model_process_code_result = cursor.fetchone()
            
            model_process_code = None
            active_task_count = 0
            related_tasks = []
            
            if model_process_code_result:
                model_process_code = model_process_code_result.get('model_process_code')
                
                if model_process_code:
                    # 统计当前执行中的任务数
                    sql = """
                        SELECT COUNT(0) as count 
                        FROM fy_cross_task 
                        WHERE model_process_code = %s 
                        AND task_status IN (0,1,6,4,9,10)
                    """
                    cursor.execute(sql, (model_process_code,))
                    count_result = cursor.fetchone()
                    active_task_count = count_result['count'] if count_result else 0
                    
                    # 查询所有相关任务
                    sql = """
                        SELECT * FROM fy_cross_task 
                        WHERE model_process_code = %s 
                        AND task_status IN (0,1,6,4,9,10)
                    """
                    cursor.execute(sql, (model_process_code,))
                    related_tasks = cursor.fetchall()
            
            result = {
                "cross_task_details": cross_task_details,
                "model_process_code": model_process_code,
                "active_task_count": active_task_count,
                "related_tasks": related_tasks
            }
            
            return result
            
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}
    finally:
        conn.close()

def get_device_ip_by_code(conn, device_code):
    """根据设备序列号获取设备IP"""
    try:
        with conn.cursor() as cursor:
            sql = "SELECT DEVICE_IP FROM agv_robot WHERE DEVICE_CODE = %s"
            cursor.execute(sql, (device_code,))
            result = cursor.fetchone()
            return result['DEVICE_IP'] if result else "未知"
    except:
        return "未知"

def get_shelf_model_name(conn, shelf_model):
    """根据货架模型编号获取货架模型名称"""
    try:
        with conn.cursor() as cursor:
            sql = "SELECT name FROM load_config WHERE model = %s"
            cursor.execute(sql, (shelf_model,))
            result = cursor.fetchone()
            return result['name'] if result else "未知"
    except:
        return "未知"

def get_task_status_name(conn, status):
    """根据任务状态值获取状态名称"""
    try:
        with conn.cursor() as cursor:
            sql = "SELECT task_status_name FROM task_status_config WHERE task_status = %s"
            cursor.execute(sql, (status,))
            result = cursor.fetchone()
            return result['task_status_name'] if result else "未知"
    except:
        return "未知"

def format_timestamp(timestamp):
    """格式化时间戳"""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return ""

def connect_to_production_db(server_ip, db_name="wms"):
    """连接到生产环境数据库"""
    try:
        conn = pymysql.connect(
            host=server_ip,
            user='wms',
            password='CCshenda889',
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        raise Exception(f"连接生产环境数据库失败: {str(e)}")

def search_tasks_by_template(template_code, server_ip="10.68.2.32"):
    """
    根据任务模板代码搜索任务
    对应Kua.php功能
    """
    conn = connect_to_production_db(server_ip)
    
    try:
        with conn.cursor() as cursor:
            # 统计当前执行中的任务数
            sql = """
                SELECT COUNT(0) as count 
                FROM fy_cross_task 
                WHERE model_process_code = %s 
                AND task_status IN (0,1,6,4,9,10)
            """
            cursor.execute(sql, (template_code,))
            count_result = cursor.fetchone()
            active_task_count = count_result['count'] if count_result else 0
            
            # 查询所有相关任务
            sql = """
                SELECT * FROM fy_cross_task 
                WHERE model_process_code = %s 
                AND task_status IN (0,1,6,4,9,10)
            """
            cursor.execute(sql, (template_code,))
            tasks = cursor.fetchall()
            
            return {
                "active_task_count": active_task_count,
                "tasks": tasks
            }
            
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}
    finally:
        conn.close()

def get_cross_model_process_info(template_code, server_ip="10.68.2.32"):
    """
    查询跨环境任务模板信息及子任务
    对应Chech_Kua_model_process.php功能
    """
    conn = connect_to_production_db(server_ip)
    
    try:
        with conn.cursor() as cursor:
            # 查询主模板信息
            sql = "SELECT * FROM fy_cross_model_process WHERE model_process_code = %s"
            cursor.execute(sql, (template_code,))
            main_template = cursor.fetchone()
            
            if not main_template:
                return {"error": "未找到对应的跨环境任务模板"}
            
            template_id = main_template['id']
            
            # 查询子任务信息
            sql = "SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = %s"
            cursor.execute(sql, (template_id,))
            sub_tasks = cursor.fetchall()
            
            return {
                "main_template": main_template,
                "sub_tasks": sub_tasks,
                "template_id": template_id
            }
            
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}
    finally:
        conn.close()