<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>跨环境任务模板信息</title>
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1, h2 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .info { background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .card { background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #007bff; }
        .info-item { padding: 5px 0; border-bottom: 1px solid #eee; }
        .info-label { color: #666; }
        .info-value { color: #333; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .form-group { margin: 10px 0; }
        label { display: inline-block; min-width: 120px; }
        input[type="text"] { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; }
        input[type="submit"] { background-color: #007bff; color: white; padding: 8px 20px; border: none; border-radius: 4px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #0056b3; }
        .back-link { display: inline-block; margin-top: 20px; color: #007bff; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
        .section { margin-top: 30px; }
    </style>
</head>
<body>

<h1>跨环境任务模板信息</h1>

<div class="info">
    <p>输入大任务模板的ID、编号或名称（三选一）进行查询，系统将展示主表（fy_cross_model_process）和子表（fy_cross_model_process_detail）的配置内容。</p>
    <p>旧版使用参数 <code>idd</code>（模板编号），新版支持多种标识符。</p>
</div>

<form method="get" action="">
    <div class="form-group">
        <label>模板ID：</label>
        <input type="text" name="id" placeholder="数字ID" value="<?php echo htmlspecialchars($_GET['id'] ?? ''); ?>">
        <small>（优先）</small>
    </div>
    <div class="form-group">
        <label>模板编号：</label>
        <input type="text" name="code" placeholder="如：MP001" value="<?php echo htmlspecialchars($_GET['code'] ?? ''); ?>">
    </div>
    <div class="form-group">
        <label>模板名称：</label>
        <input type="text" name="name" placeholder="如：入库流程" value="<?php echo htmlspecialchars($_GET['name'] ?? ''); ?>">
    </div>
    <div class="form-group">
        <label>或通用标识符：</label>
        <input type="text" name="identifier" placeholder="自动识别" value="<?php echo htmlspecialchars($_GET['identifier'] ?? ''); ?>">
    </div>
    <div class="form-group">
        <label>旧版参数 idd：</label>
        <input type="text" name="idd" placeholder="模板编号" value="<?php echo htmlspecialchars($_GET['idd'] ?? ''); ?>">
    </div>
    <input type="submit" value="查询">
</form>

<?php
require_once '../../includes/init.php';

// 获取输入参数
$identifier = $_GET['identifier'] ?? '';
$id = $_GET['id'] ?? '';
$code = $_GET['code'] ?? '';
$name = $_GET['name'] ?? '';
$idd = $_GET['idd'] ?? '';

// 兼容旧版参数 idd
if (!empty($idd) && empty($identifier) && empty($id) && empty($code) && empty($name)) {
    $identifier = $idd;
}

// 如果没有输入，不执行查询
$hasInput = !empty($identifier) || !empty($id) || !empty($code) || !empty($name);
if (!$hasInput) {
    echo '<div class="info">请输入查询条件。</div>';
    echo '<a href="../../index.html" class="back-link">← 返回首页</a>';
    exit;
}

// 确定使用哪个标识符
$usedIdentifier = null;
$type = 'unknown';

if (!empty($id) && is_numeric($id)) {
    $usedIdentifier = intval($id);
    $type = 'id';
} elseif (!empty($code)) {
    $usedIdentifier = trim($code);
    $type = 'code';
} elseif (!empty($name)) {
    $usedIdentifier = trim($name);
    $type = 'name';
} elseif (!empty($identifier)) {
    // 尝试自动判断类型
    if (is_numeric($identifier)) {
        $usedIdentifier = intval($identifier);
        $type = 'id';
    } else {
        // 假设是编号或名称，优先按编号查询
        $usedIdentifier = trim($identifier);
        $type = 'code';
    }
} else {
    echo '<div class="info">缺少标识符参数，请提供 id、code、name 或 identifier。</div>';
    echo '<a href="../../index.html" class="back-link">← 返回首页</a>';
    exit;
}

echo "<div class='info'>查询标识符：<strong>" . htmlspecialchars($usedIdentifier) . "</strong>（类型：{$type}）</div>";

// 连接跨环境数据库（默认使用IP后缀32）
$conn = connectMsqlAgvWmsNoINFO('32');
if (!$conn) {
    echo '<div class="info">数据库连接失败。</div>';
    echo '<a href="../../index.html" class="back-link">← 返回首页</a>';
    exit;
}

// 查询主表 fy_cross_model_process
$where = '';
switch ($type) {
    case 'id':
        $where = "id = " . intval($usedIdentifier);
        break;
    case 'code':
        $where = "model_process_code = '" . mysqli_real_escape_string($conn, $usedIdentifier) . "'";
        break;
    case 'name':
        $where = "model_process_name = '" . mysqli_real_escape_string($conn, $usedIdentifier) . "'";
        break;
}

$sql = "SELECT * FROM fy_cross_model_process WHERE $where LIMIT 1";
$result = mysqli_query($conn, $sql);
if (!$result) {
    echo '<div class="info">查询主表失败: ' . htmlspecialchars(mysqli_error($conn)) . '</div>';
    mysqli_close($conn);
    echo '<a href="../../index.html" class="back-link">← 返回首页</a>';
    exit;
}

$mainRecord = mysqli_fetch_assoc($result);
if (!$mainRecord) {
    echo '<div class="info">未找到匹配的任务模板。</div>';
    mysqli_close($conn);
    echo '<a href="../../index.html" class="back-link">← 返回首页</a>';
    exit;
}

$modelId = $mainRecord['id'];

// 查询子表 fy_cross_model_process_detail
$sql2 = "SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = " . intval($modelId);
$result2 = mysqli_query($conn, $sql2);
$detailRecords = [];
if ($result2) {
    while ($row = mysqli_fetch_assoc($result2)) {
        $detailRecords[] = $row;
    }
} else {
    $detailError = mysqli_error($conn);
}
?>

<div class="section">
    <h2>主表配置（fy_cross_model_process）</h2>
    <div class="card">
        <?php foreach ($mainRecord as $key => $value): ?>
            <div class="info-item">
                <span class="info-label"><?php echo htmlspecialchars($key); ?>：</span>
                <span class="info-value"><?php echo htmlspecialchars($value); ?></span>
            </div>
        <?php endforeach; ?>
    </div>
</div>

<div class="section">
    <h2>子表配置（fy_cross_model_process_detail）</h2>
    <?php if (!empty($detailError)): ?>
        <div class="info">查询子表失败: <?php echo htmlspecialchars($detailError); ?></div>
    <?php elseif (empty($detailRecords)): ?>
        <div class="info">未找到子表记录。</div>
    <?php else: ?>
        <p>共 <?php echo count($detailRecords); ?> 条子任务配置。</p>
        <?php
        // 使用 out_sql_search_form 输出表格
        $detailResult = [
            'column_names' => array_keys($detailRecords[0]),
            'data' => $detailRecords
        ];
        out_sql_search_form($detailResult);
        ?>
    <?php endif; ?>
</div>

<?php mysqli_close($conn); ?>

<br>
<a href="../../index.html" class="back-link">← 返回首页</a>

</body>
</html>