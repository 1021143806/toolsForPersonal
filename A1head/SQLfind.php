<?php
function sqlfind($conn,$name,$sql)//获取对应sql语句查询到的参数
{
    $retval = mysqli_query( $conn, $sql );//获取数据
    if(! $retval )
    {   
        die('无法读取数据: ' . mysqli_error($conn));
    }
    while($row = mysqli_fetch_array($retval, MYSQLI_ASSOC))
    {
        $a2=$name;$a2=$row[$a2];
        //echo "下发的货架模型222为：".$a2."<br>";
    }
    return $a2;
}
//echo "已成功导入头文件2!"
?>
<?php


//输入数据库和对应查询字段名，sql语句来查询对应数据
function sqlfindone($conn,$name,$sql)//获取对应sql语句查询到的参数
{
    $retval = mysqli_query( $conn, $sql );//获取数据
    if(! $retval )
    {   
        die('无法读取数据: ' . mysqli_error($conn));
    } 
    $a2=mysqli_fetch_array($retval, MYSQLI_ASSOC)[$name];
    /*
    while($row = mysqli_fetch_array($retval, MYSQLI_ASSOC))
    {
        $a2=$name;$a2=$row[$a2];
        //echo "下发的货架模型222为：".$a2."<br>";
    }
    */
    //echo $a2;
    return $a2;
}
//echo "已成功导入头文件2!"
?>