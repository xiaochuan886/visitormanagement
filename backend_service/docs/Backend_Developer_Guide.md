# 后端开发者指南

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **适用角色**: 后端开发者、新成员入职

## 🚀 快速开始

### 环境要求
- **Python**: 3.12+
- **PostgreSQL**: 15+
- **Redis**: 7+
- **Docker**: 20.10+ (可选)

### 开发环境搭建

#### 1. 克隆项目
```bash
git clone <repository_url>
cd visitormanagement/backend_service
```

#### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 环境配置
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
DATABASE_URL=postgresql://postgres:postgres@localhost:5434/visitormanagement
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
```

#### 5. 数据库初始化
```bash
# 运行数据库迁移
alembic upgrade head

# 创建测试数据
python scripts/create_test_data.py
```

#### 6. 启动服务
```bash
# 开发模式启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 访问API文档
# http://localhost:8000/docs
```

## 🏗️ 项目结构详解

### 核心目录说明
```
backend_service/
├── app/                    # 主应用代码
│   ├── api/               # API路由层
│   ├── application/       # 应用业务层
│   ├── domain/           # 领域模型层
│   ├── infrastructure/   # 基础设施层
│   └── core/            # 核心配置
├── alembic/             # 数据库迁移
├── test/               # 测试代码
├── docs/               # 项目文档
└── requirements.txt    # 依赖清单
```

### 代码组织原则
- **分层架构**: 严格按照Clean Architecture分层
- **依赖倒置**: 高层模块不依赖低层模块
- **单一职责**: 每个模块职责单一明确
- **开闭原则**: 对扩展开放，对修改关闭

## 💻 开发工作流

### 1. 功能开发流程
```bash
# 1. 创建功能分支
git checkout -b feature/visitor-export

# 2. 开发功能
# - 编写业务逻辑
# - 编写测试用例
# - 更新API文档

# 3. 运行测试
pytest test/

# 4. 代码检查
flake8 app/
black app/
isort app/

# 5. 提交代码
git add .
git commit -m "feat: 添加访客导出功能"

# 6. 推送并创建PR
git push origin feature/visitor-export
```

### 2. 代码审查标准
- **功能完整性**: 功能实现完整，边界情况处理
- **代码质量**: 符合编码规范，可读性良好
- **测试覆盖**: 单元测试覆盖率 > 80%
- **文档更新**: API文档和注释及时更新
- **性能考虑**: 查询优化，避免N+1问题

## 🧪 测试指南

### 测试策略
```
测试金字塔
├── 单元测试 (70%)     # 测试单个函数/方法
├── 集成测试 (20%)     # 测试模块间交互
└── 端到端测试 (10%)   # 测试完整流程
```

### 单元测试示例
```python
# test/unit/test_visitor_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.application.services.visitor_service import VisitorService

class TestVisitorService:
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def visitor_service(self, mock_repository):
        return VisitorService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_visitor_success(self, visitor_service, mock_repository):
        # Arrange
        visitor_data = {
            "name": "张三",
            "phone_number": "13800138000",
            "purpose": "business_meeting"
        }
        mock_repository.create.return_value = AsyncMock(id=1, **visitor_data)
        
        # Act
        result = await visitor_service.create_visitor(visitor_data, "admin")
        
        # Assert
        assert result.success == True
        assert result.data.name == "张三"
        mock_repository.create.assert_called_once()
