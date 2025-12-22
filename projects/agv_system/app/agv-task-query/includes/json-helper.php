<?php
/**
 * JSON处理帮助函数
 * JSON Helper Functions
 */

/**
 * 将数组转换为JSON字符串
 * @param array $arr 数组
 * @return string JSON字符串
 */
function ArrToJson($arr)
{
    return json_encode($arr, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
}

/**
 * 将JSON字符串转换为数组
 * @param string $json JSON字符串
 * @return array 数组
 */
function JsonToArr($json)
{
    return json_decode($json, true);
}

/**
 * 输出JSON响应
 * @param array $data 数据
 * @param int $code 状态码
 * @param string $message 消息
 */
function outputJson($data, $code = 200, $message = 'success')
{
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array(
        'code' => $code,
        'message' => $message,
        'data' => $data
    ), JSON_UNESCAPED_UNICODE);
}

/**
 * 输出成功JSON响应
 * @param array $data 数据
 * @param string $message 消息
 */
function jsonSuccess($data, $message = 'success')
{
    outputJson($data, 200, $message);
}

/**
 * 输出错误JSON响应
 * @param string $message 错误消息
 * @param int $code 错误码
 */
function jsonError($message, $code = 500)
{
    outputJson(null, $code, $message);
}
?>