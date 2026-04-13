#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python 3.9兼容性修改：使用pymysql替代mysql.connector
import pymysql
from pymysql.cursors import DictCursor
# pymysql.install_as_MySQLdb()  # 不再使用MySQLdb兼容层

"""
跨环境任务模板管理Web应用
用于查询、修改和插入跨环境任务模板
支持TOML配置文件和命令行参数指定配置文件
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
# # # # # # # # import mysql.connector  # 已由pymysql替代  # 已由pymysql替代  # 已由pymysql替代  # 已由pymysql替代  # 已由pymysql替代  # 已由pymysql替代  # 已由pymysql替代  # 已由pymysql替代
# from MySQLdb import Error  # 使用pymysql的错误
import re
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 尝试导入tomli（Python 3.11+内置tomllib，低版本使用tomli）
try:
    import tomllib
except ImportError:
    import tomli as tomllib

def load_config(config_path=None):
    """
    加载配置文件，支持.env和.toml格式
    优先级：命令行参数 > 环境变量 > 默认配置文件
    """
    config = {}
    
    # 默认配置文件路径
    default_config_path = os.path.join(os.path.dirname(__file__), 'config', 'env.toml')
    
    # 确定使用的配置文件路径
    if config_path:
        config_file = config_path
    elif os.getenv('CONFIG_PATH'):
        config_file = os.getenv('CONFIG_PATH')
    else:
        config_file = default_config_path
    
    print(f"使用配置文件: {config_file}")
    
    # 根据文件扩展名选择加载方式
    if config_file.endswith('.toml'):
        # 加载TOML配置文件
        try:
            with open(config_file, 'rb') as f:  # 使用二进制模式读取
                config = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            # 如果标准TOML解析失败，尝试作为.env格式解析
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    toml_content = f.read()
                
                # 按行解析.env格式
                for line in toml_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip().strip('"\'')  # 去掉引号
            except Exception as e:
                print(f"警告: 无法加载TOML配置文件 {config_file}: {e}")
                print("将使用环境变量和默认值")
        except Exception as e:
            print(f"警告: 无法加载TOML配置文件 {config_file}: {e}")
            print("将使用环境变量和默认值")
    elif config_file.endswith('.env'):
        # 加载.env文件
        load_dotenv(config_file)
    else:
        print(f"警告: 不支持的配置文件格式: {config_file}")
        print("将使用环境变量和默认值")
    
    return config

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='跨环境任务模板管理系统')
    parser.add_argument('--config', '-c', 
                       help='配置文件路径 (支持.env或.toml格式)',
                       default=None)
    parser.add_argument('--host', 
                       help='Flask服务主机地址',
                       default=None)
    parser.add_argument('--port', '-p', 
                       help='Flask服务端口',
                       type=int,
                       default=None)
    parser.add_argument('--debug', '-d', 
                       help='启用调试模式',
                       action='store_true')
    
    return parser.parse_args()

# 解析命令行参数
args = parse_arguments()

# 加载配置
config = load_config(args.config)

# 初始化Flask应用
app = Flask(__name__)

# 从配置或环境变量获取Flask密钥
# 注意：配置文件中flask配置在[flask]部分
flask_config = config.get('flask', {})
flask_secret_key = (flask_config.get('secret_key') or 
                   os.getenv('FLASK_SECRET_KEY') or 
                   'cross_env_manager_secret_key_2026')
app.secret_key = flask_secret_key
app.config['TEMPLATES_AUTO_RELOAD'] = True

# 数据库配置 - 从配置、环境变量或默认值读取
# 注意：配置文件中数据库配置在[database]部分
db_config = config.get('database', {})
DB_CONFIG = {
    'host': (db_config.get('host') or 
            os.getenv('DB_HOST') or 
            'localhost'),
    'port': int(db_config.get('port') or 
               os.getenv('DB_PORT') or 
               3306),
    'user': (db_config.get('user') or 
            os.getenv('DB_USER') or 
            'root'),
    'password': (db_config.get('password') or 
                os.getenv('DB_PASSWORD') or 
                ''),
    'database': (db_config.get('name') or 
                os.getenv('DB_NAME') or 
                'agv_cross_env_test'),
    'charset': (db_config.get('charset') or 
               os.getenv('DB_CHARSET') or 
               'utf8mb4')
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as e:
        print(f"数据库连接错误: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """执行SQL查询"""
    conn = get_db_connection()
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

def extract_id_from_code(model_process_code):
    """从model_process_code中提取ID后缀"""
    # 匹配末尾的数字ID，如_HJBY_test_484中的484
    match = re.search(r'_(\d+)$', model_process_code)
    if match:
        return int(match.group(1))
    return None

def get_next_available_id():
    """获取下一个可用的数据库ID（基于自增主键）"""
    # 查询当前最大的id值
    query = "SELECT MAX(id) as max_id FROM fy_cross_model_process"
    result = execute_query(query)
    
    if not result or result[0]['max_id'] is None:
        return 1
    
    return result[0]['max_id'] + 1

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
            form_data.get('min_power') if form_data.get('min_power') != '' else None,
            form_data.get('back_wait_time') if form_data.get('back_wait_time') != '' else None,
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
        change_charge_template_code = %s,
        back_wait_time = %s
    WHERE id = %s
    """
    
    # 辅助函数：处理表单中的空值和0值
    def get_form_value(data, key, default=None):
        """获取表单值，处理空字符串和'0'值"""
        value = data.get(key)
        if value is None:
            return default
        str_value = str(value).strip()
        if str_value == '' or str_value == '0':
            return default if default is not None else None
        return str_value
    
    # 对于back_wait_time需要特殊处理转换为整数
    back_wait_time_str = form_data.get('back_wait_time', '').strip()
    back_wait_time = None
    if back_wait_time_str and back_wait_time_str != '':
        try:
            back_wait_time = int(back_wait_time_str)
        except (ValueError, TypeError):
            back_wait_time = None
    
    params = (
        int(form_data.get('task_seq', 0)),
        get_form_value(form_data, 'task_servicec', ''),
        get_form_value(form_data, 'template_code', ''),
        get_form_value(form_data, 'template_name', ''),
        get_form_value(form_data, 'task_path', ''),
        get_form_value(form_data, 'backflow_template_code'),  # 空字符串或'0'会变成NULL
        get_form_value(form_data, 'comeback_template_code'),  # 空字符串或'0'会变成NULL
        get_form_value(form_data, 'change_charge_template_code'),  # 空字符串或'0'会变成NULL
        back_wait_time,  # 处理后的整数值或NULL
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
        
        # 先插入记录，获取数据库生成的id
        # 临时使用一个占位符作为model_process_code
        temp_model_process_code = f"{new_base_name}_temp"
        
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
            temp_model_process_code,
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
            form_data.get('min_power') if form_data.get('min_power') != '' else None,
            form_data.get('back_wait_time') if form_data.get('back_wait_time') != '' else None,
            form_data.get('check_area_name', original_template.get('check_area_name'))
        )
        
        new_template_id = execute_query(insert_query, params, fetch=False)
        
        if new_template_id:
            # 使用实际的数据库id更新model_process_code和model_process_name
            new_model_process_code = f"{new_base_name}_{new_template_id}"
            
            # 获取原model_process_name并添加后缀
            original_name = form_data.get('model_process_name', original_template['model_process_name'])
            # 移除原名称中可能存在的数字后缀
            import re
            original_name_clean = re.sub(r'_\d+$', '', original_name)
            new_model_process_name = f"{original_name_clean}_{new_template_id}"
            
            update_code_query = """
            UPDATE fy_cross_model_process 
            SET model_process_code = %s,
                model_process_name = %s
            WHERE id = %s
            """
            execute_query(update_code_query, (new_model_process_code, new_model_process_name, new_template_id), fetch=False)
            
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
                     comeback_template_code, change_charge_template_code, back_wait_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    # 确保正确处理NULL值
                    # 这些字段在数据库中可能是NULL，需要正确传递
                    def safe_get_value(detail, key):
                        """安全获取字典值，处理NULL和空字符串情况"""
                        value = detail.get(key)
                        if value is None:
                            return None
                        
                        # 将字符串值转为字符串处理
                        str_value = str(value).strip() if value is not None else ''
                        
                        # 处理空字符串
                        if str_value == '':
                            return None
                        
                        # 特别的：back_wait_time可能需要转换为整数
                        if key == 'back_wait_time':
                            try:
                                if str_value and str_value != '':
                                    return int(str_value)
                                else:
                                    return None
                            except (ValueError, TypeError):
                                return None
                        
                        # 对于模板代码字段，如果为'0'则视为NULL
                        code_fields = ['backflow_template_code', 'comeback_template_code', 'change_charge_template_code']
                        if key in code_fields and str_value == '0':
                            return None
                        
                        return value
                    
                    detail_params = (
                        new_template_id,
                        detail['task_seq'],
                        detail['task_servicec'],
                        detail['template_code'],
                        detail['template_name'],
                        detail['task_path'],
                        safe_get_value(detail, 'backflow_template_code'),
                        safe_get_value(detail, 'comeback_template_code'),
                        safe_get_value(detail, 'change_charge_template_code'),
                        safe_get_value(detail, 'back_wait_time')
                    )
                    
                    execute_query(insert_detail_query, detail_params, fetch=False)
            
            flash(f'模板复制成功！新模板代码: {new_model_process_code}, 新模板名称: {new_model_process_name}', 'success')
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

