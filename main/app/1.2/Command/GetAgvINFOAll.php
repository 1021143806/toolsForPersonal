<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
include 'A1head/thefirst.php';
include 'A1head/phpform.php';
include 'A1head/show.php';
include 'A1head/posttesthead.php';
include 'A1head/jsonhead.php';
include 'A1head/sqlfindcode.php';
include 'A2posthead/GetAgvStatushead.php';
$ip="31";
$arr;

header("Content-type:application/json;charset=utf-8");//utf8格式

//获取所有区域
$arrbms_area = SQLfindtoArr($ip,$sqlgetbms_area);
$arr[0]=$arrbms_area;
$data=$arrbms_area["data"];
foreach ($data as $row){
    #$ip="$ip";
    $area=$row["ID"];
    //showAgvInfoOneArea($ip,$area);
$data[$area]['AgvStatus']=GetAGVStatus($ip,$area);
}
//print_r($data);
//print_r($agvdata);
//获取一个区域内的所有设备状态
?>
<?php
// $sql = "select count(0) from task_group where FROM_UNIXTIME(create_time) >= CURDATE() - INTERVAL 1 MONTH"; // 你的 SQL 查询语句 一个月内任务
// $arr1 = SQLfindtoArr($ip,$sql);
// $json=json_encode($arr);
?>
<?php
//———————————*输出*——————————————
$arr[0]["data"]=$data;
print_r($arr);//打印数组
//$json=json_encode($arr);echo OutJsonString($json);//打印json
?>