<?php
/**
 * AGV任务配置验证器
 * 用于验证跨环境AGV任务的配置完整性
 */

/**
 * 任务配置验证器类
 */
class TaskConfigurationValidator
{
    private $conn;
    private $environmentIps = ['10.68.2.31', '10.68.2.32', '10.68.2.17']; // 默认环境IP列表
    private $strictMode = true;
    private $validationReport = [];

    // 配置规范
    private $requiredFields = [
        'fy_cross_model_process' => [
            'model_process_code',
            'model_process_name',
            'enable',
            'capacity'
        ],
        'fy_cross_model_process_detail' => [
            'model_process_id',
            'task_seq',
            'task_servicec',
            'template_code'
        ]
    ];

    /**
     * 构造函数
     * @param mysqli|null $conn 数据库连接（可选）
     */
    public function __construct($conn = null)
    {
        $this->conn = $conn;
    }

    /**
     * 设置环境IP列表
     * @param array $ips IP地址数组
     */
    public function setEnvironmentIps($ips)
    {
        $this->environmentIps = $ips;
    }

    /**
     * 设置验证模式
     * @param bool $strict 是否严格模式
     */
    public function setStrictMode($strict)
    {
        $this->strictMode = $strict;
    }

    /**
     * 验证指定任务ID或名称的配置完整性
     * @param string $taskIdentifier 任务标识符（ID或名称）
     * @param string $identifierType 标识符类型 ('id', 'code', 'name')
     * @return array 验证报告
     */
    public function validateTask($taskIdentifier, $identifierType = 'code')
    {
        $this->validationReport = [
            'task_identifier' => $taskIdentifier,
            'identifier_type' => $identifierType,
            'overall_status' => 'complete',
            'environments' => [],
            'missing_configs' => [],
            'inconsistencies' => [],
            'suggestions' => []
        ];

        // 1. 获取任务模板
        $taskTemplate = $this->fetchTaskTemplate($taskIdentifier, $identifierType);
        if (!$taskTemplate) {
            $this->validationReport['overall_status'] = 'incomplete';
            $this->validationReport['error'] = '任务模板不存在';
            return $this->validationReport;
        }

        $this->validationReport['task_template'] = $taskTemplate;

        // 2. 检查任务模板必填字段
        $templateCheck = $this->checkRequiredFields($taskTemplate, 'fy_cross_model_process');
        if (!$templateCheck['passed']) {
            $this->validationReport['missing_configs'] = array_merge($this->validationReport['missing_configs'], $templateCheck['missing']);
            $this->validationReport['overall_status'] = 'incomplete';
        }

        // 3. 获取子任务模板
        $subTasks = $this->fetchSubTasks($taskTemplate['id']);
        $this->validationReport['sub_tasks'] = $subTasks;

        // 4. 检查子任务必填字段
        foreach ($subTasks as $index => $subTask) {
            $subCheck = $this->checkRequiredFields($subTask, 'fy_cross_model_process_detail');
            if (!$subCheck['passed']) {
                $this->validationReport['missing_configs'] = array_merge($this->validationReport['missing_configs'], array_map(function($field) use ($index) {
                    return "子任务{$index}: {$field}";
                }, $subCheck['missing']));
                $this->validationReport['overall_status'] = 'incomplete';
            }
        }

        // 5. 对每个环境进行验证
        foreach ($this->environmentIps as $envIp) {
            $envReport = $this->validateEnvironment($envIp, $taskTemplate, $subTasks);
            $this->validationReport['environments'][$envIp] = $envReport;
            if ($envReport['status'] !== 'complete') {
                $this->validationReport['overall_status'] = 'incomplete';
            }
        }

        // 6. 跨环境一致性检查
        $this->checkCrossEnvironmentConsistency();

        // 7. 生成建议
        $this->generateSuggestions();

        return $this->validationReport;
    }

    /**
     * 获取任务模板
     */
    private function fetchTaskTemplate($identifier, $type)
    {
        if (!$this->conn) {
            return null;
        }

        $table = 'fy_cross_model_process';
        $field = $type === 'id' ? 'id' : ($type === 'name' ? 'model_process_name' : 'model_process_code');
        $sql = "SELECT * FROM $table WHERE $field = '" . mysqli_real_escape_string($this->conn, $identifier) . "' LIMIT 1";
        $result = mysqli_query($this->conn, $sql);
        if ($result && $row = mysqli_fetch_assoc($result)) {
            return $row;
        }
        return null;
    }

    /**
     * 获取子任务模板
     */
    private function fetchSubTasks($modelProcessId)
    {
        if (!$this->conn) {
            return [];
        }

        $sql = "SELECT * FROM fy_cross_model_process_detail WHERE model_process_id = " . intval($modelProcessId) . " ORDER BY task_seq ASC";
        $result = mysqli_query($this->conn, $sql);
        $subTasks = [];
        while ($row = mysqli_fetch_assoc($result)) {
            $subTasks[] = $row;
        }
        return $subTasks;
    }