@app.route('/api/template/<int:template_id>/details/add', methods=['POST'])
def add_detail(template_id):
    """添加新子任务"""
    try:
        data = request.get_json()
        
        # 获取当前最大的task_seq
        max_seq_query = """
        SELECT MAX(task_seq) as max_seq 
        FROM fy_cross_model_process_detail 
        WHERE model_process_id = %s
        """
        max_result = execute_query(max_seq_query, (template_id,))
        
        if max_result and max_result[0]['max_seq'] is not None:
            new_seq = max_result[0]['max_seq'] + 1
        else:
            new_seq = 1
        
        # 插入新子任务
        insert_query = """
        INSERT INTO fy_cross_model_process_detail 
        (model_process_id, task_seq, task_servicec, template_code, 
         template_name, task_path, backflow_template_code, 
         comeback_template_code, change_charge_template_code, back_wait_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # 辅助函数：处理表单中的空值和0值
        def get_form_value(data, key, default=None):
            """获取表单值，处理空字符串和'0'值"""
            value = data.get(key)
            if value is None:
                return default
            str_value = str(value).strip()
            if str_value == '' or str_value == '0':
                return default if default is not None else None
            return str_value
        
        # 对于back_wait_time需要特殊处理转换为整数
        back_wait_time_str = data.get('back_wait_time', '').strip()
        back_wait_time = None
        if back_wait_time_str and back_wait_time_str != '':
            try:
                back_wait_time = int(back_wait_time_str)
            except (ValueError, TypeError):
                back_wait_time = None
        
        params = (
            template_id,
            new_seq,
            get_form_value(data, 'task_servicec', ''),
            get_form_value(data, 'template_code', ''),
            get_form_value(data, 'template_name', ''),
            get_form_value(data, 'task_path', ''),
            get_form_value(data, 'backflow_template_code'),  # 空字符串或'0'会变成NULL
            get_form_value(data, 'comeback_template_code'),  # 空字符串或'0'会变成NULL
            get_form_value(data, 'change_charge_template_code'),  # 空字符串或'0'会变成NULL
            back_wait_time  # 处理后的整数值或NULL
        )
        
        new_detail_id = execute_query(insert_query, params, fetch=False)
        
        if new_detail_id:
            # 获取新创建的子任务详情
            detail_query = "SELECT * FROM fy_cross_model_process_detail WHERE id = %s"
            detail = execute_query(detail_query, (new_detail_id,))
            
            if detail:
                return jsonify({
                    'success': True,
                    'message': '子任务添加成功',
                    'detail': detail[0]
                })
        
        return jsonify({
            'success': False,
            'message': '子任务添加失败'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/template/<int:template_id>/details/<int:detail_id>/delete', methods=['DELETE'])
def delete_detail(template_id, detail_id):
    """删除子任务"""
    try:
        # 先验证子任务属于该模板
        verify_query = """
        SELECT id FROM fy_cross_model_process_detail 
        WHERE id = %s AND model_process_id = %s
        """
        verify_result = execute_query(verify_query, (detail_id, template_id))
        
        if not verify_result:
            return jsonify({
                'success': False,
                'message': '子任务不存在或不属于该模板'
            }), 404
        
        # 删除子任务
        delete_query = "DELETE FROM fy_cross_model_process_detail WHERE id = %s"
        result = execute_query(delete_query, (detail_id,), fetch=False)
        
        if result:
            return jsonify({
                'success': True,
                'message': '子任务删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '子任务删除失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/template/<int:template_id>/details/reorder', methods=['POST'])
def reorder_details(template_id):
    """重新排序子任务"""
    try:
        data = request.get_json()
        detail_order = data.get('order', [])  # 格式: [{"id": 1, "task_seq": 1}, ...]
        
        if not detail_order:
            return jsonify({
                'success': False,
                'message': '未提供排序数据'
            }), 400
        
        # 验证所有子任务都属于该模板
        detail_ids = [item['id'] for item in detail_order]
        placeholders = ', '.join(['%s'] * len(detail_ids))
        
        verify_query = f"""
        SELECT COUNT(*) as count FROM fy_cross_model_process_detail 
        WHERE id IN ({placeholders}) AND model_process_id = %s
        """
        verify_params = detail_ids + [template_id]
        verify_result = execute_query(verify_query, verify_params)
        
        if verify_result and verify_result[0]['count'] != len(detail_ids):
            return jsonify({
                'success': False,
                'message': '部分子任务不属于该模板'
            }), 400
        
        # 批量更新task_seq
        success_count = 0
        for item in detail_order:
            update_query = """
            UPDATE fy_cross_model_process_detail 
            SET task_seq = %s 
            WHERE id = %s AND model_process_id = %s
            """
            update_params = (item['task_seq'], item['id'], template_id)
            result = execute_query(update_query, update_params, fetch=False)
            
            if result:
                success_count += 1
        
        if success_count == len(detail_order):
            return jsonify({
                'success': True,
                'message': f'成功更新 {success_count} 个子任务的顺序'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'部分更新失败，成功更新 {success_count}/{len(detail_order)} 个'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/docs')
def show_docs():
    """显示本地README.md文档"""
    try:
        # 读取README.md文件
        readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 将Markdown转换为HTML（简单转换）
        import markdown
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        
        return render_template('docs.html', content=html_content)
    except Exception as e:
        # 如果读取失败，返回错误信息
        return f"无法读取文档: {str(e)}", 500

@app.route('/stats')
def show_stats():
    """显示统计页面"""
    return render_template('stats.html')

@app.route('/api/stats/overview')
def get_stats_overview():
    """获取系统概览统计"""
    try:
        # 模板统计
        template_stats_query = """
        SELECT 
            COUNT(*) as total_templates,
            SUM(CASE WHEN enable = 1 THEN 1 ELSE 0 END) as enabled_templates,
            SUM(CASE WHEN enable = 0 THEN 1 ELSE 0 END) as disabled_templates,
            AVG(capacity) as avg_capacity,
            MIN(capacity) as min_capacity,
            MAX(capacity) as max_capacity,
            COUNT(DISTINCT area_id) as distinct_areas,
            COUNT(DISTINCT target_points_ip) as distinct_servers
        FROM fy_cross_model_process
        """
        template_stats = execute_query(template_stats_query)
        
        # 子任务统计
        detail_stats_query = """
        SELECT 
            COUNT(*) as total_subtasks,
            COUNT(DISTINCT model_process_id) as templates_with_subtasks,
            AVG(task_seq) as avg_task_seq,
            MIN(task_seq) as min_task_seq,
            MAX(task_seq) as max_task_seq,
            COUNT(DISTINCT task_servicec) as distinct_servers,
            COUNT(DISTINCT template_code) as distinct_template_codes
        FROM fy_cross_model_process_detail
        """
        detail_stats = execute_query(detail_stats_query)
        
        # 最近创建的模板
        recent_templates_query = """
        SELECT id, model_process_code, model_process_name, enable, created_at
        FROM fy_cross_model_process
        ORDER BY id DESC
        LIMIT 5
        """
        recent_templates = execute_query(recent_templates_query)
        
        if template_stats and detail_stats:
            return jsonify({
                'success': True,
                'data': {
                    'template_stats': template_stats[0],
                    'detail_stats': detail_stats[0],
                    'recent_templates': recent_templates or []
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '无法获取统计信息'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/stats/distribution')
def get_stats_distribution():
    """获取分布统计"""
    try:
        # 启用状态分布
        enable_distribution_query = """
        SELECT 
            enable as status,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fy_cross_model_process), 2) as percentage
        FROM fy_cross_model_process
        GROUP BY enable
        ORDER BY enable DESC
        """
        enable_distribution = execute_query(enable_distribution_query)
        
        # 容量分布
        capacity_distribution_query = """
        SELECT 
            capacity,
            COUNT(*) as count
        FROM fy_cross_model_process
        WHERE capacity > 0
        GROUP BY capacity
        ORDER BY capacity
        """
        capacity_distribution = execute_query(capacity_distribution_query)
        
        # 服务器分布
        server_distribution_query = """
        SELECT 
            target_points_ip as server,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fy_cross_model_process), 2) as percentage
        FROM fy_cross_model_process
        WHERE target_points_ip IS NOT NULL AND target_points_ip != ''
        GROUP BY target_points_ip
        ORDER BY count DESC
        """
        server_distribution = execute_query(server_distribution_query)
        
        # 区域分布
        area_distribution_query = """
        SELECT 
            area_id as area,
            COUNT(*) as count
        FROM fy_cross_model_process
        WHERE area_id IS NOT NULL
        GROUP BY area_id
        ORDER BY area_id
        """
        area_distribution = execute_query(area_distribution_query)
        
        return jsonify({
            'success': True,
            'data': {
                'enable_distribution': enable_distribution or [],
                'capacity_distribution': capacity_distribution or [],
                'server_distribution': server_distribution or [],
                'area_distribution': area_distribution or []
            }
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/stats/templates_by_server')
def get_templates_by_server():
    """按服务器分组获取模板信息"""
    try:
        query = """
        SELECT 
            target_points_ip as server,
            COUNT(*) as template_count,
            GROUP_CONCAT(model_process_code ORDER BY id DESC SEPARATOR ', ') as template_codes,
            SUM(CASE WHEN enable = 1 THEN 1 ELSE 0 END) as enabled_count,
            SUM(CASE WHEN enable = 0 THEN 1 ELSE 0 END) as disabled_count
        FROM fy_cross_model_process
        WHERE target_points_ip IS NOT NULL AND target_points_ip != ''
        GROUP BY target_points_ip
        ORDER BY template_count DESC
        """
        results = execute_query(query)
        
        if results:
            return jsonify({
                'success': True,
                'data': results
            })
        else:
            return jsonify({
                'success': False,
                'message': '无法获取服务器分组信息'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/stats/template_growth')
def get_template_growth():
    """获取模板增长趋势（基于ID顺序）"""
    try:
        query = """
        SELECT 
            FLOOR((id - 1) / 10) * 10 + 1 as range_start,
            FLOOR((id - 1) / 10) * 10 + 10 as range_end,
            COUNT(*) as count,
            GROUP_CONCAT(id ORDER BY id SEPARATOR ',') as ids
        FROM fy_cross_model_process
        GROUP BY FLOOR((id - 1) / 10)
        ORDER BY range_start
        """
        results = execute_query(query)
        
        if results:
            return jsonify({
                'success': True,
                'data': results
            })
        else:
            return jsonify({
                'success': False,
                'message': '无法获取增长趋势信息'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/stats/detailed_analysis')
def get_detailed_analysis():
    """获取详细分析数据"""
    try:
        # 模板基本信息分析
        template_analysis_query = """
        SELECT 
            'total_templates' as metric,
            COUNT(*) as value
        FROM fy_cross_model_process
        UNION ALL
        SELECT 
            'enabled_templates' as metric,
            SUM(CASE WHEN enable = 1 THEN 1 ELSE 0 END) as value
        FROM fy_cross_model_process
        UNION ALL
        SELECT 
            'disabled_templates' as metric,
            SUM(CASE WHEN enable = 0 THEN 1 ELSE 0 END) as value
        FROM fy_cross_model_process
        UNION ALL
        SELECT 
            'templates_with_capacity' as metric,
            SUM(CASE WHEN capacity > 0 THEN 1 ELSE 0 END) as value
        FROM fy_cross_model_process
        UNION ALL
        SELECT 
            'templates_without_capacity' as metric,
            SUM(CASE WHEN capacity <= 0 THEN 1 ELSE 0 END) as value
        FROM fy_cross_model_process
        UNION ALL
        SELECT 
            'avg_subtasks_per_template' as metric,
            ROUND(
                (SELECT COUNT(*) FROM fy_cross_model_process_detail) * 1.0 / 
                (SELECT COUNT(*) FROM fy_cross_model_process), 
                2
            ) as value
        """
        template_analysis = execute_query(template_analysis_query)
        
        # 子任务分析
        subtask_analysis_query = """
        SELECT 
            'total_subtasks' as metric,
            COUNT(*) as value
        FROM fy_cross_model_process_detail
        UNION ALL
        SELECT 
            'templates_with_subtasks' as metric,
            COUNT(DISTINCT model_process_id) as value
        FROM fy_cross_model_process_detail
        UNION ALL
        SELECT 
            'avg_task_seq' as metric,
            ROUND(AVG(task_seq), 2) as value
        FROM fy_cross_model_process_detail
        UNION ALL
        SELECT 
            'max_task_seq' as metric,
            MAX(task_seq) as value
        FROM fy_cross_model_process_detail
        """
        subtask_analysis = execute_query(subtask_analysis_query)
        
        return jsonify({
            'success': True,
            'data': {
                'template_analysis': template_analysis or [],
                'subtask_analysis': subtask_analysis or []
            }
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    
    # 获取Flask运行参数（命令行参数优先，然后是配置，最后是环境变量）
    # 注意：配置文件使用小写字段名（如 host, port），环境变量使用大写（如 FLASK_HOST, FLASK_PORT）
    flask_config = config.get('flask', {})
    host = (args.host or 
           flask_config.get('host') or 
           os.getenv('FLASK_HOST') or 
           '0.0.0.0')
    
    port = (args.port or 
           (flask_config.get('port') and int(flask_config.get('port'))) or 
           (os.getenv('FLASK_PORT') and int(os.getenv('FLASK_PORT'))) or 
           5000)
    
    debug = (args.debug or 
            (flask_config.get('debug') and str(flask_config.get('debug')).lower() == 'true') or 
            (os.getenv('FLASK_DEBUG') and os.getenv('FLASK_DEBUG').lower() == 'true') or 
            False)
    
    print("=" * 60)
    print("跨环境任务模板管理系统")
    print("=" * 60)
    print(f"配置文件: {args.config or '默认 (config/env.toml)'}")
    print(f"数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"服务地址: http://{host}:{port}")
    print(f"调试模式: {'是' if debug else '否'}")
    print("=" * 60)
    print("启动服务中...")
    
    app.run(debug=debug, host=host, port=port)