<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>跨环境任务模板信息</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1, h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .info { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>

<?php
require_once '../../includes/init.php';
?>

<h1>跨环境任务模板详情</h1>

<?php
// 读取输入的跨环境任务模版
$in_model_process_code = $_GET["idd"];
?>

<h2>
<?php
echo "输入的跨环境任务模版：" . htmlspecialchars($in_model_process_code);
?>
</h2>

<?php
// 连接跨环境数据库
connectMsqlAgvWms("10.68.2.32");

$name = "id";
$sql = "select id from fy_cross_model_process where model_process_code ='$in_model_process_code'";
$model_process_code_id = sqlfindone($conn, $name, $sql);
echo "<div class='info'>当前查询的跨环境任务 id 为：<strong>" . $model_process_code_id . "</strong></div>";

// 查询主任务信息
$sql = "select * from fy_cross_model_process where model_process_code = '$in_model_process_code'";

if ($conn->connect_error) {
    die('连接失败: ' . $conn->connect_error);
}

$result = sqlfindall($conn, $sql);

// 输出完整表
out_sql_search_form($result);
?>

<h2>该跨环境子任务</h2>

<?php
// 按照id查询子任务
$sql = "select * from fy_cross_model_process_detail where model_process_id = '$model_process_code_id'";

if ($conn->connect_error) {
    die('连接失败: ' . $conn->connect_error);
}

$result = sqlfindall($conn, $sql);

// 输出完整表
out_sql_search_form($result);

showdownMysql();
?>

<br>
<a href="../../index.html" style="color: #007bff;">返回首页</a>

</body>
</html>