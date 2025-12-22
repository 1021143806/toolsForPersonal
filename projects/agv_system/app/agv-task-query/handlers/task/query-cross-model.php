<?php
/**
 * 跨环境任务模板相关配置验证
 * 输入：大任务模板id、编号或名称（三选一）
 * 输出：fy_cross_model_process 和 fy_cross_model_process_detail 表查询内容
 * 不要校验，不要API密钥
 */

require_once '../../includes/init.php';

header('Content-Type: application/json; charset=utf-8');

// 获取输入参数
$identifier = $_GET['identifier'] ?? '';
$id = $_GET['id'] ?? '';
$code = $_GET['code'] ?? '';
$name = $_GET['name'] ?? '';

// 确定使用哪个标识符
$usedIdentifier = null;
$type = 'unknown';

if (!empty($id) && is_numeric($id)) {
    $usedIdentifier = intval($id);
    $type = 'id';
} elseif (!empty($code)) {
    $usedIdentifier = trim($code);
    $type = 'code';
} elseif (!empty($name)) {
    $usedIdentifier = trim($name);
    $type = 'name';
} elseif (!empty($identifier)) {
    // 尝试自动判断类型
    if (is_numeric($identifier)) {
        $usedIdentifier = intval($identifier);
        $type = 'id';
    } else {
        // 假设是编号或名称，优先按编号查询
        $usedIdentifier = trim($identifier);
        $type = 'code';
    }
} else {
    http_response_code(400);
    echo json_encode(['error' => '缺少标识符参数，请提供 id、code、name 或 identifier'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 连接跨环境数据库（默认使用IP后缀32）
$conn = connectMsqlAgvWmsNoINFO('32');
if (!$conn) {
    http_response_code(500);
    echo json_encode(['error' => '数据库连接失败'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 查询主表 fy_cross_model_process
$where = '';
switch ($type) {
    case 'id':
        $where = "id = " . intval($usedIdentifier);
        break;
    case 'code':
        $where = "model_process_code = '" . mysqli_real_escape_string($conn, $usedIdentifier) . "'";
        break;
    case 'name':
        $where = "model_process_name = '" . mysqli_real_escape_string($conn, $usedIdentifier) . "'";
        break;
}

$sql = "SELECT * FROM fy_cross_model_process WHERE $where LIMIT 1";
$result = mysqli_query($conn, $sql);
if (!$result) {
    http_response_code(500);
    echo json_encode(['error' => '查询主表失败: ' . mysqli_error($conn)], JSON_UNESCAPED_UNICODE);
    mysqli_close($conn);
    exit;
}

$mainRecord = mysqli_fetch_assoc($result);
if (!$mainRecord) {
    http_response_code(404);
    echo json_encode(['error' => '未找到匹配的任务模板'], JSON_UNESCAPED_UNICODE);
    mysqli_close($conn);
    exit;
}

$modelId = $mainRecord['id'];

// 查询子表 fy_cross_model_process_detail
$sql2 = "SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = " . intval($modelId);
$result2 = mysqli_query($conn, $sql2);
$detailRecords = [];
if ($result2) {
    while ($row = mysqli_fetch_assoc($result2)) {
        $detailRecords[] = $row;
    }
} else {
    $detailRecords = ['error' => mysqli_error($conn)];
}

// 构建响应
$response = [
    'query' => [
        'identifier' => $usedIdentifier,
        'type' => $type,
        'model_id' => $modelId
    ],
    'main_table' => $mainRecord,
    'detail_table' => $detailRecords
];

echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

mysqli_close($conn);
?>