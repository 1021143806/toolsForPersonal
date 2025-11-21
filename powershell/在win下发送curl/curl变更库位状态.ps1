$response = Invoke-WebRequest -Uri "http://10.68.2.31:7000/ics/stock/update/appStockStatus" `
    -Method Post `
    -ContentType "application/json" `
    -Body "{`n`"qrContent`":`"12345737`",`n`"nodeStatus`":`"0`"`n}"
$response

write('已变更')

 function Pause(){
[System.Console]::Write('按任意键继续...')
[void][System.Console]::ReadKey(1)
}
pause
