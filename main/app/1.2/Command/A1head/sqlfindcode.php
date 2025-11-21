<?php
$sqlgetbms_area="select ID,NAME from bms_area ";//查询区域名称
$sqlGetTheAllTaskCount0 = "select count(0) from task_group where FROM_UNIXTIME(create_time) >= CURDATE() - INTERVAL 1 MONTH";//查询任务总数
$sqlrobot_usage_report = "select * from robot_usage_report"
?>
