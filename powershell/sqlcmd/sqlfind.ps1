# 假设数据库连接信息
$server = "172.19.31.186"
$database = "aaa1"
$username = "a2"
$password = "Qq13235202993"

# 定义sql查询语句
$sql = "SELECT * FROM 111"

# 使用sqlcmd从数据库获取数据
$result = Invoke-Command -ComputerName $server -ScriptBlock {
    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=$server;Database=$database;User Id=$username;Password=$password;"
    $conn.Open()
    $cmd = New-Object System.Data.SqlClient.SqlCommand
    $cmd.Connection = $conn
    $cmd.CommandText = $sql
    $result = $cmd.ExecuteScalar()
    $conn.Close()
    $result
}

# 输出结果
Write-Host $result