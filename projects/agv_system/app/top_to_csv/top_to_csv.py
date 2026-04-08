#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
top日志解析工具 - 将top命令输出解析为CSV格式
主要分析CPU使用率、内存使用率、系统负载等指标

用法：
    python3 top_to_csv.py <input_log_file> [output_csv_file]

示例：
    python3 top_to_csv.py top_out/top_20260403_140256.log top_analysis.csv
"""

import re
import sys
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class TopLogParser:
    """解析top日志文件的类"""
    
    def __init__(self):
        self.ip_pattern = re.compile(r'==========\s+([\d\.]+)\s+at\s+(.+?)\s+==========')
        self.top_header_pattern = re.compile(r'^top\s+-')
        self.cpu_pattern = re.compile(r'%Cpu\(s\):\s+([\d\.]+)\s+us,\s+([\d\.]+)\s+sy,\s+([\d\.]+)\s+ni,\s+([\d\.]+)\s+id,\s+([\d\.]+)\s+wa')
        self.mem_pattern = re.compile(r'^(KiB|MiB|GiB)\s+Mem\s*:\s*([\d\.]+)\s+total,\s+([\d\.]+)\s+free,\s+([\d\.]+)\s+used,\s+([\d\.]+)\s+buff/cache')
        self.swap_pattern = re.compile(r'^(KiB|MiB|GiB)\s+Swap\s*:\s*([\d\.]+)\s+total,\s+([\d\.]+)\s+free,\s+([\d\.]+)\s+used')
        self.load_pattern = re.compile(r'load average:\s+([\d\.]+),\s+([\d\.]+),\s+([\d\.]+)')
        self.tasks_pattern = re.compile(r'Tasks:\s+(\d+)\s+total,\s+(\d+)\s+running,\s+(\d+)\s+sleeping')
        
    def parse_log_file(self, file_path: str) -> List[Dict]:
        """
        解析整个日志文件
        
        Args:
            file_path: 日志文件路径
            
        Returns:
            解析后的数据列表，每个元素是一个设备的统计信息
        """
        results = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按设备分割
        sections = self.ip_pattern.split(content)
        
        # 第一个元素是空字符串或文件开头内容
        for i in range(1, len(sections), 3):
            if i + 2 >= len(sections):
                break
                
            ip = sections[i]
            timestamp_str = sections[i+1]
            section_content = sections[i+2]
            
            result = self.parse_section(ip, timestamp_str, section_content)
            if result:
                results.append(result)
        
        return results
    
    def parse_section(self, ip: str, timestamp_str: str, content: str) -> Optional[Dict]:
        """
        解析单个设备部分
        
        Args:
            ip: 设备IP
            timestamp_str: 时间戳字符串
            content: 该设备部分的内容
            
        Returns:
            解析后的数据字典，如果解析失败返回None
        """
        # 初始化结果
        result = {
            'timestamp': timestamp_str.strip(),
            'ip': ip.strip(),
            'status': 'failed',
            'cpu_usage': 0.0,
            'mem_usage': 0.0,
            'mem_total_mb': 0.0,
            'mem_used_mb': 0.0,
            'mem_free_mb': 0.0,
            'swap_usage': 0.0,
            'swap_total_mb': 0.0,
            'swap_used_mb': 0.0,
            'load_1min': 0.0,
            'load_5min': 0.0,
            'load_15min': 0.0,
            'io_wait': 0.0,
            'tasks_total': 0,
            'tasks_running': 0,
            'tasks_sleeping': 0,
            'uptime': '',
            'users': 0,
            'error_message': ''
        }
        
        # 检查是否连接失败
        if 'Permission denied' in content or '连接超时' in content or 'Connection timed out' in content:
            result['status'] = 'failed'
            # 提取错误信息
            error_lines = []
            for line in content.split('\n'):
                if 'Permission denied' in line or '连接超时' in line or 'Connection timed out' in line:
                    error_lines.append(line.strip())
            result['error_message'] = ' | '.join(error_lines[:2])  # 只保留前两行错误信息
            return result
        
        # 连接成功，解析top输出
        result['status'] = 'success'
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 解析uptime和load
            if line.startswith('top -'):
                # 提取uptime
                uptime_match = re.search(r'up\s+(.+?),', line)
                if uptime_match:
                    result['uptime'] = uptime_match.group(1)
                
                # 提取users
                users_match = re.search(r',\s+(\d+)\s+user', line)
                if users_match:
                    result['users'] = int(users_match.group(1))
                
                # 提取load
                load_match = self.load_pattern.search(line)
                if load_match:
                    result['load_1min'] = float(load_match.group(1))
                    result['load_5min'] = float(load_match.group(2))
                    result['load_15min'] = float(load_match.group(3))
            
            # 解析Tasks
            tasks_match = self.tasks_pattern.search(line)
            if tasks_match:
                result['tasks_total'] = int(tasks_match.group(1))
                result['tasks_running'] = int(tasks_match.group(2))
                result['tasks_sleeping'] = int(tasks_match.group(3))
            
            # 解析CPU
            cpu_match = self.cpu_pattern.search(line)
            if cpu_match:
                us = float(cpu_match.group(1))
                sy = float(cpu_match.group(2))
                ni = float(cpu_match.group(3))
                id = float(cpu_match.group(4))
                wa = float(cpu_match.group(5))
                
                # CPU使用率 = 100 - idle
                result['cpu_usage'] = 100.0 - id
                result['io_wait'] = wa
            
            # 解析内存
            mem_match = self.mem_pattern.search(line)
            if mem_match:
                unit = mem_match.group(1)
                total = float(mem_match.group(2))
                free = float(mem_match.group(3))
                used = float(mem_match.group(4))
                buff_cache = float(mem_match.group(5))
                
                # 转换为MB
                if unit == 'KiB':
                    total_mb = total / 1024
                    free_mb = free / 1024
                    used_mb = used / 1024
                elif unit == 'MiB':
                    total_mb = total
                    free_mb = free
                    used_mb = used
                elif unit == 'GiB':
                    total_mb = total * 1024
                    free_mb = free * 1024
                    used_mb = used * 1024
                else:
                    total_mb = total
                    free_mb = free
                    used_mb = used
                
                result['mem_total_mb'] = total_mb
                result['mem_free_mb'] = free_mb
                result['mem_used_mb'] = used_mb
                
                if total_mb > 0:
                    result['mem_usage'] = (used_mb / total_mb) * 100.0
            
            # 解析Swap
            swap_match = self.swap_pattern.search(line)
            if swap_match:
                unit = swap_match.group(1)
                total = float(swap_match.group(2))
                free = float(swap_match.group(3))
                used = float(swap_match.group(4))
                
                # 转换为MB
                if unit == 'KiB':
                    total_mb = total / 1024
                    used_mb = used / 1024
                elif unit == 'MiB':
                    total_mb = total
                    used_mb = used
                elif unit == 'GiB':
                    total_mb = total * 1024
                    used_mb = used * 1024
                else:
                    total_mb = total
                    used_mb = used
                
                result['swap_total_mb'] = total_mb
                result['swap_used_mb'] = used_mb
                
                if total_mb > 0:
                    result['swap_usage'] = (used_mb / total_mb) * 100.0
        
        return result
    
    def save_to_csv(self, data: List[Dict], output_path: str):
        """
        将解析结果保存为CSV文件
        
        Args:
            data: 解析后的数据列表
            output_path: 输出CSV文件路径
        """
        if not data:
            print("警告：没有数据可保存")
            return
        
        # 定义CSV字段顺序
        fieldnames = [
            'timestamp', 'ip', 'status',
            'cpu_usage', 'mem_usage', 'swap_usage',
            'mem_total_mb', 'mem_used_mb', 'mem_free_mb',
            'swap_total_mb', 'swap_used_mb',
            'load_1min', 'load_5min', 'load_15min',
            'io_wait',
            'tasks_total', 'tasks_running', 'tasks_sleeping',
            'uptime', 'users',
            'error_message'
        ]
        
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                writer.writerow(row)
        
        print(f"CSV文件已保存: {output_path}")
        print(f"共处理 {len(data)} 条记录")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n错误：请提供输入文件路径")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # 默认输出文件名
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"csv_out/{base_name}.csv"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件不存在 - {input_file}")
        sys.exit(1)
    
    print(f"开始解析文件: {input_file}")
    
    # 创建解析器
    parser = TopLogParser()
    
    try:
        # 解析日志文件
        data = parser.parse_log_file(input_file)
        
        if not data:
            print("警告：没有解析到任何数据")
            sys.exit(0)
        
        # 统计成功和失败的设备
        success_count = sum(1 for item in data if item['status'] == 'success')
        failed_count = sum(1 for item in data if item['status'] == 'failed')
        
        print(f"解析完成: 共 {len(data)} 个设备")
        print(f"  - 成功: {success_count} 个")
        print(f"  - 失败: {failed_count} 个")
        
        # 保存为CSV
        parser.save_to_csv(data, output_file)
        
        # 显示一些统计信息
        if success_count > 0:
            print("\n成功设备的统计信息:")
            cpu_avg = sum(item['cpu_usage'] for item in data if item['status'] == 'success') / success_count
            mem_avg = sum(item['mem_usage'] for item in data if item['status'] == 'success') / success_count
            print(f"  - 平均CPU使用率: {cpu_avg:.1f}%")
            print(f"  - 平均内存使用率: {mem_avg:.1f}%")
            
            # 找出CPU使用率最高的设备
            max_cpu_item = max((item for item in data if item['status'] == 'success'), 
                              key=lambda x: x['cpu_usage'], default=None)
            if max_cpu_item:
                print(f"  - 最高CPU使用率: {max_cpu_item['cpu_usage']:.1f}% (IP: {max_cpu_item['ip']})")
            
            # 找出内存使用率最高的设备
            max_mem_item = max((item for item in data if item['status'] == 'success'), 
                              key=lambda x: x['mem_usage'], default=None)
            if max_mem_item:
                print(f"  - 最高内存使用率: {max_mem_item['mem_usage']:.1f}% (IP: {max_mem_item['ip']})")
        
    except Exception as e:
        print(f"解析过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()