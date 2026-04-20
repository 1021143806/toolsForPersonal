#!/usr/bin/env python3
"""
离线部署功能测试脚本
验证项目是否完全支持离线部署
"""

import os
import re
from pathlib import Path

def check_offline_dependencies(filepath):
    """检查单个文件的离线依赖"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    
    # 检查外部CDN链接
    external_patterns = [
        r'https?://[^"\']+\.css',
        r'https?://[^"\']+\.js',
        r'https?://[^"\']+\.woff2?',
        r'https?://[^"\']+\.ttf',
        r'https?://[^"\']+\.eot',
        r'https?://[^"\']+\.svg',
        r'cdn\.',
        r'unpkg\.com',
        r'cdnjs\.cloudflare\.com',
        r'stackpath\.bootstrapcdn\.com',
        r'fonts\.googleapis\.com',
        r'fonts\.gstatic\.com',
        r'code\.jquery\.com',
        r'cdn\.jsdelivr\.net'
    ]
    
    for pattern in external_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            for match in matches:
                issues.append(f"发现外部依赖: {match}")
    
    # 检查是否使用本地vendor路径
    if '/static/vendor/' not in content:
        # 对于HTML文件，应该使用本地vendor
        if str(filepath).endswith('.html'):
            # 检查是否使用了Bootstrap或其他依赖
            if 'bootstrap' in content.lower() or 'jquery' in content.lower() or 'chart' in content.lower():
                issues.append("可能未使用本地vendor路径")
    
    return issues

def check_vendor_files():
    """检查vendor目录中的文件"""
    vendor_dir = Path(__file__).parent.parent / 'static' / 'vendor'
    required_files = [
        'bootstrap/bootstrap.min.css',
        'bootstrap/bootstrap.bundle.min.js',
        'bootstrap-icons/bootstrap-icons.min.css',
        'jquery/jquery-3.6.0.min.js',
        'chart.js/chart.min.js',
        'sortablejs/Sortable.min.js',
        'animate.css/animate.min.css'
    ]
    
    missing_files = []
    for req_file in required_files:
        file_path = vendor_dir / req_file
        if not file_path.exists():
            missing_files.append(req_file)
    
    return missing_files

def main():
    templates_dir = Path(__file__).parent.parent / 'templates'
    
    print("离线部署功能测试报告")
    print("=" * 80)
    
    # 检查vendor文件
    print("\n1. 检查本地依赖文件:")
    missing_files = check_vendor_files()
    if missing_files:
        print("❌ 缺少以下依赖文件:")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print("✅ 所有本地依赖文件都存在")
    
    # 检查所有HTML文件的外部依赖
    print("\n2. 检查HTML文件的外部依赖:")
    all_issues = {}
    total_files = 0
    files_with_external_deps = 0
    
    for html_file in templates_dir.rglob('*.html'):
        total_files += 1
        relative_path = html_file.relative_to(templates_dir.parent)
        
        issues = check_offline_dependencies(html_file)
        
        if issues:
            files_with_external_deps += 1
            all_issues[str(relative_path)] = issues
    
    if all_issues:
        print(f"❌ 发现 {files_with_external_deps}/{total_files} 个文件有外部依赖:")
        for filepath, issues in all_issues.items():
            print(f"\n{filepath}:")
            for issue in issues[:3]:  # 只显示前3个问题
                print(f"   - {issue}")
            if len(issues) > 3:
                print(f"   - ... 还有 {len(issues)-3} 个问题")
    else:
        print(f"✅ 所有 {total_files} 个HTML文件都没有外部依赖")
    
    # 检查配置文件
    print("\n3. 检查配置文件:")
    config_file = templates_dir.parent / 'static' / 'js' / 'config.js'
    if config_file.exists():
        print(f"✅ 配置文件存在: {config_file.relative_to(templates_dir.parent)}")
        
        # 检查配置文件是否在.gitignore中
        gitignore_file = templates_dir.parent / '.gitignore'
        if gitignore_file.exists():
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            if 'config.js' in gitignore_content:
                print("✅ 配置文件已在.gitignore中")
            else:
                print("⚠️  警告: 配置文件未在.gitignore中")
    else:
        print("⚠️  警告: 配置文件不存在")
    
    # 检查主题管理器
    print("\n4. 检查主题系统:")
    theme_manager = templates_dir.parent / 'static' / 'js' / 'theme-manager.js'
    if theme_manager.exists():
        print(f"✅ 主题管理器存在: {theme_manager.relative_to(templates_dir.parent)}")
        
        # 检查主题管理器功能
        with open(theme_manager, 'r', encoding='utf-8') as f:
            theme_content = f.read()
        
        required_features = [
            'localStorage',
            'data-bs-theme',
            'themeToggle',
            'dark',
            'light'
        ]
        
        missing_features = []
        for feature in required_features:
            if feature not in theme_content:
                missing_features.append(feature)
        
        if missing_features:
            print(f"⚠️  警告: 主题管理器缺少功能: {', '.join(missing_features)}")
        else:
            print("✅ 主题管理器功能完整")
    else:
        print("❌ 错误: 主题管理器不存在")
    
    print("\n" + "=" * 80)
    print("测试总结:")
    
    if missing_files or all_issues:
        print("❌ 离线部署功能存在问题，需要修复")
        return 1
    else:
        print("✅ 项目完全支持离线部署")
        return 0

if __name__ == '__main__':
    exit(main())