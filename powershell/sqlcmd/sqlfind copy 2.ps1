$server = "172.19.31.186"
$database = "aaa1"
$username = "a2"
$password = "Qq13235202993"
  
# 加载 MySQL Connector/NET  
$assemblyPath = "..\..\path\to\MySql.Data.dll"
Add-Type -Path $assemblyPath  
  
# 创建连接字符串  
$connectionString = "server=$server;user=$username;database=$database;port=3306;password=$password"  
  
# 创建连接对象  
$connection = New-Object MySql.Data.MySqlClient.MySqlConnection($connectionString)  
  
try {  
    # 打开连接  
    $connection.Open()  
      
    # 创建命令对象并执行查询  
    $command = New-Object MySql.Data.MySqlClient.MySqlCommand("SELECT * FROM 111", $connection)  
    $reader = $command.ExecuteReader()  
      
    # 读取查询结果  
    while ($reader.Read()) {  
        # 处理每一行数据，例如：  
        $row = New-Object PSObject  
        for ($i = 0; $i -lt $reader.FieldCount; $i++) {  
            $row | Add-Member -NotePropertyName $reader.GetName($i) -NotePropertyValue $reader.GetValue($i)  
        }  
        $row  
    }  
      
    # 关闭连接和读取器  
    $reader.Close()  
    $connection.Close()  
}  
catch {  
    Write-Error "Error: $_"  
}  
finally {  
    # 确保连接被关闭  
    if ($connection.State -eq "Open") {  
        $connection.Close()  
    }  
}

function Pause(){
    [System.Console]::Write('按任意键继续...')
    [void][System.Console]::ReadKey(1)
    }
    pause