# 访客管理系统 - 数据库架构文档

## 📋 文档信息
- **文档名称**: 数据库架构设计说明
- **创建日期**: 2024-12-20
- **版本**: v3.1.0
- **数据库**: PostgreSQL 13+
- **表总数**: 35个核心表
- **扩展功能**: 多租户架构、门岗前台支持

---

## 🎯 架构概览

### 核心设计原则
- **多租户架构**: 所有业务表支持租户隔离 (`tenant_id`)
- **审计追踪**: 完整的创建、更新、删除记录 (`AuditableModel`)
- **软删除**: 支持逻辑删除机制 (`is_deleted`)
- **时间戳**: 自动管理创建和更新时间
- **约束验证**: 数据库层面的业务规则约束

### 数据库连接配置
```
Host: localhost
Port: 5433
Database: visitor_management
User: postgres
Schema: public
```

---

## 📊 核心业务表

### 1. 组织架构表

#### 🏭 sites (站点表)
管理多个物理站点/园区信息

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AUTO | 站点ID |
| name | VARCHAR(100) | NOT NULL | 站点名称 |
| code | VARCHAR(50) | NOT NULL, UNIQUE | 站点编码 |
| description | TEXT | | 站点描述 |
| address | VARCHAR(200) | | 详细地址 |
| city | VARCHAR(50) | | 城市 |
| province | VARCHAR(50) | | 省份 |
| postal_code | VARCHAR(10) | | 邮政编码 |
| country | VARCHAR(50) | DEFAULT '中国' | 国家 |
| phone | VARCHAR(20) | | 联系电话 |
| email | VARCHAR(100) | EMAIL格式 | 联系邮箱 |
| website | VARCHAR(200) | | 官网地址 |
| latitude | FLOAT | | 纬度 |
| longitude | FLOAT | | 经度 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态 |
| working_hours_start | VARCHAR(5) | DEFAULT '09:00' | 工作开始时间 |
| working_hours_end | VARCHAR(5) | DEFAULT '18:00' | 工作结束时间 |
| timezone | VARCHAR(50) | DEFAULT 'Asia/Shanghai' | 时区 |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

**约束**:
- `chk_sites_status`: status IN ('active', 'inactive', 'maintenance')
- `chk_sites_email`: 邮箱格式验证

#### 🏢 departments (部门表)
组织部门层级结构

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AUTO | 部门ID |
| name | VARCHAR(100) | NOT NULL | 部门名称 |
| code | VARCHAR(50) | | 部门编码 |
| description | TEXT | | 部门描述 |
| parent_id | INTEGER | FK(departments.id) | 上级部门 |
| sort_order | INTEGER | DEFAULT 0 | 排序 |
| phone | VARCHAR(20) | | 部门电话 |
| email | VARCHAR(100) | EMAIL格式 | 部门邮箱 |
| address | VARCHAR(200) | | 部门地址 |
| manager_id | INTEGER | FK(employees.id) | 部门经理 |
| site_id | INTEGER | FK(sites.id) | 所属站点 |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

**约束**:
- `chk_departments_email`: 邮箱格式验证
- `chk_departments_no_self_parent`: parent_id != id

#### 👥 employees (员工表)
员工基本信息和组织关系

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AUTO | 员工ID |
| name | VARCHAR(100) | NOT NULL | 员工姓名 |
| employee_id | VARCHAR(50) | NOT NULL, UNIQUE | 员工工号 |
| email | VARCHAR(100) | EMAIL格式 | 邮箱地址 |
| phone_number | VARCHAR(20) | | 手机号码 |
| gender | VARCHAR(10) | | 性别 |
| department_id | INTEGER | FK(departments.id) | 所属部门 |
| designation_id | INTEGER | FK(designations.id) | 职位级别 |
| position | VARCHAR(100) | | 职位名称 |
| manager_id | INTEGER | FK(employees.id) | 直属上级 |
| about | TEXT | | 个人简介 |
| avatar | VARCHAR(200) | | 头像URL |
| hire_date | TIMESTAMP WITH TIME ZONE | | 入职日期 |
| birth_date | TIMESTAMP WITH TIME ZONE | | 出生日期 |
| address | VARCHAR(200) | | 家庭地址 |
| emergency_contact | VARCHAR(100) | | 紧急联系人 |
| emergency_phone | VARCHAR(20) | | 紧急联系电话 |
| salary | FLOAT | | 薪资 |
| status | VARCHAR(20) | DEFAULT 'active' | 员工状态 |
| site_id | INTEGER | FK(sites.id) | 工作站点 |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

