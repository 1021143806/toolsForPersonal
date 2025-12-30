<?php
/**
 * 跨环境设备序列号相关配置查询
 * 输入：设备序列号（逗号分隔），可选跨环境大任务模板或指定服务器IP地址
 * 输出：查询到的设备配置详情，包括各环境中的存在情况、缺失项，可视化展示
 * 不需要校验，不需要API密钥
 */

require_once '../../includes/init.php';

header('Content-Type: application/json; charset=utf-8');

// 获取输入参数
$deviceCodesStr = $_GET['device_codes'] ?? '';
$crossModel = $_GET['cross_model'] ?? '';
$serverIpsStr = $_GET['server_ips'] ?? '';
$strict = ($_GET['strict'] ?? 'false') === 'true'; // 严格模式：检查所有表

// 验证必要参数
if (empty($deviceCodesStr)) {
    http_response_code(400);
    echo json_encode(['error' => '缺少必要参数 device_codes'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 解析设备序列号
$deviceCodes = array_map('trim', explode(',', $deviceCodesStr));
$deviceCodes = array_filter($deviceCodes, function($code) {
    return !empty($code);
});

if (empty($deviceCodes)) {
    http_response_code(400);
    echo json_encode(['error' => '设备序列号列表为空'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 确定要检查的服务器IP列表
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

// 查询报告
$report = [
    'device_codes' => $deviceCodes,
    'cross_model' => $crossModel,
    'server_ips' => $serverIps,
    'strict_mode' => $strict,
    'overall_status' => 'complete', // 改为 complete/incomplete 而非 pass/fail
    'environment_checks' => [],
    'missing_configs' => [],
    'suggestions' => []
];

// 对每个服务器IP进行检查
foreach ($serverIps as $ip) {
    $envReport = queryDevicesInEnvironment($ip, $deviceCodes, $strict);
    $report['environment_checks'][$ip] = $envReport;
    if ($envReport['status'] === 'incomplete') {
        $report['overall_status'] = 'incomplete';
        $report['missing_configs'] = array_merge($report['missing_configs'], $envReport['missing']);
    }
}

// 生成建议
if ($report['overall_status'] === 'incomplete') {
    $report['suggestions'][] = '部分设备配置缺失，请根据缺失项补充相应配置。';
} else {
    $report['suggestions'][] = '所有设备配置完整，跨环境一致性良好。';
}

echo json_encode($report, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

/**
 * 根据跨环境大任务模板获取服务器IP列表
 */
function getServerIpsFromCrossModel($crossModel) {
    // 连接到固定服务器 10.68.2.32
    $conn = connectMsqlAgvWmsNoINFO('32');
    if (!$conn) {
        return [];
    }

    $ips = [];
    // 查询模板ID
    $sql = "SELECT id FROM fy_cross_model_process WHERE model_process_code = '" . mysqli_real_escape_string($conn, $crossModel) . "' 
            OR model_process_name = '" . mysqli_real_escape_string($conn, $crossModel) . "' 
            OR id = " . intval($crossModel);
    $result = mysqli_query($conn, $sql);
    if ($result && $row = mysqli_fetch_assoc($result)) {
        $modelId = $row['id'];
        // 查询子任务
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

/**
 * 在特定环境中查询设备配置详情
 */
function queryDevicesInEnvironment($ip, $deviceCodes, $strict) {
    $conn = connectMsqlAgvWmsNoINFO($ip);
    if (!$conn) {
        return [
            'status' => 'incomplete',
            'message' => '无法连接数据库',
            'missing' => ['数据库连接失败'],
            'details' => [],
            'tables' => []
        ];
    }

    $details = [];
    $missing = [];
    $status = 'complete';
    $tables = [];

    // 1. 查询 agv_robot 表
    $placeholders = "'" . implode("','", array_map('mysqli_real_escape_string', array_fill(0, count($deviceCodes), $conn), $deviceCodes)) . "'";
    $sql = "SELECT * FROM agv_robot WHERE device_code IN ($placeholders)";
    $result = mysqli_query($conn, $sql);
    $foundInRobot = [];
    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            $foundInRobot[] = $row['device_code'];
            $details[] = [
                'device' => $row['device_code'],
                'table' => 'agv_robot',
                'status' => 'found',
                'data' => $row
            ];
        }
        $tables['agv_robot'] = count($foundInRobot) . ' 条记录';
    } else {
        $missing[] = "agv_robot 表查询失败";
        $status = 'incomplete';
        $tables['agv_robot'] = '查询失败';
    }

    // 检查缺失的设备
    foreach ($deviceCodes as $code) {
        if (!in_array($code, $foundInRobot)) {
            $missing[] = "设备 $code 在 agv_robot 表中不存在";
            $details[] = [
                'device' => $code,
                'table' => 'agv_robot',
                'status' => 'missing',
                'data' => null
            ];
            $status = 'incomplete';
        }
    }

    // 2. 查询 agv_robot_ext 表
    $sql = "SELECT * FROM agv_robot_ext WHERE device_code IN ($placeholders)";
    $result = mysqli_query($conn, $sql);
    $foundInExt = [];
    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            $foundInExt[] = $row['device_code'];
            $details[] = [
                'device' => $row['device_code'],
                'table' => 'agv_robot_ext',
                'status' => 'found',
                'data' => $row
            ];
        }
        $tables['agv_robot_ext'] = count($foundInExt) . ' 条记录';
    } else {
        $missing[] = "agv_robot_ext 表查询失败";
        $status = 'incomplete';
        $tables['agv_robot_ext'] = '查询失败';
    }

    // 检查缺失的设备（在ext中）
    if ($strict) {
        foreach ($deviceCodes as $code) {
            if (!in_array($code, $foundInExt)) {
                $missing[] = "设备 $code 在 agv_robot_ext 表中不存在";
                $details[] = [
                    'device' => $code,
                    'table' => 'agv_robot_ext',
                    'status' => 'missing',
                    'data' => null
                ];
                $status = 'incomplete';
            }
        }
    }

    // 3. 查询 agv_model 表（根据设备型号）
    if (!empty($foundInRobot)) {
        // 获取设备型号列表
        $sql = "SELECT DISTINCT devicetype FROM agv_robot WHERE device_code IN ($placeholders)";
        $result = mysqli_query($conn, $sql);
        $deviceTypes = [];
        if ($result) {
            while ($row = mysqli_fetch_assoc($result)) {
                $deviceTypes[] = $row['devicetype'];
            }
        }
        if (!empty($deviceTypes)) {
            $typePlaceholders = "'" . implode("','", array_map('mysqli_real_escape_string', array_fill(0, count($deviceTypes), $conn), $deviceTypes)) . "'";
            $sql = "SELECT * FROM agv_model WHERE SERIES_MODEL_NAME IN ($typePlaceholders)";
            $result = mysqli_query($conn, $sql);
            if ($result) {
                $foundModels = [];
                while ($row = mysqli_fetch_assoc($result)) {
                    $foundModels[] = $row['SERIES_MODEL_NAME'];
                    $details[] = [
                        'device' => '型号 ' . $row['SERIES_MODEL_NAME'],
                        'table' => 'agv_model',
                        'status' => 'found',
                        'data' => $row
                    ];
                }
                $tables['agv_model'] = count($foundModels) . ' 条记录';
                // 检查缺失的型号
                foreach ($deviceTypes as $type) {
                    if (!in_array($type, $foundModels)) {
                        $missing[] = "设备型号 $type 在 agv_model 表中不存在";
                        $details[] = [
                            'device' => $type,
                            'table' => 'agv_model',
                            'status' => 'missing',
                            'data' => null
                        ];
                        $status = 'incomplete';
                    }
                }
            } else {
                $missing[] = "agv_model 表查询失败";
                $status = 'incomplete';
                $tables['agv_model'] = '查询失败';
            }
        }
    }

    // 4. 查询 agv_model_init 表（根据设备型号）
    if (!empty($foundInRobot) && isset($deviceTypes) && !empty($deviceTypes)) {
        $typePlaceholders = "'" . implode("','", array_map('mysqli_real_escape_string', array_fill(0, count($deviceTypes), $conn), $deviceTypes)) . "'";
        $sql = "SELECT * FROM agv_model_init WHERE SERIES_MODEL_NAME IN ($typePlaceholders)";
        $result = mysqli_query($conn, $sql);
        if ($result) {
            $foundModelInits = [];
            while ($row = mysqli_fetch_assoc($result)) {
                $foundModelInits[] = $row['SERIES_MODEL_NAME'];
                $details[] = [
                    'device' => '型号 ' . $row['SERIES_MODEL_NAME'],
                    'table' => 'agv_model_init',
                    'status' => 'found',
                    'data' => $row
                ];
            }
            $tables['agv_model_init'] = count($foundModelInits) . ' 条记录';
            // 检查缺失的型号
            foreach ($deviceTypes as $type) {
                if (!in_array($type, $foundModelInits)) {
                    $missing[] = "设备型号 $type 在 agv_model_init 表中不存在";
                    $details[] = [
                        'device' => $type,
                        'table' => 'agv_model_init',
                        'status' => 'missing',
                        'data' => null
                    ];
                    $status = 'incomplete';
                }
            }
        } else {
            // 表可能不存在，忽略
            $tables['agv_model_init'] = '表不存在或查询失败';
        }
    }

    mysqli_close($conn);

    return [
        'status' => $status,
        'message' => $status === 'complete' ? '设备配置查询完成' : '设备配置存在缺失',
        'missing' => $missing,
        'details' => $details,
        'tables_summary' => $tables
    ];
}
?>
