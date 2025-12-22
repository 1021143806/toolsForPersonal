<?php
/**
 * 表单输出帮助函数
 * Form Output Helper Functions
 */

/**
 * 输出SQL查询结果为HTML表格
 * @param array $result 包含column_names和data的查询结果数组
 */
function out_sql_search_form($result)
{
    // 输出表头
    echo '<table border="1" style="border-collapse: collapse; margin: 10px 0;">';
    echo '<tr style="background-color: #f0f0f0;">';
    foreach ($result['column_names'] as $columnName) {
        echo '<th style="padding: 8px; border: 1px solid #ddd;">' . htmlspecialchars($columnName) . '</th>';
    }
    echo '</tr>';

    // 输出数据行
    foreach ($result['data'] as $row) {
        echo '<tr>';
        foreach ($row as $value) {
            echo '<td style="padding: 8px; border: 1px solid #ddd;">' . htmlspecialchars($value) . '</td>';
        }
        echo '</tr>';
    }
    echo '</table>';
}

/**
 * 将查询结果输出为表格（简化版）
 * @param array $result 查询结果数组
 */
function ToForm_sqlfind($result)
{
    // 输出表头
    echo '<table border="1" style="border-collapse: collapse; margin: 10px 0;">';
    echo '<tr style="background-color: #e0e0e0;">';
    foreach ($result['column_names'] as $columnName) {
        echo '<th style="padding: 6px;">' . htmlspecialchars($columnName) . '</th>';
    }
    echo '</tr>';

    // 输出数据行
    foreach ($result['data'] as $row) {
        echo '<tr>';
        foreach ($row as $value) {
            echo '<td style="padding: 6px;">' . htmlspecialchars($value) . '</td>';
        }
        echo '</tr>';
    }
    echo '</table>';
}

/**
 * 输出简单的键值对列表
 * @param array $data 关联数组
 */
function out_key_value_list($data)
{
    echo '<ul style="list-style-type: none; padding: 0;">';
    foreach ($data as $key => $value) {
        echo '<li style="padding: 5px 0;"><strong>' . htmlspecialchars($key) . ':</strong> ' . htmlspecialchars($value) . '</li>';
    }
    echo '</ul>';
}

/**
 * 输出带样式的信息块
 * @param string $title 标题
 * @param string $content 内容
 * @param string $type 类型 (info/success/warning/error)
 */
function out_info_block($title, $content, $type = 'info')
{
    $colors = array(
        'info' => '#e3f2fd',
        'success' => '#e8f5e9',
        'warning' => '#fff3e0',
        'error' => '#ffebee'
    );
    $bgColor = isset($colors[$type]) ? $colors[$type] : $colors['info'];
    
    echo '<div style="background-color: ' . $bgColor . '; padding: 15px; margin: 10px 0; border-radius: 4px;">';
    echo '<h3 style="margin: 0 0 10px 0;">' . htmlspecialchars($title) . '</h3>';
    echo '<p style="margin: 0;">' . htmlspecialchars($content) . '</p>';
    echo '</div>';
}
?>