# 访客管理系统开发指南

## 项目概述

访客管理系统是一个基于Python FastAPI框架的现代化Web应用，采用Clean Architecture架构模式，提供完整的访客生命周期管理功能。

### 技术栈
- **后端框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL + SQLAlchemy 2.0 (异步)
- **缓存**: Redis 4.6.0
- **认证**: JWT (PyJWT)
- **数据验证**: Pydantic V2
- **数据库迁移**: Alembic
- **容器化**: Docker + Docker Compose

## 项目结构

```
backend_service/
├── app/                          # 应用程序主目录
│   ├── domain/                   # 领域层 (Domain Layer)
│   │   ├── entities/            # 实体类
│   │   ├── enums/               # 枚举定义
│   │   └── events/              # 领域事件
│   ├── application/             # 应用层 (Application Layer)
│   │   ├── dto/                 # 数据传输对象
│   │   ├── interfaces/          # 接口定义
│   │   └── services/            # 应用服务
│   ├── infrastructure/          # 基础设施层 (Infrastructure Layer)
│   │   ├── database/            # 数据库相关
│   │   ├── cache/               # 缓存相关
│   │   ├── auth/                # 认证相关
│   │   └── repositories/        # 数据访问层
│   ├── api/                     # API层 (Presentation Layer)
│   │   ├── routes/              # 路由定义
│   │   ├── middleware/          # 中间件
│   │   └── dependencies/        # 依赖注入
│   └── core/                    # 核心配置
├── alembic/                     # 数据库迁移
├── docs/                        # 项目文档
├── requirements.txt             # Python依赖
├── docker-compose.yml           # Docker编排
├── main.py                      # 应用入口
└── .env                         # 环境配置
```

## 开发环境搭建

### 1. 环境要求
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (可选，使用Docker)
- Redis 7+ (可选，使用Docker)

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 编辑 .env 文件，配置数据库和Redis连接信息
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/visitor_management
REDIS_URL=redis://localhost:6380/0
```

### 4. 启动数据库服务
```bash
# 启动PostgreSQL和Redis
docker-compose -f docker-compose-simple.yml up -d
```

### 5. 启动应用
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

## 架构设计

### Clean Architecture 四层架构

#### 1. 领域层 (Domain Layer)
包含业务实体、业务规则和领域逻辑，不依赖任何外部框架。

#### 2. 应用层 (Application Layer)
协调领域对象，实现用例，定义应用服务和DTO。

#### 3. 基础设施层 (Infrastructure Layer)
实现技术细节，如数据库、缓存、外部服务。

#### 4. API层 (Presentation Layer)
处理HTTP请求，调用应用服务。

## 开发规范

### 1. 代码风格
- 遵循 **PEP 8** 编码规范
- 使用类型注解 (Type Hints)
- 函数必须有docstring

### 2. 命名规范
- **类名**: PascalCase (如 `VisitorService`)
- **函数/变量名**: snake_case (如 `get_visitor_by_id`)
- **常量**: UPPER_SNAKE_CASE (如 `MAX_VISITORS_PER_DAY`)

### 3. 错误处理
- 使用自定义异常类
- 统一的错误响应格式
- 记录详细的错误日志

## API开发

### 1. 路由组织
按功能模块组织路由：

```python
from fastapi import APIRouter
from .auth import router as auth_router
from .visitors import router as visitors_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(visitors_router, prefix="/visitors", tags=["访客管理"])
```

### 2. 请求验证
使用Pydantic进行数据验证：

```python
class CreateVisitorDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="访客姓名")
    phone: str = Field(..., regex=r"^1[3-9]\d{9}$", description="手机号码")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    visit_date: date = Field(..., description="访问日期")
```

## 数据库开发

### 1. 模型定义
使用SQLAlchemy 2.0异步模型：

```python
class VisitorModel(Base):
    __tablename__ = "visitors"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
```

### 2. 数据库迁移
使用Alembic进行数据库版本管理：

```bash
# 创建迁移文件
alembic revision --autogenerate -m "Add visitor table"

# 应用迁移
alembic upgrade head
```

## 认证与授权

### 1. JWT认证
系统使用JWT进行用户认证，支持访问令牌和刷新令牌。

### 2. 权限控制
基于角色的访问控制，支持多租户架构。

## 缓存策略

使用Redis进行数据缓存，提升系统性能：

```python
class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600) -> None:
        await self.redis.set(key, value, ex=expire)
```

## 部署指南

### 1. Docker部署
```bash
# 构建镜像
docker build -t visitor-management .

# 启动服务
docker-compose up -d
```

### 2. 生产环境配置
```bash
# 环境变量
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/visitor_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"
export DEBUG=false
```

## 监控和日志

### 1. 健康检查
系统提供健康检查端点：`GET /health`

### 2. 结构化日志
使用结构化日志记录系统运行状态和错误信息。

## 测试

### 1. 单元测试
使用pytest进行单元测试：

```python
@pytest.mark.asyncio
async def test_create_visitor():
    # 测试代码
    pass
```

### 2. 集成测试
测试API端点的完整功能。

## 常见问题

### 1. 数据库连接问题
检查数据库连接配置和服务状态。

### 2. 端口冲突
修改docker-compose.yml中的端口映射。

### 3. 依赖安装问题
确保Python版本兼容，使用虚拟环境。

## 扩展开发

### 1. 添加新的API端点
1. 定义实体和DTO
2. 实现业务逻辑
3. 创建数据访问层
4. 定义API路由

### 2. 集成第三方服务
可以集成短信、邮件、支付等第三方服务。

## 开发工具推荐

### 1. IDE
- **PyCharm**: 专业Python IDE
- **VS Code**: 轻量级编辑器

### 2. 调试工具
- **FastAPI自带调试**: 自动重载和错误页面
- **pytest**: 测试框架

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 提交规范
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
```

---

更多详细信息请参考：
- [API文档](./API_Documentation.md)
- [数据库设计](../DB_Schema.md)
- [部署指南](../README.md) 