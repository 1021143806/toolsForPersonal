#!/usr/bin/env python3
"""调车模块自动驾驶测试 - 模拟真实AGV场景：负载任务有执行时长，空车由系统自动下发"""
import urllib.request, json, time, random, sys, argparse, threading
from datetime import datetime
from http.cookiejar import CookieJar

BASE = "http://127.0.0.1:5000"
DEV_POOL = [f"DJC{i}" for i in range(1, 61)]

# 空车模板（测试脚本不手动上报，由系统自动下发）
EMPTY_TPL = {"DKCqu", "DKCback"}

cookie_jar = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

def req(m, u, d=None, auth=True):
    try:
        b = json.dumps(d).encode() if d else None
        from urllib.parse import quote
        u = quote(u, safe='/:?=&')
        r = urllib.request.Request(u, data=b, method=m)
        if d: r.add_header('Content-Type','application/json')
        if auth:
            with opener.open(r, timeout=5) as x:
                return json.loads(x.read().decode())
        else:
            with urllib.request.urlopen(r, timeout=5) as x:
                return json.loads(x.read().decode())
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode())
        except: return {"success":False,"error":f"HTTP {e.code}"}
    except Exception as e:
        return {"success":False,"error":str(e)}

def login():
    r = req("POST", f"{BASE}/api/login", {
        "username":"375563","password":"DHRTA@2018",
        "admin_username":"admin","admin_password":"admin123456"
    }, auth=True)
    if r.get('success'):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 登录成功")
        return True
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 登录失败: {r.get('error','')}")
    return False

def report(tpl, dev, st, rk, device_code=None):
    """按实际报文格式上报"""
    if device_code is None:
        device_code = f"EM{random.randint(10000,99999)}DAK{random.randint(1000,9999)}"
    data = {
        "shelfCurrPosition": str(random.randint(10000000, 99999999)),
        "subTaskStatus": "3",
        "orderId": f"pad_html{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{random.randint(100,999)}_{random.randint(1000,9999)}",
        "deviceCode": device_code,
        "modelProcessCode": tpl,
        "subTaskTypeId": "75",
        "subTaskId": str(random.randint(10000000, 99999999)),
        "deviceNum": dev,
        "qrContent": str(random.randint(10000000, 99999999)),
        "subTaskSeq": "3",
        "shelfNumber": f"DJ{random.randint(1,9999):04d}",
        "icsTaskOrderDetailId": str(random.randint(100000000, 999999999)),
        "processRate": "1/1",
        "status": st
    }
    return req("POST", f"{BASE}/api/dispatch/report_status", data, auth=False)

def status(): return req("GET", f"{BASE}/api/dispatch/status")
def execute(rk): return req("POST", f"{BASE}/api/dispatch/execute/{rk}")
def clean(rk): return req("POST", f"{BASE}/api/dispatch/clean_simulated/{rk}")
def glog(): return req("GET", f"{BASE}/api/dispatch/global_log")
def cfg(): return req("GET", f"{BASE}/api/dispatch/config")
def save_cfg(d): return req("POST", f"{BASE}/api/dispatch/config", d)
def region_files(rk): return req("GET", f"{BASE}/api/dispatch/region_files/{rk}")
def region_file(rk, fn): return req("GET", f"{BASE}/api/dispatch/region_file/{rk}/{fn}")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_regions():
    """从配置文件加载区域"""
    c = cfg()
    regions = {}
    for rk, region in c.items():
        if not isinstance(region, dict) or 'templates' not in region:
            continue
        in_tpls, out_tpls = [], []
        for t in region.get('templates', []):
            name = t.get('name', '')
            d = t.get('direction', '')
            if d == 'in': in_tpls.append(name)
            elif d == 'out': out_tpls.append(name)
        if in_tpls or out_tpls:
            regions[rk] = {'in_tpls': in_tpls, 'out_tpls': out_tpls}
    return regions

def get_all_backend_tasks(regions, tpl_filter=None):
    """从后端获取所有 status=6 的任务，可选按模板过滤"""
    tasks = []
    try:
        st = status()
        for a in st.get('areas', []):
            rk = a['region_key']
            if rk not in regions: continue
            for t in a.get('templates', {}).get('incoming', []):
                if t.get('count', 0) > 0:
                    if tpl_filter and t['code'] not in tpl_filter: continue
                    files_resp = region_files(rk)
                    if files_resp.get('files'):
                        for f in files_resp['files']:
                            if f['filename'].replace('.json', '') == t['code'] and f.get('exists'):
                                cr = region_file(rk, f['filename'])
                                if cr.get('content'):
                                    try:
                                        for task in json.loads(cr['content']):
                                            if task.get('status') == 6:
                                                tasks.append((rk, t['code'], task.get('deviceCode',''), task.get('deviceNum',''), task.get('create_time','')))
                                    except: pass
            for t in a.get('templates', {}).get('outgoing', []):
                if t.get('count', 0) > 0:
                    if tpl_filter and t['code'] not in tpl_filter: continue
                    files_resp = region_files(rk)
                    if files_resp.get('files'):
                        for f in files_resp['files']:
                            if f['filename'].replace('.json', '') == t['code'] and f.get('exists'):
                                cr = region_file(rk, f['filename'])
                                if cr.get('content'):
                                    try:
                                        for task in json.loads(cr['content']):
                                            if task.get('status') == 6:
                                                tasks.append((rk, t['code'], task.get('deviceCode',''), task.get('deviceNum',''), task.get('create_time','')))
                                    except: pass
    except: pass
    return tasks

