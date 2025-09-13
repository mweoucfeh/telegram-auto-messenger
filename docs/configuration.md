# 配置说明

本文档详细说明了 Telegram Auto-Messenger 的配置选项。

## 配置文件结构

配置文件采用 YAML 格式，主要包含四个部分：

```yaml
app:          # 应用程序配置
accounts:     # Telegram 账号配置
schedules:    # 定时消息配置
monitors:     # 消息监控配置
```

## 应用程序配置 (app)

### 基础配置

```yaml
app:
  # 数据库文件路径
  database_path: 'data/telegram_auto_messenger.db'
  
  # 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_level: 'INFO'
  
  # 是否启用配置热重载
  hot_reload: true
  
  # 热重载检查间隔（秒）
  hot_reload_interval: 30
```

### 配置说明

- **database_path**: SQLite 数据库文件路径，用于存储操作日志
- **log_level**: 日志输出级别，开发时建议使用 DEBUG
- **hot_reload**: 启用后程序会自动检测配置文件变化并重载
- **hot_reload_interval**: 检查配置文件变化的时间间隔

## 账号配置 (accounts)

### 基础配置

```yaml
accounts:
  - api_id: 12345678
    api_hash: 'your_api_hash_here'
    phone: '+1234567890'
    session_name: 'account1'
    enabled: true
```

### 参数说明

- **api_id**: Telegram API ID，从 https://my.telegram.org 获取
- **api_hash**: Telegram API Hash，从 https://my.telegram.org 获取
- **phone**: 手机号码，包含国家代码
- **session_name**: 会话名称，用于标识不同账号
- **enabled**: 是否启用此账号

### 多账号配置

```yaml
accounts:
  # 主账号
  - api_id: 12345678
    api_hash: 'hash1'
    phone: '+1234567890'
    session_name: 'main_account'
    enabled: true
    
  # 备用账号
  - api_id: 87654321
    api_hash: 'hash2'
    phone: '+0987654321'
    session_name: 'backup_account'
    enabled: false
```

### 获取 API 凭据

1. 访问 https://my.telegram.org
2. 使用手机号登录
3. 选择 "API development tools"
4. 填写应用信息创建新应用
5. 获取 `api_id` 和 `api_hash`

## 定时消息配置 (schedules)

### 基础配置

```yaml
schedules:
  - name: 'daily_greeting'
    target: '@your_channel'
    message: '🌅 Good morning!'
    interval: 86400
    enabled: true
    auto_delete: false
    delete_after: 60
```

### 参数说明

- **name**: 定时任务名称，必须唯一
- **target**: 目标频道或群组（@username 或 ID）
- **message**: 要发送的消息内容
- **interval**: 发送间隔时间（秒）
- **enabled**: 是否启用此定时任务
- **auto_delete**: 是否自动删除消息
- **delete_after**: 删除延迟时间（秒）

### 时间间隔示例

```yaml
# 常用时间间隔
interval: 60      # 1分钟
interval: 300     # 5分钟
interval: 1800    # 30分钟
interval: 3600    # 1小时
interval: 86400   # 24小时
interval: 604800  # 7天
```

### 高级配置示例

```yaml
schedules:
  # 每日早安消息
  - name: 'morning_greeting'
    target: '@company_channel'
    message: |
      🌅 早上好！
      今日提醒：
      - 记得喝水 💧
      - 保持微笑 😊
      - 努力工作 💪
    interval: 86400
    enabled: true
    auto_delete: false
    
  # 闪现通知（发送后快速删除）
  - name: 'flash_notification'
    target: '@urgent_alerts'
    message: '⚡ 这是一条闪现消息，30秒后自动删除'
    interval: 3600
    enabled: true
    auto_delete: true
    delete_after: 30
```

## 消息监控配置 (monitors)

### 基础配置

```yaml
monitors:
  - name: 'help_monitor'
    target: '@your_group'
    keywords: ['help', 'support']
    reply_message: '如何帮助您？'
    enabled: true
    exact_match: false
```

### 参数说明

- **name**: 监控器名称，必须唯一
- **target**: 要监控的频道或群组
- **keywords**: 触发关键词列表
- **reply_message**: 自动回复的消息
- **enabled**: 是否启用此监控器
- **exact_match**: 是否精确匹配关键词

### 关键词匹配规则

#### 模糊匹配 (exact_match: false)

```yaml
keywords: ['help', '帮助']
# 匹配包含关键词的消息：
# ✓ "I need help"
# ✓ "请帮助我"
# ✓ "helpful"
```

#### 精确匹配 (exact_match: true)

```yaml
keywords: ['help', '帮助']
# 只匹配独立单词：
# ✓ "I need help"
# ✓ "请 帮助 我"
# ✗ "helpful"
```

### 高级监控示例

```yaml
monitors:
  # 客服支持监控
  - name: 'customer_support'
    target: '@customer_group'
    keywords: ['help', 'support', 'problem', '帮助', '支持', '问题']
    reply_message: |
      👋 您好！我是客服机器人。
      
      🔍 检测到您需要帮助，我们的客服团队将尽快回复。
      
      📞 紧急情况请联系：+1234567890
      📧 邮箱：support@example.com
    enabled: true
    exact_match: false
    
  # 管理员通知监控
  - name: 'admin_alert'
    target: '@admin_group'
    keywords: ['@admin', 'urgent', 'emergency']
    reply_message: '🚨 已通知管理员，请稍候'
    enabled: true
    exact_match: true
    
  # 新成员欢迎
  - name: 'welcome_new_members'
    target: '@welcome_group'
    keywords: ['hello', 'hi', '你好', '大家好']
    reply_message: |
      🎉 欢迎加入我们的群组！
      
      📋 请先阅读群规：
      1. 保持友善和尊重
      2. 不要发送垃圾信息
      3. 有问题请先搜索历史消息
      
      💬 祝您聊天愉快！
    enabled: true
    exact_match: false
```

## 环境变量支持

配置文件支持环境变量替换：

```yaml
accounts:
  - api_id: ${TELEGRAM_API_ID}
    api_hash: '${TELEGRAM_API_HASH}'
    phone: '${TELEGRAM_PHONE}'
    session_name: 'production'
    enabled: true
```

设置环境变量：

```bash
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=your_hash_here
export TELEGRAM_PHONE=+1234567890
```

## 配置验证

使用命令行工具验证配置：

```bash
# 验证默认配置文件
telegram-auto-messenger config validate

# 验证指定配置文件
telegram-auto-messenger config validate -c custom_config.yml
```

常见验证错误：

1. **API 凭据错误**: 检查 api_id 和 api_hash
2. **手机号格式**: 必须包含国家代码，如 +86
3. **目标无效**: 频道/群组名称或 ID 格式错误
4. **时间间隔过短**: 最小间隔为 60 秒
5. **关键词为空**: 监控器必须指定关键词

## 最佳实践

### 1. 账号管理

- 使用专门的机器人账号，避免使用个人主账号
- 定期备份会话文件
- 设置账号昵称便于区分

### 2. 定时消息

- 避免频繁发送消息，尊重群组成员
- 使用有意义的消息内容
- 合理设置发送间隔

### 3. 监控回复

- 关键词不要过于宽泛
- 回复消息要简洁明了
- 避免与其他机器人冲突

### 4. 安全考虑

- 配置文件权限设置为 600
- 使用环境变量管理敏感信息
- 定期更换 API 凭据