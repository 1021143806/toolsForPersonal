# 函数介绍

## 1. connect.php SQL 链接

### 1.1 function connectMsqlAgvWms($ip) //连接AGV数据库

### 1.2 function showdownMysql()//关闭数据库

## 2. SQLfind.php SQL 语句查找

### 2.1 function sqlfind($conn,$name,$sql) //获取对应sql语句查询到的参数

有循环，全部输出，同navicat

- $cone
- $name
- $sql

示例

### 2.2 function sqlfindone($conn,$name,$sql) //获取对应sql语句查询到的参数

无循环仅输出一行

- $cone
- $name
- $sql

示例

### 2.3 function sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,$select,$a1)//获取对应sql语句查询到的参数test

sqlfindjustone($conn,"DEVICE_IP","agv_robot","DEVICE_CODE",$row["DEVICE_CODE"])
    //优化，需要输入数据库，要取的列名，已知序列号
    //数据库$conn，要查找的字段的列$select,要查找的字段的表$form，已知的数据字段的列名$know，已知的数据的字段$a1

### 2.4 function `sqlfindjustone($conn, $select, $from, $know, $a1)`==获取对应 sql 语句查询到的参数 test==

#### 函数定义

数据库$conn，要查找的字段的列$select,要查找的字段的表$form，已知的数据字段的列名$know，已知的数据的字段$a1

`$sql = "SELECT $select FROM $from WHERE $know='$a1'ORDER BY $select DESC LIMIT 1";`

#### 示例

``` php
$DEVICE_IP=sqlfindjustone($conn,"DEVICE_IP","agv_robot","DEVICE_CODE",$row["DEVICE_CODE"]);
```

#### 返回值

SELECT ==DEVICE_IP== FROM ==agv_robot== WHERE ==DEVICE_CODE== ='==$row["DEVICE_CODE"]=='ORDER BY ==DEVICE_IP== DESC LIMIT 1

`$a2 = mysqli_fetch_array($retval, MYSQLI_ASSOC)[$select];`

`return $a2;`

仅返回A2

数据库中对应查询语句：
![alt text](image.png)
对应返回结果
![alt text](image-1.png)




``` php
//———————————^查询并返回数组^——————————————
//—*打开数据库查询并返回数组然后关闭*—
function SQLfindtoArr($ip, $sql)
{
    $conn = connectMsqlAgvWmsNoINFO($ip, $sql);
    $response = sqlfindall($conn, $sql);
    showdownMysqlNoINFO();
    return $response;
}
function SQLfindtoArr_conn($conn, $sql)
{
    $response = sqlfindall($conn, $sql);
    //showdownMysqlNoINFO();
    return $response;
}
//—^打开数据库查询并返回数组然后关闭^—
```

## 3. SQLform.php SQL 语句查找后输出表格（页面显示）

### 2.5 SQLfindtoArr 查询并返回数组

#### 函数定义

`function out_twoD_form($twoDArray)`
输入二维数组
显示表格；

# 更新记录

## 1.3 版本更新记录

- 新增 readme 帮助文档
- 新增 home 跨环境任务查询 FindTheTaskKua.php