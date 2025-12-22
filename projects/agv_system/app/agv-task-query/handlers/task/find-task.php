<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>任务查询结果</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .info-item { padding: 5px 0; border-bottom: 1px solid #eee; }
        .info-label { color: #666; }
        .info-value { color: #333; font-weight: bold; }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>

<?php
require_once '../../includes/init.php';
?>

<h1>任务查询结果</h1>

<?php
// 读取输入的任务id
$out_order_id = $_GET["idd"];
echo "<div class='info-item'><span class='info-label'>输入的任务ID：</span><span class='info-value'>" . htmlspecialchars($out_order_id) . "</span></div>";

// 读取输入的服务器
$RCSip = "10.68.2." . $_GET["RCSip"];

// 连接数据库
$dbhost = $RCSip;
$dbuser = 'wms';
$dbpass = 'CCshenda889';
$conn = mysqli_connect($dbhost, $dbuser, $dbpass);

if (!$conn) {
    die('<div class="error">数据库连接失败: ' . mysqli_error() . '</div>');
}

echo "<div class='info-item success'>数据库连接成功：" . htmlspecialchars($RCSip) . "</div>";
echo "<br>";

// SQL语句
$sql4 = "SELECT * FROM task_group WHERE third_order_id = '$out_order_id'";

mysqli_select_db($conn, 'wms');
mysqli_query($conn, "set names utf8");

// 查询对应设备
$retval = mysqli_query($conn, $sql4);
if (!$retval) {
    die('<div class="error">无法读取数据: ' . mysqli_error($conn) . '</div>');
}

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

// 释放内存
mysqli_free_result($retval);
mysqli_close($conn);
?>

<br>
<a href="../../index.html" style="color: #007bff;">返回首页</a>

</body>
</html>