#下发任务
#write('该脚本用于输入 任务编号 需回库的跨环境货架 来下发跨环境任务并上报 8 给 NOC
#输入对应任务编号后按回车 如：DHC2-90321FFBE8EA49E48600E7FB9F0562F5
#输入对应货架号后按回车 如：D0002')
#$orderId = Read-Host "异常跨环境任务 orderId"
#$qrContent = Read-Host "需要变更库位状态的点"
#$nodeStatus = Read-Host "0 空库位 2 满库位"
$dateTimeString = Get-Date -Format "MMddyyyyhhmm"#获取orderid随机值
#$ip = Read-Host "需要变更库位状态的服务器ip，如10.68.2.31 服务器，则输入31"
$ip = "17"#下发任务目标服务器
$orderid = "powershell$dateTimeString"#指定orderid
$taskPath = ""#指定点位
$deviceNum = ""#指定设备
$shelfNumber = ""#指定货架
$modelProcessCode = "K_17A2BL2F_to_19A2HXZS1F_back"#任务模板
$body = "{`"modelProcessCode`":`"$modelProcessCode`",`"priority`":6,`"orderId`":`"$orderid`",`"fromSystem`": `"powershell`",`"taskOrderDetail`":{`"taskPath`":`"$taskPath`",`"deviceNum`":`"$deviceNum`",`"shelfNumber`":`"$shelfNumber`"}}"
$url = "http://10.68.2.$ip`:7000/ics/taskOrder/addTask"

Write-Output("$body")

$response = Invoke-WebRequest -Uri $url `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
$response
#下发任务结束

Write-Output('已下发')

 function Pause(){
[System.Console]::Write('按任意键继续...')
[void][System.Console]::ReadKey(1)
}
pause
