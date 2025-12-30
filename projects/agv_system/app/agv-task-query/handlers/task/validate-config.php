<?php
/**
 * AGV任务配置查询API端点
 * 接收GET或POST请求，查询指定任务的配置内容（可视化展示）
 * 根据思维导图，输出 fy_cross_model_process 和 fy_cross_model_process_detail 表的查询内容
 * 不需要API密钥，不需要校验
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

// 获取请求参数
$taskId = $_GET['taskId'] ?? $_POST['taskId'] ?? null;
$taskCode = $_GET['taskCode'] ?? $_POST['taskCode'] ?? null;
$taskName = $_GET['taskName'] ?? $_POST['taskName'] ?? null;
$envList = $_GET['environments'] ?? $_POST['environments'] ?? '';
$strictMode = $_GET['strict'] ?? $_POST['strict'] ?? 'false';

// 确定任务标识符
$taskIdentifier = null;
$identifierType = null;
if (!empty($taskId)) {
    $taskIdentifier = $taskId;
    $identifierType = 'id';
} elseif (!empty($taskCode)) {
    $taskIdentifier = $taskCode;
    $identifierType = 'code';
} elseif (!empty($taskName)) {
    $taskIdentifier = $taskName;
    $identifierType = 'name';
} else {
    $response['message'] = 'Missing task identifier (taskId, taskCode, or taskName)';
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;
}

// 解析环境列表（可选，用于检查子任务涉及的环境）
$environments = [];
if (!empty($envList)) {
    $environments = array_map('trim', explode(',', $envList));
    // 过滤无效IP
    $environments = array_filter($environments, function($ip) {
        return filter_var($ip, FILTER_VALIDATE_IP) || preg_match('/^10\.68\.2\.\d+$/', $ip);
    });
}

// 验证模式（宽松模式仅检查核心字段）
$strict = strtolower($strictMode) === 'true' || $strictMode === '1';

try {
    // 连接到固定服务器 10.68.2.32（跨环境大模板所在服务器）
    $conn = connectMsqlAgvWmsNoINFO("32");
    if (!$conn) {
        throw new Exception('无法连接到跨环境数据库服务器 (10.68.2.32)');
    }

    // 查询任务模板
    $taskTemplate = fetchTaskTemplate($conn, $taskIdentifier, $identifierType);
    if (!$taskTemplate) {
        $response['code'] = 404;
        $response['message'] = '任务模板不存在';
        $response['data'] = [
            'task_identifier' => $taskIdentifier,
            'identifier_type' => $identifierType,
            'missing' => true,
            'suggestion' => '请检查任务标识符是否正确，或确认任务模板是否已创建'
        ];
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }

    // 查询子任务模板
    $subTasks = fetchSubTasks($conn, $taskTemplate['id']);

    // 提取子任务中涉及的所有服务器IP（用于跨环境检查）
    $serverIps = extractServerIpsFromSubTasks($subTasks);
    // 如果用户提供了环境列表，则使用用户提供的环境，否则使用提取的服务器IP
    $checkEnvironments = !empty($environments) ? $environments : $serverIps;
    // 如果仍然为空，则使用默认环境
    if (empty($checkEnvironments)) {
        $checkEnvironments = ['31', '32', '17'];
    }

    // 对每个环境进行检查（可选，根据strict模式决定是否检查）
    $environmentChecks = [];
    if ($strict) {
        foreach ($checkEnvironments as $envIp) {
            $envCheck = checkEnvironmentConfig($envIp, $taskTemplate, $subTasks);
            $environmentChecks[$envIp] = $envCheck;
        }
    }

    // 构建响应数据
    $report = [
        'task_identifier' => $taskIdentifier,
        'identifier_type' => $identifierType,
        'task_template' => $taskTemplate,
        'sub_tasks' => $subTasks,
        'extracted_server_ips' => $serverIps,
        'environments_checked' => $checkEnvironments,
        'strict_mode' => $strict,
        'environment_checks' => $environmentChecks,
        'missing_configs' => [],
        'suggestions' => []
    ];

    // 检查必填字段（仅提示，不阻止返回）
    $missing = checkRequiredFields($taskTemplate, $subTasks);
    if (!empty($missing)) {
        $report['missing_configs'] = $missing;
        $report['suggestions'][] = '任务模板或子任务缺少必填字段，请补充配置。';
    }

    $response['code'] = 200;
    $response['message'] = '查询成功';
    $response['data'] = $report;

    mysqli_close($conn);

} catch (Exception $e) {
    $response['code'] = 500;
    $response['message'] = '查询错误: ' . $e->getMessage();
}

// 输出JSON响应
echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

/**
 * 查询任务模板
 */
