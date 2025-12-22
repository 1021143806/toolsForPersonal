<?php
/**
 * 货架查询功能
 * 输入：货架编号（单个货架如HX001，多个货架如HX001-HX010），可选跨环境任务模板或指定服务器IP
 * 输出：货架配置信息，校验shelf_type一致性
 */

require_once '../../includes/init.php';

header('Content-Type: application/json; charset=utf-8');

// 获取输入参数
$shelfCodesStr = $_GET['shelf_codes'] ?? '';
$crossModel = $_GET['cross_model'] ?? '';
$serverIpsStr = $_GET['server_ips'] ?? '';

// 必须提供货架编号
if (empty($shelfCodesStr)) {
    http_response_code(400);
    echo json_encode(['error' => '需要提供 shelf_codes 参数'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 解析货架编号，支持范围如 HX001-HX010
$shelfCodes = parseShelfCodes($shelfCodesStr);

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
$shelfTypeConsistency = true;
$inconsistentShelves = [];

foreach ($serverIps as $ip) {
    $conn = connectMsqlAgvWmsNoINFO($ip);
    if (!$conn) {
        $results[$ip] = ['error' => '数据库连接失败'];
        continue;
    }

    // 查询 shelf_config 表
    $placeholders = "'" . implode("','", array_map('mysqli_real_escape_string', array_fill(0, count($shelfCodes), $conn), $shelfCodes)) . "'";
    $sql = "SELECT shelf_code, shelf_type, area_id, enable FROM shelf_config WHERE shelf_code IN ($placeholders)";
    $result = mysqli_query($conn, $sql);
    $rows = [];
    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            $rows[] = $row;
        }
        if (empty($rows)) {
            $rows = ['message' => '无匹配货架'];
        } else {
            // 记录shelf_type用于跨环境一致性检查
            foreach ($rows as $row) {
                $shelfCode = $row['shelf_code'];
                $shelfType = $row['shelf_type'];
                if (!isset($shelfTypeMap[$shelfCode])) {
                    $shelfTypeMap[$shelfCode] = [];
                }
                $shelfTypeMap[$shelfCode][$ip] = $shelfType;
            }
        }
    } else {
        $rows = ['error' => mysqli_error($conn)];
    }
    $results[$ip] = $rows;
    mysqli_close($conn);
}

// 检查shelf_type跨环境一致性
if (isset($shelfTypeMap)) {
    foreach ($shelfTypeMap as $shelfCode => $typePerIp) {
        $uniqueTypes = array_unique($typePerIp);
        if (count($uniqueTypes) > 1) {
            $shelfTypeConsistency = false;
            $inconsistentShelves[] = [
                'shelf_code' => $shelfCode,
                'types' => $typePerIp
            ];
        }
    }
}

// 汇总
$response = [
    'query' => [
        'shelf_codes' => $shelfCodes,
        'cross_model' => $crossModel,
        'server_ips' => $serverIps
    ],
    'results' => $results,
    'consistency_check' => [
        'consistent' => $shelfTypeConsistency,
        'inconsistent_shelves' => $inconsistentShelves
    ],
    'suggestions' => $shelfTypeConsistency ? [] : ['存在货架类型不一致，请检查配置。']
];

echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

/**
 * 解析货架编号字符串，支持范围扩展
 */
function parseShelfCodes($str) {
    $codes = [];
    // 按逗号分割
    $parts = explode(',', $str);
    foreach ($parts as $part) {
        $part = trim($part);
        if (strpos($part, '-') !== false) {
            // 处理范围如 HX001-HX010
            list($start, $end) = explode('-', $part, 2);
            if (preg_match('/^([A-Za-z]+)(\d+)$/', $start, $matchesStart) &&
                preg_match('/^([A-Za-z]+)(\d+)$/', $end, $matchesEnd)) {
                $prefix = $matchesStart[1];
                $startNum = intval($matchesStart[2]);
                $endNum = intval($matchesEnd[2]);
                if ($prefix === $matchesEnd[1]) {
                    for ($i = $startNum; $i <= $endNum; $i++) {
                        $codes[] = $prefix . str_pad($i, strlen($matchesStart[2]), '0', STR_PAD_LEFT);
                    }
                } else {
                    // 前缀不同，直接添加原始字符串
                    $codes[] = $part;
                }
            } else {
                $codes[] = $part;
            }
        } else {
            $codes[] = $part;
        }
    }
    return $codes;
}

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