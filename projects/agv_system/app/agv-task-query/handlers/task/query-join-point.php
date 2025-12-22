<?php
/**
 * 交接点查询功能
 * 输入：要查询的点位（交接点ID或二维码内容），可选跨环境任务模板或指定服务器IP
 * 输出：交接点配置信息
 */

require_once '../../includes/init.php';

header('Content-Type: application/json; charset=utf-8');

// 获取输入参数
$joinPointId = $_GET['join_point_id'] ?? '';
$qrContent = $_GET['qr_content'] ?? '';
$crossModel = $_GET['cross_model'] ?? '';
$serverIpsStr = $_GET['server_ips'] ?? '';

// 至少需要一个查询条件
if (empty($joinPointId) && empty($qrContent)) {
    http_response_code(400);
    echo json_encode(['error' => '需要提供 join_point_id 或 qr_content 参数'], JSON_UNESCAPED_UNICODE);
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

    // 构建查询条件
    $where = [];
    if (!empty($joinPointId)) {
        $where[] = "id = " . intval($joinPointId);
    }
    if (!empty($qrContent)) {
        $where[] = "qr_content LIKE '%" . mysqli_real_escape_string($conn, $qrContent) . "%'";
    }
    $sql = "SELECT * FROM join_qr_node_info";
    if (!empty($where)) {
        $sql .= " WHERE " . implode(' OR ', $where);
    }
    $sql .= " LIMIT 50";

    $result = mysqli_query($conn, $sql);
    $rows = [];
    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            // 脱敏敏感字段（如果有）
            unset($row['other_config']); // 示例：移除可能敏感的配置
            $rows[] = $row;
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
        'join_point_id' => $joinPointId,
        'qr_content' => $qrContent,
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
