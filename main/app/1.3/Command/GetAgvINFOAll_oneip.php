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
//http://10.68.32.185:8088/%E6%8B%89%E5%8F%96%E4%BF%A1%E6%81%AF/%E7%89%88%E6%9C%AC/1.3new/Command/GetAgvINFOAll_oneip.php?ip=9
//$ip="31";

$ip=$_GET["ip"];//ip地址
$arr;
$Statistics=array(
//$Statistics统计所有设备数量
//服务器区域  设备状态1，设备状态2，设备状态3
"column_names"=>array("areaId","AGVStatus","count")
);
$agvstatus=array("0离线","1空闲","2故障","3初始化中","4任务中","5充电中","6升级中");
header("Content-type:application/json;charset=utf-8");//utf8格式
//获取所有区域
$arrbms_area = SQLfindtoArr($ip,$sqlgetbms_area);
$arr[1]=$arrbms_area;//获取区域表
$data=$arrbms_area["data"];//获取数据并转为区域表数组
//print_r($data);       
foreach ($data as $row){//轮询区域，每个区域执行一次
    #$ip="$ip";
    $area=$row["ID"];
    //showAgvInfoOneArea($ip,$area);
    $var=$data[$area]['AgvStatus']=GetAGVStatus($ip,$area);//每个对应区域的设备数据
    //print_r($var);
    foreach ($var as $row){//轮询设备，每个设备执行一次查询状态
        //$rowarr=array($row);
        //print_r($row);
        //if(@$row -> deviceStatus < -1){continue;};
        @$varstatus=$row -> deviceStatus;
        //$varstatus++;
        //echo $varstatus;
        //echo $area;
//$arrStatistics[]=array($area=>array());
        //$arrStatistics[$area][$varstatus]=array("varstatus"=>$varstatus);
        //if($varstatus==Null){continue;};//如果当前区域无设备则跳过此次循环。
        if(!(@$arrStatistics[$area][$varstatus])){//初始化
            //echo "9999";
            $arrStatistics[$area][$varstatus]=0;
        }
        // elseif($varstatus=0){
        //     $arrStatistics[$area]["0"]=0;
        // };
        $arrStatistics[$area][$varstatus]++;//根据设备状态计数加一
        if(!@$arrStatistics["all"][$varstatus]){//初始化All
            $arrStatistics["all"][$varstatus]=0;
        };
        $arrStatistics["all"]["$varstatus"]++;//根据设备状态计数加一
        //echo "jia1";
        //print $arrStatistics[$area][$varstatus];
        //print_r($arrStatistics);
    }
}
?>
<?php
//———————————*输出*——————————————
$arr[0]=$Statistics;
$arr[0]["data"]=$arrStatistics;
$arr[0]["agv_status"]=$agvstatus;
$arr[1]["data"]=$data;
//print_r($arr);//打印数组
$json=json_encode($arr);echo $json;//打印json
//print_r(json_decode($json));
?>