# 提示用户输入变量值
$RCSip = "10.68.2." + $(Read-Host "例：10.68.2.100服务器，请输入100"`n请输入需要变更的服务器ip)  
# 显示用户输入的变量值  
Write-Host "输入的服务器 IP 为： $RCSip"

$httpRCS = "http://" + $RCSip + ":7000/ics/stock/update/appStockStatus"
$response = Invoke-WebRequest -Uri $httpRCS`
    -Method Post `
    -ContentType "application/json" `
    -Body "{`n`"qrContent`":`"12345737`",`n`"nodeStatus`":`"2`"`n}"
#$response

write('已变更')

 function Pause(){
[System.Console]::Write('按任意键继续...')
[void][System.Console]::ReadKey(1)
}
pause