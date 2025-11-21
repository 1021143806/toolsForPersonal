<?php
// $ip="31";
// #connectMsqlAgvWms("10.68.2.".$ip);
// connectMsqlAgvWms($ip);
//     getQuestion(1);
 function getQuestion($request){
$sql = "select count(0) from task_group where FROM_UNIXTIME(create_time) >= CURDATE() - INTERVAL 1 MONTH"; // 你的 SQL 查询语句 一个月内任务
out_sql_show_form($sql,$conn);//示例
        // $sql = "select * from fy_cross_model_process"; // 你的 SQL 查询语句 
        // //moveShelfToWLCKToDJS 
        // // 使用示例  
        // echo $conn;
        // if ($conn->connect_error) {  
        //     die('连接失败: ' . $conn->connect_error);  
        // }  
        // $response = sqlfindall($conn, $sql);  
        // 查找完毕之后，把查找到的数据赋值给response下的data字段
        #$response['data'] = $question;
        #$response['status'] = '2';
        #$response['msg'] = 'success';
        #return json_encode($response);
        return json_encode($response);
        #showdownMysql();
}
?>