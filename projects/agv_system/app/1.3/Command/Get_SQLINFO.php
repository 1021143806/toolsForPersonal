<?php
include 'A1head/connect.php';
include 'A1head/SQLfind.php';
header("Content-type:application/json;charset=utf-8");//utf8格式
?>
<?php
// $ip='127.0.0.1';
// $dbuser='a1';
// $dbpass='1';
// $MySQL='test';
// $type='1';
$ip=$_GET["ip"];//ip地址
$dbuser=$_GET["dbuser"];//数据库名称
$dbpass=$_GET["dbpass"];//数据库密码
$MySQL=$_GET["MySQL"];//选择数据库
$sql=$_GET["sql"];//sql语句
$type=$_GET["type"];//1返回数组，2返回json
//用法
//http://127.0.0.1:8088/%E6%8B%89%E5%8F%96%E4%BF%A1%E6%81%AF/%E7%89%88%E6%9C%AC/1.3new/Command/Get_SQLINFO.php?ip=127.0.0.1&dbuser=a1&dbpass=1&MySQL=test&sql=SELECT * FROM `test`&type=2
//?ip=10.68.2.31&dbuser=wms&dbpass=CCshenda889&MySQL=wms&sql=SELECT * FROM `agv_robot`&type=2

$conn=connectMySQLAll($ip,$dbuser,$dbpass,$MySQL);
#$sql = "SELECT * FROM `test`";
$response=SQLfindtoArr_conn($conn,$sql);

showdownMysqlNoINFO();
//echo $type;
switch($type){
    case '1':
        print_r($response);
        break;
    case '2':
        $json=json_encode($response);echo $json;
        break;
    case 'arr':
        print_r($response);
        break;
    case 'json':
        $json=json_encode($response);echo $json;
        break;
}

?>