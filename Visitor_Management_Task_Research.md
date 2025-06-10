# Context
Filename: Visitor_Management_Task_Research.md
Created On: 2024-12-28
Created By: AI Assistant
Associated Protocol: RIPER-5 + Multidimensional + Agent Protocol

# Task Description
为访客管理系统项目生成Cursor规则，提高开发效率和代码质量

# Project Overview
基于 FastAPI + Clean Architecture 的企业级访客管理系统，支持多租户、实时通信和完整的访客生命周期管理。采用领域驱动设计，具有分层架构，包含认证授权、访客管理、组织管理等核心模块。

---
*以下部分由AI在协议执行期间维护*
---

# Analysis (由 RESEARCH 模式填充)

## 代码调研结果
### 项目架构分析
- **技术栈**: FastAPI + SQLAlchemy 2.0 + Pydantic V2 + PostgreSQL + Redis
- **架构模式**: Clean Architecture + DDD (领域驱动设计)
- **分层结构**: domain(领域层) + application(应用层) + infrastructure(基础设施层) + api(API层)
- **多租户**: 基于JWT的行级数据隔离架构

### 核心文件和依赖关系
- **主入口**: `backend_service/main.py` - FastAPI应用启动点
- **领域层**: `backend_service/app/domain/` - 实体、枚举、事件、异常
- **应用层**: `backend_service/app/application/` - 服务、DTO、接口定义
- **基础设施层**: `backend_service/app/infrastructure/` - 数据访问、缓存、认证
- **API层**: `backend_service/app/api/` - 路由、中间件、依赖注入

### 关键业务模块
1. **认证授权** (`app/api/routes/auth.py`) - JWT令牌管理、RBAC权限控制
2. **访客管理** - 完整的访客生命周期管理
3. **组织架构** - 员工、部门、站点管理
4. **二维码系统** - 动态二维码生成和验证

### 现有规则文件分析
- **12个角色规则**: backendengineer, webclient, mobileclient, tester, pm, uiux等
- **基础规则**: always.mdc 包含MCP交互反馈规则
- **规则覆盖**: 主要针对角色职责，缺少项目特定的架构指导

### 技术约束和要求
- **Python 3.11+** 版本要求
- **异步编程** - 全异步架构设计
- **类型安全** - Pydantic数据验证和序列化
- **安全性** - JWT认证、密码哈希、CORS支持
- **性能优化** - Redis缓存、数据库索引优化
- **容器化** - Docker + Docker Compose部署

### 扩展能力评估
- **智能设备集成** - 具备人脸识别、车牌识别扩展基础
- **微信生态** - 支持企业微信通知和公众号OAuth
- **API成熟度** - 28个业务接口，90%业务需求满足度
- **生产就绪** - 企业级部署标准，完整的测试套件 

# Proposed Solution (由 INNOVATE 模式填充)

## 规则设计方案分析

### 方案一：分层架构指导规则
**设计思路**: 遵循Clean Architecture，为domain、application、infrastructure、api四层创建专门规则
**优势**: 
- 强制执行架构边界，防止依赖倒置
- 确保代码职责分离清晰
- 对新团队成员友好
**劣势**:
- 规则文件过多，维护复杂
- 对简单修改可能过于严格

### 方案二：业务领域驱动规则  
**设计思路**: 按访客管理、认证授权、组织架构等业务领域划分规则
**优势**:
- 与业务需求紧密对齐
- 便于业务专家理解和协作
- 保持业务逻辑一致性
**劣势**:
- 技术决策指导不足
- 跨领域功能处理复杂

### 方案三：开发场景驱动规则
**设计思路**: 基于新功能开发、Bug修复、性能优化等实际开发任务设计
**优势**:
- 与日常工作流程匹配
- 提供实用的操作指导
- 容易被开发者接受
**劣势**:
- 缺乏架构层面约束
- 规则覆盖可能不全面

### 方案四：混合分层规则体系 (推荐)
**设计思路**: 结合上述方法优点，创建三层规则体系：
1. **核心项目规则** - 架构约束和通用指导
2. **业务领域规则** - 具体业务逻辑指导  
3. **开发场景规则** - 工作流程指导

**优势**:
- 全面而灵活，适应不同需求
- 保持规则可管理性
- 支持渐进式规则应用

## 最终推荐方案
采用**混合分层规则体系**，具体包括：

### 核心规则层
- `visitor-management-core.mdc` - 项目核心架构和技术栈指导
- `clean-architecture.mdc` - Clean Architecture实施规范
- `security-standards.mdc` - 安全开发标准

### 业务领域规则层  
- `visitor-domain.mdc` - 访客管理领域逻辑
- `auth-domain.mdc` - 认证授权领域
- `organization-domain.mdc` - 组织架构管理

### 开发场景规则层
- `api-development.mdc` - API开发最佳实践
- `testing-standards.mdc` - 测试规范和流程
- `performance-optimization.mdc` - 性能优化指导

### 设计原则
- **架构约束与实用指导平衡** - 既防止架构腐化，又提高开发效率
- **通用性与特定性结合** - 项目特定深度指导 + 适度通用性
- **渐进式规则应用** - 允许团队逐步采用更严格规则 

