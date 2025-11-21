# 定义文件路径  
$filePath = "2.txt"  
  
# 读取文件内容  
$fileContent = Get-Content -Path $filePath -Raw  
  
# 将文件内容按行分割成数组  
$lines = $fileContent.Split("`n")  
  
# 初始化制表符计数器  
$tabCount = 0  
  
# 遍历每一行  
foreach ($line in $lines) {  
    # 将行内容按制表符分割成数组  
    $parts = $line.Split(" ")
      
    # 如果有多个部分，说明有制表符存在  
    if ($parts.Count -gt 1) {  
        # 累加制表符数量（每个分割点代表一个制表符）  
        $tabCount += ($parts.Count - 1)  
    }  
}  
  
# 输出制表符总数  
Write-Host "Number of tab characters: $tabCount"
