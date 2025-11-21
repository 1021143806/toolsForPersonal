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
// $url = 'http://10.68.2.10:7000/ics/out/device/list/deviceInfo';//请求地址
// $param = array('areaId' => '3','deviceType' => '0');//发送的数据
// $data = json_encode($param); 
// list($return_code, $return_content) = http_post_data($url, $data);//return_code是http状态码
//print_r($return_content);
//exit;
//echo print_r($return_content);


$file = 'K:\vscode\php-mini-tools\拉取信息\版本\1.2\Command\test\1.txt'; // 或者使用绝对路径，如 'K:/vscode/php-mini-tools/拉取信息/版本/1.2/Command/test/text.json'  

  
// $return_content=fopen($file,"r");
// echo $return_content;
// echo "<br>";
// var_dump($return_content);

$jsonString = file_get_contents($file);  
if ($jsonString === false) {  
    // 处理文件读取错误  
    echo "无法读取文件: $file";  
    exit;  
}  
  
$return = json_decode($jsonString, true); // 第二个参数设置为 true 来获取数组而不是对象  
if ($return === null && json_last_error() !== JSON_ERROR_NONE) {  
    // 处理 JSON 解码错误  
    echo "JSON 解码失败: " . json_last_error_msg();  
    exit;  
}  
  
// 现在 $data 包含了解码后的 JSON 数据
?>

<h1>获取json并转换成arr和data</h1>

<?php
// $arr1 = http_post_data($url, $data_string);
// $arr2 = $arr1 [1];
// $json=$return_content;
// $var=json_decode($json);
// var_dump($var);
// $arr1=json_decode($json, true);
// var_dump($arr1);
$data=$return["data"];
var_dump($data);
?>
<h1>获取data中的blocks数据块</h1>

<?php
$blocks=$data["blocks"];
var_dump($blocks);
?>

<h1>获取blocks中的所需要的数据</h1>
<?php
$need="a737d507-64d4-4a2e-a7a6-2b97bdb61105";
$needarr=$blocks[$need];
var_dump($needarr);
?>

<h1>获取数据中对应的子数据</h1>
<?php
$subNodes=$needarr["subNodes"];
var_dump($subNodes);
echo "<br>";
echo $subNodes[0];
?>

<h1>333</h1>

<?php
//printf($arr1);

// 现在 $dataArray 是一个包含多个关联数组的 PHP 数组  
foreach ($arr1 as $item) {  
    echo "deviceCode: " . $item["deviceCode"] . ", deviceStatus: " . $item["deviceStatus"] . "\n";  
}  
?>


</html>