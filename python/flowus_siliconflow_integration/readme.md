# FlowUs AI 内容生成器

一个自动化工具，用于从 FlowUs 页面和多维表中提取内容，通过 AI 生成新的内容，并自动创建到 FlowUs 中。

## 功能特性

- 🔄 **自动内容提取**：从 FlowUs 页面和多维表中提取文本内容及子块信息
- 🗃️ **多维表支持**：自动检测并提取数据库中的记录及多维表信息
- 🤖 **AI 内容生成**：使用硅基流动 API 生成智能回复
- 📝 **自动页面创建**：在指定父页面下自动创建新页面
- 🔗 **关联内容处理**：支持处理关系属性和关联页面
- 📊 **完整属性支持**：支持所有 FlowUs 属性类型（单选、多选、复选框、日期等）
- ⏰ **时间过滤**：可筛选最近指定天数的记录
- 💾 **本地日志**：原始内容保存到本地文件，保护隐私
- 🌐 **API 整合**：同时获取页面信息 (/v1/pages) 和子块信息 (/v1/blocks/children)

## 安装要求

### 系统要求
- Python 3.7+
- 有效的 FlowUs 账户和 API Token
- 硅基流动 API Token

### 安装依赖
```bash
pip install toml
```

## 配置说明

### 1. 配置文件 (config.toml)

创建 `config.toml` 文件：

```toml
# FlowUs API 配置
[flowus]
# FlowUs API Token（从 FlowUs 集成设置中获取）
token = "Bearer your_flowus_token_here"
# 要读取的 FlowUs 页面 URL
url = "https://flowus.cn/your-workspace/your-page-id"
# 新页面创建的父页面 ID
parent_page_id = "parent-page-id-here"

# 硅基流动 API 配置
[siliconflow]
# 硅基流动 API Token
token = "Bearer your_siliconflow_token_here"
# 使用的 AI 模型
model = "deepseek-ai/DeepSeek-V3.2-Exp"

# 输出配置
[output]
# 本地保存的 Markdown 文件名
filename = "1.md"
# 原始数据日志文件名
log_file = "data.log"

# API 请求设置
[api_settings]
# 最大 token 数
max_tokens = 8000
# 温度参数，控制生成文本的随机性 (0.0-1.0)
temperature = 0.7
# Top-p 采样参数 (0.0-1.0)
top_p = 0.7
# Top-k 采样参数
top_k = 50
# 频率惩罚参数
frequency_penalty = 0.5

# 新页面配置
[new_page]
# 新页面标题
title = "AI生成内容"
# 新页面图标
icon_emoji = "🤖"

# 块内容设置
[block_settings]
# 是否在 FlowUs 页面中包含原始输入内容
include_source = false
# 是否包含元数据信息
include_metadata = true
# 文本颜色
text_color = "default"
# 背景颜色
background_color = "default"

# 数据库配置
[database]
# 是否启用数据库功能
enabled = true
# 最大记录数
max_records = 50
# 是否包含属性信息
include_properties = true
# 是否过滤最近记录
filter_recent = true
# 最近天数筛选
recent_days = 30
# 是否包含提及的数据库
include_mentioned = true
# 是否获取关联关系内容
fetch_relations = true
# 最大关联深度
max_relation_depth = 1
```

### 2. 获取 API Token

#### FlowUs Token
1. 登录 FlowUs 账户
2. 进入「设置」→「集成」
3. 创建新的集成应用
4. 复制生成的 API Token

