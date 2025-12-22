<?php
/**
 * SQL查询帮助函数
 * SQL Query Helper Functions
 */

/**
 * 获取对应sql语句查询到的参数
 * @param mysqli $conn 数据库连接
 * @param string $name 字段名
 * @param string $sql SQL语句
 * @return mixed 查询结果
 */
function sqlfind($conn, $name, $sql)
{
    $retval = mysqli_query($conn, $sql);
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    while ($row = mysqli_fetch_array($retval, MYSQLI_ASSOC)) {
        $a2 = $name;
        $a2 = $row[$a2];
    }
    return $a2;
}

/**
 * 获取单条记录的指定字段值
 * @param mysqli $conn 数据库连接
 * @param string $name 字段名
 * @param string $sql SQL语句
 * @return mixed 查询结果
 */
function sqlfindone($conn, $name, $sql)
{
    $retval = mysqli_query($conn, $sql);
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    $a2 = mysqli_fetch_array($retval, MYSQLI_ASSOC)[$name];
    return $a2;
}

/**
 * 根据已知条件查询单个字段
 * @param mysqli $conn 数据库连接
 * @param string $select 要查询的字段
 * @param string $from 表名
 * @param string $know 已知字段名
 * @param string $a1 已知字段值
 * @return mixed 查询结果
 */
function sqlfindjustone($conn, $select, $from, $know, $a1)
{
    $sql = "SELECT $select FROM $from WHERE $know='$a1' ORDER BY $select DESC LIMIT 1";
    $retval = mysqli_query($conn, $sql);
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    $a2 = mysqli_fetch_array($retval, MYSQLI_ASSOC)[$select];
    return $a2;
}

/**
 * 从agv_robot表中根据设备编号查询指定字段
 * @param mysqli $conn 数据库连接
 * @param string $select 要查询的字段
 * @param string $a1 设备编号
 * @return mixed 查询结果
 */
function sqlfindFrom_agv_robot_ByDEVICE_CODE($conn, $select, $a1)
{
    $from = "agv_robot";
    $know = "DEVICE_CODE";
    $sql = "SELECT $select FROM $from WHERE $know='$a1'";
    $retval = mysqli_query($conn, $sql);
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    $a2 = mysqli_fetch_array($retval, MYSQLI_ASSOC)[$select];
    return $a2;
}

/**
 * 获取单条记录（遇到空值返回0）
 * @param mysqli $conn 数据库连接
 * @param string $name 字段名
 * @param string $sql SQL语句
 * @return mixed 查询结果
 */
function sqlfindoneNoFalse($conn, $name, $sql)
{
    $retval = mysqli_query($conn, $sql);
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    $a2 = mysqli_fetch_array($retval, MYSQLI_ASSOC)[$name];
    $a1 = '0';
    if ($a2 == null) {
        return $a1;
    } else {
        return $a2;
    }
}

/**
 * 查询并返回包含列名和数据的数组
 * @param mysqli $conn 数据库连接
 * @param string $sql SQL语句
 * @return array 包含column_names和data的数组
 */
function sqlfindall($conn, $sql)
{
    if ($conn->connect_error) {
        die('连接失败: ' . $conn->connect_error);
    }
    $result = $conn->query($sql);
    if (!$result) {
        die('查询失败: ' . $conn->error);
    }
    
    // 获取列名
    $field_info = $result->fetch_fields();
    $column_names = array_column($field_info, 'name');

    // 获取所有数据
    $data = array();
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }

    return array(
        'column_names' => $column_names,
        'data' => $data
    );
}

/**
 * 获取列名数组
 * @param mysqli $conn 数据库连接
 * @param string $sql SQL语句
 * @return array 列名数组
 */
function sqlfindall_field_info($conn, $sql)
{
    $result = $conn->query($sql);
    if (!$result) {
        die('查询失败: ' . $conn->error);
    }
    $field_info = $result->fetch_fields();
    $column_names = array_column($field_info, 'name');
    return $column_names;
}

/**
 * 获取所有数据行
 * @param mysqli $conn 数据库连接
 * @param string $sql SQL语句
 * @return array 数据数组
 */
function sqlfindall_data($conn, $sql)
{
    $result = $conn->query($sql);
    if (!$result) {
        die('查询失败: ' . $conn->error);
    }
    $data = array();
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
    return $data;
}

/**
 * 打开数据库查询并返回数组然后关闭
 * @param string $ip IP地址
 * @param string $sql SQL语句
 * @return array 查询结果数组
 */
function SQLfindtoArr($ip, $sql)
{
    $conn = connectMsqlAgvWmsNoINFO($ip, $sql);
    $response = sqlfindall($conn, $sql);
    showdownMysqlNoINFO();
    return $response;
}

/**
 * 使用已有连接查询并返回数组
 * @param mysqli $conn 数据库连接
 * @param string $sql SQL语句
 * @return array 查询结果数组
 */
function SQLfindtoArr_conn($conn, $sql)
{
    $response = sqlfindall($conn, $sql);
    return $response;
}
?>