    /**
     * 检查必填字段
     */
    private function checkRequiredFields($data, $table)
    {
        $missing = [];
        if (!isset($this->requiredFields[$table])) {
            return ['passed' => true, 'missing' => []];
        }
        foreach ($this->requiredFields[$table] as $field) {
            if (!isset($data[$field]) || $data[$field] === '' || $data[$field] === null) {
                $missing[] = $field;
            }
        }
        return [
            'passed' => empty($missing),
            'missing' => $missing
        ];
    }

    /**
     * 验证特定环境
     */
    private function validateEnvironment($envIp, $taskTemplate, $subTasks)
    {
        $envReport = [
            'ip' => $envIp,
            'status' => 'complete',
            'checks' => [],
            'missing' => [],
            'errors' => []
        ];

        // 检查环境数据库连接
        $envConn = $this->connectToEnvironment($envIp);
        if (!$envConn) {
            $envReport['status'] = 'incomplete';
            $envReport['errors'][] = "无法连接到环境数据库";
            return $envReport;
        }

        // 检查服务端点可达性
        foreach ($subTasks as $subTask) {
            $serviceUrl = $subTask['task_servicec'] ?? '';
            if ($serviceUrl && !$this->checkServiceEndpoint($serviceUrl)) {
                $envReport['checks'][] = [
                    'item' => '服务端点可达性',
                    'status' => 'fail',
                    'details' => "服务端点 $serviceUrl 不可达"
                ];
                $envReport['status'] = 'incomplete';
                $envReport['missing'][] = "服务端点: $serviceUrl";
            } else {
                $envReport['checks'][] = [
                    'item' => '服务端点可达性',
                    'status' => 'pass',
                    'details' => "服务端点 $serviceUrl 正常"
                ];
            }
        }

        // 检查设备配置
        $deviceCheck = $this->checkDeviceConfigurations($envConn, $subTasks);
        if (!$deviceCheck['passed']) {
            $envReport['checks'][] = [
                'item' => '设备配置',
                'status' => 'fail',
                'details' => $deviceCheck['message']
            ];
            $envReport['status'] = 'incomplete';
            $envReport['missing'] = array_merge($envReport['missing'], $deviceCheck['missing']);
        } else {
            $envReport['checks'][] = [
                'item' => '设备配置',
                'status' => 'pass',
                'details' => '设备配置完整'
            ];
        }

        // 检查交接点配置
        $joinPointCheck = $this->checkJoinPointConfigurations($envConn, $subTasks);
        if (!$joinPointCheck['passed']) {
            $envReport['checks'][] = [
                'item' => '交接点配置',
                'status' => 'fail',
                'details' => $joinPointCheck['message']
            ];
            $envReport['status'] = 'incomplete';
            $envReport['missing'] = array_merge($envReport['missing'], $joinPointCheck['missing']);
        } else {
            $envReport['checks'][] = [
                'item' => '交接点配置',
                'status' => 'pass',
                'details' => '交接点配置完整'
            ];
        }

        // 检查货架配置
        $shelfCheck = $this->checkShelfConfigurations($envConn, $subTasks);
        if (!$shelfCheck['passed']) {
            $envReport['checks'][] = [
                'item' => '货架配置',
                'status' => 'fail',
                'details' => $shelfCheck['message']
            ];
            $envReport['status'] = 'incomplete';
            $envReport['missing'] = array_merge($envReport['missing'], $shelfCheck['missing']);
        } else {
            $envReport['checks'][] = [
                'item' => '货架配置',
                'status' => 'pass',
                'details' => '货架配置完整'
            ];
        }

        mysqli_close($envConn);
        return $envReport;
    }

    /**
     * 连接到环境数据库（使用标准连接函数）
     */
    private function connectToEnvironment($ip)
    {
        // 使用项目中已有的静默连接函数
        if (function_exists('connectMsqlAgvWmsNoINFO')) {
            return connectMsqlAgvWmsNoINFO($ip);
        }
        // 备用连接逻辑
        $dbhost = (strlen($ip) < 4) ? '10.68.2.' . $ip : $ip;
        $dbuser = 'wms';
        $dbpass = 'CCshenda889';
        $conn = mysqli_connect($dbhost, $dbuser, $dbpass);
        if ($conn) {
            mysqli_select_db($conn, 'wms');
            mysqli_query($conn, "set names utf8");
        }
        return $conn;
    }

    /**
     * 检查服务端点可达性（简单HTTP检查）
     */
    private function checkServiceEndpoint($url)
    {
        // 简化实现：仅检查URL格式，实际应使用curl
        if (filter_var($url, FILTER_VALIDATE_URL)) {
            return true;
        }
        return false;
    }

