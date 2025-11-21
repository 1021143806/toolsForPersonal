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

function sqlfindjustone($conn,$select,$from,$know,$a1)//获取对应sql语句查询到的参数test
{
    //function sqlfindjustone($conn,$select,$from,$know,$a1)//获取对应sql语句查询到的参数test
    //数据库$conn，要查找的字段的列$select,要查找的字段的表$form，已知的数据字段的列名$know，已知的数据的字段$a1
    $sql="SELECT $select FROM $from WHERE $know='$a1'ORDER BY $select DESC LIMIT 1";
    //$sql="SELECT $select FROM $from WHERE $know='$a1'";
    //ORDER BY column_name DESC
    $retval = mysqli_query( $conn, $sql );//获取数据
    if(! $retval )
    {   
        die('无法读取数据: ' . mysqli_error($conn));
    } 
    $a2=mysqli_fetch_array($retval, MYSQLI_ASSOC)[$select];
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

function sqlfindFrom_agv_robot_ByDEVICE_CODE($conn,$select,$a1)//获取对应sql语句查询到的参数test
{
    //sqlfindjustone($conn,"DEVICE_IP","agv_robot","DEVICE_CODE",$row["DEVICE_CODE"])
    //优化，需要输入数据库，要取的列名，已知序列号
    //数据库$conn，要查找的字段的列$select,要查找的字段的表$form，已知的数据字段的列名$know，已知的数据的字段$a1
    $from="agv_robot";$know="DEVICE_CODE";
    $sql="SELECT $select FROM $from WHERE $know='$a1'";
    $retval = mysqli_query( $conn, $sql );//获取数据
    if(! $retval )
    {   
        die('无法读取数据: ' . mysqli_error($conn));
    } 
    $a2=mysqli_fetch_array($retval, MYSQLI_ASSOC)[$select];
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

//
//输入数据库和对应查询字段名，sql语句来查询对应数据,遇到没有数据时跳过返回0，有数据返回正确的数据
function sqlfindoneNoFalse($conn,$name,$sql)//获取对应sql语句查询到的参数
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
    $a1='0';
    if($a2 == $null)
    {
        return $a1;
    }
    else
    {
    return $a2;
    }

}



//echo "已成功导入头文件2!"
?>