function fetchTaskTemplate($conn, $identifier, $type) {
    $table = 'fy_cross_model_process';
    $field = $type === 'id' ? 'id' : ($type === 'name' ? 'model_process_name' : 'model_process_code');
    $sql = "SELECT * FROM $table WHERE $field = '" . mysqli_real_escape_string($conn, $identifier) . "' LIMIT 1";
    $result = mysqli_query($conn, $sql);
    if ($result && $row = mysqli_fetch_assoc($result)) {
        return $row;
    }
    return null;
}

/**
 * 查询子任务模板
 */
function fetchSubTasks($conn, $modelProcessId) {
    $sql = "SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = " . intval($modelProcessId) . " ORDER BY task_seq ASC";
    $result = mysqli_query($conn, $sql);
    $subTasks = [];
    while ($row = mysqli_fetch_assoc($result)) {
        $subTasks[] = $row;
    }
    return $subTasks;
}

/**
 * 从子任务中提取服务器IP（从task_servicec字段）
 */
function extractServerIpsFromSubTasks($subTasks) {
    $ips = [];
    foreach ($subTasks as $subTask) {
        $url = $subTask['task_servicec'] ?? '';
        if (preg_match('/\d+\.\d+\.\d+\.(\d+)/', $url, $matches)) {
            $ip = $matches[1];
            if (!in_array($ip, $ips)) {
                $ips[] = $ip;
            }
        }
    }
    return $ips;
}

/**
 * 检查环境配置（设备、交接点、货架等）
 */
function checkEnvironmentConfig($envIp, $taskTemplate, $subTasks) {
    $conn = connectMsqlAgvWmsNoINFO($envIp);
    if (!$conn) {
        return [
            'status' => 'fail',
            'message' => '无法连接数据库',
            'details' => []
        ];
    }

    $checks = [];

    // 检查设备表是否存在
    $sql = "SELECT COUNT(*) as cnt FROM agv_robot";
    $result = mysqli_query($conn, $sql);
    if ($result) {
        $row = mysqli_fetch_assoc($result);
        $checks['agv_robot'] = $row['cnt'] > 0 ? '存在' : '空表';
    } else {
        $checks['agv_robot'] = '表不存在';
    }

    // 检查交接点表
    $sql = "SELECT COUNT(*) as cnt FROM join_qr_node_info";
    $result = mysqli_query($conn, $sql);
    if ($result) {
        $row = mysqli_fetch_assoc($result);
        $checks['join_qr_node_info'] = $row['cnt'] > 0 ? '存在' : '空表';
    } else {
        $checks['join_qr_node_info'] = '表不存在';
    }

    // 检查货架配置表
    $sql = "SELECT COUNT(*) as cnt FROM shelf_config";
    $result = mysqli_query($conn, $sql);
    if ($result) {
        $row = mysqli_fetch_assoc($result);
        $checks['shelf_config'] = $row['cnt'] > 0 ? '存在' : '空表';
    } else {
        $checks['shelf_config'] = '表不存在';
    }

    mysqli_close($conn);

    return [
        'status' => 'pass',
        'message' => '环境配置检查完成',
        'details' => $checks
    ];
}

/**
 * 检查必填字段
 */
function checkRequiredFields($taskTemplate, $subTasks) {
    $missing = [];

    // 任务模板必填字段（根据思维导图）
    $requiredTemplateFields = ['model_process_code', 'model_process_name', 'enable', 'capacity'];
    foreach ($requiredTemplateFields as $field) {
        if (!isset($taskTemplate[$field]) || $taskTemplate[$field] === '' || $taskTemplate[$field] === null) {
            $missing[] = "任务模板字段缺失: $field";
        }
    }

    // 子任务必填字段
    $requiredSubTaskFields = ['model_process_id', 'task_seq', 'task_servicec', 'template_code'];
    foreach ($subTasks as $index => $subTask) {
        foreach ($requiredSubTaskFields as $field) {
            if (!isset($subTask[$field]) || $subTask[$field] === '' || $subTask[$field] === null) {
                $missing[] = "子任务{$index}字段缺失: $field";
            }
        }
    }

    return $missing;
}
?>
