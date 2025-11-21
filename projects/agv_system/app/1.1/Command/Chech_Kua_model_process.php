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
?>

<h2>
<?php
echo "输入的跨环境任务模版为:".$in_model_process_code;
echo "<br>";
?>
</h2>

<?php
//输入对应跨环境任务模版
//连接跨环境数据库
connectMsqlAgvWms("10.68.2.32");

$name= "id";
$sql = "select id from fy_cross_model_process where model_process_code ='$in_model_process_code'";
$model_process_code_id=sqlfindone($conn,$name,$sql);
echo "当前查询的跨环境任务 id 为：".$model_process_code_id."<br>";//获取对应sql语句查询到的参数


// 假设你已经建立了数据库连接 $conn  
$sql = "select * from fy_cross_model_process where model_process_code = '$in_model_process_code'"; // 你的 SQL 查询语句 
//moveShelfToWLCKToDJS 
// 使用示例  
if ($conn->connect_error) {  
    die('连接失败: ' . $conn->connect_error);  
}  
$result = sqlfindall($conn, $sql);  

//输出完整表
out_sql_search_form($result);
?>

<h2>该跨环境子任务</h2>

<?php
// 2按照id查询字任务
$sql = "select * from fy_cross_model_process_detail where model_process_id = '$model_process_code_id'"; // 你的 SQL 查询语句 
//A4DZSHDA2 
// 
if ($conn->connect_error) {  
    die('连接失败: ' . $conn->connect_error);  
}  
$result = sqlfindall($conn, $sql);  

//输出完整表
out_sql_search_form($result);


showdownMysql();//关闭数据库
?>
</html>