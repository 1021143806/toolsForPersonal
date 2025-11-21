<!DOCTYPE html>
<html>

<?php
include '../A1head/connect.php';
?>

<body>

<title>AGV设备统计</title>
<h1>用于读取数据库AGV设备数据</h1>

<?php
echo"Hello php!";
?>


<?php
connectMsqlAgvWms(31);//连接
catTheSqlTable('agv_robot');
?>
<?php
//释放内存
mysqli_free_result($retval);
echo('已释放内存');
showdownMysql();
?>



<?php
connectMsqlAgvWms(41);//连接
catTheSqlTable('agv_robot');
?>
<?php
//释放内存
mysqli_free_result($retval);
echo('已释放内存');
showdownMysql();
?>



</body>
</html>