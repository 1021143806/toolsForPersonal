<!DOCTYPE html>
<html>

<?php
?>

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
//header("Content-type:application/json;charset=utf-8");
$url = 'http://10.68.2.10:7000/ics/out/device/list/deviceInfo';//请求地址
$param = array('areaId' => '3','deviceType' => '0');//发送的数据
$data = json_encode($param); 
list($return_code, $return_content) = http_post_data($url, $data);//return_code是http状态码
//print_r($return_content);
//exit;
//echo print_r($return_content);
?>

<h1>111</h1>

<?php
// $arr1 = http_post_data($url, $data_string);
// $arr2 = $arr1 [1];
$json=$return_content;
$agvs=json_decode($json);
var_dump($agvs);
?>

<h1>获取AGVdata</h1>
<?php
$agvsdata=$agvs->data;
var_dump($agvsdata);
?>


<h1>设备对象数据</h1>
<?php
var_dump($agvsdata["0"]);
echo "<br>";
?>

<h1>设备是否在线</h1>
<?php
// 现在 $agvdata 是一个包含多个关联数组的 PHP 数组  
foreach ($agvsdata as $row) {  
    echo "deviceCode: " . $row->deviceCode . ", deviceStatus: " . $row->deviceStatus . "<br>";  
}  
?>


</html>