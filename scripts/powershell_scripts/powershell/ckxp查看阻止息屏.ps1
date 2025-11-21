powercfg requests

function Pause(){
    [System.Console]::Write('按任意键继续...')
    [void][System.Console]::ReadKey(1)
    }
    pause



    (Add-Type '[DllImport("user32.dll")]public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name a -Pas)::SendMessage(-1,0x0112,0xF170,2)