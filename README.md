# Telegram Auto-Messenger 🚀

一个轻量级的 Telegram 自动化消息工具，专注于简单可靠的文字消息发送。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Cross-Platform](https://img.shields.io/badge/Platform-Windows%2FmacOS%2FLinux-brightgreen)

## ✨ 核心特性

- ✅ **无数据库依赖** - 轻量运行，无需数据库
- ✅ **增强日志系统** - 文件日志记录 + 完整异常追踪，便于调试
- ✅ **跨平台支持** - 支持 Windows、macOS、Linux
- ✅ **防封号设计** - 内置延迟和限流机制，参考 tg-signer 安全实践
- ✅ **专注文字消息** - 简单可靠的文字消息发送
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
```

### 4. 获取 API 凭据

1. 访问 [my.telegram.org](https://my.telegram.org)
2. 登录你的 Telegram 账号
3. 创建新应用获取 `api_id` 和 `api_hash`

### 5. 运行程序

```bash
# 运行程序
telegram-auto-messenger run

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

## 📂 项目结构

```
telegram-auto-messenger/
├── src/telegram_auto_messenger/    # 源代码
│   ├── core/                      # 核心功能模块
│   │   ├── account.py            # 账号管理（含安全限流）
│   │   ├── scheduler.py          # 消息调度
│   │   ├── monitor.py            # 消息监控
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