```

### 集成测试示例
```python
# test/integration/test_visitor_api.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestVisitorAPI:
    @pytest.mark.asyncio
    async def test_create_visitor_endpoint(self, auth_headers):
        visitor_data = {
            "name": "李四",
            "phone_number": "13900139000",
            "purpose": "interview",
            "employee_id": 1
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/visitors/",
                json=visitor_data,
                headers=auth_headers
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "李四"
        assert "pass_code" in data
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest test/unit/test_visitor_service.py

# 运行并查看覆盖率
pytest --cov=app test/

# 生成HTML覆盖率报告
pytest --cov=app --cov-report=html test/
```

## 📝 编码规范

### Python代码规范
- **PEP 8**: 遵循Python官方代码规范
- **类型注解**: 使用类型提示增强代码可读性
- **文档字符串**: 为类和函数编写清晰的文档字符串
- **异常处理**: 明确的异常处理和错误信息

### 命名规范
```python
# 类名：大驼峰命名
class VisitorService:
    pass

# 函数/变量名：小写下划线
def create_visitor():
    pass

visitor_count = 0

# 常量：大写下划线
MAX_VISITORS_PER_DAY = 1000

# 私有成员：前缀下划线
class Service:
    def _private_method(self):
        pass
```

### 代码注释规范
```python
class VisitorService:
    """访客服务类
    
    负责处理访客相关的业务逻辑，包括创建、更新、查询和删除访客信息。
    支持多租户环境下的数据隔离和权限控制。
    
    Attributes:
        repository: 访客数据仓储
        logger: 日志记录器
    """
    
    async def create_visitor(
        self, 
        visitor_data: dict, 
        created_by: str
    ) -> ServiceResult:
        """创建新访客
        
        Args:
            visitor_data: 访客信息字典，包含姓名、电话等必要信息
            created_by: 创建者用户名
            
        Returns:
            ServiceResult: 包含创建结果和访客信息的服务结果对象
            
        Raises:
            ValidationError: 当访客数据验证失败时
            DuplicateError: 当访客已存在时
        """
        pass
```

## 🔧 配置管理

### 环境配置
```python
# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    database_url: str
    database_echo: bool = False
    
    # Redis配置
    redis_url: str
    
    # JWT配置
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    
    # 应用配置
    app_name: str = "访客管理系统"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 日志配置
```python
# app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # 创建logger
    logger = logging.getLogger("visitor_management")
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## 🚀 性能优化

### 数据库查询优化
```python
# 使用索引优化查询
async def get_visitors_by_status(status: str, tenant_id: str):
    # 好的查询：使用索引字段
    query = select(VisitorModel).where(
        and_(
            VisitorModel.tenant_id == tenant_id,
            VisitorModel.status == status,
            VisitorModel.is_deleted == False
        )
    )
    return await session.execute(query)

# 避免N+1查询问题
async def get_visitors_with_employees():
    # 使用join预加载关联数据
    query = select(VisitorModel).options(
        joinedload(VisitorModel.employee).joinedload(EmployeeModel.department)
    )
    return await session.execute(query)
```

### 缓存策略
```python
# app/core/cache.py
from functools import wraps
import json
import hashlib

def cache_result(ttl: int = 300):
    """结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hashlib.md5(
                json.dumps([args, kwargs], sort_keys=True).encode()
            ).hexdigest()}"
            
            # 尝试从缓存获取
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# 使用示例
@cache_result(ttl=600)
async def get_department_tree(tenant_id: str):
    """获取部门树结构（缓存10分钟）"""
    pass
```

## 🔐 安全开发

### 输入验证
```python
from pydantic import BaseModel, validator

class VisitorCreateDTO(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('姓名至少需要2个字符')
        if len(v) > 50:
            raise ValueError('姓名不能超过50个字符')
        return v.strip()
    
    @validator('phone_number')
    def validate_phone(cls, v):
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入正确的手机号码')
        return v
```

### SQL注入防护
```python
# 安全的查询方式
async def get_visitor_by_id(visitor_id: int, tenant_id: str):
    # 使用参数化查询，避免SQL注入
    query = select(VisitorModel).where(
        and_(
            VisitorModel.id == visitor_id,
            VisitorModel.tenant_id == tenant_id
        )
    )
    return await session.execute(query)

# 危险的查询方式（禁止使用）
# query = f"SELECT * FROM visitors WHERE id = {visitor_id}"  # SQL注入风险
```

## 🔍 调试技巧

### 日志调试
```python
import logging

logger = logging.getLogger(__name__)

async def create_visitor(visitor_data: dict):
    logger.info(f"开始创建访客: {visitor_data.get('name')}")
    
    try:
        # 业务逻辑
        result = await repository.create(visitor_data)
        logger.info(f"访客创建成功: ID={result.id}")
        return result
    except Exception as e:
        logger.error(f"访客创建失败: {str(e)}", exc_info=True)
        raise
```

### 性能分析
```python
import time
from functools import wraps

def performance_monitor(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 执行时间: {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败: {execution_time:.2f}s, 错误: {str(e)}")
            raise
    return wrapper
```

## 📚 常用工具和库

### 开发工具
- **IDE**: PyCharm, VSCode
- **代码格式化**: black, isort
- **代码检查**: flake8, pylint
- **类型检查**: mypy
- **文档生成**: sphinx

### 推荐库
```python
# 异步HTTP客户端
import httpx

# 数据验证
from pydantic import BaseModel

# 日期时间处理
from datetime import datetime, timezone
import pendulum

# 工具函数
from typing import Optional, List, Dict
from uuid import UUID, uuid4
```

## 🚨 错误处理

### 异常层次结构
```python
# app/domain/exceptions/base.py
class DomainException(Exception):
    """领域异常基类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ValidationError(DomainException):
    """数据验证异常"""
    pass

class NotFoundError(DomainException):
    """资源不存在异常"""
    pass

class PermissionDeniedError(DomainException):
    """权限拒绝异常"""
    pass
```

### 全局异常处理
```python
# app/api/middleware/exception_handler.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "timestamp": datetime.now().isoformat()
        }
    )
```

## 📋 开发清单

### 新功能开发检查清单
- [ ] **需求分析**: 理解业务需求和技术要求
- [ ] **接口设计**: 设计API接口和数据模型
- [ ] **数据库设计**: 设计表结构和索引
- [ ] **编写代码**: 实现业务逻辑和API接口
- [ ] **编写测试**: 单元测试和集成测试
- [ ] **性能测试**: 查询性能和并发测试
- [ ] **安全检查**: 输入验证和权限控制
- [ ] **文档更新**: API文档和开发文档
- [ ] **代码审查**: 同事代码审查
- [ ] **部署测试**: 测试环境验证

---

## 📞 技术支持

### 开发支持
- **负责人**: 技术负责人
- **代码规范**: 参考本文档编码规范
- **问题反馈**: 通过项目Issue或技术群讨论

### 相关文档
- [后端系统架构概览](./Backend_System_Architecture.md)
- [后端API完整参考手册](./Backend_API_Reference.md)
- [后端数据模型设计文档](./Backend_Data_Models.md)
- [性能优化指南](./Backend_Performance_Guide.md) 