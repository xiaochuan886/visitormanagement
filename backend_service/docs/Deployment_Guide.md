# 访客管理系统部署指南

## 概述

本文档详细介绍了访客管理系统的部署方法，包括开发环境、测试环境和生产环境的部署配置。

## 系统要求

### 硬件要求
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 20GB以上可用空间
- **网络**: 稳定的网络连接

### 软件要求
- **操作系统**: Linux (推荐 Ubuntu 20.04+), macOS, Windows
- **Python**: 3.11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

## 环境配置

### 1. 开发环境部署

#### 1.1 克隆项目
```bash
git clone <repository_url>
cd visitormanagement/backend_service
```

#### 1.2 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 1.3 安装依赖
```bash
pip install -r requirements.txt
```

#### 1.4 配置环境变量
创建 `.env` 文件：
```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/visitor_management
POSTGRES_DB=visitor_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis配置
REDIS_URL=redis://localhost:6380/0

# JWT配置
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用配置
APP_NAME=访客管理系统
DEBUG=true
LOG_LEVEL=INFO

# CORS配置
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

#### 1.5 启动数据库服务
```bash
docker-compose -f docker-compose-simple.yml up -d
```

#### 1.6 运行数据库迁移
```bash
alembic upgrade head
```

#### 1.7 启动应用
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### 2. Docker容器化部署

#### 2.1 构建Docker镜像
```bash
# 构建镜像
docker build -t visitor-management:latest .

# 查看镜像
docker images | grep visitor-management
```

#### 2.2 使用Docker Compose启动
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

#### 2.3 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 3. 生产环境部署

#### 3.1 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建应用目录
sudo mkdir -p /opt/visitor-management
sudo chown $USER:$USER /opt/visitor-management
cd /opt/visitor-management
```

#### 3.2 生产环境配置
创建生产环境的 `.env` 文件：
```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:your-strong-password@db:5432/visitor_management
POSTGRES_DB=visitor_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password

# Redis配置
REDIS_URL=redis://redis:6379/0

# JWT配置
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用配置
APP_NAME=访客管理系统
DEBUG=false
LOG_LEVEL=INFO

# CORS配置
ALLOWED_ORIGINS=["https://your-domain.com"]

# SSL配置
SSL_CERT_PATH=/etc/ssl/certs/your-cert.pem
SSL_KEY_PATH=/etc/ssl/private/your-key.pem
```

#### 3.3 生产环境Docker Compose
创建 `docker-compose.prod.yml`：
```yaml
version: '3.8'

services:
  app:
    image: visitor-management:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG}
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    networks:
      - visitor-network

  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - visitor-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - visitor-network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - app
    networks:
      - visitor-network

volumes:
  postgres_data:
  redis_data:

networks:
  visitor-network:
    driver: bridge
```

#### 3.4 Nginx配置
创建 `nginx.conf`：
```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/ssl/your-cert.pem;
        ssl_certificate_key /etc/ssl/your-key.pem;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /docs {
            proxy_pass http://app/docs;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 3.5 启动生产环境
```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head

# 创建初始管理员用户
docker-compose -f docker-compose.prod.yml exec app python scripts/create_admin.py
```

## 数据库管理

### 1. 数据库迁移
```bash
# 创建新的迁移文件
alembic revision --autogenerate -m "描述变更内容"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

### 2. 数据库备份
```bash
# 备份数据库
docker-compose exec db pg_dump -U postgres visitor_management > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker-compose exec -T db psql -U postgres visitor_management < backup_file.sql
```

### 3. 数据库监控
```bash
# 查看数据库连接
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# 查看数据库大小
docker-compose exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('visitor_management'));"
```

## 监控和日志

### 1. 应用日志
```bash
# 查看应用日志
docker-compose logs -f app

# 查看特定时间的日志
docker-compose logs --since="2025-06-07T10:00:00" app

# 查看最近100行日志
docker-compose logs --tail=100 app
```

### 2. 系统监控
```bash
# 查看容器状态
docker-compose ps

# 查看资源使用情况
docker stats

# 查看磁盘使用情况
df -h
```

### 3. 健康检查
```bash
# 检查应用健康状态
curl http://localhost:8000/health

# 检查API文档
curl http://localhost:8000/docs
```

## 性能优化

### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_visitors_phone ON visitors(phone);
CREATE INDEX idx_visitors_visit_date ON visitors(visit_date);
CREATE INDEX idx_visitors_status ON visitors(status);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM visitors WHERE phone = '13800138000';
```

### 2. Redis缓存配置
```bash
# Redis配置优化
echo "maxmemory 256mb" >> redis.conf
echo "maxmemory-policy allkeys-lru" >> redis.conf
```

### 3. 应用性能调优
```python
# 在main.py中添加
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # 根据CPU核心数调整
        loop="uvloop",  # 使用更快的事件循环
        http="httptools"  # 使用更快的HTTP解析器
    )
```

## 安全配置

### 1. 防火墙设置
```bash
# 配置UFW防火墙
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5432/tcp   # 禁止外部访问数据库
sudo ufw deny 6379/tcp   # 禁止外部访问Redis
```

### 2. SSL证书配置
```bash
# 使用Let's Encrypt获取免费SSL证书
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 3. 环境变量安全
```bash
# 设置文件权限
chmod 600 .env

# 使用Docker secrets (生产环境推荐)
echo "your-secret-key" | docker secret create jwt_secret -
```

## 故障排除

### 1. 常见问题

#### 应用无法启动
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 检查Docker容器状态
docker-compose ps

# 查看详细错误日志
docker-compose logs app
```

#### 数据库连接失败
```bash
# 检查数据库容器状态
docker-compose ps db

# 测试数据库连接
docker-compose exec db psql -U postgres -d visitor_management -c "SELECT 1;"

# 检查网络连接
docker network ls
docker network inspect visitor-management_default
```

#### Redis连接失败
```bash
# 检查Redis容器状态
docker-compose ps redis

# 测试Redis连接
docker-compose exec redis redis-cli ping
```

### 2. 性能问题诊断
```bash
# 查看系统资源使用
top
htop
iotop

# 查看Docker容器资源使用
docker stats

# 分析慢查询
docker-compose exec db psql -U postgres -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## 备份和恢复

### 1. 完整备份策略
```bash
#!/bin/bash
# backup.sh - 完整备份脚本

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR/$DATE

# 备份数据库
docker-compose exec -T db pg_dump -U postgres visitor_management > $BACKUP_DIR/$DATE/database.sql

# 备份应用配置
cp .env $BACKUP_DIR/$DATE/
cp docker-compose.yml $BACKUP_DIR/$DATE/

# 压缩备份
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR $DATE

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR/backup_$DATE.tar.gz"
```

### 2. 自动备份配置
```bash
# 添加到crontab
echo "0 2 * * * /opt/visitor-management/backup.sh" | crontab -
```

### 3. 灾难恢复
```bash
#!/bin/bash
# restore.sh - 恢复脚本

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "使用方法: $0 <backup_file.tar.gz>"
    exit 1
fi

# 解压备份
tar -xzf $BACKUP_FILE

# 停止服务
docker-compose down

# 恢复配置文件
cp backup_*/env .env
cp backup_*/docker-compose.yml .

# 启动数据库
docker-compose up -d db

# 等待数据库启动
sleep 10

# 恢复数据库
docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS visitor_management;"
docker-compose exec -T db psql -U postgres -c "CREATE DATABASE visitor_management;"
docker-compose exec -T db psql -U postgres visitor_management < backup_*/database.sql

# 启动所有服务
docker-compose up -d

echo "恢复完成"
```

## 更新和维护

### 1. 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build app

# 滚动更新
docker-compose up -d app

# 运行数据库迁移
docker-compose exec app alembic upgrade head
```

### 2. 系统维护
```bash
# 清理Docker资源
docker system prune -f

# 清理日志文件
find /var/log -name "*.log" -mtime +30 -delete

# 更新系统包
sudo apt update && sudo apt upgrade -y
```

### 3. 监控脚本
```bash
#!/bin/bash
# monitor.sh - 监控脚本

# 检查服务状态
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "应用服务异常，尝试重启..."
    docker-compose restart app
fi

# 检查磁盘空间
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "磁盘空间不足: ${DISK_USAGE}%"
fi

# 检查内存使用
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "内存使用过高: ${MEMORY_USAGE}%"
fi
```

---

## 总结

本部署指南涵盖了访客管理系统从开发环境到生产环境的完整部署流程。请根据实际需求选择合适的部署方式，并定期进行备份和监控，确保系统稳定运行。

如有问题，请参考故障排除章节或联系技术支持团队。 