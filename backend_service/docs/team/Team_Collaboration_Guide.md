# 团队协作指南

## 概述

本文档定义了访客管理系统开发团队的协作规范，包括代码规范、Git工作流、代码审查、CI/CD流程等，确保团队高效协作和代码质量。

## 团队结构

### 角色定义

```mermaid
graph TB
    PM[产品经理<br/>Product Manager]
    TL[技术负责人<br/>Tech Lead]
    BE[后端工程师<br/>Backend Engineer]
    FE[前端工程师<br/>Frontend Engineer]
    QA[测试工程师<br/>QA Engineer]
    DevOps[运维工程师<br/>DevOps Engineer]
    UI[UI/UX设计师<br/>UI/UX Designer]
    
    PM --> TL
    TL --> BE
    TL --> FE
    TL --> DevOps
    PM --> UI
    QA --> TL
    
    subgraph "开发团队"
        BE
        FE
        DevOps
    end
    
    subgraph "产品团队"
        PM
        UI
    end
    
    subgraph "质量团队"
        QA
    end
```

### 职责分工

#### 产品经理 (Product Manager)
- 需求分析和产品规划
- 用户故事编写和优先级排序
- 产品功能验收
- 与客户和利益相关者沟通

#### 技术负责人 (Tech Lead)
- 技术架构设计和决策
- 代码审查和技术指导
- 团队技术培训
- 技术风险评估

#### 后端工程师 (Backend Engineer)
- API设计和实现
- 数据库设计和优化
- 业务逻辑开发
- 性能优化

#### 前端工程师 (Frontend Engineer)
- 用户界面开发
- 前端架构设计
- 用户体验优化
- 前端性能优化

#### 测试工程师 (QA Engineer)
- 测试计划制定
- 自动化测试开发
- 功能测试和回归测试
- 质量保证

#### 运维工程师 (DevOps Engineer)
- CI/CD流水线维护
- 基础设施管理
- 监控和告警配置
- 部署和发布管理

## 代码规范

### 1. Python代码规范

#### 基础规范
```python
# 遵循PEP 8规范
# 使用Black进行代码格式化
# 使用isort进行导入排序

# 文件头部注释
"""
访客管理系统 - 访客服务模块

该模块提供访客相关的业务逻辑处理，包括访客创建、审批、签到等功能。

Author: 开发者姓名
Created: 2024-01-01
Modified: 2024-01-15
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

import structlog
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.visitor import Visitor
from app.domain.enums.visitor_status import VisitorStatus
from app.infrastructure.database.models import VisitorModel

logger = structlog.get_logger(__name__)


class VisitorService:
    """访客服务类
    
    提供访客相关的业务逻辑处理，包括：
    - 访客创建和更新
    - 访客审批流程
    - 访客签到签出
    """
    
    def __init__(self, db: AsyncSession):
        """初始化访客服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.logger = logger.bind(service="VisitorService")
    
    async def create_visitor(
        self, 
        visitor_data: Dict[str, Any],
        current_user: Dict[str, Any]
    ) -> Visitor:
        """创建访客
        
        Args:
            visitor_data: 访客数据
            current_user: 当前用户信息
            
        Returns:
            Visitor: 创建的访客实体
            
        Raises:
            HTTPException: 当数据验证失败时
        """
        self.logger.info(
            "创建访客请求",
            visitor_name=visitor_data.get("name"),
            user_id=current_user.get("user_id")
        )
        
        try:
            # 业务逻辑实现
            visitor = Visitor.create(visitor_data)
            
            # 保存到数据库
            visitor_model = VisitorModel.from_domain(visitor)
            self.db.add(visitor_model)
            await self.db.commit()
            
            self.logger.info(
                "访客创建成功",
                visitor_id=visitor.id,
                visitor_name=visitor.name
            )
            
            return visitor
            
        except Exception as e:
            self.logger.error(
                "访客创建失败",
                error=str(e),
                visitor_data=visitor_data
            )
            await self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"访客创建失败: {str(e)}"
            )
```