#### 硅基流动 Token
1. 访问 [硅基流动官网](https://siliconflow.cn/)
2. 注册账户并登录
3. 在控制台中获取 API Token

## 使用方法

### 基本使用
```bash
python main.py
```

### 自定义配置文件
```bash
python main.py --config custom_config.toml
```

### 工作流程
1. **读取配置**：加载 TOML 配置文件
2. **获取页面内容**：从指定 FlowUs URL 提取内容
例：
   1. 先从日记多维表页面（175409ac-4530-4b1e-b71f-4613b13b24b6）获取数据，通过配置文件中配置的日期，通过分页获取的方式进行筛选获取多维表记录。
   2. 获取到的其中一条数据页面 id（78ee0d72-6d79-4f10-a61a-3b036cf1ed2f）读取其中返回的各种信息以及页面下面的文本内容。其中存在‘问题记录总表链接‘（可能为其他名称，其他链接 id 等均需要有获取）包含了页面 id 的链接，页面 id1（5f6d3fef-877a-44ca-ab0a-a8af94e083be）页面 id2（714b7f9a-00ea-4ca4-9280-9f2ca0273ca7）
   3. 通过获取 id1 与 id2，继续获取这两个多维表页面的各种信息以及页面下面的各种内容，如表格，富文本等块的信息，结束最初该页面 id （78ee0d72-6d79-4f10-a61a-3b036cf1ed2f）的获取流程
   4. 整理获取到的数据
   5. 继续从日记页面 id（175409ac-4530-4b1e-b71f-4613b13b24b6）获取下一条记录的详细信息。
1. **处理数据库**：检测并提取关联的多维表数据
   1. 一个页面需要获取两次数据，要调用两个接口
      1. https://api.flowus.cn/v1/pages/6a1c1dc2-3f18-4f03-a2dc-118d7ab59746
      用于获取页面信息
      2. https://api.flowus.cn/v1/blocks/6a1c1dc2-3f18-4f03-a2dc-118d7ab59746/children
      用于获取页面内的各种块中的信息
      3. 如果页面获取失败，那么就跳过获取，打印获取失败的页面 id
2. **生成 AI 内容**：将提取的内容发送到硅基流动 API
3. **创建新页面**：在指定父页面下创建包含 AI 回复的新页面
4. **保存日志**：原始内容保存到本地 `data.log` 文件

## 支持的属性类型

程序支持所有 FlowUs 属性类型：

| 属性类型 | 说明 | 示例 |
|---------|------|------|
| `title` | 标题属性 | 页面标题 |
| `rich_text` | 富文本属性 | 描述内容 |
| `select` | 单选属性 | 状态：已解决 |
| `multi_select` | 多选属性 | 标签：bug, feature |
| `checkbox` | 复选框属性 | 完成：是/否 |
| `date` | 日期属性 | 创建时间：2024-01-01 |
| `number` | 数字属性 | 数量：10 |
| `url` | 链接属性 | 网站：https://example.com |
| `email` | 邮箱属性 | 邮箱：user@example.com |
| `phone_number` | 电话属性 | 电话：1234567890 |
| `people` | 人员属性 | 负责人：用户A |
| `files` | 文件属性 | 附件：document.pdf |
| `relation` | 关联属性 | 关联页面：页面A |
| `formula` | 公式属性 | 计算字段：SUM(字段) |
| `rollup` | 汇总属性 | 汇总数据 |
| `status` | 状态属性 | 项目状态 |

## 输出文件

### data.log
- 包含从 FlowUs 提取的原始内容
- 包括页面文本和数据库记录
- 用于调试和记录

### 1.md
- 包含完整的处理记录
- 包括原始内容、AI 回复和元数据
- 格式化的 Markdown 文件

### FlowUs 新页面
- 只包含 AI 生成的回复内容
- 不包含原始输入信息
- 包含生成元数据

## 高级功能

### 数据库自动检测
- 自动检测页面中嵌入的数据库
- 支持通过提及块引用的数据库
- 自动去重处理

### 时间过滤
- 使用 `after_created_at` 参数高效过滤
- 可配置过滤天数（默认 30 天）
- 服务端过滤，减少数据传输

### 关联内容处理
- 自动处理关系属性
- 获取关联页面的完整信息
- 限制关联深度避免无限递归

## 错误处理

程序包含完善的错误处理机制：

- **配置错误**：配置文件格式错误或缺失
- **API 错误**：网络请求失败或权限不足
- **数据处理错误**：内容解析失败
- **页面创建错误**：权限不足或父页面不存在

## 故障排除

### 常见问题

1. **API Token 错误**
   - 检查 Token 格式是否正确（以 "Bearer " 开头）
   - 确认 Token 是否有相应权限

2. **页面无法访问**
   - 确认页面 URL 是否正确
   - 检查机器人是否有页面访问权限

3. **数据库内容为空**
   - 确认数据库是否有记录
   - 检查时间过滤设置是否过严

4. **AI 生成失败**
   - 检查硅基流动 Token 是否有效
   - 确认 API 配额是否充足

### 日志查看
程序运行时会输出详细日志，包括：
- 配置加载状态
- 页面获取进度
- 数据库处理情况
- AI API 调用状态
- 错误信息

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本页面内容提取和 AI 生成
- 支持多维表数据处理
- 完整的属性类型支持