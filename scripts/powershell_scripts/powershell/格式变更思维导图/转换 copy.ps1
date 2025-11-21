# 设置输入和输出文件的路径  
$inputFile = ".\4.txt"  
$outputFile = ".\3.md"  
  
# 读取文本文件内容  
$content = Get-Content -Path $inputFile  
  
# 初始化 Mermaid 思维导图的代码  
$mermaidCode = @"  
```mermaid  
graph TB  
"@  
  
# 按行处理文本文件内容，并构建 Mermaid 代码  
foreach ($line in $content) {  
    # 去除行尾的换行符和可能的空白字符  
    $trimmedLine = $line.TrimEnd()  
      
    # 如果行不是空行，则将其转换为 Mermaid 代码格式  
    if (!$trimmedLine.StartsWith("#")) {  
        # 添加缩进（基于制表符的数量）  
        $indent = $line.Split("\t").Length - 1  
        $indentSpaces = "    " * $indent  
          
        # 处理节点名称和子节点  
        if ($trimmedLine.Contains("[")) {  
            # 提取节点名称和子节点命令  
            $nodeName = $trimmedLine.Substring(0, $trimmedLine.IndexOf('['))  
            $subNode = $trimmedLine.Substring($trimmedLine.IndexOf('[')).TrimStart('[').TrimEnd(']')  
              
            # 添加节点到 Mermaid 代码  
            $mermaidCode += $indentSpaces + "$nodeName --> $subNode\n"  
        }  
        else {  
            # 假设这是顶级节点  
            $mermaidCode += $indentSpaces + "$trimmedLine\n"  
        }  
    }  
}  
  
# 添加 Mermaid 代码的结束标记  
$mermaidCode += @"
"@
mermaidCode|Set-Content-PathoutputFile