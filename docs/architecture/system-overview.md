# 访客管理系统架构概览

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-18
- **最后更新**: 2025-06-18
- **维护者**: 系统架构师AI
- **适用角色**: 系统架构师、技术负责人、开发团队
- **依赖文档**: PRD.md, functional-requirements.md

## 🎯 文档目标
提供访客管理系统的整体架构设计概述，包括技术选型、架构模式、核心组件和部署方案。

## 🏗️ 系统架构总览

### 架构设计原则
- **领域驱动设计(DDD)**: 基于业务领域建模，清晰的业务边界
- **清洁架构(Clean Architecture)**: 依赖倒置，核心业务逻辑独立
- **微服务架构**: 模块化设计，独立部署和扩展
- **多租户架构**: 数据隔离，共享资源，成本优化
- **事件驱动**: 异步处理，解耦组件，提升性能

### 技术栈选型

#### 前端技术栈 - React生态统一
```
管理端应用    : React 18 + TypeScript + Ant Design Pro
访客端应用    : React 18 + TypeScript + Ant Design Mobile  
门岗端应用    : React 18 + TypeScript + PWA
前台端应用    : React 18 + TypeScript + Ant Design
设备端应用    : React 18 + TypeScript + Embedded WebView

移动端备用方案:
- React Native APP (iOS/Android)
- 微信小程序 (访客端/员工端)
```

#### 后端技术栈 - 已成熟稳定
```
API框架      : FastAPI 0.100+ (Python 3.9+)
数据库       : PostgreSQL 14+ (主库) + Redis 6+ (缓存)
消息队列     : Celery + Redis (异步任务)
认证授权     : JWT + OAuth2 + RBAC
文件存储     : MinIO/阿里云OSS
监控日志     : Prometheus + Grafana + ELK Stack
```

#### 基础设施
```
容器化       : Docker + Docker Compose / Kubernetes
CI/CD        : GitHub Actions / GitLab CI
API网关      : Nginx + Kong/Traefik
负载均衡     : HAProxy / ALB
SSL证书      : Let's Encrypt / 商业证书
```

## 🎨 系统架构图

### 整体架构图
```mermaid
graph TB
    subgraph "客户端层 (React生态)"
        WebAdmin[管理端<br/>React + Ant Design Pro]
        WebVisitor[访客端<br/>React + Ant Design Mobile]
        PWAGate[门岗端<br/>React PWA]
        PWAReception[前台端<br/>React PWA]
        RNApp[移动备用<br/>React Native]
        MiniProgram[小程序备用<br/>微信小程序]
    end
    
    subgraph "API网关层"
        Gateway[Kong API Gateway<br/>路由/限流/认证/监控]
    end
    
    subgraph "应用服务层 (FastAPI)"
        AuthService[认证服务<br/>JWT/OAuth2]
        VisitorService[访客管理服务<br/>核心业务逻辑]
        ConfigService[配置引擎服务<br/>表单/工作流/规则]
        NotificationService[通知服务<br/>消息推送]
        FileService[文件服务<br/>上传/存储/处理]
        DeviceService[设备管理服务<br/>硬件集成]
    end
    
    subgraph "数据层"
        PostgreSQL[(PostgreSQL<br/>主数据库)]
        Redis[(Redis<br/>缓存/会话)]
        MinIO[(MinIO<br/>文件存储)]
    end
    
    subgraph "基础设施层"
        Celery[Celery<br/>异步任务队列]
        Monitoring[监控系统<br/>Prometheus/Grafana]
        Logging[日志系统<br/>ELK Stack]
    end
    
    subgraph "外部集成"
        WeCom[企业微信API]
        DingTalk[钉钉API]
        SMS[短信服务]
        Email[邮件服务]
        Hardware[硬件设备<br/>门禁/摄像头/打印机]
    end
    
    WebAdmin --> Gateway
    WebVisitor --> Gateway
    PWAGate --> Gateway
    PWAReception --> Gateway
    RNApp --> Gateway
    MiniProgram --> Gateway
    
    Gateway --> AuthService
    Gateway --> VisitorService
    Gateway --> ConfigService
    Gateway --> NotificationService
    Gateway --> FileService
    Gateway --> DeviceService
    
    AuthService --> PostgreSQL
    VisitorService --> PostgreSQL
    ConfigService --> PostgreSQL
    
    AuthService --> Redis
    VisitorService --> Redis
    
    FileService --> MinIO
    NotificationService --> Celery
    
    NotificationService --> WeCom
    NotificationService --> DingTalk
    NotificationService --> SMS
    NotificationService --> Email
    
    DeviceService --> Hardware
    
    VisitorService --> Monitoring
    ConfigService --> Logging
```

