<?php
/**
 * AGV设备状态显示
 * 通过API获取指定区域的AGV设备状态信息
 */

require_once 'includes/init.php';

// 默认配置
$ip = isset($_GET['ip']) ? $_GET['ip'] : "31";
$area = isset($_GET['area']) ? $_GET['area'] : "2";
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AGV设备状态</title>
    <style>
        body { 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
            background: #f5f5f5;
        }
        h1 { 
            color: #333; 
            border-bottom: 2px solid #007bff; 
            padding-bottom: 10px; 
        }
        .config-form {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .config-form label {
            display: inline-block;
            margin-right: 10px;
        }
        .config-form input[type="text"] {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-right: 20px;
        }
        .config-form input[type="submit"] {
            padding: 8px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .config-form input[type="submit"]:hover {
            background: #0056b3;
        }
        .info {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #007bff;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<h1>AGV设备状态查询</h1>

<div class="config-form">
    <form method="get" action="">
        <label>服务器IP后缀: <input type="text" name="ip" value="<?php echo htmlspecialchars($ip); ?>" placeholder="如: 31"></label>
        <label>区域ID: <input type="text" name="area" value="<?php echo htmlspecialchars($area); ?>" placeholder="如: 2"></label>
        <input type="submit" value="查询">
    </form>
</div>

<div class="info">
    <strong>当前配置:</strong> 服务器IP: 10.68.2.<?php echo htmlspecialchars($ip); ?> | 区域: <?php echo htmlspecialchars($area); ?>
</div>

<?php
// 调用AGV状态显示函数
showAgvInfoOneArea($ip, $area);
?>

<a href="index.html" class="back-link">← 返回首页</a>

</body>
</html>