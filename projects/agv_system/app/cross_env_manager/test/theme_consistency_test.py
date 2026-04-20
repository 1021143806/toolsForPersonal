#!/usr/bin/env python3
"""
主题一致性测试脚本
检查所有HTML模板文件是否支持统一的主题系统
"""

import os
import re
from pathlib import Path

def check_template_file(filepath):
    """检查单个模板文件的主题支持情况"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    
    # 检查是否继承base.html
    if '{% extends "base.html" %}' in content:
        # 继承base.html的文件通过base.html获得主题支持
        # 不需要单独检查theme-manager.js
        return issues
    
    # 独立HTML文件检查
    # 1. 检查是否有data-bs-theme属性
    if 'data-bs-theme=' not in content:
        issues.append("缺少data-bs-theme属性")
    
    # 2. 检查是否引入Bootstrap CSS
    if 'bootstrap.min.css' not in content:
        issues.append("未引入Bootstrap CSS")
    
    # 3. 检查是否引入Bootstrap JS
    if 'bootstrap.bundle.min.js' not in content:
        issues.append("未引入Bootstrap JS")
    
    # 4. 检查是否引入主题管理器
    if 'theme-manager.js' not in content:
        issues.append("未引入统一的主题管理器")
    
    # 5. 检查是否有主题切换按钮
    if 'themeToggle' not in content and 'theme-toggle' not in content:
        issues.append("缺少主题切换按钮")
    
    return issues

def main():
    templates_dir = Path(__file__).parent.parent / 'templates'
    
    print("主题一致性测试报告")
    print("=" * 80)
    
    all_issues = {}
    total_files = 0
    files_with_issues = 0
    
    # 检查所有HTML文件
    for html_file in templates_dir.rglob('*.html'):
        total_files += 1
        relative_path = html_file.relative_to(templates_dir.parent)
        
        issues = check_template_file(html_file)
        
        if issues:
            files_with_issues += 1
            all_issues[str(relative_path)] = issues
    
    # 输出结果
    print(f"检查文件总数: {total_files}")
    print(f"存在问题的文件数: {files_with_issues}")
    print(f"通过率: {(total_files - files_with_issues) / total_files * 100:.1f}%")
    print()
    
    if all_issues:
        print("发现的问题:")
        print("-" * 80)
        for filepath, issues in all_issues.items():
            print(f"\n{filepath}:")
            for issue in issues:
                print(f"  - {issue}")
    
    # 检查主题管理器文件是否存在
    theme_manager_path = templates_dir.parent / 'static' / 'js' / 'theme-manager.js'
    if not theme_manager_path.exists():
        print(f"\n⚠️  警告: 主题管理器文件不存在: {theme_manager_path}")
    else:
        print(f"\n✓ 主题管理器文件存在: {theme_manager_path}")
    
    # 检查vendor目录是否存在
    vendor_dir = templates_dir.parent / 'static' / 'vendor'
    if not vendor_dir.exists():
        print(f"\n⚠️  警告: vendor目录不存在: {vendor_dir}")
    else:
        print(f"\n✓ vendor目录存在: {vendor_dir}")
        
        # 检查关键依赖文件
        required_files = [
            'bootstrap/bootstrap.min.css',
            'bootstrap/bootstrap.bundle.min.js',
            'bootstrap-icons/bootstrap-icons.min.css'
        ]
        
        for req_file in required_files:
            file_path = vendor_dir / req_file
            if not file_path.exists():
                print(f"⚠️  警告: 缺少依赖文件: {req_file}")
            else:
                print(f"✓ 依赖文件存在: {req_file}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    
    if files_with_issues > 0:
        print("❌ 存在主题一致性问题，需要修复")
        return 1
    else:
        print("✅ 所有文件主题一致性检查通过")
        return 0

if __name__ == '__main__':
    exit(main())