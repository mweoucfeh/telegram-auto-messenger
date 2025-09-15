# Telegram Auto-Messenger 🚀

一个轻量级的 Telegram 自动化消息工具，专注于简单可靠的消息发送和修仙频道自动化。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Cross-Platform](https://img.shields.io/badge/Platform-Windows%2FmacOS%2FLinux-brightgreen)

## ✨ 核心特性

- ✅ **无数据库依赖** - 使用内存会话，无需 SQLite 数据库
- ✅ **修仙频道自动化** - 智能解析修仙机器人回复，自动等待和重试
- ✅ **一键启动功能** - 支持快速启动定时任务和修仙自动化
- ✅ **增强日志系统** - 文件日志记录 + 完整异常追踪，便于调试
- ✅ **跨平台支持** - 支持 Windows、macOS、Linux
- ✅ **防封号设计** - 内置延迟和限流机制，参考 tg-signer 安全实践
- ✅ **多账号管理** - 支持多个 Telegram 账号
- ✅ **定时发送** - 间隔定时向指定频道/群组发送消息
- ✅ **智能监控回复** - 监控关键词并自动回复
- ✅ **本地运行** - 完全本地化，无需外部服务
- ✅ **PyCharm兼容** - 完全兼容 PyCharm 开发环境和调试功能

## 🔧 技术栈

- **Telegram API**: Telethon (稳定可靠的 Telegram 客户端库)
- **任务调度**: APScheduler (高性能异步任务调度器)  
- **配置管理**: YAML (人性化配置文件格式)
- **命令行**: Click (现代化 CLI 框架)
- **日志系统**: 增强文件日志（自动轮转 + 异常追踪）

## 🛡️ 防封号安全措施

- **消息间隔限制**: 最小发送间隔防止频繁操作
- **每小时限流**: 限制每小时消息数量
- **随机延迟**: 模拟人工操作时间
- **渐进式重试**: 失败时的智能重试机制

## 📦 快速开始

### 1. 安装依赖

```bash
git clone https://github.com/mweoucfeh/telegram-auto-messenger.git
cd telegram-auto-messenger
pip install -r requirements.txt
pip install -e .
```

### 2. 生成配置文件

```bash
telegram-auto-messenger config generate
```

### 3. 编辑配置

编辑生成的 `config/config.yml` 文件：

```yaml
# 应用配置
app:
  # 是否启用日志输出
  log_enabled: true
  
  # 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  log_level: 'INFO'
  
  # 是否启用文件日志
  log_to_file: true
  
  # 日志文件目录
  log_dir: 'logs'
  
  # 防封号安全设置
  safety:
    # 消息间最小延迟（秒）
    min_message_delay: 5
    
    # 每小时最大消息数
    max_messages_per_hour: 20
    
    # 启用随机延迟
    randomize_delays: true

# Telegram 账号配置
accounts:
  - api_id: 12345678
    api_hash: 'your_api_hash_here'
    phone: '+1234567890'
    session_name: 'account1'
    enabled: true

# 修仙频道自动化配置
cultivation:
  enabled: true
  account_name: 'account1'  # 使用的账号名
  channel: '@your_cultivation_channel'  # 修仙频道
  command: '.闭关修炼'  # 修炼命令
  auto_start: true  # 程序启动时自动开始
  response_timeout: 30  # 等待机器人回复的超时时间
  retry_on_failure: true  # 失败时重试
```

### 4. 获取 API 凭据

1. 访问 [my.telegram.org](https://my.telegram.org)
2. 登录你的 Telegram 账号
3. 创建新应用获取 `api_id` 和 `api_hash`

### 5. 运行程序

```bash
# 运行程序
telegram-auto-messenger run

# 快速启动修仙自动化
telegram-auto-messenger run --quick

# 静默运行（无控制台日志输出，但仍写入文件）
telegram-auto-messenger --quiet run

# 详细输出模式（DEBUG级别）
telegram-auto-messenger --verbose run
```

## 🖥️ 命令行使用

### 基础命令

```bash
# 发送测试消息
telegram-auto-messenger send "@channel" "Hello World"

# 查看状态
telegram-auto-messenger status

# 验证配置
telegram-auto-messenger config validate
```

### 修仙自动化命令

```bash
# 启动修仙自动化（持续运行）
telegram-auto-messenger cultivation start

# 启动指定账号和频道的修仙
telegram-auto-messenger cultivation start -a account1 -c @your_channel

# 立即执行一次修炼命令
telegram-auto-messenger cultivation execute

# 自定义修炼命令
telegram-auto-messenger cultivation execute --command ".闭关修炼"

# 查看修仙状态
telegram-auto-messenger cultivation status

# 停止修仙自动化
telegram-auto-messenger cultivation stop
```

### 定时任务管理

```bash
# 列出所有定时任务
telegram-auto-messenger schedule list

# 立即执行定时任务
telegram-auto-messenger execute schedule_name

# 暂停/恢复定时任务  
telegram-auto-messenger schedule pause task_name
telegram-auto-messenger schedule resume task_name
```

### 监控管理

```bash
# 列出所有监控
telegram-auto-messenger monitor list

# 暂停/恢复监控
telegram-auto-messenger monitor pause monitor_name
telegram-auto-messenger monitor resume monitor_name
```

## 🧘 修仙频道自动化

### 功能特点

本工具专门为修仙频道设计了智能自动化功能，能够：

1. **自动发送修炼命令** - 自动发送 `.闭关修炼` 等修炼命令
2. **智能解析回复** - 解析修仙机器人的回复消息，提取等待时间
3. **智能等待重试** - 根据机器人回复自动计算下次修炼时间
4. **成功失败统计** - 统计修炼成功和失败次数

### 支持的回复格式

工具能够智能解析以下格式的机器人回复：

#### 成功回复（带等待时间）
```
【闭关成功】
你福至心灵，成功炼化灵气，基础修为增加了 49 点。
因【星宫】灵脉加持，你额外获得了 29 点修为！
本次闭关，你的修为最终增加了 78 点。

当前境界: 筑基后期
当前修为: 1298 / 30000

你感到一阵疲惫，需要打坐调息 13 分钟方可再次闭关。
```

#### 失败回复
```
灵气尚未平复，无法立即再次闭关。请在 11分钟36秒 后再试。
```

#### 简单等待
```
你感到一阵疲惫，需要打坐调息 5 分钟方可再次闭关。
```

### 智能时间解析

- **分钟格式**: `13 分钟` → 13分钟等待
- **分钟秒格式**: `11分钟36秒` → 11分36秒等待
- **自动延迟**: 在机器人给出的时间基础上增加10秒+10%的随机延迟，避免精确定时
- **失败重试**: 如果机器人没有回复，30秒后自动重试

### 使用示例

```bash
# 快速开始修仙（一键启动）
telegram-auto-messenger run --quick

# 或者分步操作：

# 1. 配置修仙设置
vim config/config.yml  # 编辑 cultivation 部分

# 2. 启动修仙自动化
telegram-auto-messenger cultivation start

# 3. 查看运行状态
telegram-auto-messenger cultivation status
```

### 配置说明

```yaml
cultivation:
  enabled: true                      # 启用修仙功能
  account_name: 'account1'           # 使用的账号名称
  channel: '@your_cultivation_channel'  # 修仙频道
  command: '.闭关修炼'                # 修炼命令
  auto_start: true                   # 程序启动时自动开始
  response_timeout: 30               # 等待机器人回复的超时时间（秒）
  retry_on_failure: true             # 失败时重试
```

## 📂 项目结构

```
telegram-auto-messenger/
├── src/telegram_auto_messenger/    # 源代码
│   ├── core/                      # 核心功能模块
│   │   ├── account.py            # 账号管理（无数据库依赖）
│   │   ├── scheduler.py          # 消息调度
│   │   ├── monitor.py            # 消息监控
│   │   ├── cultivation.py        # 修仙自动化
│   │   └── manager.py            # 主管理器
│   ├── config/                   # 配置管理
│   ├── utils/                    # 工具模块
│   │   └── logger.py             # 增强日志工具（文件+异常追踪）
│   └── cli.py                    # 命令行界面
├── examples/                     # 配置示例
├── demo_simple.py               # 简单使用示例
├── docs/                        # 文档
│   └── LOGGING.md              # 增强日志系统使用指南
└── tests/                       # 测试文件
    ├── test_config.py          # 配置测试
    ├── test_cultivation.py     # 修仙功能测试
    └── test_utils.py           # 工具测试
```

## 📋 详细文档

- [**增强日志系统使用指南**](docs/LOGGING.md) - 详细的日志配置和使用说明
- 配置文件示例: `examples/` 目录
- API 文档: 查看源代码注释

## 🐛 调试和故障排除

### 日志文件位置
- 主日志: `logs/telegram_auto_messenger.log`
- 错误日志: `logs/errors.log` 
- 日志自动轮转（10MB最大，保留5个备份文件）

### 常见问题
1. **账号连接失败**: 检查 `errors.log` 获取详细错误信息
2. **消息发送失败**: 查看主日志文件中的详细异常堆栈
3. **配置验证错误**: 使用 `telegram-auto-messenger config validate` 验证配置
4. **PyCharm调试**: 直接在PyCharm中运行，日志会同时显示在控制台和文件中

## 🔐 安全说明

1. **API 凭据安全**: 请妥善保管你的 `api_id` 和 `api_hash`
2. **会话文件**: `sessions/` 目录包含登录会话，请勿泄露
3. **权限控制**: 确保账号有足够权限访问目标频道/群组
4. **频率控制**: 遵循内置的安全延迟设置，避免被封号

## 🚀 配置示例

### 定时消息

```yaml
schedules:
  - name: 'daily_greeting'
    target: '@your_channel'
    message: '🌅 Good morning! Have a great day!'
    interval: 86400  # 24小时
    enabled: true
```

### 智能监控回复

```yaml
monitors:
  - name: 'help_monitor' 
    target: '@your_group'
    keywords: ['help', 'support', '帮助']
    reply_message: '👋 Hello! How can I help you?'
    enabled: true
    exact_match: false
```

## 🛠️ 本地开发

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
pip install -e .

# 运行测试
pytest

# 代码格式化
black src/
flake8 src/
```

## 📝 更新日志

### v1.1.0 - 修仙自动化版本
- 🆕 **修仙频道自动化**: 专为修仙频道设计的智能自动化功能
- 🆕 **智能回复解析**: 自动解析修仙机器人回复，提取等待时间
- 🆕 **一键启动**: `--quick` 参数快速启动修仙自动化
- 🆕 **无数据库依赖**: 使用 StringSession 替代 SQLite，解决数据库连接问题
- 🆕 **修仙命令集**: 新增 `cultivation` 命令组，专门管理修仙功能
- 🔧 **配置升级**: 新增 `cultivation` 配置节，支持修仙相关设置
- 🧪 **完整测试**: 为修仙功能添加完整的单元测试

### v1.0.1 - 增强日志版本
- 🆕 **增强日志系统**: 支持文件日志记录，自动轮转管理
- 🆕 **异常追踪**: 完整的异常堆栈追踪，便于调试和问题定位
- 🆕 **PyCharm兼容**: 完全兼容PyCharm开发环境
- 🆕 **分级日志**: 主日志文件 + 专门的错误日志文件
- 🔧 **配置升级**: 新增 `log_to_file` 和 `log_dir` 配置选项

### v1.0.0 - 简化版本
- 移除数据库依赖，实现轻量化运行
- 简化日志系统为可控制的打印输出
- 增强防封号安全措施
- 优化跨平台兼容性
- 专注文字消息功能

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

本工具仅用于学习和合法用途。使用前请确保：
1. 遵守 Telegram 服务条款
2. 不要用于垃圾信息或骚扰
3. 遵守当地法律法规
4. 尊重他人隐私和权益

使用本工具产生的任何后果由使用者自行承担。