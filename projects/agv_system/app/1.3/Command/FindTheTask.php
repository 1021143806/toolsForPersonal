<!DOCTYPE html>
<html>

<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
?>

<body>


<h1>输入对应第三方任务订单以查询相关信息</h1>

<?php
//读取输入的任务id
$out_order_id=$_GET["idd"];
echo "输入的任务ID为:".$out_order_id;
echo "<br>";
//读取输入的服务器
$RCSip="10.68.2.".$_GET["RCSip"];
//echo "查询的服务器IP为:".$RCSip;
?>






<?php
date_default_timezone_set('Asia/Shanghai');//设置默认时区
//$dbhost = '10.68.2.27';  // mysql服务器主机地址
$dbhost = $RCSip;  // mysql服务器主机地址
$dbuser = 'wms';            // mysql用户名
$dbpass = 'CCshenda889';          // mysql用户名密码
$conn = mysqli_connect($dbhost, $dbuser, $dbpass);
if(! $conn )
{
    die('Could not connect: ' . mysqli_error());
}
echo '数据库连接成功:'.$RCSip."<br>";


//sql语句
//$sql='SELECT * FROM `agv_robot`';
//$sql2="SELECT * FROM task_order WHERE third_order_id = '$out_order_id'";
//$sql3="SELECT * FROM task_order WHERE third_order_id = 'ChargeBackGo16976460351938923_2_8596'";
//$sql3="SELECT * FROM task_group WHERE third_order_id = '$out_order_id'";
$sql4="SELECT * FROM task_group WHERE third_order_id = '$out_order_id'";//从任务表中选出需要的数据

// echo "____调试用1____<br>";
// echo $sql2."<br>";
// echo "____调试用2____<br>";
// echo $sql3."<br>";
echo "<br>"."<br>";//分行

mysqli_select_db($conn, 'wms' );//选择数据库

// 设置编码，防止中文乱码
mysqli_query($conn , "set names utf8");

//查询对应设备
$retval = mysqli_query( $conn, $sql4 );//获取数据
if(! $retval )
{
    die('无法读取数据: ' . mysqli_error($conn));
}
//echo "成功读取到数据"."<br>";
while($row = mysqli_fetch_array($retval, MYSQLI_ASSOC))
{
    $a1="area_id";$a1=$row[$a1];echo "所在区域id为"."：".$a1."<br>";
    $a1="template_code";$a1=$row[$a1];echo "任务模板为：".$a1."<br>";
    $a1="robot_num";$a1=$row[$a1];echo "分派的AGV为:".$a1."<br>";
    $a1="robot_id";$a1=$row[$a1];echo "设备序列号为：".$a1."<br>";
    //$a1="robot_id";$a1=$row[$a1];echo "设备IP:".sqlfindone($conn,'DEVICE_IP',"SELECT DEVICE_IP FROM agv_robot WHERE DEVICE_CODE ='$a1'")."<br>";
    $a1="robot_id";$a1=$row[$a1];echo "设备IP:".sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"DEVICE_IP",$a1)."<br>";
    $a1="path_points";$a1=$row[$a1];echo "路径点集为:".$a1."<br>";
    $a1="robot_type";$a1=$row[$a1];echo "分派的AGV设备类型为:".$a1."<br>";
    $a1="shelf_model";$a1=$row[$a1];echo "下发的货架模型编号为:".$a1."<br>";
    $a1="shelf_model";$a1=$row[$a1];echo "下发的货架模型为:".sqlfindone($conn,'name',"SELECT name FROM load_config WHERE model =$a1")."<br>";
    $a1="carrier_code";$a1=$row[$a1];echo "任务货架为：".$a1."<br>";
    $a1="error_desc";$a1=$row[$a1];echo "错误描述".":".$a1."<br>";
    $a1="create_time";$a1=$row[$a1];echo "任务创建时间".":".date("Y-m-d H:i:s",$a1)."<br>";
    $a1="start_time";$a1=$row[$a1];echo "任务开始时间".":".date("Y-m-d H:i:s",$a1)."<br>";
    $a1="end_time";$a1=$row[$a1];echo "任务结束时间".":".date("Y-m-d H:i:s",$a1)."<br>";
    $a1="status";$a1=$row[$a1];echo "任务状态值为:".$a1."<br>";
    $a1="status";$a1=$row[$a1];echo "任务状态为:".sqlfindone($conn,'task_status_name',"SELECT task_status_name FROM task_status_config WHERE task_status =$a1")."<br>";
    $a1="order_id";$a1=$row[$a1];echo "order_id".":".$a1."<br>";
    $a1="out_order_id";$a1=$row[$a1];echo "out_order_id".":".$a1."<br>";
    $a1="id";$a1=$row[$a1];echo "tg_id".":".$a1."<br>";


}

//echo "已结束";
//释放内存
mysqli_free_result($retval);
mysqli_close($conn);
?>
</body>
</html>