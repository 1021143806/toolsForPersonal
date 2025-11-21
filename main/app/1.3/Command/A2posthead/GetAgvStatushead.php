<?php
function http_post_data($url, $data_string) {
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_URL, $url);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
	curl_setopt($ch, CURLOPT_HTTPHEADER, array(
		"Content-Type: application/json; charset=utf-8",
		"Content-Length: " . strlen($data_string))
	);
	ob_start();
	curl_exec($ch);
	$return_content = ob_get_contents();
	ob_end_clean();
	$return_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
	return array($return_code, $return_content);
}
?>
<?php
function GetAGVStatus($ip,$area){
#header("Content-type:application/json;charset=utf-8");//utf8格式
$url = "http://10.68.2.".$ip.":7000/ics/out/device/list/deviceInfo";//请求地址
$param = array('areaId' => "$area",'deviceType' => '0');//发送的数据
$data = json_encode($param); 
list($return_code, $return_content) = http_post_data($url, $data);//return_code是http状态码
#print_r($return_content);//打印获取到的信息
//exit;
//echo print_r($return_content);

// $arr1 = http_post_data($url, $data_string);
// $arr2 = $arr1 [1];
$json=$return_content;
$agvs=json_decode($json);
#var_dump($agvs);

$agvsdata=$agvs->data;
#var_dump($agvsdata);


#var_dump($agvsdata["0"]);
#echo "<br>";
return $agvsdata;
// 现在 $agvdata 是一个包含多个关联数组的 PHP 数组  
}
function showAgvInfoOneArea($ip,$area)
{
#$ip="31";
$agvsdata=GetAGVStatus($ip,$area);
$agvstatus=array("离线","空闲","故障","初始化中","任务中","充电中","升级中");
$online=0;
foreach ($agvsdata as $row) {
	if(@isset($agvstatus[$row->deviceStatus])){
		echo "deviceCode: " . $row->deviceCode . ", deviceStatus: " . $agvstatus["$row->deviceStatus"] . "<br>";  
	

	if($row->deviceStatus<>0)
	{
		$online++;
	}
}
	else{
		echo "deviceCode: " . $row->deviceCode . ", deviceStatus: " . "状态未知" . "<br>";
			}
}  
echo "该区域在线设备数量为".$online;
}
function showAgvInfoOneAreaArr($ip,$area)
{
#$ip="31";
$agvsdata=GetAGVStatus($ip,$area);
$agvstatus=array("离线","空闲","故障","初始化中","任务中","充电中","升级中");
$online=0;
foreach ($agvsdata as $row) {
	if(@isset($agvstatus[$row->deviceStatus])){
		echo "deviceCode: " . $row->deviceCode . ", deviceStatus: " . $agvstatus["$row->deviceStatus"] . "<br>";  
	

	if($row->deviceStatus<>0)
	{
		$online++;
	}
}
	else{
		echo "deviceCode: " . $row->deviceCode . ", deviceStatus: " . "状态未知" . "<br>";
			}
}  
echo "该区域在线设备数量为".$online;
}
?>