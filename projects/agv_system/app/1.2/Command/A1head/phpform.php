<?php  

//以表单输出二维数组
function out_twoD_form($twoDArray)
// 假设这是您的二维数组  
// $twoDArray = array(  
//     array('姓名', '年龄', '性别'),  
//     array('张三', 25, '男'),  
//     array('李四', 30, '女'),  
//     array('王五', 35, '男')  
// );  
{  
// 输出表格的开头  
echo '<table border="1">';  
  
// 遍历二维数组  
foreach ($twoDArray as $row) {  
    // 输出表格的行  
    echo '<tr>';  
      
    // 遍历当前行的每个元素  
    foreach ($row as $cell) {  
        // 输出表格的单元格  
        echo '<td>' . $cell . '</td>';  
    }  
      
    // 输出表格的行的结尾  
    echo '</tr>';  
}  
  
// 输出表格的结尾  
echo '</table>';  
}




//以表单输出一维数组
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


//以表单输出数据库查询到的内容(三维数组)$result = sqlfindall($conn, $sql); 
function out_sql_search_form($SQLSearchArray)
{
$oneDArray = $SQLSearchArray['column_names'];
$twoDArray = $SQLSearchArray['data'];
//输出列
$arrlength = count($oneDArray);
echo '<table border="1">';  
echo '<tr>';  
for($x=0;$x<$arrlength;$x++)
{
    echo '<td>' . $oneDArray[$x] . '</td>';
}
// 输出表格的行的结尾  
echo '</tr>';  

//输出行
// 遍历二维数组  
foreach ($twoDArray as $row) {  
    // 输出表格的行  
    echo '<tr>';  
      
    // 遍历当前行的每个元素  
    foreach ($row as $cell) {  
        // 输出表格的单元格  
        echo '<td>' . $cell . '</td>';  
    }  
      
    // 输出表格的行的结尾  
    echo '</tr>';  
}  

  
// 输出表格的结尾  
echo '</table>';  
}



?>
