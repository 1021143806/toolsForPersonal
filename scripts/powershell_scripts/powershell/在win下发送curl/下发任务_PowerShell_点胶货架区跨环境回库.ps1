write('该脚本用于输入 任务编号 需回库的跨环境货架 来下发跨环境任务并上报 8 给 NOC
输入对应任务编号后按回车 如：DHC2-90321FFBE8EA49E48600E7FB9F0562F5
输入对应货架号后按回车 如：D0002')

#下发参数
$orderId = Read-Host "异常跨环境任务 orderId"
$shelfNumber = Read-Host "需要下发回库的货架"

#$ip = Read-Host "需要变更库位状态的服务器ip，如10.68.2.31 服务器，则输入31"
#$qrContent = Read-Host "需要变更库位状态的点"
#$nodeStatus = Read-Host "0 空库位 2 满库位"

#$body = "{`n`"qrContent`":`"$qrContent`",`n`"nodeStatus`":`"$nodeStatus`"`n}"
#下发参数结束


#上报NOC异常信息恢复
$body = "{`n    `"orderId`": `"$orderId`",`n    `"processRate`": `"1/1`",`n    `"status`": 8`n}"
$url = "http://10.1.107.31:5000/Api/RCS/PushJobStatus"
$response = Invoke-WebRequest -Uri $url `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
$response
write ('已上报')
#上报结束




#下发回库任务
#$ip = Read-Host "需要变更库位状态的服务器ip，如10.68.2.31 服务器，则输入31"
$ip = "27"
#$qrContent = Read-Host "需要变更库位状态的点"
#$nodeStatus = Read-Host "0 空库位 2 满库位"
$dateTimeString = Get-Date -Format "MMddyyyyhhmm"
$orderid = "powershell$dateTimeString"
#$shelfNumber = "AG051058"
$body = "{`"modelProcessCode`":`"HYBLBTODJH`",`"priority`":6,`"orderId`":`"$orderid`",`"fromSystem`": `"powershell`",`"taskOrderDetail`":{`"taskPath`":`"`",`"deviceNum`":`"`",`"shelfNumber`":`"$shelfNumber`"}}"
$url = "http://10.68.2.$ip`:7000/ics/taskOrder/addTask"

$response = Invoke-WebRequest -Uri $url `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
$response
#下发回库任务结束

#流程结束
write('已下发回库任务')

 function Pause(){
[System.Console]::Write('按任意键继续...')
[void][System.Console]::ReadKey(1)
}
pause
