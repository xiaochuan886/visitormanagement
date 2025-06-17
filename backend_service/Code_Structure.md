# 访客管理系统通用化配置引擎 - 后端代码结构

## 📁 项目目录结构

```
backend_service/
├── app/                                    # 主应用目录
│   ├── __init__.py
│   ├── main.py                            # FastAPI应用入口
│   │
│   ├── core/                              # 核心配置模块
│   │   ├── __init__.py
│   │   ├── config.py                      # 应用配置
│   │   ├── security.py                    # 安全相关工具
│   │   ├── exceptions.py                  # 全局异常处理
│   │   └── middleware.py                  # 中间件配置
│   │
│   ├── domain/                            # 领域层 (DDD核心)
│   │   ├── __init__.py
│   │   ├── entities/                      # 实体对象
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # 基础实体类
│   │   │   ├── user.py                    # 用户实体
│   │   │   ├── visitor.py                 # 访客实体
│   │   │   └── site.py                    # 站点实体
│   │   ├── enums/                         # 枚举定义
│   │   │   ├── __init__.py
│   │   │   ├── config_enums.py            # 配置相关枚举
│   │   │   ├── spatial_enums.py           # 空间相关枚举
│   │   │   └── user_enums.py              # 用户相关枚举
│   │   ├── events/                        # 领域事件
│   │   │   ├── __init__.py
│   │   │   ├── config_events.py           # 配置变更事件
│   │   │   └── workflow_events.py         # 工作流事件
│   │   └── exceptions/                    # 领域异常
│   │       ├── __init__.py
│   │       ├── config_exceptions.py       # 配置异常
│   │       └── workflow_exceptions.py     # 工作流异常
│   │
│   ├── application/                       # 应用层 (业务逻辑)
│   │   ├── __init__.py
│   │   ├── dto/                          # 数据传输对象
│   │   │   ├── __init__.py
│   │   │   ├── base.py                    # 基础DTO类
│   │   │   ├── form_config_dto.py         # 表单配置DTO
│   │   │   ├── workflow_config_dto.py     # 工作流配置DTO
│   │   │   ├── spatial_config_dto.py      # 空间配置DTO
│   │   │   ├── business_rule_dto.py       # 业务规则DTO
│   │   │   ├── visitor_dto.py             # 访客DTO
│   │   │   └── user_dto.py                # 用户DTO
│   │   ├── interfaces/                    # 接口定义
│   │   │   ├── __init__.py
│   │   │   ├── repository.py              # 仓储接口
│   │   │   └── external_services.py       # 外部服务接口
│   │   └── services/                      # 应用服务
│   │       ├── __init__.py
│   │       ├── form_configuration_service.py      # 表单配置服务
│   │       ├── workflow_configuration_service.py  # 工作流配置服务
│   │       ├── spatial_configuration_service.py   # 空间配置服务
│   │       ├── business_rule_service.py           # 业务规则服务
│   │       ├── visitor_service.py                 # 访客服务
│   │       ├── user_service.py                    # 用户服务
│   │       ├── site_service.py                    # 站点服务
│   │       ├── employee_service.py                # 员工服务
│   │       └── department_service.py              # 部门服务
│   │
│   ├── infrastructure/                    # 基础设施层
│   │   ├── __init__.py
│   │   ├── database/                      # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── connection.py              # 数据库连接
│   │   │   ├── base.py                    # 基础模型类
│   │   │   └── models.py                  # SQLAlchemy模型
│   │   ├── repositories/                  # 仓储实现
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py         # 基础仓储类
│   │   │   ├── user_repository.py         # 用户仓储
│   │   │   ├── visitor_repository.py      # 访客仓储
│   │   │   ├── site_repository.py         # 站点仓储
│   │   │   ├── form_config_repository.py  # 表单配置仓储
│   │   │   ├── workflow_repository.py     # 工作流仓储
│   │   │   ├── spatial_repository.py      # 空间仓储
│   │   │   └── business_rule_repository.py # 业务规则仓储
│   │   ├── cache/                         # 缓存相关
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py            # Redis客户端
│   │   │   └── cache_service.py           # 缓存服务
│   │   └── external/                      # 外部服务集成
│   │       ├── __init__.py
│   │       ├── notification_service.py    # 通知服务
│   │       └── device_service.py          # 设备集成服务
│   │
│   └── api/                               # API层 (接口层)
│       ├── __init__.py
│       ├── dependencies/                  # API依赖
│       │   ├── __init__.py
│       │   ├── auth.py                    # 认证依赖
│       │   ├── database.py                # 数据库依赖
│       │   └── pagination.py             # 分页依赖
│       ├── middleware/                    # API中间件
│       │   ├── __init__.py
│       │   ├── cors.py                    # CORS中间件
│       │   ├── rate_limiting.py           # 限流中间件
│       │   └── error_handling.py         # 错误处理中间件
│       └── routes/                        # API路由
│           ├── __init__.py
│           ├── auth.py                    # 认证API
│           ├── visitors.py                # 访客管理API
│           ├── employees.py               # 员工管理API
│           ├── departments.py             # 部门管理API
│           ├── sites.py                   # 站点管理API
│           ├── form_config.py             # 表单配置API
│           ├── workflow_config.py         # 工作流配置API
│           ├── spatial_config.py          # 空间配置API
│           └── business_rules.py          # 业务规则API
│
├── alembic/                               # 数据库迁移
│   ├── versions/                          # 迁移脚本
│   ├── env.py                            # Alembic环境配置
│   └── script.py.mako                    # 迁移脚本模板
│
├── tests/                                 # 测试目录
│   ├── __init__.py
│   ├── conftest.py                       # pytest配置
│   ├── unit/                             # 单元测试
│   │   ├── test_services/                # 服务层测试
│   │   ├── test_repositories/            # 仓储层测试
│   │   └── test_utils/                   # 工具类测试
│   ├── integration/                      # 集成测试
│   │   ├── test_api/                     # API集成测试
│   │   └── test_database/                # 数据库集成测试
│   └── fixtures/                         # 测试数据
│       ├── form_configs.json             # 表单配置测试数据
│       ├── workflows.json                # 工作流测试数据
│       └── spatial_data.json             # 空间数据测试数据
│
├── scripts/                              # 脚本工具
│   ├── init_database.py                 # 数据库初始化
│   ├── migrate_data.py                   # 数据迁移
│   └── seed_data.py                      # 种子数据
│
├── docs/                                 # 文档目录
│   ├── api/                              # API文档
│   ├── architecture/                     # 架构文档
│   └── deployment/                       # 部署文档
│
├── docker-compose.yml                    # Docker编排文件
├── Dockerfile                           # Docker镜像文件
├── requirements.txt                     # Python依赖
├── alembic.ini                         # Alembic配置
├── .env.example                        # 环境变量示例
└── README.md                           # 项目说明
```

