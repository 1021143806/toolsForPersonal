<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
include 'A1head/thefirst.php';
include 'A1head/phpform.php';
include 'A1head/show.php';
include 'A1head/posttesthead.php';
$ip="31";
#connectMsqlAgvWms("10.68.2.".$ip);
connectMsqlAgvWmsNoINFO($ip);
$sql = "select count(0) from task_group where FROM_UNIXTIME(create_time) >= CURDATE() - INTERVAL 1 MONTH"; // 你的 SQL 查询语句 一个月内任务
#$response=out_sql_show_form($sql,$conn);//示例
$response=sqlfindall($conn,$sql);
$json=json_encode($response);
showdownMysqlNoINFO();
?>
<?php
$jsonString = json_encode($json);
header('Content-Type:application/json');
echo $jsonString;
?>
