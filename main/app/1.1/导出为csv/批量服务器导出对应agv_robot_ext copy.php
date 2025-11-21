<!DOCTYPE html>
<html>

<?php
include '../A1head/connect.php';
include '../A1head/SQLfind.php';
include '../A1head/thefirst.php';
?>

<body>


<h1>用于读取数据库AGV设备数据</h1>

<?php
echo"Hello php!";
$csv_data = 
    "设备序列号"
    .","."所在服务器"
    .","."所在区域"
    .","."设备编号"
    .","."创建时间"
    .","."所在点位"
    .","."对应设备IP"
    .","."设备账号"
    .","."设备密码"
    .","."设备型号"
    //.","."最近执行任务创建时间的时间戳"
    .","."最近执行任务创建时间"
    .","."近期是否在线"
    .","."\n";

// 导出CSV文件
$file = fopen("所有服务器设备".".csv", "w");
fwrite($file, $csv_data);
fclose($file);
echo "数据库导出为新建CSV文件成功！";


?>

<?php
//$alldb=array("3","9","13","15","17","19","21","25","27","32","31","41");
$alldb=array("3","9","11","15","17","19","21","27","32","31");
$arrlength=count($alldb);
 
for($x=0;$x<$arrlength;$x++)
{

    $dbhost = '10.68.2.'.$alldb[$x];  // mysql服务器主机地址
    $dbuser = 'wms';            // mysql用户名
    $dbpass = 'CCshenda889';          // mysql用户名密码
    $conn = mysqli_connect($dbhost, $dbuser, $dbpass);
    if(! $conn )
    {
        die('Could not connect: ' . mysqli_error());
    }
    echo '数据库连接成功！';

    //创建数据库

    // $sql = 'CREATE DATABASE RUNOOB';
    // $retval = mysqli_query($conn,$sql );
    // if(! $retval )
    // {
    //     die('创建数据库失败: ' . mysqli_error($conn));
    // }
    // echo "数据库 RUNOOB 创建成功\n";






    //创建数据表
    // CREATE TABLE IF NOT EXISTS `runoob_tbl`(
    //     `runoob_id` INT UNSIGNED AUTO_INCREMENT,
    //     `runoob_title` VARCHAR(100) NOT NULL,
    //     `runoob_author` VARCHAR(40) NOT NULL,
    //     `submission_date` DATE,
    //     PRIMARY KEY ( `runoob_id` )
    //  )ENGINE=InnoDB DEFAULT CHARSET=utf8;

    //读取

    $sql='SELECT * FROM `agv_robot_ext`';
    mysqli_select_db($conn, 'wms' );//选择数据库
    $result = mysqli_query( $conn, $sql );
    if(! $result )
    {
        die('无法读取数据: ' . mysqli_error($conn));
    }

    // 设置编码，防止中文乱码
    mysqli_query($conn , "set names utf8");

    // echo '<h2> MySQL WHERE 子句测试<h2>';
    // echo '<table border="1"><tr><td>ID</td><td>设备序列号</td><td>设备IP</td><td>设备型号</td></tr>';
    // while($row = mysqli_fetch_array($retval, MYSQLI_ASSOC))
    // {
    //     echo "<tr><td> {$row['ID']}</td> ".
    //          "<td>{$row['DEVICE_CODE']} </td> ".
    //          "<td>{$row['DEVICE_IP']} </td> ".
    //          "<td>{$row['DEVICETYPE']} </td> ".
    //          "</tr>";
    // }

    //———————————————————————————————————————————————————————————————————————————————————————————————————————————
    // 循环输出记录信息
    if ($result->num_rows > 0) {
        // 将查询结果导出为CSV
        //————————————————————————————————————————————————————————————————————————
        //此处填写第一行标题
       
        $csv_data = "";
         /*
        "设备序列号"
        .","."所在服务器"
        .","."所在区域"
        .","."设备编号"
        .","."创建时间"
        .","."所在点位"
        .","."对应设备IP"
        .","."设备账号"
        .","."设备密码"
        .","."设备型号"
        //.","."最近执行任务创建时间的时间戳"
        .","."最近执行任务创建时间"
        .","."近期是否在线"
        .","."\n";
        */
        // CSV文件的列标题
        while ($row = $result->fetch_assoc()) {
        $a1=$row["DEVICE_CODE"];
        //$csv_data .= $row["DEVICE_CODE"] . ", " . $row["DEVICE_AREA"] . ", " . $row["DEVICE_NUMBER"] . ", " . $row["CREATE_DATE"] . ", " . $row["BIND_QRNODE"] . ", " . sqlfindone($conn,"DEVICE_IP","SELECT DEVICE_IP FROM agv_robot WHERE DEVICE_CODE='$a1'") . "\n";

        //测试相关sql语句
        // $sql2="SELECT create_time FROM task_group WHERE robot_num ='10203'";
        // $sql3="SELECT create_time FROM task_group WHERE create_time ='1700484197'";
        // $sql4="SELECT ID FROM agv_robot_error WHERE ID ='1'";
        // $sql5="SELECT create_time FROM task_group WHERE robot_num ='10203'";
        
        //——————————————————————————————————————————————————————————————————————————————————————————————————————
        //这里存放读取的数据
        $DEVICE_CODE=$row["DEVICE_CODE"];
        $DEVICE_AREA=$row["DEVICE_AREA"];
        $DEVICE_NUMBER=$row["DEVICE_NUMBER"];
        $CREATE_DATE=$row["CREATE_DATE"];
        $BIND_QRNODE=$row["BIND_QRNODE"];
        $DEVICE_IP=sqlfindjustone($conn,"DEVICE_IP","agv_robot","DEVICE_CODE",$row["DEVICE_CODE"]);
        $USRENAME=sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"USRENAME",$row["DEVICE_CODE"]);
        $PASSWORD=sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"PASSWORD",$row["DEVICE_CODE"]);
        $DEVICETYPE=sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"DEVICETYPE",$row["DEVICE_CODE"]);
        $task_group_create_time=sqlfindjustone($conn,"create_time","task_group","robot_num",$row["DEVICE_NUMBER"]);
        $task_group_create_date;$isonline;
        if(date("Y-m-d H:i:s") <> date("Y-m-d H:i:s",$task_group_create_time))
        {
            //如果task_group表中查到有该车任务，则说明现场可能在使用。
            $isonline=1;
            $task_group_create_date=date("Y-m-d H:i:s",$task_group_create_time);
        }
        else
        {
            $isonline=0;
            $task_group_create_date=0;
        }


        //——————————————————————————————————————————————————————————————————————————————————————————————————————
        //生成CSV数据
        $csv_data.=
        $DEVICE_CODE
        .",".$dbhost
        .",".$DEVICE_AREA
        .",".$DEVICE_NUMBER
        .",".$CREATE_DATE
        .",".$BIND_QRNODE
        .",".$DEVICE_IP
        .",".$USRENAME
        .",".$PASSWORD
        .",".$DEVICETYPE
        //.",".$task_group_create_time
        .",".$task_group_create_date
        .",".$isonline
        //.",".date("Y-m-d H:i:s",$task_group_create_time)
        // $row["DEVICE_CODE"].",".
        // $row["DEVICE_AREA"].",".
        // $row["DEVICE_NUMBER"].",".
        // $row["CREATE_DATE"].",".
        // $row["BIND_QRNODE"].",".
        //sqlfindjustone($conn,"DEVICE_IP","agv_robot","DEVICE_CODE",$row["DEVICE_CODE"]).",".
        //sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"USRENAME",$row["DEVICE_CODE"]).",".
        //sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"PASSWORD",$row["DEVICE_CODE"])
        //.",".sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"DEVICETYPE",$row["DEVICE_CODE"])
        //.",".date("Y-m-d H:i:s",sqlfindjustone($conn,"create_time","task_group","robot_num",$row["DEVICE_NUMBER"]))
        //.",".sqlfindjustone($conn,"create_time","task_group","robot_num",$row["DEVICE_NUMBER"])
        //if(sqlfindone($conn,"create_time",$sql2)){break}
        //date("Y-m-d H:i:s",$a1)
        ."\n";


        //——————————————————————————————————————————————————————————————————————————————————————————————————————————
        //测试语句（日志）
        {
            //echo  sqlfindone($conn,"create_time",$sql3)."\n";
            //echo sqlfindjustone($conn,"create_time","task_group","robot_num",$row["DEVICE_NUMBER"]);

            // $test = mysqli_query( $conn, $sql3 );
            // if(! $test )
            // {
            //     die('无法读取数据: ' . mysqli_error($conn));
            // }
            // else
            // {
            //     echo "可以读取数据";
            //     //echo  sqlfindoneNoFalse($conn,"create_time",$sql5)."\n";
            // }


        }
        //function sqlfindjustone($conn,$select,$from,$know,$a1)//获取对应sql语句查询到的参数test
        //数据库$conn，要查找的字段的列$select,要查找的字段的表$form，已知的数据字段的列名$know，已知的数据的字段$a1

        //sqlfindjusetone($conn,"DEVICE_IP","agv_robot","DEVICE_CODE",$row["DEVICE_CODE"]);
        //后续添加+++ ", " . sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,"USRENAME",$row["DEVICE_CODE"]) .  +++
        //$csv_data .= $row["DEVICE_CODE"] . ", " . $row["DEVICE_AREA"] . ", " . $row["DEVICE_NUMBER"] . ", " . $row["CREATE_DATE"] . $row["BIND_QRNODE"] . ", " .  sqlfindone($conn,"DEVICE_IP","SELECT * FROM agv_robot WHERE DEVICE_CODE='10.68.139.22'") . "\n";
    }


    //释放内存
    mysqli_free_result($result);
    mysqli_close($conn);

    // 导出CSV文件
    $file = fopen("所有服务器设备".".csv", "a");
    fwrite($file, $csv_data);
    fclose($file);
    echo "数据库导出为CSV文件成功！";
    }
    else {
    echo "没有符合条件的数据。";
    }

}



?>
</body>
</html>