## 🏗️ 架构层级说明

### 1. 领域层 (Domain Layer)
**职责**: 包含核心业务逻辑和规则，独立于外部技术实现

```python
# domain/entities/form_config.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from uuid import UUID

@dataclass
class FormConfiguration:
    """表单配置实体 - 纯业务逻辑，无技术依赖"""
    id: Optional[UUID]
    config_name: str
    form_type: str
    fields: List[Dict]
    validation_rules: Optional[Dict]
    
    def validate_fields(self) -> bool:
        """业务逻辑：验证字段配置合法性"""
        return all(field.get('field_name') for field in self.fields)
    
    def is_active_configuration(self) -> bool:
        """业务逻辑：判断配置是否可用"""
        return len(self.fields) > 0 and self.validate_fields()
```

**关键文件:**
- `entities/`: 核心业务实体，包含业务规则
- `enums/`: 业务枚举值定义
- `events/`: 领域事件，用于模块间解耦
- `exceptions/`: 业务异常定义

### 2. 应用层 (Application Layer)
**职责**: 协调业务流程，处理用例场景，不包含业务逻辑

```python
# application/services/form_configuration_service.py
class FormConfigurationService:
    """应用服务 - 协调业务流程"""
    
    def __init__(self, 
                 form_repo: IFormConfigurationRepository,
                 cache_service: CacheService):
        self._form_repo = form_repo
        self._cache = cache_service
    
    async def create_form_configuration(
        self, 
        tenant_id: str,
        form_config: FormConfigurationCreateDTO,
        created_by: str
    ) -> FormConfigurationResponseDTO:
        """用例：创建表单配置"""
        # 1. 数据转换 (DTO -> Entity)
        entity = self._dto_to_entity(form_config)
        
        # 2. 业务规则验证 (调用领域层)
        if not entity.validate_fields():
            raise InvalidFormConfigurationError()
        
        # 3. 持久化 (调用基础设施层)
        saved_entity = await self._form_repo.create(entity)
        
        # 4. 缓存更新
        await self._cache.invalidate_form_config(tenant_id)
        
        # 5. 返回响应DTO
        return self._entity_to_dto(saved_entity)
```

