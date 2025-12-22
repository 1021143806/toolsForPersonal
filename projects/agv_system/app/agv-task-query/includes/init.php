<?php
/**
 * 初始化文件 - 统一引入所有公共模块
 * Initialization File - Include all common modules
 */

// 设置默认时区
date_default_timezone_set('Asia/Shanghai');

// 设置字符编码
header('Content-Type: text/html; charset=utf-8');

// 获取当前文件所在目录
$includesDir = __DIR__;

// 引入数据库连接模块
require_once $includesDir . '/db-connection.php';

// 引入SQL查询帮助模块
require_once $includesDir . '/sql-helper.php';

// 引入HTTP请求帮助模块
require_once $includesDir . '/http-helper.php';

// 引入表单输出帮助模块
require_once $includesDir . '/form-helper.php';

// 引入JSON处理帮助模块
require_once $includesDir . '/json-helper.php';

// 引入任务配置验证器模块
require_once $includesDir . '/task-validator.php';
?>