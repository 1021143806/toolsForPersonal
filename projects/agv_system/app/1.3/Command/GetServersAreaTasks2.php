<!DOCTYPE html>
<html>

<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
include 'A1head/thefirst.php';
include 'A1head/phpform.php';
include 'A1head/show.php';
include 'A1head/sqlfindcode.php';
?>
<h1>输入服务器ip</h1>
<?php
$ip="31";
connectMsqlAgvWms("10.68.2.".$ip);

$sql = "select count(0) from task_group where FROM_UNIXTIME(create_time) >= CURDATE() - INTERVAL 1 MONTH"; // 你的 SQL 查询语句 一个月内任务
out_sql_show_form($sql,$conn);//示例



?>

<?php
showdownMysql();//关闭数据库
?>
</html>