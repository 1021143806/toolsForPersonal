
<?php
//输入
function out_sql_show_form($sql,$conn){
    if ($conn->connect_error) {  
        die('连接失败: ' . $conn->connect_error);  
    }  
    $result = sqlfindall($conn, $sql);  
    //输出完整表
    out_sql_search_form($result);
    return $result;
}
?>