#### 命名规范
```python
# 类名：使用PascalCase
class VisitorService:
    pass

class UserRepository:
    pass

# 函数和变量名：使用snake_case
def create_visitor():
    pass

def get_visitor_by_id():
    pass

visitor_name = "张三"
user_id = "12345"

# 常量：使用UPPER_SNAKE_CASE
MAX_VISITORS_PER_DAY = 100
DEFAULT_VISIT_DURATION = 8  # 小时

# 私有方法和属性：使用单下划线前缀
class VisitorService:
    def _validate_visitor_data(self, data):
        pass
    
    def _send_notification(self, visitor):
        pass

# 枚举类：使用PascalCase
class VisitorStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
```

#### 类型注解
```python
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID

# 函数参数和返回值类型注解
async def get_visitors(
    tenant_id: str,
    status: Optional[VisitorStatus] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Visitor]:
    """获取访客列表"""
    pass

# 类属性类型注解
class VisitorDTO:
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    visit_date: datetime
    status: VisitorStatus
    
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        # ...

# 复杂类型注解
UserPermissions = Dict[str, List[str]]
VisitorFilters = Dict[str, Union[str, int, datetime]]
```

### 2. JavaScript/TypeScript代码规范

#### 基础规范
```typescript
// 使用TypeScript进行类型检查
// 使用ESLint和Prettier进行代码格式化
// 遵循Airbnb JavaScript Style Guide

/**
 * 访客管理服务
 * 
 * 提供访客相关的API调用和数据处理功能
 * 
 * @author 开发者姓名
 * @since 2024-01-01
 */

import { AxiosResponse } from 'axios';
import { Visitor, CreateVisitorRequest, VisitorStatus } from '@/types/visitor';
import { apiClient } from '@/utils/apiClient';
import { logger } from '@/utils/logger';

interface VisitorListResponse {
  items: Visitor[];
  total: number;
  page: number;
  pageSize: number;
}

interface VisitorFilters {
  search?: string;
  status?: VisitorStatus;
  dateRange?: [string, string];
  page?: number;
  pageSize?: number;
}

/**
 * 访客服务类
 */
export class VisitorService {
  private readonly baseUrl = '/api/v1/visitors';

  /**
   * 获取访客列表
   * 
   * @param filters 过滤条件
   * @returns 访客列表响应
   */
  async getVisitors(filters: VisitorFilters = {}): Promise<VisitorListResponse> {
    try {
      logger.info('获取访客列表', { filters });
      
      const response: AxiosResponse<VisitorListResponse> = await apiClient.get(
        this.baseUrl,
        { params: filters }
      );
      
      logger.info('访客列表获取成功', { 
        total: response.data.total,
        page: response.data.page 
      });
      
      return response.data;
    } catch (error) {
      logger.error('访客列表获取失败', { error, filters });
      throw error;
    }
  }

  /**
   * 创建访客
   * 
   * @param visitorData 访客数据
   * @returns 创建的访客
   */
  async createVisitor(visitorData: CreateVisitorRequest): Promise<Visitor> {
    try {
      logger.info('创建访客', { visitorName: visitorData.name });
      
      const response: AxiosResponse<Visitor> = await apiClient.post(
        this.baseUrl,
        visitorData
      );
      
      logger.info('访客创建成功', { 
        visitorId: response.data.id,
        visitorName: response.data.name 
      });
      
      return response.data;
    } catch (error) {
      logger.error('访客创建失败', { error, visitorData });
      throw error;
    }
  }
}

// 导出单例实例
export const visitorService = new VisitorService();
```

