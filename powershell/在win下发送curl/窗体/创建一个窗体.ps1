Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

#创建form
$form = New-Object System.Windows.Forms.Form
$form.Text = 'enter'  #窗口的标题
$form.Size = New-Object System.Drawing.Size(1200,700)#窗口的大小
$form.StartPosition = 'CenterScreen'#让窗体每次加载时都自动显示在屏幕中间

#添加确定按钮
$okButton = New-Object System.Windows.Forms.Button
$okButton.Location = New-Object System.Drawing.Point(75,120)#按钮位置
$okButton.Size = New-Object System.Drawing.Size(75,30)#按钮大小
$okButton.Text = 'OK'
#$okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK  #获取或设置一个值，该值在单击按钮时返回到父窗体。
$form.AcceptButton = $okButton
$form.Controls.Add($okButton)

#取消按钮
$cancelButton = New-Object System.Windows.Forms.Button
$cancelButton.Location = New-Object System.Drawing.Point(180,120)
$cancelButton.Size = New-Object System.Drawing.Size(75,30)
$cancelButton.Text = 'Cancel'
$cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$form.CancelButton = $cancelButton
$form.Controls.Add($cancelButton)

#标签文本用于描述你希望用户提供的信息
$label = New-Object System.Windows.Forms.Label
$label.Location = New-Object System.Drawing.Point(10,20)
$label.Size = New-Object System.Drawing.Size(280,20)
$label.Text = '请输入'
$form.Controls.Add($label)

##添加文本框
$textBox = New-Object System.Windows.Forms.TextBox
$textBox.Location = New-Object System.Drawing.Point(10,40)
$textBox.Size = New-Object System.Drawing.Size(260,20)
$form.Controls.Add($textBox)

$form.Topmost = $true #将 Topmost 属性设置为 $True，以强制此窗口在其他已打开的窗口和对话框之上打开。

$form.Add_Shown({$textBox.Select()})
$result = $form.ShowDialog() #在 Windows 中显示该窗体。

if ($result -eq [System.Windows.Forms.DialogResult]::OK)
{
    $x = $textBox.Text
    $x
}
#$result = $form.ShowDialog() #在 Windows 中显示该窗体。