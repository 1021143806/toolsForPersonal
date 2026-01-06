#!/usr/bin/env python3
"""
提取 config 并生成表格
"""

import re
import sys
from pathlib import Path

try:
    import json5
except ImportError:
    print("请安装 json5: pip install json5")
    sys.exit(1)

def find_balanced_braces(text, start):
    """从 start 位置找到匹配的 }"""
    count = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch == '{':
            count += 1
        elif ch == '}':
            count -= 1
            if count == 0:
                return i
        i += 1
    return -1

def extract_config(html_content):
    """从 HTML 中提取 config 对象"""
    # 查找 const config = {
    pattern = r'const config\s*='
    match = re.search(pattern, html_content)
    if not match:
        raise ValueError("未找到 config 对象")
    
    start = match.end()
    # 跳过空白
    while start < len(html_content) and html_content[start].isspace():
        start += 1
    if html_content[start] != '{':
        raise ValueError("预期 {")
    
    # 找到匹配的 }
    end = find_balanced_braces(html_content, start)
    if end == -1:
        raise ValueError("未找到匹配的 }")
    
    config_str = html_content[start:end+1]
    # 移除注释行（可选）
    config_str = re.sub(r'//.*?\n', '\n', config_str)
    # 使用 json5 解析
    try:
        config = json5.loads(config_str)
    except Exception as e:
        print(f"解析错误: {e}")
        # 输出有问题的部分
        lines = config_str.split('\n')
        for i, line in enumerate(lines[:15]):
            print(f'{i+1}: {repr(line)}')
        raise
    
    return config

def generate_markdown_table(config):
    """生成 markdown 表格"""
    areas = config.get('areas', {})
    if not areas:
        return "无区域配置"
    
    # 表头
    table = "| 区域 | 任务名称 | 任务代码 | 货架要求 | 路径要求 | 路径选项 |\n"
    table += "|------|----------|----------|----------|----------|----------|\n"
    
    for area_name, area_data in areas.items():
        tasks = area_data.get('tasks', {})
        if not tasks:
            # 该区域无任务，仍显示一行
            table += f"| {area_name} | - | - | - | - | - |\n"
            continue
        
        first_task = True
        for task_name, task in tasks.items():
            code = task.get('code', '')
            requires_shelf = '是' if task.get('requires_shelf') else '否'
            requires_task_path = '是' if task.get('requires_task_path') else '否'
            path_options = task.get('task_path_options', [])
            # 格式化路径选项
            if isinstance(path_options, list):
                if len(path_options) == 0:
                    path_str = '无'
                else:
                    # 提取每个选项的 value 和 label
                    items = []
                    for opt in path_options:
                        if isinstance(opt, dict):
                            val = opt.get('value', '')
                            label = opt.get('label', '')
                            if label:
                                items.append(f"{val} ({label})")
                            else:
                                items.append(val)
                        else:
                            items.append(str(opt))
                    path_str = '<br>'.join(items)
            else:
                path_str = str(path_options)
            
            if first_task:
                table += f"| {area_name} | {task_name} | {code} | {requires_shelf} | {requires_task_path} | {path_str} |\n"
                first_task = False
            else:
                # 后续任务，区域列留空
                table += f"| | {task_name} | {code} | {requires_shelf} | {requires_task_path} | {path_str} |\n"
    
    return table

def main():
    base_dir = Path(__file__).parent
    html_path = base_dir / 'index.html'
    readme_path = base_dir / 'readme.md'
    
    if not html_path.exists():
        print(f"错误: {html_path} 不存在")
        sys.exit(1)
    
    if not readme_path.exists():
        print(f"错误: {readme_path} 不存在")
        sys.exit(1)
    
    # 读取 HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 提取 config
    config = extract_config(html_content)
    print("成功提取 config")
    
    # 生成表格
    table = generate_markdown_table(config)
    print("生成的表格预览（前5行）：")
    lines = table.split('\n')
    for line in lines[:7]:
        print(line)
    
    # 插入到 readme.md
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到“已配置区域”部分
    pattern = r'(## 已配置区域.*?\n)(.*?)(?=\n##|\n---|\n\*|\n$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        before = content[:match.end()]
        after = content[match.end():]
        new_section = "\n### 任务模板详情\n\n以下表格列出了所有区域的任务模板配置：\n\n" + table + "\n"
        new_content = before + new_section + after
    else:
        # 如果找不到，则在“系统配置”节后插入
        pattern = r'(## 系统配置.*?\n)(.*?)(?=\n##|\n---|\n\*|\n$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            before = content[:match.end()]
            after = content[match.end():]
            new_section = "\n### 任务模板详情\n\n以下表格列出了所有区域的任务模板配置：\n\n" + table + "\n"
            new_content = before + new_section + after
        else:
            # 最后插入到文件末尾
            new_content = content + "\n## 任务模板详情\n\n" + table + "\n"
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n表格已插入到 {readme_path}")

if __name__ == '__main__':
    main()