**约束**:
- `chk_employees_status`: status IN ('active', 'inactive', 'terminated', 'on_leave')
- `chk_employees_email`: 邮箱格式验证
- `chk_employees_gender`: gender IN ('male', 'female', 'other')
- `chk_employees_no_self_manager`: manager_id != id
- `chk_employees_salary`: salary >= 0

### 2. 访客管理表

#### 🧑‍💼 visitors (访客表)
访客核心信息和访问记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AUTO | 访客ID |
| pass_code | VARCHAR(50) | | 通行码 |
| name | VARCHAR(100) | NOT NULL | 访客姓名 |
| email | VARCHAR(100) | EMAIL格式 | 邮箱地址 |
| phone_number | VARCHAR(20) | | 手机号码 |
| identification_no | VARCHAR(50) | | 身份证号 |
| license_plate_number | VARCHAR(20) | | 车牌号 |
| address | VARCHAR(200) | | 地址 |
| gender | VARCHAR(10) | | 性别 |
| company_name | VARCHAR(100) | | 公司名称 |
| purpose | VARCHAR(50) | | 访问目的 |
| comment | TEXT | | 备注 |
| employee_id | INTEGER | FK(employees.id) | 被访问员工 |
| checkin_date | TIMESTAMP WITH TIME ZONE | | 签到时间 |
| checkout_date | TIMESTAMP WITH TIME ZONE | | 签出时间 |
| expected_date | TIMESTAMP WITH TIME ZONE | | 预期访问日期 |
| expected_time | TIME | | 预期访问时间 |
| avatar | VARCHAR(200) | | 头像URL |
| status | visitor_status_enum | DEFAULT 'pending' | 访客状态 |
| approved | BOOLEAN | | 是否已审批 |
| approval_outcome | VARCHAR(20) | | 审批结果 |
| approval_comment | TEXT | | 审批意见 |
| site_id | INTEGER | FK(sites.id) | 访问站点 |
| privacy_policy | BOOLEAN | | 隐私政策同意 |
| promise | BOOLEAN | | 信息真实承诺 |
| **current_status** | VARCHAR(50) | | **当前状态** |
| **entry_time** | TIMESTAMP WITH TIME ZONE | | **实际入园时间** |
| **exit_time** | TIMESTAMP WITH TIME ZONE | | **实际离园时间** |
| **current_location** | VARCHAR(200) | | **当前位置** |
| **reception_desk_id** | VARCHAR(50) | | **前台设备ID** |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

**新增门岗前台扩展字段** (已于2024-12-20迁移添加):
- `current_status`: 门岗状态跟踪 (pending, approved, checked_in, in_park, exited)
- `entry_time`, `exit_time`: 实际进出园时间
- `current_location`: 园区内当前位置
- `reception_desk_id`: 前台签到设备标识

**约束**:
- `chk_visitors_checkout_after_checkin`: checkout_date > checkin_date
- `chk_visitors_email`: 邮箱格式验证
- `chk_visitors_gender`: gender IN ('male', 'female', 'other')
- `chk_visitors_park_time_order`: exit_time > entry_time

---

## 🔧 智能设备管理表

