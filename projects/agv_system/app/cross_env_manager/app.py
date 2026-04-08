#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨环境任务模板管理Web应用
用于查询、修改和插入跨环境任务模板
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'cross_env_manager_secret_key_2026')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 数据库配置 - 从环境变量读取
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'agv_cross_env_test'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """执行SQL查询"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch and query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid if query.strip().upper().startswith('INSERT') else cursor.rowcount
        
        return result
    except Error as e:
        print(f"查询执行错误: {e}")
        conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def extract_id_from_code(model_process_code):
    """从model_process_code中提取ID后缀"""
    # 匹配末尾的数字ID，如_HJBY_test_484中的484
    match = re.search(r'_(\d+)$', model_process_code)
    if match:
        return int(match.group(1))
    return None

def get_next_available_id(base_name):
    """获取下一个可用的ID"""
    # 查询所有以base_name开头的记录
    query = "SELECT model_process_code FROM fy_cross_model_process WHERE model_process_code LIKE %s"
    params = (f"{base_name}_%",)
    results = execute_query(query, params)
    
    if not results:
        return 1
    
    # 提取所有ID
    ids = []
    for row in results:
        code = row['model_process_code']
        id_num = extract_id_from_code(code)
        if id_num is not None:
            ids.append(id_num)
    
    if not ids:
        return 1
    
    return max(ids) + 1

@app.route('/')
def index():
    """主页 - 搜索页面"""
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """搜索任务模板"""
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
    else:  # GET请求
        search_term = request.args.get('search_term', '').strip()
    
    if not search_term:
        flash('请输入搜索关键词', 'warning')
        return redirect(url_for('index'))
    
    # 查询匹配的任务模板
    query = """
    SELECT * FROM fy_cross_model_process 
    WHERE model_process_code LIKE %s 
    ORDER BY id DESC
    """
    params = (f'%{search_term}%',)
    templates = execute_query(query, params)
    
    if not templates:
        flash(f'未找到包含 "{search_term}" 的任务模板', 'info')
        return redirect(url_for('index'))
    
    # 获取每个模板的子任务
    for template in templates:
        detail_query = """
        SELECT * FROM fy_cross_model_process_detail 
        WHERE model_process_id = %s 
        ORDER BY task_seq
        """
        details = execute_query(detail_query, (template['id'],))
        template['details'] = details or []
    
    return render_template('search_results.html', 
                         templates=templates, 
                         search_term=search_term)

@app.route('/template/<int:template_id>')
def view_template(template_id):
    """查看单个任务模板详情"""
    # 获取主模板信息
    query = "SELECT * FROM fy_cross_model_process WHERE id = %s"
    template = execute_query(query, (template_id,))
    
    if not template:
        flash('任务模板不存在', 'error')
        return redirect(url_for('index'))
    
    template = template[0]
    
    # 获取子任务
    detail_query = """
    SELECT * FROM fy_cross_model_process_detail 
    WHERE model_process_id = %s 
    ORDER BY task_seq
    """
    details = execute_query(detail_query, (template_id,))
    
    return render_template('template_detail.html', 
                         template=template, 
                         details=details)

@app.route('/edit/<int:template_id>', methods=['GET', 'POST'])
def edit_template(template_id):
    """编辑任务模板"""
    if request.method == 'GET':
        # 获取主模板信息
        query = "SELECT * FROM fy_cross_model_process WHERE id = %s"
        template = execute_query(query, (template_id,))
        
        if not template:
            flash('任务模板不存在', 'error')
            return redirect(url_for('index'))
        
        template = template[0]
        
        # 获取子任务
        detail_query = """
        SELECT * FROM fy_cross_model_process_detail 
        WHERE model_process_id = %s 
    ORDER BY task_seq
        """
        details = execute_query(detail_query, (template_id,))
        
        return render_template('edit_template.html', 
                             template=template, 
                             details=details)
    
    else:  # POST请求 - 更新模板
        # 获取表单数据
        form_data = request.form
        
        # 更新主模板
        update_query = """
        UPDATE fy_cross_model_process 
        SET model_process_name = %s,
            enable = %s,
            request_url = %s,
            capacity = %s,
            target_points = %s,
            area_id = %s,
            target_points_ip = %s,
            backflow_template_code = %s,
            comeback_template_code = %s,
            change_charge_template_code = %s,
            min_power = %s,
            back_wait_time = %s,
            check_area_name = %s
        WHERE id = %s
        """
        
        params = (
            form_data.get('model_process_name'),
            int(form_data.get('enable', 0)),
            form_data.get('request_url'),
            int(form_data.get('capacity', -1)),
            form_data.get('target_points'),
            int(form_data.get('area_id', 0)),
            form_data.get('target_points_ip'),
            form_data.get('backflow_template_code'),
            form_data.get('comeback_template_code'),
            form_data.get('change_charge_template_code'),
            int(form_data.get('min_power', 0)),
            int(form_data.get('back_wait_time', 0)),
            form_data.get('check_area_name'),
            template_id
        )
        
        result = execute_query(update_query, params, fetch=False)
        
        if result is not None:
            flash('任务模板更新成功', 'success')
        else:
            flash('任务模板更新失败', 'error')
        
        return redirect(url_for('view_template', template_id=template_id))

@app.route('/edit_detail/<int:detail_id>', methods=['POST'])
def edit_detail(detail_id):
    """编辑子任务"""
    form_data = request.form
    
    update_query = """
    UPDATE fy_cross_model_process_detail 
    SET task_seq = %s,
        task_servicec = %s,
        template_code = %s,
        template_name = %s,
        task_path = %s,
        backflow_template_code = %s,
        comeback_template_code = %s,
        back_wait_time = %s
    WHERE id = %s
    """
    
    params = (
        int(form_data.get('task_seq', 0)),
        form_data.get('task_servicec'),
        form_data.get('template_code'),
        form_data.get('template_name'),
        form_data.get('task_path'),
        form_data.get('backflow_template_code'),
        form_data.get('comeback_template_code'),
        int(form_data.get('back_wait_time', 0)),
        detail_id
    )
    
    result = execute_query(update_query, params, fetch=False)
    
    if result is not None:
        flash('子任务更新成功', 'success')
    else:
        flash('子任务更新失败', 'error')
    
    # 获取模板ID以便重定向
    query = "SELECT model_process_id FROM fy_cross_model_process_detail WHERE id = %s"
    detail = execute_query(query, (detail_id,))
    
    if detail:
        template_id = detail[0]['model_process_id']
        return redirect(url_for('view_template', template_id=template_id))
    
    return redirect(url_for('index'))

@app.route('/copy/<int:template_id>', methods=['GET', 'POST'])
def copy_template(template_id):
    """复制任务模板"""
    if request.method == 'GET':
        # 获取原模板信息
        query = "SELECT * FROM fy_cross_model_process WHERE id = %s"
        template = execute_query(query, (template_id,))
        
        if not template:
            flash('任务模板不存在', 'error')
            return redirect(url_for('index'))
        
        template = template[0]
        
        # 获取子任务
        detail_query = """
        SELECT * FROM fy_cross_model_process_detail 
        WHERE model_process_id = %s 
        ORDER BY task_seq
        """
        details = execute_query(detail_query, (template_id,))
        
        return render_template('copy_template.html', 
                             template=template, 
                             details=details)
    
    else:  # POST请求 - 创建新模板
        form_data = request.form
        new_base_name = form_data.get('new_base_name', '').strip()
        
        if not new_base_name:
            flash('请输入新模板的基础名称', 'error')
            return redirect(url_for('copy_template', template_id=template_id))
        
        # 获取下一个可用ID
        next_id = get_next_available_id(new_base_name)
        new_model_process_code = f"{new_base_name}_{next_id}"
        
        # 获取原模板信息
        query = "SELECT * FROM fy_cross_model_process WHERE id = %s"
        original_templates = execute_query(query, (template_id,))
        
        if not original_templates:
            flash('原模板不存在或无法访问', 'error')
            return redirect(url_for('copy_template', template_id=template_id))
        
        original_template = original_templates[0]
        
        # 插入新模板
        insert_query = """
        INSERT INTO fy_cross_model_process 
        (model_process_code, model_process_name, enable, request_url, capacity, 
         target_points, area_id, target_points_ip, backflow_template_code, 
         comeback_template_code, change_charge_template_code, min_power, 
         back_wait_time, check_area_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # 辅助函数：安全地将值转换为整数，处理None值
        def safe_int(value, default=0):
            if value is None:
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        
        params = (
            new_model_process_code,
            form_data.get('model_process_name', original_template['model_process_name']),
            safe_int(form_data.get('enable'), original_template['enable']),
            form_data.get('request_url', original_template['request_url']),
            safe_int(form_data.get('capacity'), original_template['capacity']),
            form_data.get('target_points', original_template['target_points']),
            safe_int(form_data.get('area_id'), original_template['area_id']),
            form_data.get('target_points_ip', original_template['target_points_ip']),
            form_data.get('backflow_template_code', original_template.get('backflow_template_code')),
            form_data.get('comeback_template_code', original_template.get('comeback_template_code')),
            form_data.get('change_charge_template_code', original_template.get('change_charge_template_code')),
            safe_int(form_data.get('min_power'), original_template.get('min_power', 0)),
            safe_int(form_data.get('back_wait_time'), original_template.get('back_wait_time', 0)),
            form_data.get('check_area_name', original_template.get('check_area_name'))
        )
        
        new_template_id = execute_query(insert_query, params, fetch=False)
        
        if new_template_id:
            # 复制子任务
            detail_query = """
            SELECT * FROM fy_cross_model_process_detail 
            WHERE model_process_id = %s 
            ORDER BY task_seq
            """
            original_details = execute_query(detail_query, (template_id,))
            
            if original_details:
                for detail in original_details:
                    insert_detail_query = """
                    INSERT INTO fy_cross_model_process_detail 
                    (model_process_id, task_seq, task_servicec, template_code, 
                     template_name, task_path, backflow_template_code, 
                     comeback_template_code, back_wait_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    detail_params = (
                        new_template_id,
                        detail['task_seq'],
                        detail['task_servicec'],
                        detail['template_code'],
                        detail['template_name'],
                        detail['task_path'],
                        detail['backflow_template_code'],
                        detail['comeback_template_code'],
                        detail['back_wait_time']
                    )
                    
                    execute_query(insert_detail_query, detail_params, fetch=False)
            
            flash(f'模板复制成功！新模板代码: {new_model_process_code}', 'success')
            return redirect(url_for('view_template', template_id=new_template_id))
        else:
            flash('模板复制失败', 'error')
            return redirect(url_for('copy_template', template_id=template_id))

@app.route('/api/search_suggestions', methods=['GET'])
def search_suggestions():
    """搜索建议API"""
    term = request.args.get('term', '').strip()
    
    if not term:
        return jsonify([])
    
    query = """
    SELECT model_process_code, model_process_name 
    FROM fy_cross_model_process 
    WHERE model_process_code LIKE %s OR model_process_name LIKE %s
    LIMIT 10
    """
    params = (f'%{term}%', f'%{term}%')
    results = execute_query(query, params)
    
    suggestions = []
    for row in results:
        suggestions.append({
            'code': row['model_process_code'],
            'name': row['model_process_name']
        })
    
    return jsonify(suggestions)

if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"启动跨环境任务模板管理系统...")
    print(f"数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"服务地址: http://{host}:{port}")
    print(f"调试模式: {debug}")
    
    app.run(debug=debug, host=host, port=port)