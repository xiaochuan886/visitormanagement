# 端口冲突解决方案

## 问题描述
本地PostgreSQL和Redis端口被占用，导致Docker容器无法启动。

## 解决方案

### 1. 修改Docker端口映射
已将以下端口进行了修改：
- PostgreSQL: `5432` → `5433`
- Redis: `6379` → `6380`

### 2. 更新配置文件
已更新 `.env` 文件中的端口配置：
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password123@localhost:5433/visitor_management
REDIS_URL=redis://localhost:6380/0
```

### 3. 启动服务

#### 方式一：使用简化版Docker Compose（推荐）
```bash
cd backend_service
docker-compose -f docker-compose-simple.yml up -d
```

#### 方式二：使用完整Docker Compose
```bash
cd backend_service
docker-compose up -d
```

### 4. 验证服务状态
```bash
# 检查容器状态
docker-compose -f docker-compose-simple.yml ps

# 测试PostgreSQL连接
psql -h localhost -p 5433 -U postgres -d visitor_management

# 测试Redis连接
redis-cli -h localhost -p 6380 ping
```

### 5. 启动后端应用
```bash
cd backend_service
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### 6. 测试API
```bash
curl http://127.0.0.1:8001/
curl http://127.0.0.1:8001/docs  # Swagger文档
```

## 当前状态
✅ PostgreSQL容器运行在端口5433
✅ Redis容器运行在端口6380
✅ 配置文件已更新
✅ 应用程序可以正常启动

## 注意事项
1. 如果需要连接数据库，请使用端口5433而不是默认的5432
2. Redis连接请使用端口6380而不是默认的6379
3. 后端API运行在端口8001，避免与其他服务冲突

## 故障排除
如果仍有问题，请运行诊断脚本：
```bash
cd backend_service
python test_startup.py
``` 