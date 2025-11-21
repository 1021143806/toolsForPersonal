<!DOCTYPE html>
<html>
<body>



<?php
//定义全局变量
global $dbhost ,  // mysql服务器主机地址
$dbuser ,  // mysql用户名
$dbpass ,  // mysql用户名密码
$conn ,    //当前连接数据库
$ip1 ,
$retval;


function connectMsqlAgvWms($ip)//连接AGV数据库
{
  global $dbhost,$dbuser,$dbpass,$conn,$ip1;
      // 要执行的代码
  $ip1=$ip;
  echo strlen($ip1);
  if(strlen($ip1) < 4)
  {
    $dbhost = '10.68.2.';  // mysql服务器主机地址简写
  }
  else
  {
    $dbhost = '';  // 完整ip地址
  }
  //$dbhost = '10.68.2.';  // mysql服务器主机地址
  $dbuser = 'wms';            // mysql用户名
  $dbpass = 'CCshenda889';          // mysql用户名密码
  $conn = mysqli_connect($dbhost.$ip, $dbuser, $dbpass);
  if(! $conn )
  {
      die('Could not connect: ' . mysqli_error());
  }
  echo "数据库 $ip1 连接成功！<br>";
  mysqli_select_db($conn, 'wms' );//选择数据库
    // 设置编码，防止中文乱码
    mysqli_query($conn , "set names utf8");

}


function showdownMysql()//关闭数据库
{
  global $dbhost,$dbuser,$dbpass,$conn,$ip1;
  //释放内存


  mysqli_close($conn);  
  echo('成功关闭数据库'.$dbhost.$ip1);
}

function catTheSqlTable($table)//查询表数据
{
  global $dbhost,$dbuser,$dbpass,$conn,$ip1,$retval;
  //
  $sql='SELECT * FROM '. $table;
  mysqli_select_db($conn, 'wms' );//选择数据库
  $retval = mysqli_query( $conn, $sql );
  if(! $retval )
  {
      die('无法读取数据: ' . mysqli_error($conn));
  }
  
  // 设置编码，防止中文乱码
  mysqli_query($conn , "set names utf8");
  
  echo '<h2> MySQL WHERE 子句测试<h2>';
  echo '<table border="1"><tr><td>ID</td><td>设备序列号</td><td>设备IP</td><td>设备型号</td></tr>';
  while($row = mysqli_fetch_array($retval, MYSQLI_ASSOC))
  {
      echo "<tr><td> {$row['ID']}</td> ".
           "<td>{$row['DEVICE_CODE']} </td> ".
           "<td>{$row['DEVICE_IP']} </td> ".
           "<td>{$row['DEVICETYPE']} </td> ".
           "</tr>";
  }
  
}
function catTheSqlTable2($table,$a1,$a2,$a3,$a4)//查询表数据详细参数
{
  global $dbhost,$dbuser,$dbpass,$conn,$ip1,$retval;
  //
  $sql='SELECT * FROM '. $table;
  mysqli_select_db($conn, 'wms' );//选择数据库
  $retval = mysqli_query( $conn, $sql );
  if(! $retval )
  {
      die('无法读取数据: ' . mysqli_error($conn));
  }
  
  // 设置编码，防止中文乱码
  mysqli_query($conn , "set names utf8");
  
  echo '<h2> MySQL WHERE 子句测试<h2>';
  echo '<table border="1"><tr><td>'.$a1.'</td><td>'.$a2.'</td><td>'.$a3.'</td><td>'.$a4.'</td></tr>';
  while($row = mysqli_fetch_array($retval, MYSQLI_ASSOC))
  {
      echo "<tr><td> {$row[$a1]}</td> ".
           "<td>{$row[$a2]} </td> ".
           "<td>{$row[$a3]} </td> ".
           "<td>{$row[$a4]} </td> ".
           "</tr>";
  }
  
}
//echo "已成功导入头文件！"
?>

</body>