#### React组件规范
```typescript
// 使用函数组件和Hooks
// 使用TypeScript进行类型定义
// 遵循组件命名和结构规范

import React, { useState, useEffect, useCallback } from 'react';
import { Table, Button, Space, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Visitor, VisitorStatus } from '@/types/visitor';
import { visitorService } from '@/services/visitorService';
import { useAppSelector, useAppDispatch } from '@/hooks/redux';
import { VisitorFilters } from '@/components/VisitorFilters';
import { VisitorModal } from '@/components/VisitorModal';

interface VisitorListProps {
  /** 是否显示操作列 */
  showActions?: boolean;
  /** 自定义过滤器 */
  defaultFilters?: Record<string, any>;
  /** 选择变化回调 */
  onSelectionChange?: (selectedVisitors: Visitor[]) => void;
}

/**
 * 访客列表组件
 * 
 * 显示访客列表，支持搜索、过滤、分页等功能
 */
export const VisitorList: React.FC<VisitorListProps> = ({
  showActions = true,
  defaultFilters = {},
  onSelectionChange,
}) => {
  // 状态定义
  const [visitors, setVisitors] = useState<Visitor[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  // Redux状态
  const currentUser = useAppSelector(state => state.auth.user);
  const dispatch = useAppDispatch();

  /**
   * 加载访客列表
   */
  const loadVisitors = useCallback(async (filters = {}) => {
    setLoading(true);
    try {
      const response = await visitorService.getVisitors({
        ...defaultFilters,
        ...filters,
      });
      setVisitors(response.items);
    } catch (error) {
      message.error('加载访客列表失败');
    } finally {
      setLoading(false);
    }
  }, [defaultFilters]);

  /**
   * 处理访客创建
   */
  const handleCreateVisitor = useCallback(async (visitorData: any) => {
    try {
      await visitorService.createVisitor(visitorData);
      message.success('访客创建成功');
      setModalVisible(false);
      await loadVisitors();
    } catch (error) {
      message.error('访客创建失败');
    }
  }, [loadVisitors]);

  // 组件挂载时加载数据
  useEffect(() => {
    loadVisitors();
  }, [loadVisitors]);

  // 表格列定义
  const columns = [
    {
      title: '访客姓名',
      dataIndex: 'name',
      key: 'name',
      sorter: true,
    },
    {
      title: '联系电话',
      dataIndex: 'phone',
      key: 'phone',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: VisitorStatus) => (
        <VisitorStatusTag status={status} />
      ),
    },
    ...(showActions ? [{
      title: '操作',
      key: 'actions',
      render: (_: any, record: Visitor) => (
        <Space>
          <Button size="small" onClick={() => handleViewVisitor(record.id)}>
            查看
          </Button>
          <Button size="small" onClick={() => handleEditVisitor(record.id)}>
            编辑
          </Button>
        </Space>
      ),
    }] : []),
  ];

  return (
    <div className="visitor-list">
      <div className="visitor-list__header">
        <h2>访客管理</h2>
        {showActions && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            新增访客
          </Button>
        )}
      </div>

      <VisitorFilters onFilter={loadVisitors} />

      <Table
        columns={columns}
        dataSource={visitors}
        loading={loading}
        rowKey="id"
        rowSelection={{
          selectedRowKeys,
          onChange: (keys, rows) => {
            setSelectedRowKeys(keys as string[]);
            onSelectionChange?.(rows);
          },
        }}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条记录`,
        }}
      />

      <VisitorModal
        visible={modalVisible}
        onCancel={() => setModalVisible(false)}
        onSubmit={handleCreateVisitor}
      />
    </div>
  );
};
```

## Git工作流

### 1. 分支策略

```mermaid
gitgraph
    commit id: "Initial"
    
    branch develop
    checkout develop
    commit id: "Dev setup"
    
    branch feature/visitor-management
    checkout feature/visitor-management
    commit id: "Add visitor model"
    commit id: "Add visitor API"
    commit id: "Add visitor tests"
    
    checkout develop
    merge feature/visitor-management
    commit id: "Merge visitor feature"
    
    branch release/v1.0.0
    checkout release/v1.0.0
    commit id: "Prepare release"
    commit id: "Fix bugs"
    
    checkout main
    merge release/v1.0.0
    commit id: "Release v1.0.0"
    
    checkout develop
    merge release/v1.0.0
    
    branch hotfix/critical-bug
    checkout hotfix/critical-bug
    commit id: "Fix critical bug"
    
    checkout main
    merge hotfix/critical-bug
    commit id: "Hotfix v1.0.1"
    
    checkout develop
    merge hotfix/critical-bug
