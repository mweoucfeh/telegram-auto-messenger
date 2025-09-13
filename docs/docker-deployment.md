# Docker 部署指南

本文档介绍如何使用 Docker 部署 Telegram Auto-Messenger。

## 快速开始

### 1. 准备工作

确保已安装 Docker 和 Docker Compose：

```bash
# 检查 Docker 版本
docker --version
docker-compose --version
```

### 2. 获取项目

```bash
git clone https://github.com/mweoucfeh/telegram-auto-messenger.git
cd telegram-auto-messenger
```

### 3. 准备配置

```bash
# 创建必要目录
mkdir -p config data sessions logs

# 复制配置模板
cp examples/config.yml config/config.yml

# 编辑配置文件
nano config/config.yml
```

### 4. 启动服务

```bash
cd docker
docker-compose up -d
```

### 5. 检查状态

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 目录结构

部署后的目录结构：

```
telegram-auto-messenger/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── config/
│   └── config.yml          # 配置文件
├── data/
│   └── *.db                # 数据库文件
├── sessions/
│   └── *.session           # Telegram 会话文件
└── logs/
    └── *.log               # 日志文件
```

## Docker Compose 配置

### 基础配置

```yaml
version: '3.8'

services:
  telegram-auto-messenger:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: telegram-auto-messenger
    restart: unless-stopped
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./sessions:/app/sessions
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
```

### 环境变量配置

如果使用环境变量管理配置：

```yaml
services:
  telegram-auto-messenger:
    # ... 其他配置
    environment:
      - PYTHONUNBUFFERED=1
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
      - TELEGRAM_PHONE=${TELEGRAM_PHONE}
```

创建 `.env` 文件：

```bash
# .env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890
```

## 常用 Docker 命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps
```

### 日志管理

```bash
# 查看所有日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看最近的日志
docker-compose logs --tail=100
```

### 容器操作

```bash
# 进入容器
docker-compose exec telegram-auto-messenger bash

# 在容器中执行命令
docker-compose exec telegram-auto-messenger telegram-auto-messenger status

# 查看容器资源使用
docker stats telegram-auto-messenger
```

## 数据持久化

### 重要数据目录

- **config/**: 配置文件
- **data/**: 数据库文件
- **sessions/**: Telegram 会话文件
- **logs/**: 应用日志

### 备份策略

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

mkdir -p "$BACKUP_DIR"

# 备份配置和数据
cp -r config "$BACKUP_DIR/"
cp -r data "$BACKUP_DIR/"
cp -r sessions "$BACKUP_DIR/"

# 压缩备份
tar -czf "backup_$DATE.tar.gz" "$BACKUP_DIR"

echo "Backup created: backup_$DATE.tar.gz"
EOF

chmod +x backup.sh
```

### 恢复数据

```bash
# 停止服务
docker-compose down

# 恢复数据
tar -xzf backup_20231201_120000.tar.gz
cp -r backups/20231201_120000/* ./

# 重启服务
docker-compose up -d
```

## 生产环境部署

### 1. 系统要求

- **CPU**: 至少 1 核心
- **内存**: 至少 512MB
- **存储**: 至少 1GB 可用空间
- **网络**: 稳定的互联网连接

### 2. 安全配置

#### 文件权限

```bash
# 设置配置文件权限
chmod 600 config/config.yml
chmod 700 sessions/

# 设置目录权限
chown -R 1000:1000 config data sessions logs
```

#### 防火墙配置

```bash
# 如果需要暴露端口（未来的 Web 界面）
sudo ufw allow 8080/tcp
```

### 3. 生产环境 Docker Compose

```yaml
version: '3.8'

services:
  telegram-auto-messenger:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: telegram-auto-messenger
    restart: unless-stopped
    volumes:
      - ./config:/app/config:ro
      - ./data:/app/data
      - ./sessions:/app/sessions
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - telegram-net
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
    healthcheck:
      test: ["CMD", "telegram-auto-messenger", "status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

networks:
  telegram-net:
    driver: bridge
```

### 4. 监控和日志

#### 集成 Prometheus 监控

```yaml
services:
  # ... telegram-auto-messenger 配置
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### 日志聚合

```yaml
services:
  # ... 其他服务
  
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
      
  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./logs:/var/log/app
      - ./monitoring/promtail.yml:/etc/promtail/config.yml
```

## 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看详细错误信息
docker-compose logs telegram-auto-messenger

# 检查配置文件
docker-compose exec telegram-auto-messenger telegram-auto-messenger config validate
```

#### 2. 权限问题

```bash
# 修复权限
sudo chown -R $(id -u):$(id -g) config data sessions logs
```

#### 3. 网络连接问题

```bash
# 测试网络连接
docker-compose exec telegram-auto-messenger ping telegram.org

# 检查 DNS 解析
docker-compose exec telegram-auto-messenger nslookup telegram.org
```

#### 4. 内存不足

```bash
# 查看资源使用
docker stats

# 增加交换空间
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 调试模式

启用调试模式进行问题排查：

```yaml
services:
  telegram-auto-messenger:
    # ... 其他配置
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=DEBUG
    command: ["telegram-auto-messenger", "run", "--verbose"]
```

## 更新升级

### 1. 更新代码

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose down
docker-compose up -d
```

### 2. 数据库迁移

如果有数据库结构变更：

```bash
# 备份数据
./backup.sh

# 停止服务
docker-compose down

# 更新并启动
docker-compose up -d

# 检查服务状态
docker-compose logs -f
```

## 性能优化

### 1. 资源限制

```yaml
services:
  telegram-auto-messenger:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### 2. 镜像优化

使用多阶段构建减小镜像大小：

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY src/ ./src/
COPY pyproject.toml README.md ./

RUN pip install --user -e .
```

## 集群部署

对于高可用部署，可以使用 Docker Swarm 或 Kubernetes：

### Docker Swarm

```yaml
version: '3.8'

services:
  telegram-auto-messenger:
    image: telegram-auto-messenger:latest
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    networks:
      - telegram-net
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: telegram-auto-messenger
spec:
  replicas: 2
  selector:
    matchLabels:
      app: telegram-auto-messenger
  template:
    metadata:
      labels:
        app: telegram-auto-messenger
    spec:
      containers:
      - name: telegram-auto-messenger
        image: telegram-auto-messenger:latest
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
```