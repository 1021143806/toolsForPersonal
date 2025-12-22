<?php
/**
 * 数据库连接工具类
 * Database Connection Helper
 */

// 定义全局变量
global $dbhost,  // mysql服务器主机地址
    $dbuser,     // mysql用户名
    $dbpass,     // mysql用户名密码
    $conn,       // 当前连接数据库
    $ip,
    $ip1,
    $retval,
    $result;

/**
 * 连接AGV数据库（带信息输出）
 * @param string $ip IP地址或IP最后一段
 * @return mysqli 数据库连接对象
 */
function connectMsqlAgvWms($ip)
{
    global $dbhost, $dbuser, $dbpass, $conn, $ip1;
    
    $ip1 = $ip;
    echo mb_strlen($ip1, 'UTF-8');
    
    if (mb_strlen($ip1, 'UTF-8') < 4) {
        $dbhost = '10.68.2.';  // mysql服务器主机地址简写
    } else {
        $dbhost = '';  // 完整ip地址
    }
    
    $dbuser = 'wms';
    $dbpass = 'CCshenda889';
    
    $conn = mysqli_connect($dbhost . $ip, $dbuser, $dbpass);
    if (!$conn) {
        die('Could not connect: ' . mysqli_error($conn));
    }
    
    echo "数据库 $ip1 连接成功！<br>";
    mysqli_select_db($conn, 'wms');
    mysqli_query($conn, "set names utf8");
    
    return $conn;
}

/**
 * 连接AGV数据库（静默模式）
 * @param string $ip IP地址或IP最后一段
 * @return mysqli 数据库连接对象
 */
function connectMsqlAgvWmsNoINFO($ip)
{
    global $dbhost, $dbuser, $dbpass, $conn, $ip1;
    
    $ip1 = $ip;
    
    if (strlen($ip1) < 4) {
        $dbhost = '10.68.2.';
    } else {
        $dbhost = '';
    }
    
    $dbuser = 'wms';
    $dbpass = 'CCshenda889';
    
    $conn = mysqli_connect($dbhost . $ip, $dbuser, $dbpass);
    if (!$conn) {
        die('Could not connect: ' . mysqli_error($conn));
    }
    
    mysqli_select_db($conn, 'wms');
    mysqli_query($conn, "set names utf8");
    
    return $conn;
}

/**
 * 连接其他数据库
 * @param string $ip IP地址
 * @param string $dbuser 用户名
 * @param string $dbpass 密码
 * @param string $MySQL 数据库名
 * @return mysqli 数据库连接对象
 */
function connectMySQLAll($ip, $dbuser, $dbpass, $MySQL)
{
    global $dbhost, $conn, $ip1;
    
    $ip1 = $ip;
    
    if (strlen($ip1) < 4) {
        $dbhost = '10.68.2.';
    } else {
        $dbhost = '';
    }
    
    $conn = mysqli_connect($dbhost . $ip, $dbuser, $dbpass);
    if (!$conn) {
        die('Could not connect: ' . mysqli_error());
    }
    
    mysqli_select_db($conn, $MySQL);
    mysqli_query($conn, "set names utf8");
    
    return $conn;
}

/**
 * 关闭数据库连接（带信息输出）
 */
function showdownMysql()
{
    global $dbhost, $conn, $ip1;
    mysqli_close($conn);
    echo('成功关闭数据库' . $dbhost . $ip1);
}

/**
 * 关闭数据库连接（静默模式）
 */
function showdownMysqlNoINFO()
{
    global $conn;
    mysqli_close($conn);
}

/**
 * 查询表数据
 * @param string $table 表名
 */
function catTheSqlTable($table)
{
    global $conn, $retval;
    
    $sql = 'SELECT * FROM ' . $table;
    mysqli_select_db($conn, 'wms');
    $retval = mysqli_query($conn, $sql);
    
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    
    mysqli_query($conn, "set names utf8");
    
    echo '<h2> MySQL WHERE 子句测试</h2>';
    echo '<table border="1"><tr><td>ID</td><td>设备序列号</td><td>设备IP</td><td>设备型号</td></tr>';
    
    while ($row = mysqli_fetch_array($retval, MYSQLI_ASSOC)) {
        echo "<tr><td> {$row['ID']}</td> " .
            "<td>{$row['DEVICE_CODE']} </td> " .
            "<td>{$row['DEVICE_IP']} </td> " .
            "<td>{$row['DEVICETYPE']} </td> " .
            "</tr>";
    }
}

/**
 * 查询表数据（自定义列）
 * @param string $table 表名
 * @param string $a1 列名1
 * @param string $a2 列名2
 * @param string $a3 列名3
 * @param string $a4 列名4
 */
function catTheSqlTable2($table, $a1, $a2, $a3, $a4)
{
    global $conn, $retval;
    
    $sql = 'SELECT * FROM ' . $table;
    mysqli_select_db($conn, 'wms');
    $retval = mysqli_query($conn, $sql);
    
    if (!$retval) {
        die('无法读取数据: ' . mysqli_error($conn));
    }
    
    mysqli_query($conn, "set names utf8");
    
    echo '<h2> MySQL WHERE 子句测试</h2>';
    echo '<table border="1"><tr><td>' . $a1 . '</td><td>' . $a2 . '</td><td>' . $a3 . '</td><td>' . $a4 . '</td></tr>';
    
    while ($row = mysqli_fetch_array($retval, MYSQLI_ASSOC)) {
        echo "<tr><td> {$row[$a1]}</td> " .
            "<td>{$row[$a2]} </td> " .
            "<td>{$row[$a3]} </td> " .
            "<td>{$row[$a4]} </td> " .
            "</tr>";
    }
}
?>