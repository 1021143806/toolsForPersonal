<!DOCTYPE html>
<html>

<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
include 'A1head/thefirst.php';
include 'A1head/phpform.php';
include 'A1head/jsonhead.php';
?>
<h1>输入对应跨环境任务id以查询相关信息</h1>
<?php
function getLastIpSegmentSimplified($url) {  
    // 查找URL中最后一个冒号的位置  
    $pos = strrpos($url, ':');  
    if ($pos === false) {  
        return null; // URL格式不正确  
    }  
  
    // 截取从协议部分到冒号之前的字符串，即IP地址  
    $ip = substr($url, 7, $pos - 7); // 7是因为'http://'的长度是7  
  
    // 查找IP地址中最后一个点的位置  
    $dotPos = strrpos($ip, '.');  
    if ($dotPos === false) {  
        return null; // IP地址格式不正确  
    }  
  
    // 返回IP地址的最后一个部分  
    return substr($ip, $dotPos + 1);  
}  
function SearchAllTaskINFO($conn,$array){
    //遍历数组获取对应orderid然后执行任务详细查询
    // 输出表头  
    //echo '<table border="1">';  
    //echo '<tr>';  
    foreach ($array['column_names'] as $columnName) {  
        //echo htmlspecialchars($columnName) ;  //列名
    }  
    //echo '</tr>';  
    //print_r($array);
    // 输出数据行  
    foreach ($array['data'] as $row) {   
        //foreach ($row as $columnName => $value) {  
            //echo $columnName . "</br>";
            //echo htmlspecialchars($value).'</br>'; 
            //if ($columnName ="sub_order_id"){
                //echo "sub_order_id 为：".$value."</br>";
                //FindTheTaskphp($conn,$value);
                //echo "111111";
           //}
        //}  
        //echo '</br>'.$row["sub_order_id"];
        //echo '</br>'."<br>";
        echo "<h2>"."sub_order_id 为：".$row["sub_order_id"]."</h2>";
        //echo "</br>";
        $service_url=$row['service_url'];
        $ip=getLastIpSegmentSimplified($service_url);
        echo '最终IP为：'.$ip;
        //echo strpos($service_url,":700")-15;
        FindTheTaskphp($ip,$row["sub_order_id"]);
    }  
}
//_____________________显示任务信息___________________________
function FindTheTaskphp($ip,$out_order_id){
    //显示任务信息
    date_default_timezone_set('Asia/Shanghai');//设置默认时区
    //$dbhost = '10.68.2.27';  // mysql服务器主机地址
    $conn=connectMsqlAgvWmsNoINFO($ip);
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

    //echo "<br>"."<br>";//分行
    mysqli_select_db($conn, 'wms' );//选择数据库
    // 设置编码，防止中文乱码
    mysqli_query($conn , "set names utf8");

    //查询对应设备
    $retval = mysqli_query($conn, $sql4 );//获取数据
    if(! $retval )
    {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    //echo "成功读取到数据"."<br>";
    while($row = mysqli_fetch_array($retval, MYSQLI_ASSOC))
    {
        $a1="area_id";$a1=$row[$a1];echo "所在区域id为".":".$a1."<br>";
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
}

?>
<?php
//1.读取输入的任务id
$order_id=$_GET["idd"];
echo "输入的任务ID为:".$order_id;
echo "<br>";
//2.读取输入的服务器
//$RCSip="10.68.2.".$_GET["RCSip"];
$RCSip="10.68.2.32";
//echo "查询的服务器IP为:".$RCSip;

//3.连接跨环境数据库
connectMsqlAgvWmsNoINFO("10.68.2.32");

//4.获取表 fy_cross_task_detail 数据并创建数组保存子任务orderid数据
$sql="select * from fy_cross_task_detail where order_id ='$order_id'";
$arrfy_cross_task_detail=SQLfindtoArr_conn($conn,$sql);

echo $sql;
//print_r($arrfy_cross_task_detail);
//echo $arrfy_cross_task_detail;
//echo ArrToJson($arrfy_cross_task_detail);
ToForm_sqlfind($arrfy_cross_task_detail);

//5.获取对应跨环境任务模板in_model_process_code并统计当前执行数量
$name= "count(0)";
$in_model_process_code=sqlfindjustone($conn,'model_process_code','fy_cross_task','orderId',$order_id);//统计该模板当前任务总数
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

//6.遍历数组获取对应orderid然后执行任务详细查询
//print(ArrToJson($arrfy_cross_task_detail));
showdownMysqlNoINFO();//关闭数据库
SearchAllTaskINFO($conn,$arrfy_cross_task_detail);
//showdownMysql();//关闭数据库
?>
</html>