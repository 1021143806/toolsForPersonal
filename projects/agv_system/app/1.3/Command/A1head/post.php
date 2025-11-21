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
function http_get_data($url)
{
    //$url = 'http://127.0.0.1:8088/%E6%8B%89%E5%8F%96%E4%BF%A1%E6%81%AF/%E7%89%88%E6%9C%AC/1.3new/Command/GetAgvINFOAll_oneip.php?ip=1';
    $data=file_get_contents($url);
    if($data === false){
        //请求失败，处理错误
        die('failed to get data');
    }
    //echo $data;
	return $data;
}
?>