```

#### 分支类型说明

**主分支 (main)**
- 生产环境代码
- 只接受来自release和hotfix分支的合并
- 每次合并都应该打tag

**开发分支 (develop)**
- 开发环境代码
- 功能分支的合并目标
- 定期合并到release分支

**功能分支 (feature/***)**
- 新功能开发
- 从develop分支创建
- 完成后合并回develop分支

**发布分支 (release/***)**
- 准备发布的代码
- 从develop分支创建
- 只允许bug修复，不允许新功能
- 完成后合并到main和develop

**热修复分支 (hotfix/***)**
- 紧急bug修复
- 从main分支创建
- 完成后合并到main和develop

### 2. 提交规范

#### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 类型说明
```bash
# 功能相关
feat: 新功能
fix: bug修复
perf: 性能优化

# 代码质量
refactor: 重构（不是新功能，也不是修复bug）
style: 格式（不影响代码运行的变动）
test: 增加测试

# 构建和工具
build: 影响构建系统或外部依赖的更改
ci: 持续集成配置文件和脚本的更改
chore: 其他不修改src或测试文件的更改

# 文档
docs: 文档更新
```

#### 提交示例
```bash
# 新功能
git commit -m "feat(visitor): 添加访客审批功能

- 实现访客审批API
- 添加审批历史记录
- 支持批量审批操作

Closes #123"

# Bug修复
git commit -m "fix(auth): 修复JWT令牌过期问题

修复了令牌刷新时的时间计算错误，确保令牌在正确的时间过期。

Fixes #456"

# 重构
git commit -m "refactor(database): 优化数据库查询性能

- 添加复合索引
- 优化N+1查询问题
- 使用连接查询替代子查询"
```

### 3. 代码审查流程

#### Pull Request模板
```markdown
## 变更描述
简要描述本次变更的内容和目的。

## 变更类型
- [ ] 新功能 (feature)
- [ ] Bug修复 (fix)
- [ ] 重构 (refactor)
- [ ] 性能优化 (perf)
- [ ] 文档更新 (docs)
- [ ] 测试 (test)

## 测试
- [ ] 单元测试已通过
- [ ] 集成测试已通过
- [ ] 手动测试已完成
- [ ] 性能测试已完成（如适用）

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 已添加必要的测试
- [ ] 已更新相关文档
- [ ] 已考虑向后兼容性
- [ ] 已考虑安全性影响

## 相关Issue
Closes #123
Related to #456

## 截图（如适用）
如果是UI相关的变更，请提供截图。

## 部署说明
如果需要特殊的部署步骤，请在此说明。
```

#### 审查要点
```python
# 代码审查检查清单

class CodeReviewChecklist:
    """代码审查检查清单"""
    
    FUNCTIONALITY = [
        "代码是否实现了预期功能？",
        "是否有明显的逻辑错误？",
        "边界条件是否处理正确？",
        "错误处理是否充分？"
    ]
    
    CODE_QUALITY = [
        "代码是否易于理解？",
        "命名是否清晰有意义？",
        "函数是否过于复杂？",
        "是否有重复代码？",
        "是否遵循项目规范？"
    ]
    
    PERFORMANCE = [
        "是否有性能问题？",
        "数据库查询是否优化？",
        "是否有内存泄漏风险？",
        "算法复杂度是否合理？"
    ]
    
    SECURITY = [
        "是否有安全漏洞？",
        "输入验证是否充分？",
        "敏感信息是否正确处理？",
        "权限检查是否到位？"
    ]
    
    TESTING = [
        "测试覆盖率是否足够？",
        "测试用例是否有意义？",
        "是否测试了边界条件？",
        "是否有集成测试？"
    ]
