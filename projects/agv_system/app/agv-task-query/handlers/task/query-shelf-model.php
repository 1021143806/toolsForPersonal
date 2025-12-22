<?php
/**
 * 货架模型查询功能
 * 输入：货架模型ID（如100），可选跨环境任务模板或指定服务器IP
 * 输出：货架模型配置信息
 */

require_once '../../includes/init.php';

header('Content-Type: application/json; charset=utf-8');

// 获取输入参数
$shelfModelId = $_GET['shelf_model_id'] ?? '';
$crossModel = $_GET['cross_model'] ?? '';
$serverIpsStr = $_GET['server_ips'] ?? '';

// 必须提供货架模型ID
if (empty($shelfModelId)) {
    http_response_code(400);
    echo json_encode(['error' => '需要提供 shelf_model_id 参数'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 确定要查询的服务器IP列表
$serverIps = [];
if (!empty($serverIpsStr)) {
    $serverIps = array_map('trim', explode(',', $serverIpsStr));
    $serverIps = array_filter($serverIps, function($ip) {
        return !empty($ip);
    });
} elseif (!empty($crossModel)) {
    // 根据跨环境大任务模板获取服务器IP列表
    $serverIps = getServerIpsFromCrossModel($crossModel);
} else {
    // 默认使用所有已知环境IP
    $serverIps = ['31', '32', '17'];
}

// 查询结果
$results = [];
foreach ($serverIps as $ip) {
    $conn = connectMsqlAgvWmsNoINFO($ip);
    if (!$conn) {
        $results[$ip] = ['error' => '数据库连接失败'];
        continue;
    }

    // 查询 load_config 表（根据思维导图，货架模型表可能是 load_config）
    $sql = "SELECT * FROM load_config WHERE id = " . intval($shelfModelId);
    $result = mysqli_query($conn, $sql);
    $rows = [];
    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            // 脱敏敏感字段
            unset($row['config']); // 示例
            $rows[] = $row;
        }
        if (empty($rows)) {
            $rows = ['message' => '货架模型不存在'];
        }
    } else {
        $rows = ['error' => mysqli_error($conn)];
    }
    $results[$ip] = $rows;
    mysqli_close($conn);
}

// 汇总
$response = [
    'query' => [
        'shelf_model_id' => $shelfModelId,
        'cross_model' => $crossModel,
        'server_ips' => $serverIps
    ],
    'results' => $results
];

echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

/**
 * 根据跨环境大任务模板获取服务器IP列表（复用之前的函数）
 */
function getServerIpsFromCrossModel($crossModel) {
    $conn = connectMsqlAgvWmsNoINFO('32');
    if (!$conn) {
        return [];
    }

    $ips = [];
    $sql = "SELECT id FROM fy_cross_model_process WHERE model_process_code = '" . mysqli_real_escape_string($conn, $crossModel) . "' 
            OR model_process_name = '" . mysqli_real_escape_string($conn, $crossModel) . "' 
            OR id = " . intval($crossModel);
    $result = mysqli_query($conn, $sql);
    if ($result && $row = mysqli_fetch_assoc($result)) {
        $modelId = $row['id'];
        $sql2 = "SELECT task_servicec FROM fy_cross_model_process_detail WHERE model_process_id = " . intval($modelId);
        $result2 = mysqli_query($conn, $sql2);
        while ($row2 = mysqli_fetch_assoc($result2)) {
            $url = $row2['task_servicec'];
            // 从URL中提取IP，例如 http://10.68.2.27:7000
            if (preg_match('/\d+\.\d+\.\d+\.(\d+)/', $url, $matches)) {
                $ip = $matches[1];
                if (!in_array($ip, $ips)) {
                    $ips[] = $ip;
                }
            }
        }
    }
    mysqli_close($conn);
    return $ips;
}
?>