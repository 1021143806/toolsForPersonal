<?php
/**
 * AGV任务配置验证API端点
 * 接收GET或POST请求，验证指定任务的配置完整性
 * 安全要求：API密钥验证、数据脱敏
 */

require_once '../../includes/init.php';

// 设置响应头为JSON
header('Content-Type: application/json; charset=utf-8');

// 默认响应
$response = [
    'code' => 400,
    'message' => 'Invalid request',
    'data' => null
];

// 安全配置（在实际环境中应从环境变量或配置文件中读取）
define('API_KEY', 'agv_validation_2025_key'); // 示例密钥，请在生产环境中更改

/**
 * 验证API密钥
 */
function validateApiKey() {
    // 从Authorization头获取
    $headers = getallheaders();
    $authHeader = $headers['Authorization'] ?? $headers['authorization'] ?? '';
    if (strpos($authHeader, 'Bearer ') === 0) {
        $providedKey = substr($authHeader, 7);
    } else {
        // 从查询参数获取
        $providedKey = $_GET['api_key'] ?? $_POST['api_key'] ?? '';
    }
    return $providedKey === API_KEY;
}

// 检查API密钥
if (!validateApiKey()) {
    $response['code'] = 401;
    $response['message'] = 'Unauthorized: Invalid or missing API key';
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

// 获取请求参数
$taskId = $_GET['taskId'] ?? $_POST['taskId'] ?? null;
$taskName = $_GET['taskName'] ?? $_POST['taskName'] ?? null;
$envList = $_GET['environments'] ?? $_POST['environments'] ?? '';
$strictMode = $_GET['strict'] ?? $_POST['strict'] ?? 'true';
$identifierType = 'code'; // 默认按任务代码标识

// 确定任务标识符
$taskIdentifier = null;
if (!empty($taskId)) {
    $taskIdentifier = $taskId;
    $identifierType = 'id';
} elseif (!empty($taskName)) {
    $taskIdentifier = $taskName;
    $identifierType = 'name';
} else {
    // 尝试从任务代码获取
    $taskIdentifier = $_GET['taskCode'] ?? $_POST['taskCode'] ?? null;
    if (empty($taskIdentifier)) {
        $response['message'] = 'Missing task identifier (taskId, taskName, or taskCode)';
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }
}

// 解析环境列表
$environments = [];
if (!empty($envList)) {
    $environments = array_map('trim', explode(',', $envList));
    // 过滤无效IP
    $environments = array_filter($environments, function($ip) {
        return filter_var($ip, FILTER_VALIDATE_IP) || preg_match('/^10\.68\.2\.\d+$/', $ip);
    });
} else {
    // 默认环境
    $environments = ['10.68.2.31', '10.68.2.32', '10.68.2.17'];
}

// 验证模式
$strict = strtolower($strictMode) === 'true' || $strictMode === '1';

try {
    // 连接数据库（使用默认连接）
    global $conn;
    if (!$conn) {
        // 如果没有全局连接，则连接到跨环境数据库（默认IP）
        $conn = connectMsqlAgvWmsNoINFO("32");
    }

    // 创建验证器并执行验证
    $validator = new TaskConfigurationValidator($conn);
    $validator->setEnvironmentIps($environments);
    $validator->setStrictMode($strict);
    $report = $validator->validateTask($taskIdentifier, $identifierType);

    // 脱敏处理（移除敏感信息）
    $report = sanitizeReport($report);

    $response['code'] = 200;
    $response['message'] = 'Validation completed';
    $response['data'] = $report;

} catch (Exception $e) {
    $response['code'] = 500;
    $response['message'] = 'Validation error: ' . $e->getMessage();
    // 生产环境中不应返回详细错误信息，这里只返回通用错误
    // 如果需要调试，可以启用以下行
    // $response['data'] = ['trace' => $e->getTraceAsString()];
}

// 输出JSON响应
echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

/**
 * 脱敏验证报告（移除敏感信息如密码、密钥等）
 */
function sanitizeReport($report) {
    // 递归清理数组中的敏感字段
    $sensitiveKeys = ['password', 'pass', 'secret', 'key', 'token', 'auth', 'credential', 'private'];
    array_walk_recursive($report, function(&$value, $key) use ($sensitiveKeys) {
        foreach ($sensitiveKeys as $sensitive) {
            if (stripos($key, $sensitive) !== false) {
                $value = '***REDACTED***';
                break;
            }
        }
    });
    // 移除数据库连接信息
    unset($report['db_host'], $report['db_user'], $report['db_pass']);
    return $report;
}
?>