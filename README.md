# 个人工具集 (Personal Tools Collection)

## 📋 项目简介

这是一个综合性的个人工具集仓库，包含了多个实用项目和脚本工具，涵盖Web开发、自动化脚本、AI集成、设备管理等多个领域。

## 🗂️ 目录结构

```
toolsForPersonal/
├── projects/                    # 项目目录
│   ├── flowus_integration/      # FlowUs AI内容生成器
│   ├── agv_system/             # AGV设备管理系统
│   ├── file_upload/            # 文件上传系统
│   └── web/                    # Web相关项目
├── scripts/                     # 脚本工具
│   ├── powershell_scripts/      # PowerShell脚本集合
│   └── shell_scripts/          # Shell脚本集合
├── docs/                        # 文档目录
│   ├── readme_files/           # README文档
│   └── 迁移说明.md             # 目录重构迁移说明
├── .gitignore                   # Git忽略文件
├── nginx.htaccess              # Nginx配置
├── output.txt                  # 输出文件
├── README.en.md                # 英文README
└── README.md                   # 中文README（本文件）
```

## 🚀 主要项目

### 1. FlowUs AI内容生成器
**位置**: `projects/flowus_integration/flowus_siliconflow_integration/`

一个智能内容生成工具，集成了FlowUs和SiliconFlow API：
- 📝 从FlowUs获取日记数据
- 🤖 使用AI生成月报和周报
- 📊 自动生成Mermaid图表和统计分析
- 💾 将生成内容发布到FlowUs页面

**快速开始**:
```bash
cd projects/flowus_integration/flowus_siliconflow_integration
python main.py
```

### 2. AGV设备管理系统
**位置**: `projects/agv_system/`

AGV（自动导引车）设备管理和统计系统，包含多个子项目：

#### 2.1 主管理系统
**位置**: `projects/agv_system/main/`
- 📊 多服务器设备统计
- 📈 设备状态监控
- 📋 任务管理
- 📤 CSV数据导出

**主要功能**:
- 设备信息查询和统计
- 任务分配和跟踪
- 跨服务器数据整合

#### 2.2 跨环境任务模板管理系统
**位置**: `projects/agv_system/app/cross_env_manager/`

一个基于Python Flask的Web应用，用于管理AGV跨环境任务模板：

**核心功能**:
- 🔍 **智能搜索**: 支持模糊搜索任务模板代码和名称
- 📋 **模板详情查看**: 显示模板完整信息及子任务列表
- ✏️ **模板编辑**: 修改模板配置信息
- 📝 **子任务管理**: 编辑子任务详细信息
- 📋 **模板复制**: 基于现有模板创建新模板，自动生成ID后缀
- 📊 **数据统计**: 模板分布、增长趋势等统计分析
- 🎨 **用户友好界面**: 响应式设计，操作直观

**技术特性**:
- 🐍 **Python 3.9.9兼容**: 专门优化支持Python 3.9环境
- 🗄️ **数据库支持**: 使用PyMySQL连接MySQL数据库
- 📁 **配置管理**: 支持TOML配置文件格式
- 🔄 **离线部署**: 提供完整的离线部署解决方案
- 🚀 **Supervisor集成**: 支持进程管理和自动重启

**部署方式**:
1. **在线部署**: 使用标准Python虚拟环境部署
2. **离线部署**: 使用`deploy_iraypleos/`目录中的离线部署脚本
   ```bash
   cd projects/agv_system/app/cross_env_manager
   ./deploy_iraypleos/deploy_iraypleos.sh
   ```

**关键文件**:
- `app.py` - 主应用文件
- `deploy_iraypleos/deploy_iraypleos.sh` - 离线部署脚本
- `vendor_packages3.9/` - Python 3.9兼容的离线依赖包
- `config/env.toml` - 配置文件模板
- `test/DEPLOYMENT_TEST_REPORT.md` - 部署测试报告

### 3. 文件上传系统
**位置**: `projects/file_upload/`

简单高效的文件上传解决方案：
- 📁 多文件上传支持
- 🔒 安全文件处理
- 🌐 Web界面操作

### 4. Web项目
**位置**: `projects/web/`

Web相关的应用和工具集合。

## 🛠️ 脚本工具

### PowerShell脚本
**位置**: `scripts/powershell_scripts/`

包含多种实用脚本：
- 🔗 数据库连接和查询
- 📡 HTTP请求和API调用
- 🖥️ 系统管理和监控
- 📊 数据处理和导出
- 🪟 窗体应用脚本

**常用脚本**:
- `curl变更库位状态.ps1` - 库位状态变更
- `curl下发任务.ps1` - 任务下发
- `sqlfind.ps1` - 数据库查询
- `导出服务的状态.ps1` - 服务状态导出

### Shell脚本
**位置**: `scripts/shell_scripts/`

Linux/Unix环境下的脚本工具集合。

## 📚 文档

- **迁移说明**: [`docs/迁移说明.md`](docs/迁移说明.md) - 详细的目录重构说明
- **项目文档**: `docs/readme_files/` - 各项目的详细文档

## 🔧 环境要求

### Python项目
- Python 3.9+
- 相关依赖包（见各项目的requirements.txt）

### PHP项目
- PHP 7.4+
- MySQL/MariaDB
- Web服务器（Apache/Nginx）

### PowerShell脚本
- Windows PowerShell 5.1+
- 相关模块依赖

## 📦 安装和使用

### 1. 克隆仓库
```bash
git clone https://github.com/your-username/toolsForPersonal.git
cd toolsForPersonal
```

### 2. 运行Python项目
```bash
cd projects/flowus_integration/flowus_siliconflow_integration
pip install -r requirements.txt
python main.py
```

### 3. 运行PowerShell脚本
```powershell
cd scripts/powershell_scripts
.\curl变更库位状态.ps1
```

### 4. 部署PHP项目
将PHP项目目录部署到Web服务器，配置数据库连接即可。

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/toolsForPersonal/issues)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户。

---

**最后更新**: 2026-04-14  
**版本**: 2.1.0 (新增跨环境任务模板管理系统)