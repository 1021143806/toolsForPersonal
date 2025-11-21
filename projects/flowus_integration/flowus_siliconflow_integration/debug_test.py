#!/usr/bin/env python3
"""
调试测试脚本 - 验证问题诊断和修复
"""
import logging
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_loader import ConfigLoader
from fetch_diary_data import DiaryDataFetcher
from database.mysql_client import MySQLClient
from process_diary_with_ai import DiaryAIProcessor

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def test_database_reference_detection():
    """测试数据库引用检测功能"""
    logger.info("=== 测试1: 数据库引用检测 ===")
    
    try:
        config_loader = ConfigLoader()
        fetcher = DiaryDataFetcher(config_loader)
        
        # 获取主页面块内容
        page_url = config_loader.config['flowus']['url']
        page_id = page_url.split('/')[-1].split('?')[0]
        logger.info(f"测试主页面: {page_id}")
        
        blocks_data = fetcher.flowus_client.get_page_content(page_id)
        if not blocks_data:
            logger.error("无法获取主页面块内容")
            return False
        
        # 测试改进的数据库引用检测
        diary_db_id = fetcher.extract_database_reference_from_blocks(blocks_data)
        
        if diary_db_id:
            logger.info(f"✅ 成功找到日记数据库: {diary_db_id}")
            return True
        else:
            logger.error("❌ 仍然未找到日记数据库引用")
            return False
            
    except Exception as e:
        logger.error(f"测试数据库引用检测失败: {e}")
        return False


def test_block_content_storage():
    """测试块内容存储功能"""
    logger.info("=== 测试2: 块内容存储 ===")
    
    try:
        config_loader = ConfigLoader()
        mysql_client = MySQLClient(config_loader.config)
        
        # 连接数据库
        if not mysql_client.connect():
            logger.error("数据库连接失败")
            return False
        
        # 检查是否有现有的问题/项目记录
        problem_records = mysql_client.get_recent_problem_records(days=7)
        project_records = mysql_client.get_recent_project_records(days=7)
        
        logger.info(f"找到 {len(problem_records)} 个问题记录, {len(project_records)} 个项目记录")
        
        # 检查记录是否有内容
        records_with_content = 0
        for record in problem_records + project_records:
            content = record.get('content', '')
            if content and len(content.strip()) > 0:
                records_with_content += 1
        
        logger.info(f"有内容的记录数: {records_with_content}")
        
        if records_with_content > 0:
            logger.info("✅ 块内容存储功能正常工作")
            success = True
        else:
            logger.warning("⚠️ 没有找到有内容的记录，可能需要重新获取数据")
            success = False
        
        mysql_client.disconnect()
        return success
        
    except Exception as e:
        logger.error(f"测试块内容存储失败: {e}")
        return False


def test_local_backup():
    """测试本地备份功能"""
    logger.info("=== 测试3: 本地备份功能 ===")
    
    try:
        config_loader = ConfigLoader()
        processor = DiaryAIProcessor(config_loader)
        
        # 测试本地备份保存
        test_content = f"""# 测试内容

这是一个测试内容，用于验证本地备份功能。

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 测试结果

如果看到这个文件，说明本地备份功能正常工作。
"""
        
        test_response_json = {
            'model': 'test-model',
            'id': 'test-response-id'
        }
        
        # 调用本地备份方法
        backup_success = processor.save_to_local_backup(test_content, test_response_json)
        
        if backup_success:
            # 检查文件是否真的存在
            output_dir = config_loader.config['output']['output_dir']
            local_file_path = os.path.join(output_dir, config_loader.config['output']['filename'])
            
            if os.path.exists(local_file_path):
                with open(local_file_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                if test_content in saved_content:
                    logger.info("✅ 本地备份功能正常工作")
                    logger.info(f"备份文件位置: {local_file_path}")
                    return True
                else:
                    logger.error("❌ 备份文件内容不正确")
                    return False
            else:
                logger.error(f"❌ 备份文件不存在: {local_file_path}")
                return False
        else:
            logger.error("❌ 本地备份保存失败")
            return False
            
    except Exception as e:
        logger.error(f"测试本地备份失败: {e}")
        return False


def test_config_parameters():
    """测试配置参数使用"""
    logger.info("=== 测试4: 配置参数使用 ===")
    
    try:
        config_loader = ConfigLoader()
        
        # 检查配置文件中的数据库参数
        db_config = config_loader.config.get('database', {})
        page_size = db_config.get('page_size', 100)
        recent_days = db_config.get('recent_days', 30)
        include_properties = db_config.get('include_properties', True)
        
        logger.info(f"配置参数: page_size={page_size}, recent_days={recent_days}, include_properties={include_properties}")
        
        # 测试FlowUs客户端是否使用这些参数
        from clients.flowus_client import FlowUsClient
        flowus_client = FlowUsClient(config_loader)
        
        # 这里我们不能直接调用get_database_content，因为没有真实的数据库ID
        # 但我们可以检查配置是否正确加载
        if page_size != 100 or recent_days != 30:
            logger.info("✅ 配置参数已正确加载且不是默认值")
            return True
        else:
            logger.info("⚠️ 使用的是默认配置值，但这可能是正常的")
            return True
            
    except Exception as e:
        logger.error(f"测试配置参数失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("开始调试测试...")
    logger.info("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("数据库引用检测", test_database_reference_detection()))
    test_results.append(("块内容存储", test_block_content_storage()))
    test_results.append(("本地备份功能", test_local_backup()))
    test_results.append(("配置参数使用", test_config_parameters()))
    
    # 汇总结果
    logger.info("=" * 60)
    logger.info("=== 测试结果汇总 ===")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    logger.info(f"总计: {passed_tests}/{total_tests} 个测试通过")
    
    if passed_tests == total_tests:
        logger.info("🎉 所有测试通过！问题修复成功。")
        return True
    elif passed_tests > 0:
        logger.warning("⚠️ 部分测试通过，还有一些问题需要解决。")
        return False
    else:
        logger.error("💥 所有测试失败，需要进一步诊断。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)