# Telegram Auto-Messenger 🚀

一个强大的 Telegram 自动化消息工具，支持多账号管理、定时消息推送、智能监控回复等功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## ✨ 项目特性

- ✅ **多账号管理** - 支持同时运行多个Telegram个人账号
- ✅ **定时消息推送** - 间隔定时向指定频道/群组发送消息
- ✅ **智能监控回复** - 监控用户消息并按关键字自动回复
- ✅ **即发即删功能** - 支持消息自动撤回的闪现消息
- ✅ **配置热重载** - 运行时动态加载配置文件
- ✅ **Docker部署** - 一键容器化部署
- ✅ **完整中文文档** - 详细的设置教程和使用指南
- ✅ **数据库日志** - 完整的操作日志和统计功能
- ✅ **命令行界面** - 友好的CLI管理工具

## 🔧 技术栈

- **Telegram API**: Telethon (稳定可靠的Telegram客户端库)
- **任务调度**: APScheduler (高性能异步任务调度器)
- **数据存储**: SQLite (轻量级数据库)
- **配置管理**: YAML (人性化配置文件格式)
- **容器化**: Docker + Docker Compose
- **命令行**: Click (现代化CLI框架)

## 📦 快速开始

### 方式一：Docker 部署 (推荐)

1. **克隆项目**
```bash
git clone https://github.com/mweoucfeh/telegram-auto-messenger.git
cd telegram-auto-messenger
```

2. **创建配置文件**
```bash
mkdir -p config data sessions logs
cp examples/config.yml config/config.yml
```

3. **编辑配置文件**
```bash
vim config/config.yml
# 填入你的 Telegram API 凭据和配置
```

4. **启动服务**
```bash
cd docker
docker-compose up -d
```

### 方式二：本地安装

1. **安装依赖**
```bash
pip install -r requirements.txt
pip install -e .
```

2. **生成配置文件**
```bash
telegram-auto-messenger config generate
```

3. **编辑配置**
```bash
vim config/config.yml
```

4. **运行程序**
```bash
telegram-auto-messenger run
```

## ⚙️ 配置说明

### 账号配置

获取 Telegram API 凭据：
1. 访问 [my.telegram.org](https://my.telegram.org)
2. 登录你的 Telegram 账号
3. 创建新应用获取 `api_id` 和 `api_hash`

```yaml
accounts:
  - api_id: 12345678
    api_hash: 'your_api_hash_here'
    phone: '+1234567890'
    session_name: 'account1'
    enabled: true
```

### 定时消息配置

```yaml
schedules:
  - name: 'daily_greeting'
    target: '@your_channel'
    message: '🌅 Good morning! Have a great day!'
    interval: 86400  # 24小时
    enabled: true
    auto_delete: false
    delete_after: 60
```

### 监控回复配置

```yaml
monitors:
  - name: 'help_monitor'
    target: '@your_group'
    keywords: ['help', 'support', '帮助']
    reply_message: '👋 Hello! How can I help you?'
    enabled: true
    exact_match: false
```

## 🖥️ 命令行使用

### 基础命令

```bash
# 运行程序
telegram-auto-messenger run

# 查看状态
telegram-auto-messenger status

# 发送测试消息
telegram-auto-messenger send "@channel" "Hello World"

# 立即执行定时任务
telegram-auto-messenger execute schedule_name
```

### 配置管理

```bash
# 验证配置文件
telegram-auto-messenger config validate

# 生成示例配置
telegram-auto-messenger config generate -o config.yml
```

### 定时任务管理

```bash
# 列出所有定时任务
telegram-auto-messenger schedule list

# 暂停定时任务
telegram-auto-messenger schedule pause task_name

# 恢复定时任务
telegram-auto-messenger schedule resume task_name
```

### 监控管理

```bash
# 列出所有监控
telegram-auto-messenger monitor list

# 暂停监控
telegram-auto-messenger monitor pause monitor_name

# 恢复监控
telegram-auto-messenger monitor resume monitor_name
```

## 📂 项目结构

```
telegram-auto-messenger/
├── src/telegram_auto_messenger/    # 源代码
│   ├── core/                      # 核心功能模块
│   │   ├── account.py            # 账号管理
│   │   ├── scheduler.py          # 消息调度
│   │   ├── monitor.py            # 消息监控
│   │   └── manager.py            # 主管理器
│   ├── config/                   # 配置管理
│   ├── utils/                    # 工具模块
│   │   ├── database.py           # 数据库管理
│   │   └── logger.py             # 日志工具
│   └── cli.py                    # 命令行界面
├── docker/                       # Docker 部署文件
├── examples/                     # 配置示例
├── docs/                         # 详细文档
└── tests/                        # 测试文件
```

## 🔐 安全说明

1. **API 凭据安全**：请妥善保管你的 `api_id` 和 `api_hash`
2. **会话文件**：`sessions/` 目录包含登录会话，请勿泄露
3. **生产环境**：建议使用环境变量管理敏感配置
4. **权限控制**：确保机器人账号有足够的权限访问目标频道/群组

## 🚀 高级功能

### 热重载配置

程序支持运行时重载配置文件，无需重启服务：

```yaml
app:
  hot_reload: true
  hot_reload_interval: 30  # 检查间隔（秒）
```

### 闪现消息

支持发送后自动删除的消息：

```yaml
schedules:
  - name: 'flash_message'
    message: '⚡ 这条消息将在30秒后自动删除'
    auto_delete: true
    delete_after: 30
```

### 数据库日志

所有操作都会记录到 SQLite 数据库，支持：
- 消息发送历史
- 定时任务执行记录
- 监控触发日志
- 应用事件日志

## 🛠️ 开发指南

### 本地开发

```bash
# 克隆项目
git clone https://github.com/mweoucfeh/telegram-auto-messenger.git
cd telegram-auto-messenger

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -e .[dev]

# 运行测试
pytest

# 代码格式化
black src/
flake8 src/
```

### 贡献代码

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📖 更多文档

- [详细配置说明](docs/configuration.md)
- [Docker 部署指南](docs/docker-deployment.md)
- [API 文档](docs/api-reference.md)
- [故障排除](docs/troubleshooting.md)
- [更新日志](CHANGELOG.md)

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 支持

如果你觉得这个项目有用，请给它一个 ⭐️！

有问题或建议？欢迎：
- 提交 [Issue](https://github.com/mweoucfeh/telegram-auto-messenger/issues)
- 发起 [讨论](https://github.com/mweoucfeh/telegram-auto-messenger/discussions)
- 贡献代码

## ⚠️ 免责声明

本工具仅用于学习和合法用途。使用前请确保：
1. 遵守 Telegram 服务条款
2. 不要用于垃圾信息或骚扰
3. 遵守当地法律法规
4. 尊重他人隐私和权益

使用本工具产生的任何后果由使用者自行承担。