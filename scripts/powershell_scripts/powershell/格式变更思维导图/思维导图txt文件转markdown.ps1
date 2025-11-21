#用于更新计算节点编号
function mermaidCodeUpdate ($mermaidCode,$A,$Abefore,$line){
$mermaidCode += "$Abefore" + "-->" + "$A("+$line+")
"
}

#转换txt成markdown格式
function ConvertTxtToMermaid($inputFile, $outputFile) {  


# 初始化 Mermaid 思维导图的代码  
$mermaidCode = @"  
``````mermaid

graph TB

"@  
$nowline=0#记录当前所在的行数
$A=0#记录当前思维导图索引位置
# 读取文件内容  
$fileContent = Get-Content -Path $inputFile -Raw  

# 将文件内容按行分割成数组  
$lines = $fileContent.Split("`n")  
# 遍历每一行  
foreach ($line in $lines) {  
    $nowline++
    Write-Output(”当前任务为第 $nowline 行”)



    
    # 初始化制表符计数器  
    $tabCount = 0  
        # 将行内容按制表符分割成数组  
        $parts = $line.Split("`t")
        
        # 如果有多个部分，说明有制表符存在  
        if ($parts.Count -gt 1) {  
            # 累加制表符数量（每个分割点代表一个制表符）  
            $tabCount += ($parts.Count - 1)  
        }  

        # 将行内容按制表符(4个空格）分割成数组  
        $parts = $line.Split(" ")

        # 如果有多个部分，说明有制表符存在  
        if ($parts.Count -gt 1) {  
            # 累加制表符数量（每个分割点代表一个制表符）  
            $tabCount += ($parts.Count - 1)/4  
        }  
    
    # 输出制表符总数  
    Write-Host "Number of 空格 characters: $tabCount"
    
    $line = $line.Trim()#去除空白

    #第一行
    if($nowline -eq 1){
    $mermaidCode += "$A(" + $line + ")
"
    Write-Output(”第一行初始化$mermaidCode”)
    }
    #下一级
    elseif($tabCount -gt $befortabCount){
    $Abefore=$A
    $A=$A*1000+1
    $mermaidCode += "$Abefore" + "-->" + "$A("+$line+")
"
    Write-Output(”下一级已生成$mermaidCode”)
    }
    #同级
    elseif($tabCount -eq $befortabCount){
    $A=$A+1
    $mermaidCode += "$Abefore" + "-->" + "$A("+$line+")
"
    Write-Output(”同级已生成$mermaidCode”)
    }
    #上一级
    else{
    $Abefore=($Abefore - $Abefore % 1000 )/1000
    $A=($A - $A % 1000 )/1000 +1
    #mermaidCodeUpdate -mermaidCode $mermaidCode -A $A -Abefore $Abefore -line $line
    $mermaidCode += "$Abefore" + "-->" + "$A("+$line+")
"
    Write-Output(”上一级已生成$mermaidCode”)
    }
    $befortabCount=$tabCount#记录上一次的位置
}
#Write-Output ("in2")

# 添加 Mermaid 代码的结束标记  
$mermaidCode += @"

``````
"@

# 将生成的Mermaid代码写入输出文件  
$mermaidCode | Set-Content -Path $outputFile

}

$inputFile = ".\2.txt"  
#$inputFile = ".\导出.txt" 
$outputFile = ".\3.md"  


ConvertTxtToMermaid   -inputFile $inputFile -outputFile $outputFile
Write-Output ("输入$inputFile")
Get-Content -Path $inputFile
Write-Output ("输出$outputFile")
Get-Content -Path $outputFile
