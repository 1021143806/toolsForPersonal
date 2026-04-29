#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调车管理路由蓝图 - 空车调车模块
"""

from flask import Blueprint, render_template, jsonify, request
from datetime import datetime
import os, json, threading

dispatch_bp = Blueprint('dispatch', __name__, template_folder='../templates')

# 数据目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'dispatch')
CACHE_INDEX_PATH = os.path.join(DATA_DIR, 'cache_index.json')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

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
    """加载 JSON 文件"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
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
    """获取区域文件路径"""
    return os.path.join(DATA_DIR, f"{region_key}_{filename}")


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
        "enabled": enabled,
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
        return False, f"区域 {region_key} 不存在"
    
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
        # 避免重复记录
        if not any(t.get('deviceCode') == device_code and t.get('status') == 6 for t in tasks):
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
def dashboard():
    """调车管理主看板"""
    return render_template('dispatch/dashboard.html')


@dispatch_bp.route('/dispatch/config')
def config_page():
    """配置管理页"""
    return render_template('dispatch/config.html')


@dispatch_bp.route('/dispatch/area/<int:area_id>')
def area_detail(area_id):
    """区域详情页"""
    data = get_all_areas_status()
    area = next((a for a in data['areas'] if a['areaId'] == str(area_id)), None)
    if not area:
        return "区域不存在", 404
    return render_template('dispatch/area_detail.html', area=area)


# ========== API ==========

@dispatch_bp.route('/api/dispatch/status')
def api_status():
    """获取所有区域状态"""
    return jsonify(get_all_areas_status())


@dispatch_bp.route('/api/dispatch/report_status', methods=['POST'])
def api_report_status():
    """任务状态上报接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求体为空'}), 400
        
        success, message = handle_status_report(data)
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dispatch_bp.route('/api/dispatch/config')
def get_config():
    """获取配置"""
    return jsonify(_load_cache_index())


@dispatch_bp.route('/api/dispatch/config', methods=['POST'])
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
def get_backup(backup_name):
    """获取备份内容"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        return jsonify({'error': '备份文件不存在'}), 404
    with open(backup_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@dispatch_bp.route('/api/dispatch/config/backup/<backup_name>/restore', methods=['POST'])
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
def delete_backup(backup_name):
    """删除备份"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(backup_path):
        return jsonify({'error': '备份文件不存在'}), 404
    os.remove(backup_path)
    return jsonify({'success': True})


# ========== 区域 JSON 文件查看/编辑 API ==========

@dispatch_bp.route('/api/dispatch/region_files/<region_key>')
def api_region_files(region_key):
    """获取区域关联的文件列表"""
    index = _load_cache_index()
    region = index.get(region_key)
    if not region:
        return jsonify({'error': f'区域 {region_key} 不存在'}), 404

    files = []
    # 从 templates 中提取
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
    # 添加 currentCount.json
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
def api_region_file_get(region_key, filename):
    """获取区域文件内容，文件不存在时返回空数组"""
    fpath = _get_region_file(region_key, filename)
    if not os.path.exists(fpath):
        # 文件不存在时返回空数组作为默认内容
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
def api_region_file_save(region_key, filename):
    """保存区域文件内容，文件不存在时自动创建"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        # 验证 JSON 格式
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'JSON 格式错误: {str(e)}'}), 400

        fpath = _get_region_file(region_key, filename)
        _save_json(fpath, json.loads(content))
        return jsonify({'success': True, 'message': f'{filename} 保存成功'})
    except Exception as e:
        return jsonify({'error': f'保存失败: {str(e)}'}), 500