```

## CI/CD流程

### 1. GitHub Actions配置

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  # 代码质量检查
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run Black
        run: black --check .
      
      - name: Run isort
        run: isort --check-only .
      
      - name: Run flake8
        run: flake8 .
      
      - name: Run mypy
        run: mypy .

  # 安全扫描
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r app/ -f json -o bandit-report.json
      
      - name: Run Safety
        run: |
          pip install safety
          safety check --json --output safety-report.json
      
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json

  # 后端测试
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest --cov=app --cov-report=xml --cov-report=html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  # 前端测试
  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Run ESLint
        working-directory: frontend
        run: npm run lint
      
      - name: Run tests
        working-directory: frontend
        run: npm run test:coverage
      
      - name: Build
        working-directory: frontend
        run: npm run build

  # 构建Docker镜像
  build:
    needs: [lint, security, backend-test, frontend-test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            visitor-management:${{ github.sha }}
            visitor-management:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # 部署到测试环境
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment"
          # 部署脚本

  # 部署到生产环境
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying to production environment"
          # 部署脚本
```

### 2. 质量门禁

```yaml
# .github/workflows/quality-gate.yml
name: Quality Gate

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # 获取完整历史用于SonarQube分析
      
      - name: SonarQube Scan
        uses: sonarqube-quality-gate-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          scanMetadataReportFile: target/sonar/report-task.txt
      
      - name: Check coverage threshold
        run: |
          coverage_percent=$(python -c "
          import xml.etree.ElementTree as ET
          tree = ET.parse('coverage.xml')
          root = tree.getroot()
          coverage = float(root.attrib['line-rate']) * 100
          print(f'{coverage:.1f}')
          ")
          
          if (( $(echo "$coverage_percent < 80" | bc -l) )); then
            echo "Coverage $coverage_percent% is below threshold 80%"
            exit 1
          fi
          
          echo "Coverage $coverage_percent% meets threshold"
      
      - name: Check security vulnerabilities
        run: |
          # 检查是否有高危漏洞
          if grep -q '"severity": "HIGH"' bandit-report.json; then
            echo "High severity security issues found"
            exit 1
          fi
```

## 开发环境配置

### 1. 开发工具配置

#### VS Code配置
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".coverage": true,
    "htmlcov": true
  }
}
```

#### 推荐扩展
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-vscode-remote.remote-containers"
  ]
}
```

### 2. 预提交钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]

  - repo: https://github.com/prettier/prettier
    rev: v2.8.4
    hooks:
      - id: prettier
        files: \.(js|jsx|ts|tsx|json|css|md)$
```

## 沟通协作

### 1. 会议规范

#### 每日站会 (Daily Standup)
- **时间**: 每天上午9:30，15分钟
- **参与者**: 开发团队所有成员
- **内容**:
  - 昨天完成了什么
  - 今天计划做什么
  - 遇到了什么阻碍

#### 迭代规划会 (Sprint Planning)
- **时间**: 每两周一次，2小时
- **参与者**: 产品经理、技术负责人、开发团队
- **内容**:
  - 回顾上个迭代
  - 规划下个迭代任务
  - 估算工作量

#### 代码审查会 (Code Review)
- **时间**: 每周一次，1小时
- **参与者**: 技术负责人、开发团队
- **内容**:
  - 审查重要代码变更
  - 分享最佳实践
  - 讨论技术改进

### 2. 文档协作

#### 技术文档规范
```markdown
# 文档标题

## 概述
简要描述文档内容和目的。

## 目标读者
明确文档的目标读者群体。

## 前置条件
列出阅读本文档需要的前置知识。

## 详细内容
...

## 示例
提供具体的代码示例。

## 常见问题
列出常见问题和解决方案。

## 参考资料
列出相关的参考资料和链接。

---
作者: 姓名
创建时间: YYYY-MM-DD
最后更新: YYYY-MM-DD
审核者: 姓名
```

#### 知识分享
- **技术分享会**: 每月一次，团队成员轮流分享
- **代码走读**: 重要功能完成后进行团队走读
- **最佳实践文档**: 及时记录和分享最佳实践
- **问题解决记录**: 记录重要问题的解决过程

---

本团队协作指南确保了开发团队的高效协作和代码质量，为项目的成功交付提供了坚实的基础。 