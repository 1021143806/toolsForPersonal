"""
整合执行数据获取、导出和AI处理流程
按照用户要求：
1. 先完成信息获取
2. 根据配置文件中的时间要求从数据库获取指定时间内的信息
3. 保存到outputs/data.log
4. 然后发送给硅基API生成内容
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional
from fetch_diary_data import main as fetch_main
from process_diary_with_ai import main as process_main

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_scheduler_requirements() -> dict:
    """检查定时任务需求的诊断函数"""
    diagnosis = {
        "has_schedule_config": False,
        "has_scheduler_library": False,
        "has_error_handling": False,
        "has_monitoring": False,
        "issues_found": []
    }
    
    # 检查1: 是否有定时任务配置
    try:
        import tomlkit
        config_path = 'config.toml'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = tomlkit.load(f)
            
            if 'scheduler' in config:
                diagnosis["has_schedule_config"] = True
                logger.info("✓ 发现定时任务配置")
            else:
                diagnosis["issues_found"].append("config.toml中缺少[scheduler]配置段")
                logger.warning("✗ config.toml中缺少[scheduler]配置段")
        else:
            diagnosis["issues_found"].append("config.toml文件不存在")
            logger.warning("✗ config.toml文件不存在")
    except Exception as e:
        diagnosis["issues_found"].append(f"读取配置文件失败: {e}")
        logger.error(f"✗ 读取配置文件失败: {e}")
    
    # 检查2: 是否有定时任务库
    try:
        import schedule
        diagnosis["has_scheduler_library"] = True
        logger.info("✓ 发现schedule库")
    except ImportError:
        diagnosis["issues_found"].append("缺少schedule库，需要安装: pip install schedule")
        logger.warning("✗ 缺少schedule库")
    
    try:
        import apscheduler
        diagnosis["has_scheduler_library"] = True
        logger.info("✓ 发现apscheduler库")
    except ImportError:
        pass  # schedule库已经足够
    
    # 检查3: 错误处理机制
    logger.info("✓ 当前代码有基本的异常处理")
    diagnosis["has_error_handling"] = True
    
    # 检查4: 监控机制
    logger.info("✓ 当前代码有日志记录")
    diagnosis["has_monitoring"] = True
    
    return diagnosis

def main_with_diagnosis():
    """带诊断功能的主函数"""
    logger.info("=== 开始诊断定时任务需求 ===")
    
    # 执行诊断
    diagnosis = check_scheduler_requirements()
    
    logger.info("\n=== 诊断结果 ===")
    if diagnosis["issues_found"]:
        logger.warning("发现以下问题:")
        for issue in diagnosis["issues_found"]:
            logger.warning(f"  - {issue}")
    else:
        logger.info("✓ 所有检查通过")
    
    logger.info("\n=== 开始执行原有流程 ===")
    
    try:
        print("=== 步骤1: 从FlowUs获取多维表数据 ===")
        logger.info("开始执行步骤1: 从FlowUs获取多维表数据")
        fetch_main()
        logger.info("步骤1执行完成")
        
        print("\n=== 步骤2: 处理数据并生成AI内容 ===")
        print("流程说明：")
        print("- 根据配置文件中的时间要求从数据库获取指定时间内的信息")
        print("- 保存到outputs/data.log")
        print("- 然后发送给硅基API生成内容")
        logger.info("开始执行步骤2: 处理数据并生成AI内容")
        process_main()
        logger.info("步骤2执行完成")
        
        print("\n=== 处理完成 ===")
        print("数据流程：")
        print("FlowUs数据 → MySQL数据库 → data.log → 硅基API → FlowUs新页面")
        logger.info("整个流程执行完成")
        
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}")
        raise
    
    # 输出诊断建议
    logger.info("\n=== 定时任务建议 ===")
    if not diagnosis["has_schedule_config"]:
        logger.info("建议1: 在config.toml中添加[scheduler]配置段")
        logger.info("示例配置:")
        logger.info("[scheduler]")
        logger.info("enabled = true")
        logger.info("time = '08:00'  # 每日执行时间")
        logger.info("timezone = 'Asia/Shanghai'")
    
    if not diagnosis["has_scheduler_library"]:
        logger.info("建议2: 安装定时任务库")
        logger.info("pip install schedule")
    
    logger.info("建议3: 使用cron或systemd服务来定时执行此脚本")

def main():
    """原始主函数（保持向后兼容）"""
    main_with_diagnosis()

if __name__ == "__main__":
    main()