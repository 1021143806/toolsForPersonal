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

    //sqlfindjustone($conn,"DEVICE_IP","agv_robot","DEVICE_CODE",$row["DEVICE_CODE"])
    //优化，需要输入数据库，要取的列名，已知序列号
    //数据库$conn，要查找的字段的列$select,要查找的字段的表$form，已知的数据字段的列名$know，已知的数据的字段$a1