### 数据流架构图
```mermaid
graph LR
    subgraph "数据生产"
        A[用户操作] --> B[API请求]
        C[设备上报] --> D[设备API]
        E[定时任务] --> F[系统事件]
    end
    
    subgraph "数据处理"
        B --> G[业务逻辑层]
        D --> G
        F --> G
        G --> H[数据验证]
        H --> I[业务规则引擎]
        I --> J[权限检查]
    end
    
    subgraph "数据存储"
        J --> K[(主数据库<br/>PostgreSQL)]
        J --> L[(缓存<br/>Redis)]
        J --> M[(文件存储<br/>MinIO)]
    end
    
    subgraph "数据消费"
        K --> N[实时查询]
        L --> O[快速响应]
        K --> P[数据分析]
        K --> Q[报表生成]
    end
    
    subgraph "数据同步"
        K --> R[事件发布]
        R --> S[消息队列]
        S --> T[异步处理]
        T --> U[外部通知]
        T --> V[设备同步]
    end
```

## 🏛️ 核心架构模式

### 1. 清洁架构 (Clean Architecture)
```
┌─────────────────────────────────────────┐
│              Frameworks & Drivers        │  ← Web, Database, External APIs
├─────────────────────────────────────────┤
│           Interface Adapters            │  ← Controllers, Gateways, Presenters  
├─────────────────────────────────────────┤
│              Application                │  ← Use Cases, Services
├─────────────────────────────────────────┤
│               Enterprise                │  ← Entities, Domain Logic
└─────────────────────────────────────────┘
```

**层级职责**:
- **Enterprise Business Rules**: 核心实体和业务规则 (entities/)
- **Application Business Rules**: 应用用例和服务 (application/)
- **Interface Adapters**: 接口适配器和数据转换 (api/, repositories/)
- **Frameworks & Drivers**: 外部框架和驱动 (infrastructure/)

### 2. 领域驱动设计 (DDD)
```
访客管理域 (Visitor Domain)
├── 访客实体 (Visitor Entity)
├── 访问申请 (VisitApplication)
├── 审批流程 (ApprovalProcess)
└── 访客状态 (VisitorStatus)

组织管理域 (Organization Domain)  
├── 租户实体 (Tenant Entity)
├── 部门实体 (Department Entity)
├── 员工实体 (Employee Entity)
└── 权限管理 (Permission Management)

配置引擎域 (Configuration Domain)
├── 表单配置 (Form Configuration)
├── 工作流配置 (Workflow Configuration)
├── 业务规则配置 (Business Rules)
└── 空间配置 (Spatial Configuration)
```

### 3. 多租户架构
```mermaid
graph TB
    subgraph "SaaS平台层"
        Platform[SaaS管理平台]
    end
    
    subgraph "租户A (企业A)"
        TenantA_DB[(租户A数据)]
        TenantA_Config[租户A配置]
        TenantA_Users[租户A用户]
    end
    
    subgraph "租户B (企业B)"
        TenantB_DB[(租户B数据)]
        TenantB_Config[租户B配置]
        TenantB_Users[租户B用户]
    end
    
    subgraph "共享服务层"
        SharedAPI[共享API服务]
        SharedCache[共享缓存]
        SharedFiles[共享文件存储]
    end
    
    Platform --> SharedAPI
    TenantA_Users --> SharedAPI
    TenantB_Users --> SharedAPI
    
    SharedAPI --> TenantA_DB
    SharedAPI --> TenantB_DB
    SharedAPI --> SharedCache
    SharedAPI --> SharedFiles
```

**租户隔离策略**:
- **数据隔离**: 每个租户独立的数据库schema
- **配置隔离**: 租户级别的独立配置
- **用户隔离**: 基于tenant_id的用户权限控制
- **资源隔离**: 计算资源按租户分配和监控

## 📱 多端应用架构

### 前端应用矩阵
| 应用端 | 技术栈 | 主要用户 | 核心功能 | 部署方式 |
|--------|--------|----------|----------|----------|
| 管理端 | React + Ant Design Pro | 管理员、HR | 系统配置、数据分析 | Web部署 |
| 访客端 | React + Ant Design Mobile | 访客 | 申请访问、查看状态 | Web + PWA |
| 门岗端 | React + PWA | 门岗人员 | 身份验证、放行控制 | PWA + 专用设备 |
| 前台端 | React + Ant Design | 前台人员 | 访客签到、接待服务 | Web + PWA |
| 设备端 | React + WebView | 硬件设备 | 自助服务、设备控制 | 嵌入式WebView |

