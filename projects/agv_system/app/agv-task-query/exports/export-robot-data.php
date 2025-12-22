<?php
/**
 * AGV设备数据导出为CSV
 * 支持单服务器和批量服务器导出
 */

require_once '../includes/init.php';

// 设置CSV头
header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename="agv_robot_data_' . date('Y-m-d_H-i-s') . '.csv"');

// 添加BOM以支持Excel正确识别UTF-8
echo "\xEF\xBB\xBF";

/**
 * 导出单个服务器的设备数据
 */
function exportSingleServer($ip) {
    global $conn;
    
    $conn = connectMsqlAgvWmsNoINFO($ip);
    if (!$conn) {
        return false;
    }
    
    mysqli_select_db($conn, 'wms');
    mysqli_query($conn, "set names utf8");
    
    $sql = "SELECT * FROM agv_robot_ext";
    $result = mysqli_query($conn, $sql);
    
    if (!$result) {
        return false;
    }
    
    $data = [];
    while ($row = mysqli_fetch_assoc($result)) {
        $row['server_ip'] = "10.68.2." . $ip;
        $data[] = $row;
    }
    
    mysqli_free_result($result);
    mysqli_close($conn);
    
    return $data;
}

/**
 * 导出所有服务器的设备数据
 */
function exportAllServers($servers) {
    $allData = [];
    
    foreach ($servers as $ip) {
        $data = exportSingleServer($ip);
        if ($data) {
            $allData = array_merge($allData, $data);
        }
    }
    
    return $allData;
}

/**
 * 输出CSV数据
 */
function outputCSV($data) {
    if (empty($data)) {
        echo "没有数据可导出";
        return;
    }
    
    $output = fopen('php://output', 'w');
    
    // 输出表头
    $headers = array_keys($data[0]);
    fputcsv($output, $headers);
    
    // 输出数据行
    foreach ($data as $row) {
        fputcsv($output, $row);
    }
    
    fclose($output);
}

// 获取参数
$mode = isset($_GET['mode']) ? $_GET['mode'] : 'single';
$ip = isset($_GET['ip']) ? $_GET['ip'] : '31';

// 预定义的服务器列表
$allServers = ['19', '31', '32', '33'];
$customServers = isset($_GET['servers']) ? explode(',', $_GET['servers']) : [];

// 根据模式导出
switch ($mode) {
    case 'all':
        $data = exportAllServers($allServers);
        break;
    case 'custom':
        $data = exportAllServers($customServers);
        break;
    case 'single':
    default:
        $data = exportSingleServer($ip);
        break;
}

// 输出CSV
if ($data) {
    outputCSV($data);
} else {
    echo "导出失败，无法获取数据";
}
?>