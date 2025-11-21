Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Net.Http

# 创建主窗体
$form = New-Object System.Windows.Forms.Form
$form.Text = "PowerShell Postman"
$form.Size = New-Object System.Drawing.Size(800, 600)
$form.StartPosition = "CenterScreen"

# 创建标签和文本框用于URL输入
$urlLabel = New-Object System.Windows.Forms.Label
$urlLabel.Text = "URL:"
$urlLabel.Location = New-Object System.Drawing.Point(10, 20)
$urlLabel.AutoSize = $true

$urlTextBox = New-Object System.Windows.Forms.TextBox
$urlTextBox.Location = New-Object System.Drawing.Point(50, 20)
$urlTextBox.Width = 600

# 创建标签和组合框用于HTTP方法选择
$methodLabel = New-Object System.Windows.Forms.Label
$methodLabel.Text = "Method:"
$methodLabel.Location = New-Object System.Drawing.Point(10, 60)
$methodLabel.AutoSize = $true

$methodComboBox = New-Object System.Windows.Forms.ComboBox
$methodComboBox.Items.AddRange(@("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"))
$methodComboBox.Location = New-Object System.Drawing.Point(50, 60)
$methodComboBox.Width = 150

# 创建标签和多行文本框用于请求头部输入
$headersLabel = New-Object System.Windows.Forms.Label
$headersLabel.Text = "Headers:"
$headersLabel.Location = New-Object System.Drawing.Point(10, 100)
$headersLabel.AutoSize = $true

$headersTextBox = New-Object System.Windows.Forms.TextBox
$headersTextBox.Location = New-Object System.Drawing.Point(50, 120)
$headersTextBox.Width = 600
$headersTextBox.Height = 80
$headersTextBox.Multiline = $true

# 创建标签和多行文本框用于请求主体输入
$bodyLabel = New-Object System.Windows.Forms.Label
$bodyLabel.Text = "Body:"
$bodyLabel.Location = New-Object System.Drawing.Point(10, 220)
$bodyLabel.AutoSize = $true

$bodyTextBox = New-Object System.Windows.Forms.TextBox
$bodyTextBox.Location = New-Object System.Drawing.Point(50, 240)
$bodyTextBox.Width = 600
$bodyTextBox.Height = 200
$bodyTextBox.Multiline = $true

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
$form.Controls.AddRange(@($urlLabel, $urlTextBox, $methodLabel, $methodComboBox, $headersLabel, $headersTextBox, $bodyLabel, $bodyTextBox, $sendButton))

# 显示窗体
[void]$form.ShowDialog()