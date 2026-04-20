#!/usr/bin/env python3
"""
为独立HTML页面添加主题切换按钮和主题管理器
"""

import os
import re
from pathlib import Path

def add_theme_support(filepath):
    """为单个HTML文件添加主题支持"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经继承base.html
    if '{% extends "base.html" %}' in content:
        print(f"跳过: {filepath} (继承base.html)")
        return False
    
    # 检查是否已经有主题切换按钮
    if 'themeToggle' in content or 'theme-toggle' in content:
        print(f"跳过: {filepath} (已有主题切换按钮)")
        return False
    
    # 检查是否已经有主题管理器
    has_theme_manager = 'theme-manager.js' in content
    
    # 修改内容
    modified = False
    
    # 1. 在标题后添加主题切换按钮
    # 查找第一个h1标签后的位置
    h1_pattern = r'(<h1[^>]*>.*?</h1>)'
    h1_match = re.search(h1_pattern, content, re.DOTALL)
    
    if h1_match:
        h1_tag = h1_match.group(1)
        # 在h1标签后添加主题切换按钮
        theme_button = '''<div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="mb-0">AGV任务查询系统</h1>
            <button class="btn btn-outline-secondary" id="themeToggle">
                <i class="bi bi-moon-stars me-2"></i>暗黑模式
            </button>
        </div>'''
        
        # 替换h1标签
        new_content = content.replace(h1_tag, theme_button)
        if new_content != content:
            content = new_content
            modified = True
            print(f"已添加主题切换按钮到: {filepath}")
    
    # 2. 确保引入Bootstrap Icons
    if 'bootstrap-icons' not in content and 'bootstrap-icons.min.css' not in content:
        # 在Bootstrap CSS后添加Bootstrap Icons
        bootstrap_css_pattern = r'(<link[^>]*bootstrap\.min\.css[^>]*>)'
        bootstrap_css_match = re.search(bootstrap_css_pattern, content)
        
        if bootstrap_css_match:
            bootstrap_css = bootstrap_css_match.group(1)
            bootstrap_icons = '\n    <link rel="stylesheet" href="/static/vendor/bootstrap-icons/bootstrap-icons.min.css">'
            new_content = content.replace(bootstrap_css, bootstrap_css + bootstrap_icons)
            if new_content != content:
                content = new_content
                modified = True
                print(f"已添加Bootstrap Icons到: {filepath}")
    
    # 3. 确保引入主题管理器
    if not has_theme_manager:
        # 在Bootstrap JS后添加主题管理器
        bootstrap_js_pattern = r'(<script[^>]*bootstrap\.bundle\.min\.js[^>]*></script>)'
        bootstrap_js_match = re.search(bootstrap_js_pattern, content)
        
        if bootstrap_js_match:
            bootstrap_js = bootstrap_js_match.group(1)
            theme_manager = '\n    <!-- 统一的主题管理器 -->\n    <script src="/static/js/theme-manager.js"></script>'
            new_content = content.replace(bootstrap_js, bootstrap_js + theme_manager)
            if new_content != content:
                content = new_content
                modified = True
                print(f"已添加主题管理器到: {filepath}")
    
    # 保存修改
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    templates_dir = Path(__file__).parent.parent / 'templates'
    
    print("为独立页面添加主题支持")
    print("=" * 80)
    
    # 需要处理的文件列表（从测试结果中获取）
    files_to_process = [
        'task_query_home.html',
        'task_query_result.html',
        'cross_task_by_template.html',
        'cross_model_process_info.html',
        'cross_task_info.html'
    ]
    
    # 处理query目录下的文件
    query_dir = templates_dir / 'query'
    if query_dir.exists():
        for html_file in query_dir.glob('*.html'):
            files_to_process.append(f'query/{html_file.name}')
    
    total_processed = 0
    total_modified = 0
    
    for filename in files_to_process:
        filepath = templates_dir / filename
        if filepath.exists():
            total_processed += 1
            if add_theme_support(filepath):
                total_modified += 1
    
    print(f"\n处理完成:")
    print(f"  处理文件数: {total_processed}")
    print(f"  修改文件数: {total_modified}")
    print(f"  无需修改: {total_processed - total_modified}")
    
    # 运行测试验证
    print("\n运行主题一致性测试验证...")
    os.system(f'cd {templates_dir.parent} && python3 test/theme_consistency_test.py')

if __name__ == '__main__':
    main()