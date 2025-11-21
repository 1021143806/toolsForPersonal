	# 加载MySQL Connector/NET模块

	[void][System.Reflection.Assembly]::LoadWithPartialName("MySql.Data")


# 定义连接字符串
$connectionString = "Server=localhost;Uid=root;Pwd=1;database=test;SslMode=None;"

# 创建数据库连接对象
$connection = New-Object MySql.Data.MySqlClient.MySqlConnection($connectionString)

try {
    # 打开数据库连接
    $connection.Open()
    Write-Host "数据库连接已打开"

    # 定义SQL查询语句
    $query = "SELECT * FROM ` test111` "

    # 创建命令对象
    $command = New-Object MySql.Data.MySqlClient.MySqlCommand($query, $connection)

    # 执行查询并获取结果
    $reader = $command.ExecuteReader()

    # 创建一个窗口来显示结果（这里使用简单的控制台输出）
    Write-Host "从` test111`表中检索到的数据："
    Write-Host "-------------------------"

    # 获取列的数量
    $columnCount = $reader.FieldCount

    # 读取每一行数据
    while ($reader.Read()) {
        # 初始化一个字符串来存储当前行的数据
        $rowData = ""

        # 遍历每一列
        for ($i = 0; $i -lt $columnCount; $i++) {
            # 获取列名
            $columnName = $reader.GetName($i)

            # 获取列值，并将其转换为字符串（如果需要）
            $columnValue = $reader.GetValue($i).ToString()

            # 将列名和列值添加到行数据中
            $rowData += "$columnName : $columnValue | "
        }

        # 移除最后一个多余的 "|"
        $rowData = $rowData.TrimEnd(" | ")

        # 输出当前行的数据
        Write-Host $rowData
        Write-Host "-------------------------"  # 分隔行
    }

    # 关闭数据读取器
    $reader.Close()
}
catch {
    # 捕获并显示任何异常
    Write-Error "发生错误: $_"
}
finally {
    # 确保数据库连接被关闭
    if ($connection.State -eq [System.Data.ConnectionState]::Open) {
        $connection.Close()
        Write-Host "数据库连接已关闭"
    }
}