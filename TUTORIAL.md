# Telegram Auto-Messenger 修仙自动化教程

本教程将帮助您快速上手 Telegram Auto-Messenger 的修仙自动化功能。

## 🚀 快速开始

### 1. 安装和配置

```bash
# 克隆项目
git clone https://github.com/mweoucfeh/telegram-auto-messenger.git
cd telegram-auto-messenger

# 安装依赖
pip install -r requirements.txt
pip install -e .

# 生成配置文件
telegram-auto-messenger config generate
```

### 2. 配置账号和修仙设置

编辑 `config/config.yml` 文件：

```yaml
# Telegram 账号配置
accounts:
  - api_id: 12345678              # 你的 API ID
    api_hash: 'your_api_hash'     # 你的 API Hash
    phone: '+1234567890'          # 你的手机号
    session_name: 'account1'      # 会话名称
    enabled: true                 # 启用这个账号

# 修仙自动化配置
cultivation:
  enabled: true                   # 启用修仙功能
  account_name: 'account1'        # 使用的账号名称
  channel: '@your_cultivation_channel'  # 修仙频道（替换为实际频道）
  command: '.闭关修炼'             # 修炼命令
  auto_start: true                # 程序启动时自动开始
  response_timeout: 30            # 等待机器人回复的超时时间
  retry_on_failure: true          # 失败时重试
```

### 3. 获取 Telegram API 凭据

1. 访问 https://my.telegram.org
2. 使用你的 Telegram 账号登录
3. 创建新应用，获取 `api_id` 和 `api_hash`
4. 将这些信息填入配置文件

## 🧘 使用方法

### 方法一：一键启动（推荐）

```bash
# 快速启动修仙自动化
telegram-auto-messenger run --quick
```

这个命令会：
- 启动 Telegram Auto-Messenger
- 自动开始修仙自动化
- 持续运行，自动处理修炼和等待

### 方法二：分步操作

```bash
# 1. 启动主程序
telegram-auto-messenger run

# 2. 在另一个终端中启动修仙
telegram-auto-messenger cultivation start
```

### 方法三：单次修炼

```bash
# 立即执行一次修炼命令
telegram-auto-messenger cultivation execute

# 使用特定账号和频道
telegram-auto-messenger cultivation execute -a account1 -c @my_channel

# 使用自定义命令
telegram-auto-messenger cultivation execute --command ".特殊修炼"
```

## 📊 监控和管理

### 查看状态

```bash
# 查看修仙状态
telegram-auto-messenger cultivation status

# 查看整体状态
telegram-auto-messenger status
```

### 停止修仙

```bash
# 停止修仙自动化
telegram-auto-messenger cultivation stop

# 或者直接按 Ctrl+C 停止主程序
```

## 🧠 智能特性

### 自动解析机器人回复

工具会自动解析以下格式的回复：

**成功回复：**
```
【闭关成功】
你福至心灵，成功炼化灵气，基础修为增加了 49 点。
...
你感到一阵疲惫，需要打坐调息 13 分钟方可再次闭关。
```
→ 解析出 13 分钟等待时间

**失败回复：**
```
灵气尚未平复，无法立即再次闭关。请在 11分钟36秒 后再试。
```
→ 解析出 11 分 36 秒等待时间

### 智能重试机制

- **成功修炼**：根据机器人给出的等待时间自动安排下次修炼
- **修炼失败**：根据提示的等待时间重试
- **无回复**：30 秒后自动重试
- **智能延迟**：在等待时间基础上增加随机延迟，避免被检测为机器人

## 🎮 交互式演示

运行交互式演示脚本：

```bash
python demo_cultivation.py
```

这个脚本提供：
- 单次修炼演示
- 自动修仙演示
- 状态查看
- 消息解析测试

## ⚠️ 注意事项

1. **网络连接**：确保网络稳定，避免频繁断线
2. **账号安全**：使用官方 API，遵守 Telegram 使用条款
3. **频率控制**：内置安全延迟，避免被频率限制
4. **监控运行**：建议定期查看日志和状态
5. **备份配置**：保存好配置文件和 sessions 目录

## 🔧 故障排除

### 常见问题

**1. "unable to open database file" 错误**
- ✅ 已解决：新版本使用内存会话，不再依赖 SQLite

**2. 连接失败**
```bash
# 检查配置
telegram-auto-messenger config validate

# 查看详细错误
telegram-auto-messenger --verbose run
```

**3. 机器人不回复**
- 确认频道地址正确
- 确认机器人名称匹配
- 检查账号是否有发送权限

**4. 解析失败**
- 查看 `logs/` 目录中的日志文件
- 机器人回复格式可能发生变化，可以提 issue 反馈

### 日志文件

- 主日志：`logs/telegram_auto_messenger.log`
- 错误日志：`logs/errors.log`

## 🎯 最佳实践

1. **测试先行**：首先使用单次修炼测试功能
2. **配置备份**：定期备份配置文件和会话文件
3. **监控运行**：使用 `cultivation status` 定期检查状态
4. **适度使用**：避免过于频繁的修炼，注意账号安全
5. **日志检查**：定期查看日志，及时发现问题

## 📞 获取帮助

- 查看命令帮助：`telegram-auto-messenger --help`
- 查看子命令帮助：`telegram-auto-messenger cultivation --help`
- 项目 Issues：https://github.com/mweoucfeh/telegram-auto-messenger/issues

祝您修仙之路顺利！🧘‍♀️✨