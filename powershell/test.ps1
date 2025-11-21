$filePath = ".\创建一个窗体.ps1"

$content = get-content $filePath

Write-Output $content

function Pause(){
    [System.Console]::Write('按任意键继续...')
    [void][System.Console]::ReadKey(1)
    }
    pause