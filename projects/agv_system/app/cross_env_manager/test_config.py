#!/usr/bin/env python3
"""
测试配置文件加载
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import load_config, DB_CONFIG

print("测试配置文件加载...")
print("=" * 60)

# 加载配置
config = load_config()
print(f"加载的配置: {config}")

print("\n数据库配置:")
print(f"  host: {DB_CONFIG['host']}")
print(f"  port: {DB_CONFIG['port']}")
print(f"  user: {DB_CONFIG['user']}")
print(f"  database: {DB_CONFIG['database']}")
print(f"  charset: {DB_CONFIG['charset']}")

print("\n预期配置 (来自 config/env.toml):")
print("  host: 47.98.244.173")
print("  port: 53308")
print("  user: root")
print("  database: ds")
print("  charset: utf8mb4")

print("\n" + "=" * 60)
if DB_CONFIG['database'] == 'ds' and DB_CONFIG['host'] == '47.98.244.173':
    print("✅ 配置加载成功！")
else:
    print("❌ 配置加载失败，使用了默认值")
    print(f"   当前数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"   预期数据库: ds@47.98.244.173:53308")