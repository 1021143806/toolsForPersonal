$test = Get-Content -Path ".\2.txt"
$test

function ConvertTxtToMermaid($inputFile, $outputFile) {  
    # 初始化变量  
    $mermaidCode = @"  
```mermaid  
graph TB  
"@  
    $currentLevel = 0  
    $indentRegex = '^\s+'  
    #在正则表达式中，^\s+ 是一个模式，用于匹配以空白字符开始的行。下面是这个模式的各个部分的解释：
# ^：表示行的开始。在正则表达式中，^ 是一个元字符，用于匹配输入字符串的开始位置或行的开始位置。
# \s：表示空白字符。\s 是一个特殊的字符类，它匹配任何空白字符，包括空格、制表符、换页符等。
# +：表示匹配前面的元素一次或多次。在这个例子中，+ 作用于 \s，意味着它会匹配一个或多个连续的空白字符。
  
    # 读取输入文件的每一行  
    Get-Content -Path $inputFile | ForEach-Object {  
        $line = $_.Trim()  #trim修剪
  
        # 跳过空行  
        if ($line -eq '') {  
            return  
        }  
  
        # 使用 Regex 对象来查找缩进  
        $regex = New-Object System.Text.RegularExpressions.Regex($indentRegex)  
        $matches = $regex.Matches($line)  
  
        # 根据匹配项的数量确定缩进级别  
        $indent = $matches.Count  
  
        # 根据缩进级别构建Mermaid代码  
        for ($i = 0; $i -lt $indent; $i++) {  
            $mermaidCode += "    "  
        }  
        $mermaidCode += $line + " --> "  
  
        # 更新当前层级  
        $currentLevel = $indent  
    }  
  
    # 移除最后一行的" --> "  
    $mermaidCode = $mermaidCode.TrimEnd(" --> ")  
  
    # 添加Mermaid代码的结束标记  
    $mermaidCode += @"
"@
# 将生成的Mermaid代码写入输出文件  
$mermaidCode | Set-Content -Path $outputFile
}
Write-Output ("输出$test")

ConvertTxtToMermaid   -inputFile '.\5.txt' -outputFile '.\3.md'