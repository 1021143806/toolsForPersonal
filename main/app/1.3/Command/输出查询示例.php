<!DOCTYPE html>
<html>

<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
include 'A1head/thefirst.php';
include 'A1head/phpform.php';
?>

<?php
//输入对应跨环境任务模版
//连接跨环境数据库
connectMsqlAgvWms("10.68.2.32");

$name= "count(0)";
$sql = "select count(0) from fy_cross_task where model_process_code = 'A2DZSKDA4' AND task_status in (0,1,6,4,9,10)";
//$sql = "select count(0) from fy_cross_task where task_status in (0,1,6,4,9,10)";
//$sql = "select * from fy_cross_task where task_status in (0,1,6,4,9,10)";
echo "当前该跨环境正在执行的任务数为：".sqlfindone($conn,$name,$sql)."<br>";//获取对应sql语句查询到的参数


// 假设你已经建立了数据库连接 $conn  
$sql = "SELECT * FROM agv_robot_error"; // 你的 SQL 查询语句  
// 使用示例  
if ($conn->connect_error) {  
    die('连接失败: ' . $conn->connect_error);  
}  
$result = sqlfindall($conn, $sql);  
  
// 输出列名  
echo '列名: ';  
//print_r($result['column_names']); 
out_oneD_form($result['column_names']);
echo "<br>";  
  
// 输出所有数据  
echo '数据: ';  
out_twoD_form($result['data']);

//输出完整表
out_sql_search_form($result);


showdownMysql();//关闭数据库
?>
</html>