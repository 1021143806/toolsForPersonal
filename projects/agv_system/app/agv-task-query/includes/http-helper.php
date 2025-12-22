<?php
/**
 * HTTP请求帮助函数
 * HTTP Request Helper Functions
 */

/**
 * 发送POST请求
 * @param string $url 请求地址
 * @param string $data_string JSON数据字符串
 * @return array [状态码, 响应内容]
 */
function http_post_data($url, $data_string)
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        "Content-Type: application/json; charset=utf-8",
        "Content-Length: " . strlen($data_string)
    ));
    ob_start();
    curl_exec($ch);
    $return_content = ob_get_contents();
    ob_end_clean();
    $return_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    return array($return_code, $return_content);
}

/**
 * 获取AGV状态数据
 * @param string $ip 服务器IP最后一段
 * @param string $area 区域ID
 * @return array AGV设备数据数组
 */
function GetAGVStatus($ip, $area)
{
    $url = "http://10.68.2." . $ip . ":7000/ics/out/device/list/deviceInfo";
    $param = array('areaId' => "$area", 'deviceType' => '0');
    $data = json_encode($param);
    list($return_code, $return_content) = http_post_data($url, $data);
    
    $json = $return_content;
    $agvs = json_decode($json);
    $agvsdata = $agvs->data;
    
    return $agvsdata;
}

/**
 * 显示单个区域的AGV信息
 * @param string $ip 服务器IP最后一段
 * @param string $area 区域ID
 */
function showAgvInfoOneArea($ip, $area)
{
    $agvsdata = GetAGVStatus($ip, $area);
    $agvstatus = array("离线", "空闲", "故障", "初始化中", "任务中", "充电中", "升级中");
    $online = 0;
    
    foreach ($agvsdata as $row) {
        if (@isset($agvstatus[$row->deviceStatus])) {
            echo "deviceCode: " . $row->deviceCode . ", deviceStatus: " . $agvstatus["$row->deviceStatus"] . "<br>";
            if ($row->deviceStatus <> 0) {
                $online++;
            }
        } else {
            echo "deviceCode: " . $row->deviceCode . ", deviceStatus: " . "状态未知" . "<br>";
        }
    }
    echo "该区域在线设备数量为" . $online;
}

/**
 * 显示单个区域的AGV信息（返回数组）
 * @param string $ip 服务器IP最后一段
 * @param string $area 区域ID
 * @return array AGV信息数组
 */
function showAgvInfoOneAreaArr($ip, $area)
{
    $agvsdata = GetAGVStatus($ip, $area);
    $agvstatus = array("离线", "空闲", "故障", "初始化中", "任务中", "充电中", "升级中");
    $online = 0;
    $result = array();
    
    foreach ($agvsdata as $row) {
        if (@isset($agvstatus[$row->deviceStatus])) {
            $result[] = array(
                'deviceCode' => $row->deviceCode,
                'deviceStatus' => $agvstatus[$row->deviceStatus]
            );
            if ($row->deviceStatus <> 0) {
                $online++;
            }
        } else {
            $result[] = array(
                'deviceCode' => $row->deviceCode,
                'deviceStatus' => '状态未知'
            );
        }
    }
    
    return array(
        'devices' => $result,
        'onlineCount' => $online
    );
}
?>