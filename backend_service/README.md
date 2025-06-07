# 访客管理系统 - Python FastAPI版

基于 FastAPI 的现代化访客管理系统，采用 Clean Architecture 设计，支持多租户、实时通信和完整的访客生命周期管理。

## 🚀 特性

- **现代化架构**: 基于 FastAPI + SQLAlchemy 2.0 + Pydantic V2
- **异步支持**: 全异步架构，高性能并发处理
- **Clean Architecture**: 分层架构设计，职责分离
- **多租户支持**: 基于 JWT 的多租户数据隔离
- **实时通信**: WebSocket 支持实时通知
- **缓存优化**: Redis 缓存提升性能
- **API文档**: 自动生成 OpenAPI/Swagger 文档
- **容器化部署**: Docker + Docker Compose 一键部署

## 📋 功能模块

### 核心功能
- **访客管理**: 访客注册、信息完善、状态跟踪
- **签到签出**: 二维码扫描、自动记录访问时长
- **审批流程**: 多级审批、审批历史追踪
- **员工管理**: 员工信息、部门职位管理
- **站点管理**: 多站点支持、地理位置管理

### 系统功能
- **认证授权**: JWT 访问令牌 + 刷新令牌
- **权限管理**: 基于角色的权限控制
- **审计日志**: 完整的操作记录
- **通知服务**: 邮件/短信通知集成
- **数据导出**: 访客报表和统计分析

## 🛠️ 技术栈

### 后端框架
- **FastAPI**: 高性能 Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **Pydantic V2**: 数据验证和序列化
- **Alembic**: 数据库迁移工具

### 数据存储
- **PostgreSQL**: 主数据库
- **Redis**: 缓存 + 消息队列

### 认证安全
- **JWT**: 无状态认证
- **Bcrypt**: 密码哈希
- **CORS**: 跨域支持

### 任务队列
- **Celery**: 异步任务处理
- **Redis**: 消息代理

### 开发工具
- **Docker**: 容器化部署
- **pytest**: 单元测试
- **Black**: 代码格式化
- **Mypy**: 类型检查

## 📦 项目结构

```
backend_service/
├── app/                    # 应用核心代码
│   ├── domain/            # 领域层
│   │   ├── entities/      # 实体定义
│   │   ├── enums/         # 枚举类型
│   │   └── events/        # 领域事件
│   ├── application/       # 应用层
│   │   ├── services/      # 应用服务
│   │   ├── dto/          # 数据传输对象
│   │   └── interfaces/    # 接口定义
│   ├── infrastructure/    # 基础设施层
│   │   ├── database/      # 数据访问
│   │   ├── cache/         # 缓存服务
│   │   └── auth/         # 认证服务
│   ├── api/              # API层
│   │   ├── routes/       # 路由定义
│   │   ├── middleware/   # 中间件
│   │   └── dependencies/ # 依赖注入
│   └── core/             # 核心配置
├── tests/                # 测试代码
├── docs/                 # 项目文档
├── requirements.txt      # Python依赖
├── docker-compose.yml    # Docker编排
├── Dockerfile           # Docker构建
└── main.py             # 应用入口
```

## 🚀 快速开始

### 环境要求
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd backend_service
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件设置数据库连接等配置
```

4. **启动服务**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

1. **启动所有服务**
```bash
docker-compose up -d
```

2. **查看服务状态**
```bash
docker-compose ps
```

3. **查看日志**
```bash
docker-compose logs -f visitor-backend
```

## 📚 API 文档

启动服务后访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 认证示例

1. **登录获取令牌**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

2. **使用令牌访问API**
```bash
curl -X GET "http://localhost:8000/api/v1/visitors/" \
  -H "Authorization: Bearer <access_token>"
```

## 🔧 配置说明

### 主要配置项

```python
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/visitor_management

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 多租户配置

系统支持多租户架构，通过 JWT 令牌中的 `tenant_id` 实现数据隔离：

```python
# 创建租户特定的令牌
tokens = jwt_handler.create_user_tokens(
    user_id="1",
    username="admin",
    tenant_id="company_a",  # 租户标识
    roles=["admin"],
    permissions=["visitor:read", "visitor:write"]
)
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_visitors.py

# 生成覆盖率报告
pytest --cov=app
```

### 测试账户
- **用户名**: admin
- **密码**: admin123

## 📈 性能优化

### 缓存策略
- 访客信息缓存 1 小时
- 部门员工数据缓存 30 分钟
- API 响应缓存机制

### 数据库优化
- 索引优化（租户ID、状态字段）
- 查询优化（使用 selectinload 预加载关联数据）
- 连接池配置

## 🔒 安全考虑

### 认证安全
- JWT 令牌过期机制
- 刷新令牌轮换
- 密码哈希存储

### 数据安全
- 多租户数据隔离
- SQL 注入防护
- CORS 配置

### API 安全
- 请求频率限制
- 输入验证
- 错误信息脱敏

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：

1. 创建 Issue
2. 发送邮件至 support@example.com
3. 查看 [文档](docs/) 获取更多信息

---

**注意**: 这是从 .NET 版本转换而来的 Python FastAPI 实现，保持了原有系统的所有核心功能和业务逻辑。 