### 📱 devices (设备表)
门岗、前台、移动设备统一管理

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AUTO | 设备ID |
| device_id | VARCHAR(50) | NOT NULL, UNIQUE | 设备标识 |
| device_name | VARCHAR(100) | NOT NULL | 设备名称 |
| device_type | device_type_enum | NOT NULL | 设备类型 |
| device_model | VARCHAR(100) | | 设备型号 |
| serial_number | VARCHAR(100) | | 序列号 |
| location | VARCHAR(200) | | 设备位置 |
| site_id | INTEGER | FK(sites.id) | 所属站点 |
| zone | VARCHAR(100) | | 区域 |
| floor | VARCHAR(50) | | 楼层 |
| ip_address | VARCHAR(45) | | IP地址 |
| mac_address | VARCHAR(17) | | MAC地址 |
| port | INTEGER | | 端口号 |
| status | device_status_enum | DEFAULT 'offline' | 设备状态 |
| last_heartbeat | TIMESTAMP WITH TIME ZONE | | 最后心跳 |
| capabilities | JSONB | | 设备能力列表 |
| configuration | JSONB | | 设备配置参数 |
| firmware_version | VARCHAR(50) | | 固件版本 |
| software_version | VARCHAR(50) | | 软件版本 |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

**设备类型枚举** (device_type_enum):
- `gate_device`: 门岗设备
- `reception_desk`: 前台设备  
- `mobile_terminal`: 移动终端
- `camera`: 摄像头
- `card_reader`: 读卡器

**设备状态枚举** (device_status_enum):
- `online`: 在线
- `offline`: 离线
- `maintenance`: 维护中
- `error`: 故障

---

## ⚙️ 配置引擎表

### 📝 form_configurations (表单配置表)
动态表单定义和管理

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 配置ID |
| form_type | VARCHAR(50) | NOT NULL | 表单类型 |
| form_name | VARCHAR(100) | NOT NULL | 表单名称 |
| form_version | INTEGER | DEFAULT 1 | 表单版本 |
| is_active | BOOLEAN | DEFAULT true | 是否激活 |
| is_default | BOOLEAN | DEFAULT false | 是否默认 |
| description | TEXT | | 表单描述 |
| form_schema | JSONB | | 完整表单结构 |
| ui_schema | JSONB | | UI渲染配置 |
| validation_schema | JSONB | | 验证规则 |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

**表单类型约束**:
- `chk_form_type`: form_type IN ('visitor_registration', 'approval_form', 'employee_form', 'site_form', 'department_form')

### 🔄 workflow_configurations (工作流配置表)
业务流程自动化配置

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 工作流ID |
| workflow_name | VARCHAR(100) | NOT NULL | 工作流名称 |
| workflow_type | VARCHAR(50) | NOT NULL | 工作流类型 |
| workflow_version | INTEGER | DEFAULT 1 | 版本号 |
| trigger_conditions | JSONB | NOT NULL | 触发条件 |
| workflow_steps | JSONB | NOT NULL | 工作流步骤定义 |
| failure_handling | JSONB | | 失败处理策略 |
| timeout_settings | JSONB | | 超时设置 |
| is_active | BOOLEAN | DEFAULT true | 是否激活 |
| priority_level | INTEGER | DEFAULT 1 | 优先级(1-10) |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

**工作流类型约束**:
- `chk_workflow_type`: workflow_type IN ('visitor_approval', 'device_control', 'notification', 'data_sync', 'security_check')

---

## 🎭 场景管理表

### 📋 scenario_templates (场景模板表)
可复用的业务场景模板

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 模板ID |
| template_name | VARCHAR(100) | NOT NULL | 模板名称 |
| template_code | VARCHAR(50) | NOT NULL | 模板代码 |
| template_version | INTEGER | DEFAULT 1 | 模板版本 |
| template_category | VARCHAR(50) | NOT NULL | 模板分类 |
| template_description | TEXT | | 模板描述 |
| is_builtin | BOOLEAN | DEFAULT false | 是否内置模板 |
| is_template_active | BOOLEAN | DEFAULT true | 是否启用 |
| scenario_features | JSONB | NOT NULL | 场景特征配置 |
| default_configurations | JSONB | NOT NULL | 默认配置集合 |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

