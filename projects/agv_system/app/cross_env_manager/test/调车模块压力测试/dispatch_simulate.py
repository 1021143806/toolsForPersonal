#!/usr/bin/env python3
"""调车模块压力测试 - 按实际报文格式上报，从配置文件动态获取区域和模板"""
import urllib.request, json, time, random, sys
from datetime import datetime
from http.cookiejar import CookieJar

BASE = "http://127.0.0.1:5000"
DEV_POOL = [f"DJC{i}" for i in range(1, 61)]

cookie_jar = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

def req(m, u, d=None, auth=True):
    try:
        b = json.dumps(d).encode() if d else None
        # URL 编码中文
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

def report(tpl, dev, st, rk):
    """按实际报文格式上报（字段顺序与报文一致）"""
    data = {
        "shelfCurrPosition": str(random.randint(10000000, 99999999)),
        "subTaskStatus": "3",
        "orderId": f"pad_html{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{random.randint(100,999)}_{random.randint(1000,9999)}",
        "deviceCode": f"EM{random.randint(10000,99999)}DAK{random.randint(1000,9999)}",
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

def pa(a):
    if not a: return
    print(f"  [{a.get('name','?')}] cur:{a.get('currentCount',0)} a:{a.get('a',0)} b:{a.get('b',0)} need:{a.get('need',0)} x:{a.get('xmin',0)}~{a.get('xmax',0)} dir:{a.get('direction','none')} en:{a.get('enabled',False)}")
    print(f"  来:", [(t['code'],t['count']) for t in a.get('templates',{}).get('incoming',[])])
    print(f"  离:", [(t['code'],t['count']) for t in a.get('templates',{}).get('outgoing',[])])

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_regions_from_config():
    """从配置文件动态加载区域和模板"""
    c = cfg()
    regions = {}
    for rk, region in c.items():
        if not isinstance(region, dict) or 'templates' not in region:
            continue
        in_tpls = []
        out_tpls = []
        for t in region.get('templates', []):
            name = t.get('name', '')
            direction = t.get('direction', '')
            if direction == 'in':
                in_tpls.append(name)
            elif direction == 'out':
                out_tpls.append(name)
        if in_tpls or out_tpls:
            regions[rk] = {'in_tpls': in_tpls, 'out_tpls': out_tpls}
    return regions

def get_backend_tasks(regions):
    """从后端各区域模板文件中获取所有 status=6 的任务"""
    tasks = []  # [(rk, template, deviceCode, deviceNum, create_time)]
    try:
        st = status()
        for a in st.get('areas', []):
            rk = a['region_key']
            if rk not in regions:
                continue
            # 遍历来区域和离开模板
            for t in a.get('templates', {}).get('incoming', []):
                if t.get('count', 0) > 0:
                    files_resp = region_files(rk)
                    if files_resp.get('files'):
                        for f in files_resp['files']:
                            if f['filename'].replace('.json', '') == t['code'] and f.get('exists'):
                                content_resp = region_file(rk, f['filename'])
                                if content_resp.get('content'):
                                    try:
                                        for task in json.loads(content_resp['content']):
                                            if task.get('status') == 6:
                                                tasks.append((
                                                    rk, t['code'],
                                                    task.get('deviceCode', ''),
                                                    task.get('deviceNum', ''),
                                                    task.get('create_time', '')
                                                ))
                                    except: pass
            for t in a.get('templates', {}).get('outgoing', []):
                if t.get('count', 0) > 0:
                    files_resp = region_files(rk)
                    if files_resp.get('files'):
                        for f in files_resp['files']:
                            if f['filename'].replace('.json', '') == t['code'] and f.get('exists'):
                                content_resp = region_file(rk, f['filename'])
                                if content_resp.get('content'):
                                    try:
                                        for task in json.loads(content_resp['content']):
                                            if task.get('status') == 6:
                                                tasks.append((
                                                    rk, t['code'],
                                                    task.get('deviceCode', ''),
                                                    task.get('deviceNum', ''),
                                                    task.get('create_time', '')
                                                ))
                                    except: pass
    except: pass
    return tasks

def main():
    print("="*60)
    print(f"  调车模块压力测试(实际报文格式)")
    print(f"  开始:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    if not login(): sys.exit(1)
    
    # 从配置文件动态加载区域
    REGIONS = load_regions_from_config()
    if not REGIONS:
        log("错误: 未从配置中找到有效区域")
        sys.exit(1)
    
    log(f"从配置加载 {len(REGIONS)} 个区域: {list(REGIONS.keys())}")
    for rk, r in REGIONS.items():
        log(f"  {rk}: 来{len(r['in_tpls'])}个模板 {r['in_tpls']}, 离{len(r['out_tpls'])}个模板 {r['out_tpls']}")
    
    # 禁用所有区域（模拟下发模式）
    log("阶段1: 禁用所有区域(模拟下发模式)")
    c = cfg()
    for rk in REGIONS:
        if rk in c:
            c[rk]['enabled'] = False
    r = save_cfg(c)
    log(f"  {'OK' if r.get('success') else 'FAIL'}")
    
    # 清理所有区域旧数据
    log("阶段2: 清理旧数据")
    for rk in REGIONS:
        r = clean(rk)
        log(f"  {rk}: {r.get('message','')}")
    
    log("阶段3: 初始状态")
    for a in status().get('areas',[]):
        if a['region_key'] in REGIONS: pa(a)
    
    log("阶段4: 开始循环(每1秒, Ctrl+C停止)")
    round_num = 0
    active = {}  # {region_key: {device: {template, direction, create_time}}}
    
    try:
        while True:
            round_num += 1
            log(f"\n--- 第{round_num}轮 ---")
            
            # 随机选择操作
            op = random.choice(['start_in','start_out','complete','execute','status'])
            
            # 随机选择区域
            rk = random.choice(list(REGIONS.keys()))
            region = REGIONS[rk]
            
            if op == 'start_in' and region['in_tpls']:
                tpl = random.choice(region['in_tpls'])
                dev = random.choice(DEV_POOL)
                r = report(tpl, dev, 6, rk)
                if r.get('success'):
                    if rk not in active: active[rk] = {}
                    active[rk][dev] = {'template': tpl, 'direction': 'in', 'create_time': time.time()}
                    log(f"  [{rk}] IN {tpl} {dev} OK")
                else:
                    log(f"  [{rk}] IN FAIL: {r.get('error','')}")
            
            elif op == 'start_out' and region['out_tpls']:
                tpl = random.choice(region['out_tpls'])
                dev = random.choice(DEV_POOL)
                r = report(tpl, dev, 6, rk)
                if r.get('success'):
                    if rk not in active: active[rk] = {}
                    active[rk][dev] = {'template': tpl, 'direction': 'out', 'create_time': time.time()}
                    log(f"  [{rk}] OUT {tpl} {dev} OK")
                else:
                    log(f"  [{rk}] OUT FAIL: {r.get('error','')}")
            
            elif op == 'complete':
                # 优先从后端文件中获取已有 status=6 的任务上报状态8
                backend_tasks = get_backend_tasks(REGIONS)
                
                if backend_tasks:
                    # 按创建时间升序排序（最早的排最前）
                    backend_tasks.sort(key=lambda x: x[4] if x[4] else '')
                    rk2, tpl, dev_code, dev_num, _ = backend_tasks[0]
                    r = report(tpl, dev_num or dev_code, 8, rk2)
                    log(f"  [{rk2}] DONE(后端记录) {tpl} {dev_num or dev_code} {'OK' if r.get('success') else 'FAIL'}")
                    # 从 active 中同步移除
                    if rk2 in active and (dev_num or dev_code) in active[rk2]:
                        del active[rk2][dev_num or dev_code]
                        if not active[rk2]:
                            del active[rk2]
                else:
                    # 没有后端记录时，从 active 内存中取
                    all_tasks = []
                    for rk2, devices in active.items():
                        for dev, info in devices.items():
                            all_tasks.append((rk2, dev, info))
                    
                    if all_tasks:
                        all_tasks.sort(key=lambda x: x[2].get('create_time', 0))
                        rk2, dev, info = all_tasks[0]
                        del active[rk2][dev]
                        if not active[rk2]:
                            del active[rk2]
                        r = report(info['template'], dev, 8, rk2)
                        log(f"  [{rk2}] DONE(内存) {info['template']} {dev} {'OK' if r.get('success') else 'FAIL'}")
                    else:
                        log(f"  无执行中的任务可完成")
            
            elif op == 'execute':
                r = execute(rk)
                if r.get('success'):
                    log(f"  [{rk}] EXEC: {'模拟' if r.get('simulated',True) else '真实'}下发{r.get('dispatch_count',0)}台 OK")
                elif r.get('error'):
                    log(f"  [{rk}] EXEC阻止: {r.get('error','')}")
                else:
                    log(f"  [{rk}] EXEC失败: {r.get('error','?')}")
            
            elif op == 'status':
                for a in status().get('areas',[]):
                    if a['region_key'] in REGIONS:
                        log(f"  [{a['region_key']}] cur:{a['currentCount']} a:{a['a']} b:{a['b']} need:{a['need']} dir:{a['direction']}")
            
            # 每5轮打印详细状态
            if round_num % 5 == 0:
                for a in status().get('areas',[]):
                    if a['region_key'] in REGIONS: pa(a)
            
            # 每10轮打印操作日志
            if round_num % 10 == 0:
                gl = glog().get('logs',[])
                log(f"  LOG: {len(gl)}条")
                for l in gl[:3]:
                    log(f"    [{l.get('time','')[11:19]}] [{l.get('region_key','?')}] {l.get('action','')}: {l.get('detail','')[:60]}")
            
            time.sleep(1)
    except KeyboardInterrupt:
        log("\n手动停止")
    
    log("\n阶段5: 最终状态")
    for a in status().get('areas',[]):
        if a['region_key'] in REGIONS: pa(a)
    
    log("阶段6: 清理所有区域")
    for rk in REGIONS:
        r = clean(rk)
        log(f"  {rk}: {r.get('message','')}")
    
    log("阶段7: 操作日志")
    gl = glog().get('logs',[])
    log(f"  {len(gl)}条")
    for l in gl[:5]:
        log(f"    [{l.get('time','')[11:19]}] [{l.get('region_key','?')}] {l.get('action','')}: {l.get('detail','')[:80]}")
    
    print(f"\n{'='*60}\n  完成! 共{round_num}轮\n{'='*60}")

if __name__=="__main__":
    main()
