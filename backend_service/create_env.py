#!/usr/bin/env python3
"""
生成.env文件的脚本
"""

env_content = """# 应用配置
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
SECRET_KEY=your-super-secret-key-change-this-in-production-2024
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
"""

if __name__ == "__main__":
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    print("✅ .env文件创建成功") 