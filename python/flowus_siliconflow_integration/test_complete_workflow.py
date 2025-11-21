#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流程测试脚本
测试从数据获取到AI处理的完整流程
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.config_loader import ConfigLoader
from database.mysql_client import MySQLClient
from fetch_diary_data import DiaryDataFetcher
from process_diary_with_ai import DiaryAIProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_complete_workflow():
    """测试完整的工作流程"""
    logger.info("开始测试完整工作流程...")
    
    try:
        # 1. 初始化配置
        logger.info("步骤1: 初始化配置...")
        config_loader = ConfigLoader()
        config = config_loader.config
        
        # 2. 测试数据库连接
        logger.info("步骤2: 测试数据库连接...")
        mysql_client = MySQLClient(config)
        if not mysql_client.connect():
            logger.error("数据库连接失败")
            return False
        logger.info("数据库连接成功")
        
        # 3. 获取并处理日记数据
        logger.info("步骤3: 获取并处理日记数据...")
        fetcher = DiaryDataFetcher(config_loader)
        success = fetcher.fetch_all_data()
        
        if not success:
            logger.error("数据获取失败")
            return False
        
        # 4. 验证数据存储
        logger.info("步骤4: 验证数据存储...")
        diary_count = mysql_client.get_recent_diary_records(days=30).__len__()
        problem_count = mysql_client.get_recent_problem_records(days=30).__len__()
        project_count = mysql_client.get_recent_project_records(days=30).__len__()
        
        logger.info(f"数据验证结果:")
        logger.info(f"  - 日记记录: {diary_count} 条")
        logger.info(f"  - 问题记录: {problem_count} 条")
        logger.info(f"  - 项目记录: {project_count} 条")
        
        if diary_count == 0:
            logger.warning("没有找到日记记录，可能需要检查数据获取逻辑")
        
        # 5. 测试AI处理
        logger.info("步骤5: 测试AI处理...")
        ai_processor = DiaryAIProcessor(config_loader)
        
        # 测试不同时间范围的处理
        time_ranges = [7, 30, 90]
        for days in time_ranges:
            logger.info(f"测试 {days} 天数据范围...")
            try:
                result = ai_processor.process_with_ai(days)
                if result:
                    logger.info(f"  {days} 天数据处理成功")
                else:
                    logger.warning(f"  {days} 天数据处理失败或无数据")
            except Exception as e:
                logger.error(f"  {days} 天数据处理出错: {e}")
        
        logger.info("完整工作流程测试完成")
        return True
        
    except Exception as e:
        logger.error(f"工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_quality():
    """测试数据质量"""
    logger.info("开始数据质量测试...")
    
    try:
        config_loader = ConfigLoader()
        config = config_loader.config
        mysql_client = MySQLClient(config)
        
        # 测试时间范围过滤
        logger.info("测试时间范围过滤...")
        
        # 获取最近7天的数据
        recent_diary = mysql_client.get_recent_diary_records(days=7)
        recent_problems = mysql_client.get_recent_problem_records(days=7)
        recent_projects = mysql_client.get_recent_project_records(days=7)
        
        logger.info(f"最近7天数据:")
        logger.info(f"  - 日记: {len(recent_diary)} 条")
        logger.info(f"  - 问题: {len(recent_problems)} 条")
        logger.info(f"  - 项目: {len(recent_projects)} 条")
        
        # 检查数据完整性
        if recent_diary:
            logger.info("日记数据样本:")
            for i, diary in enumerate(recent_diary[:3]):
                logger.info(f"  {i+1}. {diary.get('date', 'N/A')} - {diary.get('category', 'N/A')}")
        
        if recent_problems:
            logger.info("问题数据样本:")
            for i, problem in enumerate(recent_problems[:3]):
                logger.info(f"  {i+1}. {problem.get('problem_title', 'N/A')} - {problem.get('status', 'N/A')}")
        
        if recent_projects:
            logger.info("项目数据样本:")
            for i, project in enumerate(recent_projects[:3]):
                logger.info(f"  {i+1}. {project.get('project_name', 'N/A')} - {project.get('status', 'N/A')}")
        
        logger.info("数据质量测试完成")
        return True
        
    except Exception as e:
        logger.error(f"数据质量测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("FlowUs 多维表数据处理 - 完整工作流程测试")
    logger.info("=" * 60)
    
    # 测试完整工作流程
    workflow_success = test_complete_workflow()
    
    # 测试数据质量
    quality_success = test_data_quality()
    
    # 输出测试结果
    logger.info("=" * 60)
    logger.info("测试结果汇总:")
    logger.info(f"  工作流程测试: {'通过' if workflow_success else '失败'}")
    logger.info(f"  数据质量测试: {'通过' if quality_success else '失败'}")
    
    if workflow_success and quality_success:
        logger.info("所有测试通过！系统可以正常使用。")
        return 0
    else:
        logger.error("部分测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)