**关键文件:**
- `dto/`: 数据传输对象，API和服务间数据交换
- `interfaces/`: 接口定义，依赖倒置原则
- `services/`: 应用服务，用例实现

### 3. 基础设施层 (Infrastructure Layer)
**职责**: 提供技术实现，如数据库访问、外部服务集成

```python
# infrastructure/repositories/form_config_repository.py
class FormConfigurationRepository(BaseRepository):
    """基础设施：数据访问实现"""
    
    async def create(self, entity: FormConfiguration) -> FormConfiguration:
        """技术实现：SQLAlchemy数据持久化"""
        model = FormConfigurationModel(
            config_name=entity.config_name,
            form_type=entity.form_type,
            fields=entity.fields,
            validation_rules=entity.validation_rules
        )
        
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        return self._model_to_entity(model)
    
    async def find_by_tenant_and_type(
        self, 
        tenant_id: str, 
        form_type: str
    ) -> List[FormConfiguration]:
        """技术实现：复杂查询"""
        query = select(FormConfigurationModel).where(
            and_(
                FormConfigurationModel.tenant_id == tenant_id,
                FormConfigurationModel.form_type == form_type,
                FormConfigurationModel.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]
```

**关键文件:**
- `database/`: 数据库连接和模型定义
- `repositories/`: 数据访问层实现
- `cache/`: 缓存服务实现
- `external/`: 外部服务集成

### 4. API层 (API Layer)
**职责**: HTTP接口暴露，请求处理，响应格式化

```python
# api/routes/form_config.py
@router.post("/", response_model=FormConfigurationResponseDTO)
async def create_form_configuration(
    form_config: FormConfigurationCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """API接口：创建表单配置"""
    service = FormConfigurationService(
        form_repo=FormConfigurationRepository(db),
        cache_service=get_cache_service()
    )
    
    return await service.create_form_configuration(
        tenant_id=current_user.tenant_id,
        form_config=form_config,
        created_by=current_user.username
    )
```

## 🎯 设计模式应用

### 1. 依赖注入 (Dependency Injection)
```python
# 通过FastAPI的Depends机制实现依赖注入
def get_form_service(
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service)
) -> FormConfigurationService:
    return FormConfigurationService(
        form_repo=FormConfigurationRepository(db),
        cache_service=cache
    )

@router.get("/")
async def list_forms(
    service: FormConfigurationService = Depends(get_form_service)
):
    return await service.list_configurations()
```

### 2. 仓储模式 (Repository Pattern)
```python
# 抽象仓储接口
class IFormConfigurationRepository(ABC):
    @abstractmethod
    async def create(self, entity: FormConfiguration) -> FormConfiguration:
        pass
    
    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[FormConfiguration]:
        pass

# 具体实现
class FormConfigurationRepository(IFormConfigurationRepository):
    async def create(self, entity: FormConfiguration) -> FormConfiguration:
        # SQLAlchemy实现
        pass
```

### 3. 工厂模式 (Factory Pattern)
```python
# 服务工厂
class ServiceFactory:
    @staticmethod
    def create_form_service(db: AsyncSession) -> FormConfigurationService:
        return FormConfigurationService(
            form_repo=FormConfigurationRepository(db),
            cache_service=RedisCacheService()
        )
    
    @staticmethod  
    def create_workflow_service(db: AsyncSession) -> WorkflowConfigurationService:
        return WorkflowConfigurationService(
            workflow_repo=WorkflowConfigurationRepository(db),
            notification_service=NotificationService()
        )
```

