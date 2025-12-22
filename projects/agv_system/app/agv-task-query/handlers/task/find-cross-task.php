<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>跨环境任务详细查询</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1, h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .info { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .task-block { background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #007bff; }
        .info-item { padding: 5px 0; border-bottom: 1px solid #eee; }
        .info-label { color: #666; }
        .info-value { color: #333; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>

<?php
require_once '../../includes/init.php';

/**
 * 从URL中提取IP地址最后一段
 */
function getLastIpSegmentSimplified($url)
{
    $pos = strrpos($url, ':');
    if ($pos === false) {
        return null;
    }
    $ip = substr($url, 7, $pos - 7);
    $dotPos = strrpos($ip, '.');
    if ($dotPos === false) {
        return null;
    }
    return substr($ip, $dotPos + 1);
}

/**
 * 搜索所有任务信息
 */
function SearchAllTaskINFO($conn, $array)
{
    foreach ($array['data'] as $row) {
        echo "<h2>sub_order_id: " . htmlspecialchars($row["sub_order_id"]) . "</h2>";
        $service_url = $row['service_url'];
        $ip = getLastIpSegmentSimplified($service_url);
        echo '<div class="info">服务器IP: ' . htmlspecialchars($ip) . '</div>';
        FindTheTaskphp($ip, $row["sub_order_id"]);
    }
}

/**
 * 查询单个任务详情
 */
function FindTheTaskphp($ip, $out_order_id)
{
    $conn = connectMsqlAgvWmsNoINFO($ip);
    $sql4 = "SELECT * FROM task_group WHERE third_order_id = '$out_order_id'";

    mysqli_select_db($conn, 'wms');
    mysqli_query($conn, "set names utf8");

    $retval = mysqli_query($conn, $sql4);
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }

    echo '<div class="task-block">';
    while ($row = mysqli_fetch_array($retval, MYSQLI_ASSOC)) {
        echo "<div class='info-item'><span class='info-label'>所在区域id：</span><span class='info-value'>" . $row["area_id"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>任务模板：</span><span class='info-value'>" . $row["template_code"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>分派的AGV：</span><span class='info-value'>" . $row["robot_num"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>设备序列号：</span><span class='info-value'>" . $row["robot_id"] . "</span></div>";
        
        $robot_id = $row["robot_id"];
        echo "<div class='info-item'><span class='info-label'>设备IP：</span><span class='info-value'>" . sqlfindFrom_agv_robot_ByDEVICE_CODE($conn, "DEVICE_IP", $robot_id) . "</span></div>";
        
        echo "<div class='info-item'><span class='info-label'>路径点集：</span><span class='info-value'>" . $row["path_points"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>分派的AGV设备类型：</span><span class='info-value'>" . $row["robot_type"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>下发的货架模型编号：</span><span class='info-value'>" . $row["shelf_model"] . "</span></div>";
        
        $shelf_model = $row["shelf_model"];
        echo "<div class='info-item'><span class='info-label'>下发的货架模型：</span><span class='info-value'>" . sqlfindone($conn, 'name', "SELECT name FROM load_config WHERE model =$shelf_model") . "</span></div>";
        
        echo "<div class='info-item'><span class='info-label'>任务货架：</span><span class='info-value'>" . $row["carrier_code"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>错误描述：</span><span class='info-value'>" . $row["error_desc"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>任务创建时间：</span><span class='info-value'>" . date("Y-m-d H:i:s", $row["create_time"]) . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>任务开始时间：</span><span class='info-value'>" . date("Y-m-d H:i:s", $row["start_time"]) . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>任务结束时间：</span><span class='info-value'>" . date("Y-m-d H:i:s", $row["end_time"]) . "</span></div>";
        
        $status = $row["status"];
        echo "<div class='info-item'><span class='info-label'>任务状态值：</span><span class='info-value'>" . $status . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>任务状态：</span><span class='info-value'>" . sqlfindone($conn, 'task_status_name', "SELECT task_status_name FROM task_status_config WHERE task_status =$status") . "</span></div>";
        
        echo "<div class='info-item'><span class='info-label'>order_id：</span><span class='info-value'>" . $row["order_id"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>out_order_id：</span><span class='info-value'>" . $row["out_order_id"] . "</span></div>";
        echo "<div class='info-item'><span class='info-label'>tg_id：</span><span class='info-value'>" . $row["id"] . "</span></div>";
    }
    echo '</div>';

    mysqli_free_result($retval);
    mysqli_close($conn);
}
?>

<h1>跨环境任务详细查询</h1>

<?php
// 1.读取输入的任务id
$order_id = trim($_GET["idd"]);
echo "<div class='info'>输入的任务ID：<strong>" . htmlspecialchars($order_id) . "</strong></div>";

// 2.连接跨环境数据库
connectMsqlAgvWmsNoINFO("10.68.2.32");

// 3.获取表 fy_cross_task_detail 数据
$sql = "select * from fy_cross_task_detail where order_id ='$order_id'";
$arrfy_cross_task_detail = SQLfindtoArr_conn($conn, $sql);

echo "<h2>子任务列表</h2>";
ToForm_sqlfind($arrfy_cross_task_detail);

// 4.获取对应跨环境任务模板并统计当前执行数量
$name = "count(0)";
$in_model_process_code = sqlfindjustone($conn, 'model_process_code', 'fy_cross_task', 'orderId', $order_id);
$sql = "select count(0) from fy_cross_task where model_process_code ='$in_model_process_code' AND task_status in (0,1,6,4,9,10)";
echo "<div class='info'>当前该跨环境正在执行的任务数为：<strong>" . sqlfindone($conn, $name, $sql) . "</strong></div>";

// 5.查询执行中的任务
$sql = "select * from fy_cross_task where model_process_code = '$in_model_process_code' AND task_status in (0,1,6,4,9,10)";

if ($conn->connect_error) {
    die('连接失败: ' . $conn->connect_error);
}

$result = sqlfindall($conn, $sql);

echo "<h2>执行中的任务</h2>";
out_sql_search_form($result);

// 6.关闭数据库并查询各子任务详情
showdownMysqlNoINFO();
echo "<h2>子任务详细信息</h2>";
SearchAllTaskINFO($conn, $arrfy_cross_task_detail);
?>

<br>
<a href="../../index.html" style="color: #007bff;">返回首页</a>

</body>
</html>