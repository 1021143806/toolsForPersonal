<!DOCTYPE html>
<html>

<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
include 'A1head/thefirst.php';
include 'A1head/phpform.php';
?>
<h1>输入对应跨环境任务模板以查询相关信息</h1>

<?php
//读取输入的跨环境任务模版
$in_model_process_code=$_GET["idd"];
echo "输入的跨环境任务模版为:".$in_model_process_code;
echo "<br>";

//输入对应跨环境任务模版
//连接跨环境数据库
connectMsqlAgvWms("10.68.2.32");

$name= "count(0)";
$sql = "select count(0) from fy_cross_task where model_process_code ='$in_model_process_code'AND task_status in (0,1,6,4,9,10)";
echo "当前该跨环境正在执行的任务数为：".sqlfindone($conn,$name,$sql)."<br>";//获取对应sql语句查询到的参数


// 假设你已经建立了数据库连接 $conn  
$sql = "select * from fy_cross_task where model_process_code = '$in_model_process_code' AND task_status in (0,1,6,4,9,10)"; // 你的 SQL 查询语句  
// 使用示例  
if ($conn->connect_error) {  
    die('连接失败: ' . $conn->connect_error);  
}  
$result = sqlfindall($conn, $sql);  

//输出完整表
out_sql_search_form($result);




showdownMysql();//关闭数据库
?>
</html>