### 4. 策略模式 (Strategy Pattern)
```python
# 规则执行策略
class IRuleExecutionStrategy(ABC):
    @abstractmethod
    async def execute(self, rule: BusinessRule, data: dict) -> RuleResult:
        pass

class ValidationRuleStrategy(IRuleExecutionStrategy):
    async def execute(self, rule: BusinessRule, data: dict) -> RuleResult:
        # 验证规则执行逻辑
        pass

class AutoApprovalRuleStrategy(IRuleExecutionStrategy):
    async def execute(self, rule: BusinessRule, data: dict) -> RuleResult:
        # 自动审批规则执行逻辑
        pass

# 规则执行器
class RuleExecutor:
    def __init__(self):
        self._strategies = {
            'validation': ValidationRuleStrategy(),
            'auto_approval': AutoApprovalRuleStrategy()
        }
    
    async def execute_rule(self, rule: BusinessRule, data: dict) -> RuleResult:
        strategy = self._strategies.get(rule.rule_type)
        return await strategy.execute(rule, data)
```

## 📦 模块依赖关系

### 依赖方向 (Clean Architecture)
```
API层 (routes/) 
  ↓ 依赖
应用层 (application/services/)
  ↓ 依赖  
领域层 (domain/entities/)
  ↑ 实现
基础设施层 (infrastructure/)
```

### 模块间通信
```python
# 1. API层调用应用层
@router.post("/forms")
async def create_form(service: FormService = Depends(get_form_service)):
    return await service.create_configuration(...)

# 2. 应用层调用领域层
class FormConfigurationService:
    async def create_configuration(self, dto: FormConfigDTO):
        entity = FormConfiguration(...)  # 创建领域实体
        if not entity.validate_fields():  # 调用领域逻辑
            raise ValidationError()
        
        return await self._repo.create(entity)  # 调用基础设施层

# 3. 基础设施层实现领域接口
class FormConfigurationRepository(IFormConfigurationRepository):
    async def create(self, entity: FormConfiguration):
        # 具体的数据库实现
        pass
```

## 🧪 测试结构

### 测试金字塔
```
End-to-End Tests (少量)
    ↑
Integration Tests (中等)
    ↑
Unit Tests (大量)
```

### 测试示例
```python
# tests/unit/test_services/test_form_configuration_service.py
class TestFormConfigurationService:
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=IFormConfigurationRepository)
    
    @pytest.fixture
    def service(self, mock_repository):
        return FormConfigurationService(
            form_repo=mock_repository,
            cache_service=Mock()
        )
    
    async def test_create_valid_configuration(self, service, mock_repository):
        # 测试有效配置创建
        form_dto = FormConfigurationCreateDTO(...)
        mock_repository.create.return_value = FormConfiguration(...)
        
        result = await service.create_form_configuration(
            tenant_id="test",
            form_config=form_dto,
            created_by="admin"
        )
        
        assert result.config_name == form_dto.config_name
        mock_repository.create.assert_called_once()
```

## 🚀 部署和运行

### 开发环境
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 数据库迁移
alembic upgrade head

# 3. 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📋 代码规范

### 1. 命名约定
- **类名**: PascalCase (例: `FormConfigurationService`)
- **函数名**: snake_case (例: `create_form_configuration`)
- **常量**: UPPER_SNAKE_CASE (例: `MAX_FIELD_COUNT`)
- **私有成员**: 下划线前缀 (例: `_private_method`)

### 2. 文件组织
- 每个文件单一职责
- 相关功能模块化组织
- 避免循环依赖

### 3. 注释和文档
```python
class FormConfigurationService:
    """表单配置管理服务
    
    负责表单配置的生命周期管理，包括创建、更新、验证和删除。
    支持多租户隔离和缓存优化。
    """
    
    async def create_form_configuration(
        self,
        tenant_id: str,
        form_config: FormConfigurationCreateDTO,
        created_by: str
    ) -> FormConfigurationResponseDTO:
        """创建表单配置
        
        Args:
            tenant_id: 租户ID
            form_config: 表单配置数据
            created_by: 创建者用户名
            
        Returns:
            创建成功的表单配置
            
        Raises:
            ValidationError: 配置验证失败
            DuplicateConfigurationError: 配置名称重复
        """
        pass
```

---

**文档维护**: 后端开发团队  
**最后更新**: 2025年1月1日  
**代码结构版本**: v2.0 