write('该脚本用于输入 点位 和 空满状态 来变更库位状态，可使用txt直接打开编辑所在服务器的ip，然后运行')

$qrContent = "12345737"
$nodeStatus = "0"
$ip = "27"

$ip = Read-Host "需要变更库位状态的服务器ip，如10.68.2.31 服务器，则输入31"
$qrContent = Read-Host "需要变更库位状态的点"
$nodeStatus = Read-Host "0 空库位 2 满库位"
$body = "{`n`"qrContent`":`"$qrContent`",`n`"nodeStatus`":`"$nodeStatus`"`n}"
$url = "http://10.68.2.$ip`:7000/ics/stock/update/appStockStatus"

$response = Invoke-WebRequest -Uri $url `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response

write('已变更')

 function Pause(){
[System.Console]::Write('按任意键继续...')
[void][System.Console]::ReadKey(1)
}
pause
