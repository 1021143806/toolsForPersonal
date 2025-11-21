<?php
   $json = '{"a":"1","b":"2","c":"3","d":"4","e":"5"}';
echo $json;
echo '</br>';
var_dump(json_decode($json));
echo '</br>';
var_dump(json_decode($json, true));
$arr1=json_decode($json, true);
   //var_dump $arr1;

   function out_oneD_form($oneDArray)
   {  
   $arrlength = count($oneDArray);
   echo '<table border="1">';  
   echo '<tr>';  
   for($x=0;$x<$arrlength;$x++)
   {
       echo '<td>' . $oneDArray[$x] . '</td>';
   }
   // 输出表格的行的结尾  
   echo '</tr>';  
     
   // 输出表格的结尾  
   echo '</table>';  
   }
   echo $arr1["a"];



?>
<h1>111</h1>
<?php


// 假设你有如下的并列 JSON 数据字符串  
$jsonString = '[{"name":"John", "age":30}, {"name":"Jane", "age":25}, {"name":"Doe", "age":40}]';  
  
// 使用 json_decode() 函数将 JSON 字符串转换为 PHP 数组  
$dataArray = json_decode($jsonString, true);  
  
// 现在 $dataArray 是一个包含多个关联数组的 PHP 数组  
foreach ($dataArray as $item) {  
    echo "Name: " . $item['name'] . ", Age: " . $item['age'] . "</br>";  
}  

?>