### 移动端备用方案
| 方案类型 | 技术实现 | 适用场景 | 功能范围 |
|----------|----------|----------|----------|
| React Native APP | RN + TypeScript | 设备故障备用 | 完整验证功能 |
| 微信小程序 | 微信小程序框架 | 预算限制场景 | 基础验证功能 |
| 移动Web | React + PWA | 临时部署 | 核心验证功能 |

### 响应式设计适配
```
桌面端 (≥1200px)  : 完整功能界面，多列布局
平板端 (768-1199px): 适中功能界面，双列布局  
手机端 (≤767px)   : 核心功能界面，单列布局
```

## 🔧 核心技术组件

### 1. 配置引擎架构
```mermaid
graph TB
    subgraph "配置引擎核心"
        FormEngine[表单引擎<br/>动态表单生成]
        WorkflowEngine[工作流引擎<br/>审批流程管理]
        RuleEngine[规则引擎<br/>业务规则执行]
        SpatialEngine[空间引擎<br/>区域权限管理]
    end
    
    subgraph "配置数据"
        FormConfig[(表单配置)]
        WorkflowConfig[(工作流配置)]
        RuleConfig[(规则配置)]
        SpatialConfig[(空间配置)]
    end
    
    subgraph "业务应用"
        VisitorApp[访客申请]
        ApprovalApp[审批流程]
        AccessControl[访问控制]
        ReportApp[数据报表]
    end
    
    FormEngine --> FormConfig
    WorkflowEngine --> WorkflowConfig
    RuleEngine --> RuleConfig
    SpatialEngine --> SpatialConfig
    
    VisitorApp --> FormEngine
    VisitorApp --> WorkflowEngine
    ApprovalApp --> WorkflowEngine
    ApprovalApp --> RuleEngine
    AccessControl --> SpatialEngine
    AccessControl --> RuleEngine
    ReportApp --> FormEngine
```

### 2. 实时通信架构
```mermaid
graph TB
    subgraph "客户端"
        WebSocket1[管理端WebSocket]
        WebSocket2[门岗端WebSocket]
        WebSocket3[前台端WebSocket]
        WebSocket4[移动端WebSocket]
    end
    
    subgraph "消息网关"
        WSGateway[WebSocket网关<br/>连接管理/消息路由]
    end
    
    subgraph "消息处理"
        MessageBroker[消息代理<br/>Redis Pub/Sub]
        EventProcessor[事件处理器<br/>业务事件处理]
    end
    
    subgraph "业务服务"
        VisitorService2[访客服务]
        NotificationService2[通知服务]
        DeviceService2[设备服务]
    end
    
    WebSocket1 --> WSGateway
    WebSocket2 --> WSGateway
    WebSocket3 --> WSGateway
    WebSocket4 --> WSGateway
    
    WSGateway --> MessageBroker
    MessageBroker --> EventProcessor
    
    EventProcessor --> VisitorService2
    EventProcessor --> NotificationService2
    EventProcessor --> DeviceService2
    
    VisitorService2 --> MessageBroker
    NotificationService2 --> MessageBroker
    DeviceService2 --> MessageBroker
```

### 3. 缓存架构设计
```mermaid
graph TB
    subgraph "缓存层级"
        L1[L1: 应用内存缓存<br/>热点数据/配置信息]
        L2[L2: Redis缓存<br/>会话/临时数据]
        L3[L3: 数据库缓存<br/>查询结果缓存]
    end
    
    subgraph "缓存策略"
        ReadThrough[Read Through<br/>读取穿透]
        WriteBack[Write Back<br/>写回策略]
        CacheAside[Cache Aside<br/>旁路缓存]
    end
    
    subgraph "缓存数据类型"
        UserSessions[用户会话<br/>30分钟TTL]
        ConfigData[配置数据<br/>1小时TTL]
        VisitorData[访客数据<br/>24小时TTL]
        StatData[统计数据<br/>15分钟TTL]
    end
    
    L1 --> ReadThrough
    L2 --> CacheAside
    L3 --> WriteBack
    
    UserSessions --> L2
    ConfigData --> L1
    VisitorData --> L2
    StatData --> L2
```

## 🚀 部署架构

