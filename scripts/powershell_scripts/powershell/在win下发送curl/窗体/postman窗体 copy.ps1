Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Net.Http

# 创建主窗体
$form = New-Object System.Windows.Forms.Form
$form.Text = "PowerShell Postman"
$form.Size = New-Object System.Drawing.Size(800, 600)
$form.StartPosition = "CenterScreen"

# 创建发送按钮
$sendButton = New-Object System.Windows.Forms.Button
$sendButton.Text = "Send"
$sendButton.Location = New-Object System.Drawing.Point(50, 460)
$sendButton.Width = 100

$sendButton.Add_Click({
    try {
        $url = $urlTextBox.Text
        $method = $methodComboBox.SelectedItem
        $headers = $headersTextBox.Text -split "`r`n" | ForEach-Object {
            $pair = $_.Split(":", 2)
            [PSCustomObject]@{ Name = $pair[0].Trim(); Value = $pair[1].Trim() }
        } | ConvertTo-Json -Depth 100 | ConvertFrom-Json
        $body = $bodyTextBox.Text

        $httpClient = [System.Net.Http.HttpClient]::new()
        $requestMessage = [System.Net.Http.HttpRequestMessage]::new($method, [Uri]::new($url))

        foreach ($header in $headers) {
            $requestMessage.Headers.Add($header.Name, $header.Value)
        }

        if ($method -eq "POST" -or $method -eq "PUT" -or $method -eq "PATCH") {
            $content = [System.Net.Http.StringContent]::new($body, [System.Text.Encoding]::UTF8, "application/json")
            $requestMessage.Content = $content
        }

        $response = $httpClient.SendAsync($requestMessage).Result
        $responseData = $response.Content.ReadAsStringAsync().Result

        $resultBox = New-Object System.Windows.Forms.TextBox
        $resultBox.Location = New-Object System.Drawing.Point(50, 500)
        $resultBox.Width = 600
        $resultBox.Height = 80
        $resultBox.Multiline = $true
        $resultBox.Text = $responseData
        $resultBox.ReadOnly = $true
        $form.Controls.Add($resultBox)

        $form.Refresh()
    }
    catch {
        [System.Windows.Forms.MessageBox]::Show("Error: $_")
    }
})

# 将控件添加到窗体
$form.Controls.AddRange(@( $sendButton))

# 显示窗体
[void]$form.ShowDialog()