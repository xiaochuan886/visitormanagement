# 环境配置指导

## 创建 .env 文件

请在 `backend_service/` 目录下创建 `.env` 文件，并填入以下环境变量：

```bash
# 应用配置
APP_NAME="访客管理系统"
APP_VERSION="1.0.0"
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password123@localhost:5432/visitor_management
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=visitor_management
DATABASE_USER=postgres
DATABASE_PASSWORD=password123

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT认证配置
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 安全配置
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080","http://127.0.0.1:3000"]

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# 邮件配置 (可选)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com

# Celery配置 (可选)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## 生产环境建议

### 安全配置
- `SECRET_KEY`: 使用强密码生成器生成至少32位的随机字符串
- `DATABASE_PASSWORD`: 使用复杂密码
- `REDIS_PASSWORD`: 为Redis设置密码
- `DEBUG`: 生产环境设置为 `false`

### 数据库配置
- 使用独立的PostgreSQL实例
- 定期备份数据库
- 配置连接池和超时设置

### Redis配置
- 使用独立的Redis实例
- 配置持久化策略
- 设置适当的内存限制

## 快速开始

1. 复制上述模板到 `.env` 文件
2. 根据你的环境修改相应配置
3. 确保PostgreSQL和Redis服务正在运行
4. 运行 `docker-compose up -d` 启动所有服务 