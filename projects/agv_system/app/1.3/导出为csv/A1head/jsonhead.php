<?php
function ArrToJson($arr){
    $jsonString = json_encode($arr);//数组转json
    header('Content-Type:application/json');
    return $jsonString;
}
function JsonToArr($json){
    //print $json;
    $arr = json_decode($json,true,512);//数组转json
    //header('Content-Type:application/json');
    //var_dump($arr);
    return $arr;
}
?>