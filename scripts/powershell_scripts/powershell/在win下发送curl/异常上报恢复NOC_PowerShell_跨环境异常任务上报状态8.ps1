write ('该脚本用于手动恢复异常任务未上报 NOC 的问题，输入 orderId 会上报一次状态 8 （已完成）')

#$qrContent = "12345737"
#$nodeStatus = "0"
#$ip = "32"

#$ip = Read-Host "需要变更库位状态的服务器ip，如10.68.2.31 服务器，则输入31"
#$qrContent = Read-Host "需要变更库位状态的点"
#$nodeStatus = Read-Host "0 空库位 2 满库位"
$orderId = Read-Host "异常跨环境任务 orderId"
#$body = "{`n`"qrContent`":`"$qrContent`",`n`"nodeStatus`":`"$nodeStatus`"`n}"
$body = "{`n    `"orderId`": `"$orderId`",`n    `"processRate`": `"1/1`",`n    `"status`": 8`n}"
$url = "http://10.1.107.31:5000/Api/RCS/PushJobStatus"

$response = Invoke-WebRequest -Uri $url `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response

write ('已上报')

 function Pause(){
[System.Console]::Write('按任意键继续...')
[void][System.Console]::ReadKey(1)
}
pause
