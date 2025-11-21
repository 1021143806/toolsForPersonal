<?php
include 'A1head/post.php';
include 'A1head/jsonhead.php';
header("Content-type:application/json;charset=utf-8");//utf8格式

$url = 'http://127.0.0.1:8088/%E6%8B%89%E5%8F%96%E4%BF%A1%E6%81%AF/%E7%89%88%E6%9C%AC/1.3new/Command/GetAgvINFOAll_oneip.php?ip=31';
$data=http_get_data($url);
//print $data;
$datarr=JsonToArr($data);
var_dump($datarr);
print($datarr);
?>