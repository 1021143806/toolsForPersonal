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
<h1>输入服务器ip地址查询任务数量</h1>
<?php
$ip="31";
connectMsqlAgvWms("10.68.2.".$ip);

// $sql = "select count(0) from task_group where FROM_UNIXTIME(create_time) >= CURDATE() - INTERVAL 1 MONTH"; // 你的 SQL 查询语句 一个月内任务
// out_sql_show_form($sql,$conn);//示例

//获取该服务器区域
$arrArea = out_sql_show_form($sqlgetbms_area,$conn);
print json_encode($arrArea);//转换JSON

$arr2Areas=$arrArea["data"];
//格式化输出数组
//print("<pre>"); print_r($arr2Areas);print("</pre>");

echo "<br>";



//遍历二维数组
foreach ($arr2Areas as $row) {  
    // 输出表格的行  
    echo "区域：".$row["ID"]."  ".$row["NAME"];
    echo '<tr>';  
      
    // 遍历当前行的每个元素  
    // foreach ($row as $cell) {  
    //     // 输出表格的单元格  
    //     echo '<td>' . $cell . '</td>';  
    // }  

    //print("<pre>"); print_r($row);print("</pre>");
    echo "当前区域总任务<br>";
    $sql = $sqlGetTheAllTaskCount0." and area_id =".$row["ID"];//查询任务
    #echo $sql;
    out_sql_show_form($sql,$conn);
    echo "当前区域任务：已完成<br>";//8
    $sql = $sqlGetTheAllTaskCount0." and area_id =".$row["ID"]." and status = 8";//查询任务
    #echo $sql;
    out_sql_show_form($sql,$conn);
    echo "当前区域任务：已失败<br>";//7
    $sql = $sqlGetTheAllTaskCount0." and area_id =".$row["ID"]." and status = 7";//查询任务
    #echo $sql;
    out_sql_show_form($sql,$conn);
    echo "当前区域任务：已取消<br>";//3
    $sql = $sqlGetTheAllTaskCount0." and area_id =".$row["ID"]." and status = 3";//查询任务
    #echo $sql;
    out_sql_show_form($sql,$conn);
      
    // 输出表格的行的结尾  
    echo '</tr>';  
}  





?>

<?php
showdownMysql();//关闭数据库
?>
</html>