### 开发环境部署
```yaml
开发环境 (Docker Compose):
  - 后端API: 1个容器 (FastAPI)
  - 数据库: 1个容器 (PostgreSQL)  
  - 缓存: 1个容器 (Redis)
  - 前端: 开发服务器 (npm run dev)
  - 文件存储: 本地存储

资源要求:
  - CPU: 4核心
  - 内存: 8GB
  - 存储: 50GB SSD
```

### 测试环境部署  
```yaml
测试环境 (Docker Swarm):
  - 后端API: 2个副本 + 负载均衡
  - 数据库: 主从架构
  - 缓存: Redis Cluster (3节点)
  - 前端: Nginx静态文件服务
  - 文件存储: MinIO集群

资源要求:
  - CPU: 8核心
  - 内存: 16GB  
  - 存储: 200GB SSD
```

### 生产环境部署
```yaml
生产环境 (Kubernetes):
  - 后端API: 3-5个Pod + HPA自动扩缩容
  - 数据库: 高可用PostgreSQL集群 
  - 缓存: Redis Cluster (6节点)
  - 前端: CDN + Nginx集群
  - 文件存储: 高可用MinIO集群
  - 监控: Prometheus + Grafana + ELK

资源要求:
  - CPU: 16-32核心
  - 内存: 64-128GB
  - 存储: 1TB+ SSD (数据) + NVMe (缓存)
```

### 灾备架构
```mermaid
graph TB
    subgraph "主数据中心"
        Primary_LB[主负载均衡]
        Primary_App[主应用集群]
        Primary_DB[主数据库]
        Primary_Cache[主缓存]
    end
    
    subgraph "备数据中心"
        Backup_LB[备负载均衡]
        Backup_App[备应用集群]
        Backup_DB[备数据库]
        Backup_Cache[备缓存]
    end
    
    subgraph "数据同步"
        DBReplication[数据库主从复制]
        FileSync[文件存储同步]
        ConfigSync[配置同步]
    end
    
    Primary_DB --> DBReplication
    DBReplication --> Backup_DB
    
    Primary_App --> FileSync
    FileSync --> Backup_App
    
    Primary_LB --> ConfigSync
    ConfigSync --> Backup_LB
```

## 📊 性能设计目标

### 响应时间目标
- **API响应**: 平均<200ms, 99%<500ms
- **页面加载**: 首屏<3秒, 交互<1秒
- **数据查询**: 简单查询<100ms, 复杂查询<1秒
- **文件上传**: 10MB文件<30秒

### 并发性能目标
- **同时在线用户**: >1000人
- **API TPS**: >500 TPS
- **数据库连接**: >100并发连接
- **WebSocket连接**: >2000并发连接

### 可用性目标
- **系统可用性**: 99.5% (年停机<43.8小时)
- **核心功能可用性**: 99.9% (年停机<8.76小时)
- **故障恢复时间**: <30分钟
- **数据备份**: RTO<4小时, RPO<1小时

## 🔒 安全架构设计

### 安全防护层级
```
┌─────────────────────────────────────────┐
│           网络安全层                      │  ← WAF, DDoS防护, 网络隔离
├─────────────────────────────────────────┤
│           接入安全层                      │  ← API网关, 限流, 认证
├─────────────────────────────────────────┤
│           应用安全层                      │  ← 输入验证, 权限控制, 加密
├─────────────────────────────────────────┤
│           数据安全层                      │  ← 数据加密, 脱敏, 审计
└─────────────────────────────────────────┘
```

### 认证授权架构
```mermaid
graph TB
    subgraph "认证层"
        OAuth2[OAuth2认证]
        JWT[JWT Token]
        MFA[多因子认证]
        SSO[单点登录]
    end
    
    subgraph "授权层"
        RBAC[基于角色的访问控制]
        ABAC[基于属性的访问控制]
        ResourceAuth[资源级权限控制]
    end
    
    subgraph "安全策略"
        PasswordPolicy[密码策略]
        SessionPolicy[会话策略]
        AccessPolicy[访问策略]
        AuditPolicy[审计策略]
    end
    
    OAuth2 --> RBAC
    JWT --> RBAC
    MFA --> ABAC
    SSO --> ResourceAuth
    
    RBAC --> PasswordPolicy
    ABAC --> SessionPolicy
    ResourceAuth --> AccessPolicy
    AccessPolicy --> AuditPolicy
```

---
**文档版本**: v2.0.0 | **最后更新**: 2025-06-18 