# Implementation Plan (由 PLAN 模式生成)

## 实施计划详细规范

### 文件路径和组件关系
- **目标目录**: `.cursor/rules/`  
- **现有文件**: 已存在12个角色规则文件和always.mdc基础规则  
- **新增文件**: 9个项目特定规则文件  
- **命名约定**: 采用kebab-case命名，.mdc扩展名  

### 规则文件架构设计

#### 核心规则层 (3个文件)
1. **visitor-management-core.mdc** - 项目整体架构指导、技术栈标准、开发环境配置
2. **clean-architecture.mdc** - Clean Architecture实施规范、层次依赖约束、代码组织标准  
3. **security-standards.mdc** - 安全开发标准、JWT处理、数据验证、权限控制

#### 业务领域规则层 (3个文件)  
4. **visitor-domain.mdc** - 访客管理业务逻辑、状态流转、二维码系统
5. **auth-domain.mdc** - 认证授权领域、用户管理、多租户架构
6. **organization-domain.mdc** - 组织架构管理、员工部门站点关系

#### 开发场景规则层 (3个文件)
7. **api-development.mdc** - API开发最佳实践、路由设计、错误处理
8. **testing-standards.mdc** - 测试规范、测试策略、覆盖率要求
9. **performance-optimization.mdc** - 性能优化指导、缓存策略、数据库优化

### 规则内容架构标准
每个规则文件包含：
- **规则概述**: 职责范围和适用场景
- **架构指导**: 具体的技术实施约束  
- **代码示例**: 最佳实践代码片段
- **文件引用**: 相关项目文件的mdc引用
- **检查清单**: 开发和代码审查要点

### 实施策略
- **规则优先级**: 核心规则 > 业务领域规则 > 开发场景规则
- **冲突解决**: 更具体的规则覆盖通用规则
- **引用完整性**: 确保所有mdc文件引用的有效性
- **版本兼容**: 与现有规则文件保持兼容

## Implementation Checklist:
1. 创建核心规则层第一个文件 - visitor-management-core.mdc
2. 创建核心规则层第二个文件 - clean-architecture.mdc  
3. 创建核心规则层第三个文件 - security-standards.mdc
4. 创建业务领域规则层第一个文件 - visitor-domain.mdc
5. 创建业务领域规则层第二个文件 - auth-domain.mdc
6. 创建业务领域规则层第三个文件 - organization-domain.mdc
7. 创建开发场景规则层第一个文件 - api-development.mdc
8. 创建开发场景规则层第二个文件 - testing-standards.mdc
9. 创建开发场景规则层第三个文件 - performance-optimization.mdc
10. 验证所有规则文件的mdc引用有效性
11. 更新任务文件记录实施计划完成情况 

# Current Execution Step (由 EXECUTE 模式在开始步骤时更新)
> Currently executing: "步骤5 - 创建业务领域规则层第二个文件 - auth-domain.mdc"

# Task Progress (由 EXECUTE 模式在每个步骤完成后追加)
*   2024-12-28 [完成]
    *   Step: 1. 创建核心规则层第一个文件 - visitor-management-core.mdc
    *   Modifications: 创建新文件 .cursor/rules/visitor-management-core.mdc，包含项目核心架构指导、技术栈标准、开发环境配置等内容
    *   Change Summary: 建立访客管理系统的核心架构规则，涵盖技术栈要求、项目结构标准、开发约束和性能基准
    *   Reason: 执行计划步骤1
    *   Blockers: None
    *   User Confirmation Status: Success

*   2024-12-28 [完成]
    *   Step: 2. 创建核心规则层第二个文件 - clean-architecture.mdc
    *   Modifications: 创建新文件 .cursor/rules/clean-architecture.mdc，包含Clean Architecture实施规范、分层职责定义、依赖规则和DTO设计原则
    *   Change Summary: 建立Clean Architecture分层架构实施规范，确保代码职责分离和依赖方向正确
    *   Reason: 执行计划步骤2
    *   Blockers: None
    *   User Confirmation Status: Success

*   2024-12-28 [完成]
    *   Step: 3. 创建核心规则层第三个文件 - security-standards.mdc
    *   Modifications: 创建新文件 .cursor/rules/security-standards.mdc，包含JWT认证、权限控制、数据验证、密码安全和安全配置标准
    *   Change Summary: 建立全面的安全开发标准，涵盖认证授权、多租户安全隔离、输入验证和安全配置
    *   Reason: 执行计划步骤3
    *   Blockers: None
    *   User Confirmation Status: Success

*   2024-12-28 [完成]
    *   Step: 4. 创建业务领域规则层第一个文件 - visitor-domain.mdc
    *   Modifications: 创建新文件 .cursor/rules/visitor-domain.mdc，包含访客状态管理、二维码系统、数据验证规则、查询构建器和领域事件定义
    *   Change Summary: 建立访客管理业务领域的核心逻辑规范，确保业务规则一致性和状态流转正确性
    *   Reason: 执行计划步骤4
    *   Blockers: None
    *   User Confirmation Status: Success 