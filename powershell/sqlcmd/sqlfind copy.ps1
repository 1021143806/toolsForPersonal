# 导入 Microsoft.Data.SqlClient 命名空间  
Add-Type -AssemblyName Microsoft.Data.SqlClient  
  
# 定义数据库连接字符串  
$connectionString = "Server=172.19.31.186;Database=aaa1;User Id=a2;Password=Qq13235202993;"  
  
# 创建数据库连接对象  
$connection = New-Object Microsoft.Data.SqlClient.SqlConnection $connectionString  
  
try {  
    # 打开数据库连接  
    $connection.Open()  
  
    # 定义 SQL 查询语句  
    $sqlQuery = "SELECT * FROM 111" # 替换为你的表名  
  
    # 创建 SQL 命令对象  
    $command = New-Object Microsoft.Data.SqlClient.SqlCommand $sqlQuery, $connection  
  
    # 执行查询并获取结果集  
    $reader = $command.ExecuteReader()  
  
    # 遍历结果集并输出每一行  
    while ($reader.Read()) {  
        # 假设你的表有两列，分别是 Id 和 Name  
        $id = $reader["Id"]  
        $name = $reader["Name"]  
        Write-Host "ID: $id, Name: $name"  
    }  
  
    # 关闭结果集和连接  
    $reader.Close()  
    $connection.Close()  
}  
catch {  
    # 输出错误信息  
    Write-Host "Error: $($_.Exception.Message)"  
}  
finally {  
    # 确保连接被关闭  
    if ($connection.State -eq 'Open') {  
        $connection.Close()  
    }  
}