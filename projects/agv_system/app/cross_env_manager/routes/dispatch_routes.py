#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调车管理路由蓝图 - 空车调车模块
"""

from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from datetime import datetime
import os, json, threading

dispatch_bp = Blueprint('dispatch', __name__, template_folder='../templates')


def login_required(f):
    """登录验证装饰器（普通用户或管理员均可）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': '需要登录', 'redirect': '/login'}), 401
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': '需要管理员权限，请在首页启用管理员提权'}), 403
            return '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"></head>
<body><script>alert('需要管理员权限，请在首页启用管理员提权');history.back();</script></body></html>''', 403
        return f(*args, **kwargs)
    return decorated_function

# 数据目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'dispatch')
CACHE_INDEX_PATH = os.path.join(DATA_DIR, 'cache_index.json')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
GLOBAL_LOG_PATH = os.path.join(DATA_DIR, 'global_log.json')

# 线程锁
_write_lock = threading.Lock()


# ========== 数据读写 ==========

def _load_cache_index():
    """加载 cache_index.json"""
    if not os.path.exists(CACHE_INDEX_PATH):
        return {}
    try:
        with open(CACHE_INDEX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Dispatch] 加载配置失败: {e}")
        return {}


def _save_cache_index(data):
    """保存 cache_index.json"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with _write_lock:
        with open(CACHE_INDEX_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _load_json(filepath):
    """加载 JSON 文件，确保返回列表"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 如果不是列表，返回空列表
        return data if isinstance(data, list) else []
    except:
        return []


def _save_json(filepath, data):
    """保存 JSON 文件（原子写入）"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with _write_lock:
        tmp = filepath + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, filepath)


def _get_region_file(region_key, filename):
    """获取区域文件路径（按区域文件夹存放）"""
    return os.path.join(DATA_DIR, region_key, filename)


# ========== 全局操作日志 ==========

def write_global_log(action, region_key, detail='', level='info'):
    """写入全局操作日志（自动清理超过2天的日志）"""
    logs = _load_json(GLOBAL_LOG_PATH)
    logs.append({
        "time": datetime.now().isoformat(),
        "action": action,
        "region_key": region_key,
        "detail": detail,
        "level": level
    })
    # 自动清理超过2天的日志
    from datetime import timedelta
    two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
    logs = [log for log in logs if log.get('time', '') >= two_days_ago]
    _save_json(GLOBAL_LOG_PATH, logs)


@dispatch_bp.route('/api/dispatch/global_log')
@login_required
def api_global_log():
    """获取全局操作日志"""
    logs = _load_json(GLOBAL_LOG_PATH)
    logs.sort(key=lambda x: x.get('time', ''), reverse=True)
    return jsonify({'logs': logs})


# ========== 核心计算逻辑 ==========

def calculate_area_balance(region_key, region_config):
    """
    计算区域设备平衡
    
    公式:
      a = 所有来区域模板中 status=6 的任务数之和
      b = 所有离开模板中 status=6 的任务数之和
      currentCount = now.json 中的设备数
      expectedCount = currentCount + a - b
      
      if expectedCount > xmax: need = expectedCount - xmax (正数, 车过多, 下发回空车)
      if expectedCount < xmin: need = expectedCount - xmin (负数, 车不够, 下发调空车)
      else: need = 0 (平衡)
    """
    xmin = region_config.get('xmin', 2)
    xmax = region_config.get('xmax', 4)
    max_once = region_config.get('max_dispatch_once', 3)
    enabled = region_config.get('enabled', False)
    
    # 分时段配置解析（始终解析，不受手动开关影响，用于展示）
    time_slot_active = False
    time_slot_matched = None
    time_slots_config = region_config.get('time_slots', {})
    if time_slots_config.get('enabled', False):
        now_time = datetime.now().strftime('%H:%M')
        matched_slots = []
        for slot in time_slots_config.get('slots', []):
            start = slot.get('start', '00:00')
            end = slot.get('end', '00:00')
            # 处理跨天时段（如 20:00 ~ 08:00）
            if start <= end:
                matched = start <= now_time <= end
            else:
                matched = now_time >= start or now_time <= end
            if matched:
                # 计算时段长度（分钟），用于选择最精确的时段
                if start <= end:
                    duration = (int(end[:2])*60 + int(end[3:])) - (int(start[:2])*60 + int(start[3:]))
                else:
                    duration = (24*60 - (int(start[:2])*60 + int(start[3:]))) + (int(end[:2])*60 + int(end[3:]))
                matched_slots.append((duration, slot))
        
        if matched_slots:
            # 选择时间范围最小的时段（最精确匹配）
            matched_slots.sort(key=lambda x: x[0])
            best_slot = matched_slots[0][1]
            xmin = best_slot.get('xmin', xmin)
            xmax = best_slot.get('xmax', xmax)
            time_slot_active = True
            time_slot_matched = best_slot
    
    # 分时配置中 xmin=-1, xmax=-1 表示禁用真实任务（仅在手动启用时生效）
    effective_enabled = enabled
    if enabled and time_slot_active and xmin == -1 and xmax == -1:
        effective_enabled = False  # 走模拟逻辑
    
    # 统计 a: 来区域模板中 status=6 的任务数
    a = 0
    incoming_templates = []
    outgoing_templates = []
    
    for t in region_config.get('templates', []):
        fpath = _get_region_file(region_key, t['file'])
        tasks = _load_json(fpath)
        count = len([task for task in tasks if task.get('status') == 6])
        
        item = {"code": t['name'], "name": t['name'], "count": count}
        if t['direction'] == 'in':
            a += count
            incoming_templates.append(item)
        else:
            outgoing_templates.append(item)
    
    # 统计 b: 离开模板中 status=6 的任务数
    b = sum(t['count'] for t in outgoing_templates)
    
    # currentCount: currentCount.json 中的设备数
    now_file = _get_region_file(region_key, 'currentCount.json')
    now_devices = _load_json(now_file)
    currentCount = len(now_devices)
    
    # expectedCount = currentCount + a - b
    expectedCount = currentCount + a - b
    
    # 计算 need
    if expectedCount > xmax:
        need = expectedCount - xmax  # 正数：车过多，下发回空车
        direction = "out"
        direction_text = f"车过多，需调出{need}辆"
        direction_icon = "bi-arrow-up"
        direction_color = "danger"
    elif expectedCount < xmin:
        need = expectedCount - xmin  # 负数：车不够，下发调空车
        direction = "in"
        direction_text = f"车不够，需调入{abs(need)}辆"
        direction_icon = "bi-arrow-down"
        direction_color = "warning"
    else:
        need = 0
        direction = "none"
        direction_text = "平衡"
        direction_icon = "bi-check-circle"
        direction_color = "success"
    
    # 容量管控：限制每次下发数量
    dispatch_count = min(abs(need), max_once) if need != 0 else 0
    
    # 互斥检查：检查是否有未完成的同方向或反方向空车任务
    can_dispatch = True
    mutex_reason = ""
    if enabled and need != 0:
        # 检查所有模板中是否有未完成的空车任务
        for t in region_config.get('templates', []):
            fpath = _get_region_file(region_key, t['file'])
            tasks = _load_json(fpath)
            pending = [task for task in tasks if task.get('status') == 6]
            if pending:
                # 如果要下发去空车(in)，但存在未完成的回空车(out)任务
                # 如果要下发回空车(out)，但存在未完成的去空车(in)任务
                if t['direction'] != direction:
                    can_dispatch = False
                    mutex_reason = f"存在未完成的{t['name']}任务，互斥"
                    break
    
    return {
        "region_key": region_key,
        "areaId": region_config.get('areaId', '0'),
        "name": region_key,
        "server": region_config.get('server', ''),
        "enabled": enabled,  # 手动开关状态（前端显示用）
        "effective_enabled": effective_enabled,  # 实际生效状态（计算用）
        "xmin": xmin,
        "xmax": xmax,
        "max_dispatch_once": max_once,
        "currentCount": currentCount,
        "a": a,
        "b": b,
        "expectedCount": expectedCount,
        "need": need,
        "dispatch_count": dispatch_count if need != 0 else 0,
        "direction": direction,
        "direction_text": direction_text,
        "direction_icon": direction_icon,
        "direction_color": direction_color,
        "can_dispatch": can_dispatch,
        "mutex_reason": mutex_reason,
        "time_slot_active": time_slot_active,
        "time_slot_matched": time_slot_matched,
        "templates": {
            "incoming": incoming_templates,
            "outgoing": outgoing_templates
        }
    }


def get_all_areas_status():
    """获取所有区域状态"""
    index = _load_cache_index()
    areas = []
    total_devices = 0
    need_dispatch = 0
    balanced = 0
    
    for region_key, region in index.items():
        balance = calculate_area_balance(region_key, region)
        areas.append(balance)
        total_devices += balance['currentCount']
        if balance['direction'] != 'none':
            need_dispatch += 1
        else:
            balanced += 1
    
    return {
        "summary": {
            "total_areas": len(areas),
            "total_devices": total_devices,
            "need_dispatch": need_dispatch,
            "balanced": balanced
        },
        "areas": areas
    }


# ========== 状态上报处理 ==========

def handle_status_report(data):
    """
    处理任务状态上报（兼容两种报文格式）
    
    格式1（内部格式）:
      - region_key: 区域标识 (如 region_1)
      - template_name: 模板代码 (如 DKCqu)
      - deviceNum: 设备编号 (如 C185)
      - deviceCode: 设备序列号 (如 BL11637BAK00010)
      - status: 任务状态 (6=开始, 8=完成)
      - order_id: 任务单号 (可选)
    
    格式2（外部上报格式）:
      - deviceCode: 设备序列号
      - deviceNum: 设备编号 (如 DJC5)
      - modelProcessCode: 任务模板 (如 JuSheng_HJQ2_4-23)
      - subTaskStatus: 子任务状态 (字符串 "3"=执行中, "8"=完成)
      - status: 任务状态 (数字 8=完成)
      - orderId: 任务单号
      - shelfNumber: 货架编号 (可选)
      - shelfCurrPosition: 货架当前点位 (可选)
    
    处理逻辑:
      status=6/subTaskStatus="3": 记录到模板 JSON
      status=8/subTaskStatus="8": 
        来区域模板 → 从模板 JSON 删除, 写入 currentCount.json
        离开模板 → 从模板 JSON 删除, 从 currentCount.json 删除
    """
    # === 兼容两种报文格式 ===
    
    # 1. 解析 status：直接使用报文中的 status 字段
    # 报文示例: "status": 8 (完成)
    # 内部定义: 6=开始, 8=完成
    raw_status = data.get('status', 0)
    try:
        status = int(raw_status)
    except (ValueError, TypeError):
        status = 0
    
    # 3. 解析设备信息
    device_code = data.get('deviceCode', '')
    device_num = data.get('deviceNum', '')
    
    # 4. 解析 order_id
    # 兼容 orderId 和 order_id
    order_id = data.get('orderId') or data.get('order_id', '')
    
    # 5. 解析 template_name
    # 兼容 modelProcessCode 和 template_name
    template_name = data.get('modelProcessCode') or data.get('template_name', '')
    
    # 6. 解析 region_key
    # 优先使用传入的 region_key，否则通过 modelProcessCode 自动匹配
    region_key = data.get('region_key', '')
    if not region_key and template_name:
        # 遍历所有区域，查找包含该模板的区域
        index = _load_cache_index()
        for rk, region in index.items():
            for t in region.get('templates', []):
                if t['name'] == template_name or t['file'].replace('.json', '') == template_name:
                    region_key = rk
                    break
            if region_key:
                break
    
    if not region_key or not template_name:
        return False, "缺少 region_key 或 template_name，且无法通过 modelProcessCode 自动匹配区域"
    
    # 查找模板配置
    index = _load_cache_index()
    region = index.get(region_key)
    if not region:
        # 区域不存在，从配置中删除并清理文件夹
        if region_key in index:
            del index[region_key]
            _save_cache_index(index)
        # 清理区域文件夹
        import shutil
        region_dir = os.path.join(DATA_DIR, region_key)
        if os.path.exists(region_dir):
            shutil.rmtree(region_dir, ignore_errors=True)
        return False, f"区域 {region_key} 不存在，已自动清理"
    
    template_config = None
    for t in region.get('templates', []):
        if t['name'] == template_name:
            template_config = t
            break
    
    if not template_config:
        # 尝试通过文件名匹配
        for t in region.get('templates', []):
            if t['file'].replace('.json', '') == template_name:
                template_config = t
                break
    
    if not template_config:
        return False, f"模板 {template_name} 不存在于区域 {region_key}"
    
    direction = template_config['direction']
    template_file = _get_region_file(region_key, template_config['file'])
    now_file = _get_region_file(region_key, 'currentCount.json')
    
    now = datetime.now().isoformat()
    
    if status == 6:
        # 任务开始（运行中）：记录到模板 JSON
        tasks = _load_json(template_file)
        # 查找是否已有该设备的记录，有则覆盖，无则新增
        existing = None
        for t in tasks:
            if t.get('deviceCode') == device_code and t.get('status') == 6:
                existing = t
                break
        
        if existing:
            # 覆盖更新
            existing['deviceNum'] = device_num
            existing['order_id'] = order_id
            existing['shelfNumber'] = data.get('shelfNumber', '')
            existing['shelfCurrPosition'] = data.get('shelfCurrPosition', '')
            existing['update_time'] = now
        else:
            # 新增
            tasks.append({
                "deviceCode": device_code,
                "deviceNum": device_num,
                "status": 6,
                "order_id": order_id,
                "shelfNumber": data.get('shelfNumber', ''),
                "shelfCurrPosition": data.get('shelfCurrPosition', ''),
                "create_time": now,
                "update_time": now
            })
        _save_json(template_file, tasks)
        
    else:
        # 非 6 的状态（包括 8=完成 及其他状态）：执行清理逻辑
        # 从模板 JSON 中删除该设备记录
        tasks = _load_json(template_file)
        tasks = [t for t in tasks if not (t.get('deviceCode') == device_code and t.get('status') == 6)]
        _save_json(template_file, tasks)
        
        # 更新 currentCount.json
        now_devices = _load_json(now_file)
        if direction == 'in':
            # 来区域完成：写入 currentCount.json
            if not any(d.get('deviceCode') == device_code for d in now_devices):
                now_devices.append({
                    "deviceCode": device_code,
                    "deviceNum": device_num,
                    "order_id": order_id,
                    "shelfNumber": data.get('shelfNumber', ''),
                    "create_time": now
                })
        elif direction == 'out':
            # 离开完成：从 currentCount.json 删除
            now_devices = [d for d in now_devices if d.get('deviceCode') != device_code]
        
        _save_json(now_file, now_devices)
    
    return True, "状态上报成功"


# ========== 路由 ==========

@dispatch_bp.route('/dispatch')
@login_required
def dashboard():
    """调车管理主看板"""
    return render_template('dispatch/dashboard.html')


@dispatch_bp.route('/dispatch/config')
@login_required
@admin_required
def config_page():
    """配置管理页"""
    return render_template('dispatch/config.html')


@dispatch_bp.route('/dispatch/area/<int:area_id>')
@login_required
def area_detail(area_id):
    """区域详情页"""
    data = get_all_areas_status()
    area = next((a for a in data['areas'] if a['areaId'] == str(area_id)), None)
    if not area:
        return "区域不存在", 404
    return render_template('dispatch/area_detail.html', area=area)


# ========== API ==========

@dispatch_bp.route('/api/dispatch/status')
@login_required
def api_status():
    """获取所有区域状态"""
    return jsonify(get_all_areas_status())


@dispatch_bp.route('/api/dispatch/report_status', methods=['POST'])
def api_report_status():
    """任务状态上报接口（外部设备上报，无需登录）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求体为空'}), 400
        
        success, message = handle_status_report(data)
        # 记录日志（不阻塞主流程）
        try:
            rk = data.get('region_key') or 'auto'
            tn = data.get('modelProcessCode') or data.get('template_name', '?')
            dn = data.get('deviceNum', '?')
            st = data.get('status', '?')
            write_global_log('report_status', rk, f'{tn} {dn} status={st}: {message}',
                           'info' if success else 'warning')
        except:
            pass
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dispatch_bp.route('/api/dispatch/config')
@login_required
def get_config():
    """获取配置"""
    return jsonify(_load_cache_index())


@dispatch_bp.route('/api/dispatch/config', methods=['POST'])
@login_required
@admin_required
def save_config():
    """保存配置"""
    try:
        data = request.get_json()
        _save_cache_index(data)
        return jsonify({'success': True, 'message': '配置保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== 备份 API ==========

@dispatch_bp.route('/api/dispatch/config/backups')
@login_required
def list_backups():
    """列出备份"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backups = []
    for filename in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if filename.endswith('.json'):
            filepath = os.path.join(BACKUP_DIR, filename)
            stat = os.stat(filepath)
            message = ''
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first = f.readline()
                    if first.startswith('// commit:'):
                        message = first[10:].strip()
            except:
                pass
            backups.append({
                'name': filename,
                'message': message,
                'timestamp': stat.st_mtime * 1000,
                'size': stat.st_size
            })
    return jsonify(backups)


@dispatch_bp.route('/api/dispatch/config/backup', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """创建备份"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        message = request.json.get('message', '').strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"dispatch_config_{timestamp}.json"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        config = _load_cache_index()
        commit_line = f"// commit: {message}\n" if message else "// commit: (no message)\n"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(commit_line)
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'backup_name': backup_name})
    except Exception as e:
        return jsonify({'error': f'创建备份失败: {str(e)}'}), 500


@dispatch_bp.route('/api/dispatch/config/backup/<backup_name>')
@login_required
def get_backup(backup_name):
    """获取备份内容"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        return jsonify({'error': '备份文件不存在'}), 404
    with open(backup_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@dispatch_bp.route('/api/dispatch/config/backup/<backup_name>/restore', methods=['POST'])
@login_required
@admin_required
def restore_backup(backup_name):
    """恢复备份"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        return jsonify({'error': '备份文件不存在'}), 404
    with open(backup_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    content = ''.join(line for line in lines if not line.startswith('// '))
    try:
        data = json.loads(content)
        _save_cache_index(data)
        return jsonify({'success': True})
    except json.JSONDecodeError as e:
        return jsonify({'error': f'备份文件格式错误: {str(e)}'}), 500


@dispatch_bp.route('/api/dispatch/config/backup/<backup_name>', methods=['DELETE'])
@login_required
@admin_required
def delete_backup(backup_name):
    """删除备份"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        return jsonify({'error': '备份文件不存在'}), 404
    os.remove(backup_path)
    return jsonify({'success': True})


# ========== 区域 JSON 文件查看/编辑 API ==========

@dispatch_bp.route('/api/dispatch/region_files/<region_key>')
@login_required
def api_region_files(region_key):
    """获取区域关联的文件列表"""
    index = _load_cache_index()
    region = index.get(region_key)
    if not region:
        return jsonify({'error': f'区域 {region_key} 不存在'}), 404

    files = []
    for t in region.get('templates', []):
        fpath = _get_region_file(region_key, t['file'])
        exists = os.path.exists(fpath)
        files.append({
            'filename': t['file'],
            'name': t['name'],
            'direction': t['direction'],
            'exists': exists,
            'size': os.path.getsize(fpath) if exists else 0
        })
    now_path = _get_region_file(region_key, 'currentCount.json')
    now_exists = os.path.exists(now_path)
    files.append({
        'filename': 'currentCount.json',
        'name': '当前设备',
        'direction': 'system',
        'exists': now_exists,
        'size': os.path.getsize(now_path) if now_exists else 0
    })

    return jsonify({'region_key': region_key, 'files': files})


@dispatch_bp.route('/api/dispatch/region_file/<region_key>/<filename>')
@login_required
def api_region_file_get(region_key, filename):
    """获取区域文件内容"""
    fpath = _get_region_file(region_key, filename)
    if not os.path.exists(fpath):
        return jsonify({
            'region_key': region_key,
            'filename': filename,
            'content': '[]',
            'size': 0,
            'exists': False
        })
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            'region_key': region_key,
            'filename': filename,
            'content': content,
            'size': os.path.getsize(fpath),
            'exists': True
        })
    except Exception as e:
        return jsonify({'error': f'读取文件失败: {str(e)}'}), 500


@dispatch_bp.route('/api/dispatch/region_file/<region_key>/<filename>', methods=['POST'])
@login_required
@admin_required
def api_region_file_save(region_key, filename):
    """保存区域文件内容"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'JSON 格式错误: {str(e)}'}), 400

        fpath = _get_region_file(region_key, filename)
        _save_json(fpath, json.loads(content))
        return jsonify({'success': True, 'message': f'{filename} 保存成功'})
    except Exception as e:
        return jsonify({'error': f'保存失败: {str(e)}'}), 500


# ========== 下发记录 API ==========

def write_dispatch_log(region_key, template_name, direction, dispatch_url, request_body, simulated, device_code='', device_num='', result='success', response_body=None, reason='manual'):
    """写入下发记录到 dispatch_log.json"""
    log_file = _get_region_file(region_key, 'dispatch_log.json')
    logs = _load_json(log_file)
    logs.append({
        "time": datetime.now().isoformat(),
        "template_name": template_name,
        "direction": direction,
        "dispatch_url": dispatch_url,
        "request_body": request_body,
        "response_body": response_body,
        "simulated": simulated,
        "deviceCode": device_code,
        "deviceNum": device_num,
        "result": result,
        "reason": reason
    })
    _save_json(log_file, logs)
    return True


@dispatch_bp.route('/api/dispatch/dispatch_log/<region_key>')
@login_required
def api_dispatch_log(region_key):
    """获取下发记录"""
    log_file = _get_region_file(region_key, 'dispatch_log.json')
    logs = _load_json(log_file)
    logs.sort(key=lambda x: x.get('time', ''), reverse=True)
    return jsonify({'region_key': region_key, 'logs': logs})


@dispatch_bp.route('/api/dispatch/dispatch_log/<region_key>', methods=['POST'])
@login_required
@admin_required
def api_dispatch_log_write(region_key):
    """写入下发记录"""
    try:
        data = request.get_json()
        write_dispatch_log(
            region_key=region_key,
            template_name=data.get('template_name', ''),
            direction=data.get('direction', ''),
            dispatch_url=data.get('dispatch_url', ''),
            request_body=data.get('request_body', {}),
            simulated=data.get('simulated', False),
            device_code=data.get('deviceCode', ''),
            device_num=data.get('deviceNum', ''),
            result=data.get('result', 'success')
        )
        return jsonify({'success': True, 'message': '下发记录已保存'})
    except Exception as e:
        return jsonify({'error': f'写入失败: {str(e)}'}), 500


# ========== 执行计算 API ==========

@dispatch_bp.route('/api/dispatch/execute/<region_key>', methods=['POST'])
@login_required
def api_execute(region_key):
    """执行单区域全流程：检查→计算→下发"""
    try:
        index = _load_cache_index()
        region = index.get(region_key)
        if not region:
            return jsonify({'error': f'区域 {region_key} 不存在'}), 404
        
        enabled = region.get('enabled', False)
        server = region.get('server', '')
        max_once = region.get('max_dispatch_once', 3)
        
        # 1. 计算平衡
        balance = calculate_area_balance(region_key, region)
        
        if balance['direction'] == 'none':
            write_global_log('execute_balanced', region_key, '区域平衡，无需下发')
            return jsonify({
                'success': True,
                'message': '区域平衡，无需下发',
                'balance': balance,
                'dispatched': False
            })
        
        # 2. 互斥检查
        if not balance['can_dispatch']:
            write_global_log('execute_mutex', region_key, balance['mutex_reason'], 'warning')
            return jsonify({
                'success': False,
                'error': balance['mutex_reason'],
                'balance': balance
            }), 409
        
        # 3. 确定下发模板和方向
        dispatch_count = balance['dispatch_count']
        direction = balance['direction']
        
        # 选择对应方向的模板
        target_template = None
        for t in region.get('templates', []):
            if t['direction'] == direction:
                target_template = t
                break
        
        if not target_template:
            return jsonify({'error': f'未找到方向 {direction} 的模板'}), 400
        
        # 4. 构建下发请求体（与任务下发界面格式一致）
        import random as _random
        sim_id = datetime.now().strftime('%Y%m%d%H%M%S')
        simulated = not balance.get('effective_enabled', enabled)
        
        # 生成 orderId: CEM_auto_YYYY-MM-DD HH:MM:SS.ms__随机数
        now_dt = datetime.now()
        date_str = now_dt.strftime('%Y-%m-%d %H:%M:%S')
        ms = now_dt.microsecond // 1000
        rand = _random.randint(0, 9999)
        order_id = f"CEM_auto_{date_str}.{ms:03d}__{rand:04d}"
        
        dispatch_url = f"http://{server}/ics/taskOrder/addTask" if server else ''
        request_body = [{
            "modelProcessCode": target_template['name'],
            "priority": 6,
            "orderId": order_id,
            "fromSystem": "CEM_auto",
            "taskOrderDetail": {
                "taskPath": "",
                "shelfNumber": ""
            }
        }]
        
        # 5. 非模拟时实际发送 HTTP 请求
        result = 'simulated'
        response_body = None
        if not simulated and dispatch_url:
            try:
                import urllib.request as _urllib
                req = _urllib.Request(dispatch_url, 
                    data=json.dumps(request_body).encode('utf-8'),
                    headers={'Content-Type': 'application/json'})
                resp = _urllib.urlopen(req, timeout=10)
                resp_raw = resp.read().decode('utf-8')
                response_body = json.loads(resp_raw)
                result = 'success' if response_body.get('code') == 1000 else f'code={response_body.get("code")}'
            except Exception as e:
                result = f'请求失败: {str(e)}'
                response_body = {"error": str(e)}
        
        # 6. 写入模板 JSON（模拟数据也写入）
        template_file = _get_region_file(region_key, target_template['file'])
        tasks = _load_json(template_file)
        now = datetime.now().isoformat()
        
        for i in range(dispatch_count):
            device_code = f"SIM_{sim_id}_{i}" if simulated else f"DISP_{sim_id}_{i}"
            device_num = f"SIM_D{i}" if simulated else f"DISP_D{i}"
            tasks.append({
                "deviceCode": device_code,
                "deviceNum": device_num,
                "status": 6,
                "_simulated": simulated,
                "order_id": order_id,
                "create_time": now,
                "update_time": now
            })
        _save_json(template_file, tasks)
        
        # 7. 写入下发记录（区分原因）
        log_url = dispatch_url if not simulated else f'(模拟-未实际请求)\n真实地址: {dispatch_url}'
        # 判断 reason
        if not region.get('enabled', False):
            reason = 'manual_disabled'  # 手动禁用
        elif balance.get('time_slot_active') and balance['time_slot_matched'] and \
             balance['time_slot_matched'].get('xmin') == -1 and balance['time_slot_matched'].get('xmax') == -1:
            reason = 'time_slot_disabled'  # 分时禁用
        elif balance.get('time_slot_active'):
            reason = 'time_slot'  # 分时控制
        else:
            reason = 'manual'  # 手动触发
        
        write_dispatch_log(
            region_key=region_key,
            template_name=target_template['name'],
            direction=direction,
            dispatch_url=log_url,
            request_body=request_body,
            simulated=simulated,
            device_code=f"SIM_{sim_id}" if simulated else f"DISP_{sim_id}",
            device_num=f"共{dispatch_count}台",
            result=result,
            response_body=response_body,
            reason=reason
        )
        
        write_global_log('execute', region_key,
            f'{"模拟" if simulated else "真实"}下发 {dispatch_count} 台, 模板:{target_template["name"]}, 方向:{direction}, 原因:{reason}')
        
        return jsonify({
            'success': True,
            'message': f'{"模拟" if simulated else "真实"}下发 {dispatch_count} 台设备',
            'balance': balance,
            'dispatched': True,
            'simulated': simulated,
            'dispatch_count': dispatch_count,
            'template_name': target_template['name'],
            'direction': direction
        })
        
    except Exception as e:
        return jsonify({'error': f'执行失败: {str(e)}'}), 500


# ========== 清理模拟数据 API ==========

@dispatch_bp.route('/api/dispatch/clean_simulated/<region_key>', methods=['POST'])
@login_required
def api_clean_simulated(region_key):
    """清理指定区域所有模板 JSON 中的模拟数据"""
    try:
        index = _load_cache_index()
        region = index.get(region_key)
        if not region:
            return jsonify({'error': f'区域 {region_key} 不存在'}), 404
        
        cleaned_count = 0
        
        # 清理所有模板 JSON 文件
        for t in region.get('templates', []):
            fpath = _get_region_file(region_key, t['file'])
            tasks = _load_json(fpath)
            old_len = len(tasks)
            tasks = [task for task in tasks if not task.get('_simulated')]
            new_len = len(tasks)
            if old_len != new_len:
                _save_json(fpath, tasks)
                cleaned_count += (old_len - new_len)
        
        # 清理 currentCount.json
        now_file = _get_region_file(region_key, 'currentCount.json')
        now_devices = _load_json(now_file)
        old_len = len(now_devices)
        now_devices = [d for d in now_devices if not d.get('_simulated')]
        if old_len != len(now_devices):
            _save_json(now_file, now_devices)
            cleaned_count += (old_len - len(now_devices))
        
        write_global_log('clean_simulated', region_key, f'清理了 {cleaned_count} 条模拟数据')
        
        return jsonify({
            'success': True,
            'message': f'已清理 {cleaned_count} 条模拟数据',
            'cleaned_count': cleaned_count
        })
        
    except Exception as e:
        write_global_log('clean_simulated_error', region_key, str(e), 'error')
        return jsonify({'error': f'清理失败: {str(e)}'}), 500