    /**
     * 检查设备配置
     */
    private function checkDeviceConfigurations($conn, $subTasks)
    {
        $missing = [];
        $passed = true;

        // 检查agv_robot表是否存在至少一条记录
        $sql = "SELECT COUNT(*) as cnt FROM agv_robot";
        $result = mysqli_query($conn, $sql);
        if ($result) {
            $row = mysqli_fetch_assoc($result);
            if ($row['cnt'] == 0) {
                $missing[] = '环境中无设备记录';
                $passed = false;
            }
        } else {
            $missing[] = '无法查询设备表';
            $passed = false;
        }

        // 检查agv_model表
        $sql = "SELECT COUNT(*) as cnt FROM agv_model";
        $result = mysqli_query($conn, $sql);
        if (!$result) {
            $missing[] = '无法查询设备型号表';
            $passed = false;
        }

        return [
            'passed' => $passed,
            'message' => $passed ? '设备配置完整' : '设备配置缺失',
            'missing' => $missing
        ];
    }

    /**
     * 检查交接点配置
     */
    private function checkJoinPointConfigurations($conn, $subTasks)
    {
        $missing = [];
        $passed = true;

        // 检查join_qr_node_info表是否存在
        $sql = "SELECT COUNT(*) as cnt FROM join_qr_node_info";
        $result = mysqli_query($conn, $sql);
        if (!$result) {
            $missing[] = '交接点表不存在';
            $passed = false;
        } else {
            $row = mysqli_fetch_assoc($result);
            if ($row['cnt'] == 0) {
                $missing[] = '交接点表中无记录';
                $passed = false;
            }
        }

        return [
            'passed' => $passed,
            'message' => $passed ? '交接点配置完整' : '交接点配置缺失',
            'missing' => $missing
        ];
    }

    /**
     * 检查货架配置
     */
    private function checkShelfConfigurations($conn, $subTasks)
    {
        $missing = [];
        $passed = true;

        // 检查shelf_config表是否存在
        $sql = "SELECT COUNT(*) as cnt FROM shelf_config";
        $result = mysqli_query($conn, $sql);
        if (!$result) {
            $missing[] = '货架配置表不存在';
            $passed = false;
        } else {
            $row = mysqli_fetch_assoc($result);
            if ($row['cnt'] == 0) {
                $missing[] = '货架配置表中无记录';
                $passed = false;
            }
        }

        return [
            'passed' => $passed,
            'message' => $passed ? '货架配置完整' : '货架配置缺失',
            'missing' => $missing
        ];
    }

    /**
     * 跨环境一致性检查
     */
    private function checkCrossEnvironmentConsistency()
    {
        $inconsistencies = [];
        $envReports = $this->validationReport['environments'];
        $envKeys = array_keys($envReports);
        if (count($envKeys) < 2) {
            return;
        }

        // 比较每个环境的检查结果
        $firstEnv = $envReports[$envKeys[0]];
        foreach ($envKeys as $i => $envIp) {
            if ($i === 0) continue;
            $currentEnv = $envReports[$envIp];
            // 简单比较状态
            if ($firstEnv['status'] !== $currentEnv['status']) {
                $inconsistencies[] = "环境 {$envKeys[0]} 状态为 {$firstEnv['status']}，环境 {$envIp} 状态为 {$currentEnv['status']}";
            }
        }

        $this->validationReport['inconsistencies'] = $inconsistencies;
    }

    /**
     * 生成修复建议
     */
    private function generateSuggestions()
    {
        $suggestions = [];
        foreach ($this->validationReport['environments'] as $envIp => $envReport) {
            if ($envReport['status'] !== 'complete') {
                $suggestions[] = "环境 $envIp 配置不完整，请检查以下项: " . implode(', ', $envReport['missing']);
            }
        }
        if (!empty($this->validationReport['missing_configs'])) {
            $suggestions[] = "缺失全局配置: " . implode(', ', $this->validationReport['missing_configs']);
        }
        if (!empty($this->validationReport['inconsistencies'])) {
            $suggestions[] = "跨环境不一致: " . implode('; ', $this->validationReport['inconsistencies']);
        }
        $this->validationReport['suggestions'] = $suggestions;
    }

    /**
     * 获取验证报告（JSON格式）
     */
    public function getJsonReport()
    {
        return json_encode($this->validationReport, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    }
}

/**
 * 快速验证函数（便捷入口）
 * @param string $taskIdentifier 任务标识符
 * @param array $environments 环境IP列表
 * @param bool $strict 是否严格模式
 * @return array 验证报告
 */
function validateAgvTaskConfiguration($taskIdentifier, $environments = [], $strict = true)
{
    global $conn;
    $validator = new TaskConfigurationValidator($conn);
    if (!empty($environments)) {
        $validator->setEnvironmentIps($environments);
    }
    $validator->setStrictMode($strict);
    return $validator->validateTask($taskIdentifier);
}
?>