def print_summary(regions):
    try:
        for a in status().get('areas', []):
            if a['region_key'] in regions:
                log(f"  [{a['region_key']}] cur:{a['currentCount']} a:{a['a']} b:{a['b']} need:{a['need']} dir:{a['direction']}")
    except: pass

def main():
    parser = argparse.ArgumentParser(description='调车模块自动驾驶测试')
    parser.add_argument('--duration', type=int, default=0, help='运行时长(秒)，0=无限')
    parser.add_argument('--load-interval', type=float, default=0.5, help='负载任务上报间隔(秒)')
    parser.add_argument('--load-done', type=float, default=0.6, help='负载任务完成间隔(秒)')
    parser.add_argument('--empty-done', type=float, default=0.4, help='空车任务完成间隔(秒)')
    args = parser.parse_args()
    
    print("="*60)
    print(f"  调车模块自动驾驶测试（真实场景模拟）")
    print(f"  负载上报:{args.load_interval}s  负载完成:{args.load_done}s  空车完成:{args.empty_done}s")
    print(f"  时长:{'无限' if args.duration==0 else str(args.duration)+'s'}")
    print(f"  开始:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    if not login(): sys.exit(1)
    
    REGIONS = load_regions()
    if not REGIONS:
        log("错误: 未从配置中找到有效区域")
        sys.exit(1)
    
    log(f"加载 {len(REGIONS)} 个区域: {list(REGIONS.keys())}")
    for rk, r in REGIONS.items():
        log(f"  {rk}: 来{len(r['in_tpls'])}个 {r['in_tpls']}, 离{len(r['out_tpls'])}个 {r['out_tpls']}")
    
    # 禁用所有区域（模拟下发模式）
    log("初始化: 禁用所有区域（模拟下发）")
    c = cfg()
    for rk in REGIONS:
        if rk in c: c[rk]['enabled'] = False
    save_cfg(c)
    
    # 清理旧数据
    log("初始化: 清理旧数据")
    for rk in REGIONS: clean(rk)
    
    log("开始自动驾驶循环")
    round_num, total_ops = 0, {'load_in':0, 'load_out':0, 'done_load':0, 'done_empty':0, 'exec':0}
    start_time = time.time()
    
    # 设备 deviceCode 映射：deviceNum -> deviceCode
    # 确保同一设备的来/离使用相同 deviceCode
    dev_code_map = {}
    
    # 线程1：完成负载任务（每 load_done 秒）
    def done_load_loop():
        while True:
            time.sleep(args.load_done)
            try:
                tasks = get_all_backend_tasks(REGIONS, tpl_filter=None)
                # 排除空车模板
                load_tasks = [t for t in tasks if t[1] not in EMPTY_TPL]
                if load_tasks:
                    load_tasks.sort(key=lambda x: x[4] if x[4] else '')
                    rk2, tpl, dev_code, dev_num, _ = load_tasks[0]
                    r = report(tpl, dev_num or dev_code, 8, rk2, device_code=dev_code)
                    if r.get('success'):
                        log(f"  [{rk2}] 完成负载 {tpl} {dev_num or dev_code}")
            except: pass
    
    # 线程2：完成空车任务（每 empty_done 秒）
    # DKCqu(来空车)用后端记录完成，DKCback(回空车)从currentCount中选设备完成
    def done_empty_loop():
        while True:
            time.sleep(args.empty_done)
            try:
                tasks = get_all_backend_tasks(REGIONS, tpl_filter=EMPTY_TPL)
                if tasks:
                    tasks.sort(key=lambda x: x[4] if x[4] else '')
                    rk2, tpl, dev_code, dev_num, _ = tasks[0]
                    if tpl == 'DKCback':
                        # 回空车：从 currentCount 中选一个真实设备来"离开"
                        st = status()
                        for a in st.get('areas', []):
                            if a['region_key'] == rk2 and a.get('currentCount', 0) > 0:
                                # 获取 currentCount.json 中的设备
                                cr = region_file(rk2, 'currentCount.json')
                                if cr.get('content'):
                                    try:
                                        devices = json.loads(cr['content'])
                                        if devices:
                                            dev_info = random.choice(devices)
                                            real_dc = dev_info.get('deviceCode', '')
                                            real_dn = dev_info.get('deviceNum', '')
                                            r = report(tpl, real_dn, 8, rk2, device_code=real_dc)
                                            if r.get('success'):
                                                log(f"  [{rk2}] 完成空车(离开) {tpl} {real_dn}")
                                            break
                                    except: pass
                    else:
                        # 来空车：用后端记录完成
                        r = report(tpl, dev_num or dev_code, 8, rk2, device_code=dev_code)
                        if r.get('success'):
                            log(f"  [{rk2}] 完成空车(来) {tpl} {dev_num or dev_code}")
            except: pass
    
    threading.Thread(target=done_load_loop, daemon=True).start()
    threading.Thread(target=done_empty_loop, daemon=True).start()
    
    try:
        while True:
            elapsed = time.time() - start_time
            if args.duration > 0 and elapsed >= args.duration:
                log(f"\n达到运行时长 {args.duration}s，自动停止")
                break
            
            round_num += 1
            
            # 真实场景：模拟负载高峰/低谷
            # 用正弦波模拟一天中的负载变化，周期约60轮
            import math
            wave = math.sin(round_num * math.pi / 30)  # 周期60轮
            # wave ∈ [-1, 1]，映射到来任务概率 [0.3, 0.7]
            in_prob = 0.5 + wave * 0.2
            
            rk = random.choice(list(REGIONS.keys()))
            region = REGIONS[rk]
            
            # 根据高峰/低谷调整来/离比例
            is_in = random.random() < in_prob
            if is_in and region['in_tpls']:
                load_in = [t for t in region['in_tpls'] if t not in EMPTY_TPL]
                if load_in:
                    tpl = random.choice(load_in)
                    dev = random.choice(DEV_POOL)
                    # 为新设备生成 deviceCode 并记录
                    if dev not in dev_code_map:
                        dev_code_map[dev] = f"EM{random.randint(10000,99999)}DAK{random.randint(1000,9999)}"
                    dc = dev_code_map[dev]
                    r = report(tpl, dev, 6, rk, device_code=dc)
                    if r.get('success'):
                        total_ops['load_in'] += 1
                        log(f"  [{rk}] 来负载 {tpl} {dev}")
            elif not is_in and region['out_tpls']:
                load_out = [t for t in region['out_tpls'] if t not in EMPTY_TPL]
                if load_out:
                    tpl = random.choice(load_out)
                    dev = random.choice(DEV_POOL)
                    # 使用已有 deviceCode 或生成新的
                    if dev not in dev_code_map:
                        dev_code_map[dev] = f"EM{random.randint(10000,99999)}DAK{random.randint(1000,9999)}"
                    dc = dev_code_map[dev]
                    r = report(tpl, dev, 6, rk, device_code=dc)
                    if r.get('success'):
                        total_ops['load_out'] += 1
                        log(f"  [{rk}] 离负载 {tpl} {dev}")
            
            # 每5轮执行一次计算（让系统自动下发空车）
            if round_num % 5 == 0:
                rk_exec = random.choice(list(REGIONS.keys()))
                r = execute(rk_exec)
                if r.get('success'):
                    total_ops['exec'] += 1
                    log(f"  [{rk_exec}] 执行计算: {'模拟' if r.get('simulated',True) else '真实'}下发{r.get('dispatch_count',0)}台")
                elif r.get('error'):
                    log(f"  [{rk_exec}] 执行阻止: {r.get('error','')}")
            
            # 每10轮打印统计
            if round_num % 10 == 0:
                elapsed_s = time.time() - start_time
                log(f"轮{round_num} | 负载来:{total_ops['load_in']} 负载离:{total_ops['load_out']} 执行:{total_ops['exec']} 耗时:{elapsed_s:.0f}s")
                print_summary(REGIONS)
            
            time.sleep(args.load_interval)
    except KeyboardInterrupt:
        log("\n手动停止")
    
    # 最终统计
    elapsed_s = time.time() - start_time
    log(f"\n=== 最终统计 ===")
    log(f"运行 {round_num} 轮, 耗时 {elapsed_s:.0f}s")
    log(f"负载来:{total_ops['load_in']} 负载离:{total_ops['load_out']} 执行:{total_ops['exec']}")
    log(f"操作日志:")
    gl = glog().get('logs',[])
    log(f"  共 {len(gl)} 条")
    for l in gl[:5]:
        log(f"    [{l.get('time','')[11:19]}] [{l.get('region_key','?')}] {l.get('action','')}: {l.get('detail','')[:80]}")
    
    # 清理
    log("清理所有区域")
    for rk in REGIONS: clean(rk)
    
    print(f"\n{'='*60}\n  完成!\n{'='*60}")

if __name__=="__main__":
    main()