### 🎯 scenario_instances (场景实例表)
基于模板创建的具体业务场景

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 实例ID |
| instance_name | VARCHAR(100) | NOT NULL | 实例名称 |
| instance_code | VARCHAR(50) | NOT NULL | 实例代码 |
| template_id | UUID | FK(scenario_templates.id) | 模板ID |
| instance_status | VARCHAR(50) | DEFAULT 'draft' | 实例状态 |
| priority_level | INTEGER | DEFAULT 1 | 优先级(1-10) |
| custom_configurations | JSONB | | 自定义配置 |
| routing_rules | JSONB | NOT NULL | 路由规则 |
| trigger_conditions | JSONB | NOT NULL | 触发条件 |
| auto_routing_enabled | BOOLEAN | DEFAULT true | 自动路由 |
| execution_count | INTEGER | DEFAULT 0 | 执行次数 |
| success_count | INTEGER | DEFAULT 0 | 成功次数 |
| tenant_id | VARCHAR(50) | DEFAULT 'default' | 租户ID |

---

## 🔗 数据关系图

```
Sites (站点)
├── Departments (部门)
│   ├── Employees (员工)
│   │   ├── Visitors (访客) - 被访问员工
│   │   └── Manager (上级员工)
│   └── Department Manager
├── Devices (设备)
├── Spatial Entities (空间实体)
└── Meeting Rooms (会议室)

Visitors (访客)
├── Visitor Histories (访客历史)
├── Approval Histories (审批历史)
├── Visitor Entries (入园记录)
├── Reception Checkins (前台签到)
├── Host Notifications (主机通知)
└── Visitor Verifications (验证记录)

Configurations (配置引擎)
├── Form Configurations (表单配置)
├── Workflow Configurations (工作流配置)
├── Spatial Configurations (空间配置)
└── Business Rules (业务规则)

Scenarios (场景管理)
├── Scenario Templates (场景模板)
├── Scenario Instances (场景实例)
├── Scenario Executions (场景执行)
└── Scenario Analytics (场景分析)
```

---

## 📈 数据统计

### 当前数据状态
- **站点**: 2个 (总部大厦, 研发中心)
- **部门**: 5个 (技术部, 市场部, 人事部, 研发一部, 研发二部)
- **员工**: 5个 (张三-技术总监, 李四-市场总监, 王五-人事总监, 赵六-前端工程师, 孙七-后端工程师)
- **访客**: 动态数据 (通过API创建)

### 扩展字段状态
✅ **已完成**: visitors表门岗前台扩展字段 (2024-12-20迁移完成)
- current_status, entry_time, exit_time, current_location, reception_desk_id

---

## 🚀 数据库迁移记录

### 最新迁移
- **20250620_000000**: 添加访客表扩展字段支持门岗前台功能
  - 添加5个门岗前台扩展字段
  - 添加时间顺序约束检查
  - 状态：✅ 已成功执行

### 数据修复记录
- **员工表字段补充**: 手动添加employee_id, position, manager_id等缺失字段
- **租户ID统一**: 将测试数据从'default_tenant'统一为'default'

---

## 🔧 开发者注意事项

### 必须字段
1. **所有业务表**: `tenant_id` (多租户隔离)
2. **审计表**: `created_by`, `updated_by`, `is_deleted`
3. **时间字段**: `created_at`, `updated_at` (自动管理)

### 约束规则
1. **邮箱验证**: 所有email字段都有格式约束
2. **状态约束**: 枚举类型严格验证
3. **业务约束**: 防止自引用、时间顺序等

### 性能优化
1. **索引策略**: 主键、外键、tenant_id都有索引
2. **分页查询**: 使用OFFSET/LIMIT进行分页
3. **软删除**: 使用is_deleted而非物理删除

### 多租户最佳实践
1. **查询过滤**: 所有业务查询必须包含tenant_id条件
2. **数据隔离**: 不同租户间数据完全隔离
3. **默认值**: 新记录使用配置的默认租户ID 