#!/usr/bin/env python3
"""
FlowUs+SiliconFlow集成定时任务调度器
支持每日定时执行数据获取和AI处理流程
"""
import logging
import schedule
import time
import signal
import sys
import os
from datetime import datetime, timezone
import pytz
from typing import Optional
from config.config_loader import ConfigLoader

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FlowUsScheduler:
    """FlowUs定时任务调度器"""
    
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_config()
        self.scheduler_config = self.config.get('scheduler', {})
        self.running = False
        
        # 设置时区
        timezone_str = self.scheduler_config.get('timezone', 'Asia/Shanghai')
        try:
            self.timezone = pytz.timezone(timezone_str)
            logger.info(f"使用时区: {timezone_str}")
        except pytz.UnknownTimeZoneError:
            logger.warning(f"未知时区 {timezone_str}，使用默认时区 Asia/Shanghai")
            self.timezone = pytz.timezone('Asia/Shanghai')
    
    def load_main_module(self):
        """动态加载main模块"""
        try:
            # 确保在正确的目录中
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            
            from main import main_with_diagnosis
            return main_with_diagnosis
        except ImportError as e:
            logger.error(f"无法加载main模块: {e}")
            return None
    
    def execute_task(self):
        """执行定时任务"""
        logger.info("=" * 60)
        logger.info("开始执行定时任务")
        start_time = datetime.now(self.timezone)
        logger.info(f"任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查是否在周末运行
        if not self.scheduler_config.get('run_on_weekends', True):
            weekday = start_time.weekday()  # 0=Monday, 6=Sunday
            if weekday >= 5:  # Saturday=5, Sunday=6
                logger.info("周末跳过任务执行")
                return
        
        # 加载主函数
        main_func = self.load_main_module()
        if not main_func:
            logger.error("无法加载主函数，任务执行失败")
            return
        
        # 执行任务（带重试机制）
        max_retries = self.scheduler_config.get('max_retries', 3)
        retry_interval = self.scheduler_config.get('retry_interval', 300)
        timeout = self.scheduler_config.get('timeout', 3600)
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"执行尝试 {attempt + 1}/{max_retries + 1}")
                
                # 设置超时
                import threading
                result_container = {'success': False, 'error': None}
                
                def run_with_timeout():
                    try:
                        main_func()
                        result_container['success'] = True
                    except Exception as e:
                        result_container['error'] = e
                
                thread = threading.Thread(target=run_with_timeout)
                thread.daemon = True
                thread.start()
                thread.join(timeout)
                
                if thread.is_alive():
                    logger.error(f"任务执行超时（{timeout}秒）")
                    if attempt < max_retries:
                        logger.info(f"等待 {retry_interval} 秒后重试...")
                        time.sleep(retry_interval)
                        continue
                    else:
                        logger.error("任务执行失败：达到最大重试次数")
                        return
                
                if result_container['error']:
                    raise result_container['error']
                
                # 任务成功完成
                end_time = datetime.now(self.timezone)
                duration = (end_time - start_time).total_seconds()
                logger.info(f"任务执行成功，耗时: {duration:.2f} 秒")
                logger.info(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("=" * 60)
                return
                
            except Exception as e:
                logger.error(f"任务执行失败 (尝试 {attempt + 1}): {e}")
                if attempt < max_retries:
                    logger.info(f"等待 {retry_interval} 秒后重试...")
                    time.sleep(retry_interval)
                else:
                    logger.error("任务执行失败：达到最大重试次数")
                    end_time = datetime.now(self.timezone)
                    logger.info(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info("=" * 60)
    
    def setup_schedule(self):
        """设置定时任务"""
        if not self.scheduler_config.get('enabled', False):
            logger.info("定时任务已禁用")
            return
        
        schedule_time = self.scheduler_config.get('time', '08:00')
        logger.info(f"设置每日定时任务: {schedule_time}")
        
        # 验证时间格式
        try:
            hour, minute = map(int, schedule_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("时间格式错误")
        except ValueError:
            logger.error(f"无效的时间格式: {schedule_time}，使用默认时间 08:00")
            schedule_time = '08:00'
        
        # 设置每日任务
        schedule.every().day.at(schedule_time).do(self.execute_task)
        logger.info(f"定时任务已设置: 每日 {schedule_time} 执行")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，准备停止调度器...")
        self.running = False
    
    def run(self):
        """运行调度器"""
        logger.info("启动FlowUs定时任务调度器")
        
        # 检查配置
        if not self.scheduler_config.get('enabled', False):
            logger.warning("定时任务未启用，请检查config.toml中的[scheduler]配置")
            return
        
        # 设置信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 设置定时任务
        self.setup_schedule()
        
        # 显示下次执行时间
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.running = True
        logger.info("调度器已启动，按 Ctrl+C 停止")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止调度器...")
        finally:
            self.running = False
            logger.info("调度器已停止")
    
    def run_once(self):
        """立即执行一次任务（用于测试）"""
        logger.info("立即执行模式")
        self.execute_task()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FlowUs定时任务调度器')
    parser.add_argument('--run-once', action='store_true', 
                       help='立即执行一次任务（用于测试）')
    parser.add_argument('--test-config', action='store_true',
                       help='测试配置文件')
    
    args = parser.parse_args()
    
    scheduler = FlowUsScheduler()
    
    if args.test_config:
        # 测试配置
        logger.info("=== 配置测试 ===")
        logger.info(f"定时任务启用: {scheduler.scheduler_config.get('enabled', False)}")
        logger.info(f"执行时间: {scheduler.scheduler_config.get('time', '08:00')}")
        logger.info(f"时区: {scheduler.scheduler_config.get('timezone', 'Asia/Shanghai')}")
        logger.info(f"最大重试次数: {scheduler.scheduler_config.get('max_retries', 3)}")
        logger.info(f"重试间隔: {scheduler.scheduler_config.get('retry_interval', 300)}秒")
        logger.info(f"周末执行: {scheduler.scheduler_config.get('run_on_weekends', True)}")
        logger.info(f"超时时间: {scheduler.scheduler_config.get('timeout', 3600)}秒")
        return
    
    if args.run_once:
        scheduler.run_once()
    else:
        scheduler.run()

if __name__ == "__main__":
    main()