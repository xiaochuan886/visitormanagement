# 访客管理系统后端 API 完整参考手册

## 📋 文档信息
- **版本**: v2.0.0
- **API版本**: v1
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **Base URL**: `http://localhost:8000/api/v1`
- **适用角色**: 前端开发者、API集成开发者、测试工程师

## 🎯 API概述

访客管理系统提供 **28个API端点**，覆盖访客管理、员工管理、配置引擎等完整业务功能。所有API遵循 **RESTful** 设计原则，支持 **JSON** 数据格式，提供完整的 **OpenAPI 3.0** 规范文档。

### API特性
- ✅ **RESTful设计**: 标准的HTTP方法和状态码
- ✅ **多租户支持**: 所有API支持租户隔离
- ✅ **JWT认证**: 基于Token的无状态认证
- ✅ **数据验证**: Pydantic模型严格验证
- ✅ **错误处理**: 统一的错误响应格式
- ✅ **自动文档**: Swagger UI 和 ReDoc 支持

### 快速导航
- [认证API](#🔐-认证api) - 用户登录、Token管理
- [访客管理API](#👥-访客管理api) - 访客CRUD、审批、签到
- [员工管理API](#🧑‍💼-员工管理api) - 员工信息管理
- [部门管理API](#🏢-部门管理api) - 组织结构管理
- [站点管理API](#🏬-站点管理api) - 站点信息管理
- [配置引擎API](#⚙️-配置引擎api) - 动态配置管理

## 🔧 通用规范

### 请求格式
```http
Content-Type: application/json
Authorization: Bearer <jwt_token>
X-Tenant-ID: <tenant_id>  # 可选，默认从Token解析
```

### 响应格式
#### 成功响应
```json
{
  "id": "string",
  "name": "string",
  "created_at": "2025-06-17T07:00:00Z",
  "updated_at": "2025-06-17T07:00:00Z"
}
```

#### 错误响应
```json
{
  "detail": "错误描述信息",
  "error_code": "BUSINESS_ERROR_CODE",
  "timestamp": "2025-06-17T07:00:00Z"
}
```

### HTTP状态码
| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| 200 | OK | 成功获取资源 |
| 201 | Created | 成功创建资源 |
| 204 | No Content | 成功删除资源 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 500 | Internal Server Error | 服务器内部错误 |

### 分页参数
```
?skip=0&limit=20&sort_by=created_at&sort_order=desc
```

## 🔐 认证API

### 1. 用户登录
**获取JWT访问令牌**

```http
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "username": "admin",
  "password": "secure_password",
  "tenant_id": "default_tenant"
}
```

**响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_info": {
    "username": "admin",
    "tenant_id": "default_tenant",
    "permissions": ["read", "write", "admin"]
  }
}
```

### 2. Token刷新
**刷新访问令牌**

```http
POST /api/v1/auth/refresh
```

**请求体**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 👥 访客管理API

### 3. 创建访客
**注册新访客**

```http
POST /api/v1/visitors/
```

**请求体**:
```json
{
  "name": "张三",
  "phone_number": "13800138000",
  "email": "zhangsan@example.com",
  "identification_no": "110101199001011234",
  "company_name": "ABC公司",
  "purpose": "business_meeting",
  "expected_date": "2025-06-17T09:00:00Z",
  "employee_id": 1,
  "comment": "访问产品部门"
}
```

**响应** (201):
```json
{
  "id": 1,
  "pass_code": "V20250617001",
  "name": "张三",
  "phone_number": "13800138000",
  "email": "zhangsan@example.com",
  "identification_no": "110101199001011234",
  "company_name": "ABC公司",
  "purpose": "business_meeting",
  "status": "pending",
  "expected_date": "2025-06-17T09:00:00Z",
  "employee_id": 1,
  "tenant_id": "default_tenant",
  "created_at": "2025-06-17T07:00:00Z",
  "updated_at": "2025-06-17T07:00:00Z"
}
```

### 4. 获取访客列表
**获取当前租户的访客列表**

```http
GET /api/v1/visitors/?skip=0&limit=20&status=pending
```

**查询参数**:
- `skip` (int): 跳过记录数，默认0
- `limit` (int): 每页记录数，默认20，最大100
- `status` (string): 状态筛选 (`pending`, `approved`, `rejected`, `checked_in`, `checked_out`, `cancelled`, `expired`)
- `employee_id` (int): 接待员工ID筛选
- `date_from` (string): 开始日期 (ISO格式)
- `date_to` (string): 结束日期 (ISO格式)

**响应** (200):
```json
{
  "items": [
    {
      "id": 1,
      "pass_code": "V20250617001",
      "name": "张三",
      "phone_number": "13800138000",
      "status": "pending",
      "purpose": "business_meeting",
      "expected_date": "2025-06-17T09:00:00Z",
      "employee": {
        "id": 1,
        "name": "李经理",
        "department": "产品部"
      },
      "created_at": "2025-06-17T07:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### 5. 获取访客详情
**根据ID获取访客详细信息**

```http
GET /api/v1/visitors/{visitor_id}
```

**路径参数**:
- `visitor_id` (int): 访客ID

**响应** (200):
```json
{
  "id": 1,
  "pass_code": "V20250617001",
  "name": "张三",
  "phone_number": "13800138000",
  "email": "zhangsan@example.com",
  "identification_no": "110101199001011234",
  "company_name": "ABC公司",
  "purpose": "business_meeting",
  "status": "approved",
  "expected_date": "2025-06-17T09:00:00Z",
  "checkin_date": null,
  "checkout_date": null,
  "employee": {
    "id": 1,
    "name": "李经理",
    "department": "产品部",
    "phone_number": "13900139000"
  },
  "approval_history": [
    {
      "approver": "李经理",
      "outcome": "approved",
      "comment": "同意访问",
      "approval_date": "2025-06-17T08:00:00Z"
    }
  ],
  "tenant_id": "default_tenant",
  "created_at": "2025-06-17T07:00:00Z",
  "updated_at": "2025-06-17T08:00:00Z"
}
```

### 6. 更新访客信息
**更新访客信息**

```http
PUT /api/v1/visitors/{visitor_id}
```

**请求体** (部分字段):
```json
{
  "phone_number": "13800138001",
  "email": "zhangsan_new@example.com",
  "purpose": "site_visit",
  "comment": "更新联系方式"
}
```

**响应** (200): 返回更新后的完整访客信息

### 7. 删除访客
**软删除访客记录**

```http
DELETE /api/v1/visitors/{visitor_id}
```

**响应** (204): 无内容

### 8. 审批访客
**审批访客申请**

```http
POST /api/v1/visitors/{visitor_id}/approve
```

**请求体**:
```json
{
  "outcome": "approved",
  "comment": "同意访问，请按时到达"
}
```

**响应** (200):
```json
{
  "id": 1,
  "status": "approved",
  "approval_outcome": "approved",
  "approval_comment": "同意访问，请按时到达",
  "updated_at": "2025-06-17T08:00:00Z"
}
```

### 9. 访客签到
**访客到达签到**

```http
POST /api/v1/visitors/{visitor_id}/checkin
```

**请求体**:
```json
{
  "checkin_point": "main_entrance",
  "comment": "访客已到达前台"
}
```

**响应** (200):
```json
{
  "id": 1,
  "status": "checked_in",
  "checkin_date": "2025-06-17T09:00:00Z",
  "checkin_point": "main_entrance",
  "updated_at": "2025-06-17T09:00:00Z"
}
```

### 10. 访客签出
**访客离开签出**

```http
POST /api/v1/visitors/{visitor_id}/checkout
```

**请求体**:
```json
{
  "checkout_point": "main_entrance",
  "comment": "访客已离开"
}
```

**响应** (200):
```json
{
  "id": 1,
  "status": "checked_out",
  "checkout_date": "2025-06-17T11:00:00Z",
  "checkout_point": "main_entrance",
  "updated_at": "2025-06-17T11:00:00Z"
}
```

## 🧑‍💼 员工管理API

### 11. 创建员工
**注册新员工**

```http
POST /api/v1/employees/
```

**请求体**:
```json
{
  "name": "李经理",
  "employee_id": "EMP001",
  "email": "li.manager@company.com",
  "phone_number": "13900139000",
  "department_id": 1,
  "position": "产品经理",
  "hire_date": "2025-01-01T00:00:00Z"
}
```

**响应** (201): 返回创建的员工信息

### 12. 获取员工列表
**获取当前租户的员工列表**

```http
GET /api/v1/employees/?skip=0&limit=20&department_id=1&status=active
```

**查询参数**:
- `skip` (int): 跳过记录数
- `limit` (int): 每页记录数
- `department_id` (int): 部门ID筛选
- `status` (string): 状态筛选 (`active`, `inactive`, `terminated`, `on_leave`)
- `search` (string): 姓名模糊搜索

**响应** (200): 返回员工列表

### 13. 获取员工详情
**根据ID获取员工详细信息**

```http
GET /api/v1/employees/{employee_id}
```

**响应** (200): 返回员工详细信息

### 14. 更新员工信息
**更新员工信息**

```http
PUT /api/v1/employees/{employee_id}
```

**响应** (200): 返回更新后的员工信息

### 15. 删除员工
**软删除员工记录**

```http
DELETE /api/v1/employees/{employee_id}
```

**响应** (204): 无内容

## 🏢 部门管理API

### 16. 创建部门
**创建新部门**

```http
POST /api/v1/departments/
```

**请求体**:
```json
{
  "name": "产品部",
  "code": "PRODUCT",
  "description": "负责产品设计和开发",
  "parent_id": null,
  "manager_id": 1,
  "site_id": 1
}
```

**响应** (201): 返回创建的部门信息

### 17. 获取部门列表
**获取当前租户的部门列表**

```http
GET /api/v1/departments/?skip=0&limit=20&parent_id=1
```

**响应** (200): 返回部门列表

### 18. 获取部门详情
**根据ID获取部门详细信息**

```http
GET /api/v1/departments/{department_id}
```

**响应** (200): 返回部门详细信息

### 19. 更新部门信息
**更新部门信息**

```http
PUT /api/v1/departments/{department_id}
```

**响应** (200): 返回更新后的部门信息

### 20. 删除部门
**软删除部门记录**

```http
DELETE /api/v1/departments/{department_id}
```

**响应** (204): 无内容

## 🏬 站点管理API

### 21. 创建站点
**创建新站点**

```http
POST /api/v1/sites/
```

**请求体**:
```json
{
  "name": "北京总部",
  "code": "BJ_HQ",
  "address": "北京市朝阳区xxx路xxx号",
  "city": "北京",
  "province": "北京",
  "country": "中国",
  "phone": "010-12345678",
  "email": "bj.hq@company.com"
}
```

**响应** (201): 返回创建的站点信息

### 22. 获取站点列表
**获取当前租户的站点列表**

```http
GET /api/v1/sites/?skip=0&limit=20&status=active
```

**响应** (200): 返回站点列表

### 23. 获取站点详情
**根据ID获取站点详细信息**

```http
GET /api/v1/sites/{site_id}
```

**响应** (200): 返回站点详细信息

### 24. 更新站点信息
**更新站点信息**

```http
PUT /api/v1/sites/{site_id}
```

**响应** (200): 返回更新后的站点信息

## ⚙️ 配置引擎API

配置引擎提供4大模块的动态配置管理能力。

### 表单配置API

### 25. 创建表单配置
**创建动态表单配置**

```http
POST /api/v1/config/forms/
```

**请求体**:
```json
{
  "form_name": "访客登记表单",
  "form_type": "visitor_registration",
  "description": "标准访客登记表单",
  "is_default": false,
  "form_fields": [
    {
      "field_key": "visitor_name",
      "field_label": "访客姓名",
      "field_type": "text",
      "field_order": 1,
      "is_required": true,
      "placeholder_text": "请输入访客姓名"
    },
    {
      "field_key": "phone_number",
      "field_label": "联系电话",
      "field_type": "phone",
      "field_order": 2,
      "is_required": true,
      "validation_rules": {
        "pattern": "^1[3-9]\\d{9}$"
      }
    },
    {
      "field_key": "visit_purpose",
      "field_label": "访问目的",
      "field_type": "select",
      "field_order": 3,
      "is_required": true,
      "field_options": {
        "options": [
          {"value": "business_meeting", "label": "商务会议"},
          {"value": "interview", "label": "面试"},
          {"value": "site_visit", "label": "参观访问"}
        ]
      }
    }
  ]
}
```

**响应** (201):
```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "form_name": "访客登记表单",
  "form_type": "visitor_registration",
  "form_version": 1,
  "description": "标准访客登记表单",
  "is_active": true,
  "is_default": false,
  "form_fields": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "field_key": "visitor_name",
      "field_label": "访客姓名",
      "field_type": "text",
      "field_order": 1,
      "is_required": true,
      "is_readonly": false,
      "is_visible": true,
      "placeholder_text": "请输入访客姓名",
      "created_at": "2025-06-17T07:00:00Z"
    }
  ],
  "form_schema": {},
  "ui_schema": {},
  "validation_schema": {},
  "tenant_id": "default_tenant",
  "created_at": "2025-06-17T07:00:00Z",
  "updated_at": "2025-06-17T07:00:00Z",
  "created_by": "admin",
  "updated_by": "admin"
}
```

### 26. 获取表单配置列表
**获取表单配置列表**

```http
GET /api/v1/config/forms/?skip=0&limit=10&form_type=visitor_registration&is_active=true
```

**查询参数**:
- `skip` (int): 跳过记录数
- `limit` (int): 每页记录数
- `form_type` (string): 表单类型筛选
- `is_active` (bool): 激活状态筛选

**响应** (200): 返回表单配置列表

### 工作流配置API

### 27. 获取工作流配置列表
**获取工作流配置列表**

```http
GET /api/v1/config/workflows/?skip=0&limit=10&workflow_type=visitor_approval
```

**响应** (200): 返回工作流配置列表

### 空间配置API

### 28. 获取空间配置列表
**获取空间配置列表**

```http
GET /api/v1/config/spatial/?skip=0&limit=10&is_active=true
```

**响应** (200): 返回空间配置列表

### 业务规则API

### 29. 获取业务规则列表
**获取业务规则列表**

```http
GET /api/v1/config/rules/?skip=0&limit=10&rule_category=validation
```

**响应** (200): 返回业务规则列表

## 🔍 API测试

### Swagger文档
访问 `http://localhost:8000/docs` 查看交互式API文档

### ReDoc文档
访问 `http://localhost:8000/redoc` 查看ReDoc格式文档

### 健康检查
```http
GET /health
```

**响应** (200):
```json
{
  "status": "healthy",
  "timestamp": "2025-06-17T07:00:00Z",
  "database": "connected",
  "cache": "connected"
}
```

## 🚨 错误处理

### 常见错误代码
| 错误代码 | HTTP状态 | 说明 | 解决方案 |
|----------|----------|------|----------|
| `VALIDATION_ERROR` | 422 | 数据验证失败 | 检查请求数据格式 |
| `AUTHENTICATION_FAILED` | 401 | 认证失败 | 检查Token有效性 |
| `PERMISSION_DENIED` | 403 | 权限不足 | 检查用户权限 |
| `RESOURCE_NOT_FOUND` | 404 | 资源不存在 | 检查资源ID |
| `DUPLICATE_RESOURCE` | 400 | 资源重复 | 检查唯一性约束 |
| `TENANT_MISMATCH` | 403 | 租户不匹配 | 检查租户权限 |

### 错误响应示例
```json
{
  "detail": "访客不存在或已被删除",
  "error_code": "RESOURCE_NOT_FOUND",
  "timestamp": "2025-06-17T07:00:00Z",
  "path": "/api/v1/visitors/999",
  "method": "GET"
}
```

## 📊 性能指标

### API响应时间
- **平均响应时间**: < 200ms
- **P95响应时间**: < 500ms
- **P99响应时间**: < 1000ms

### 并发支持
- **最大并发**: 1000+ 请求/秒
- **连接池大小**: 50个数据库连接
- **缓存命中率**: > 90%

## 🔄 版本管理

### API版本策略
- **当前版本**: v1
- **版本格式**: `/api/v{major}/`
- **向后兼容**: 保证同一大版本内向后兼容
- **废弃通知**: 新版本发布前6个月通知

### 更新日志
- **v1.0.0** (2025-06-17): 初始版本发布
- **配置引擎**: 完整的动态配置支持
- **多租户**: 全面的多租户架构

---

## 📞 技术支持

### API文档维护
- **负责人**: API开发团队
- **更新频率**: 随API版本更新
- **问题反馈**: 通过项目Issue提交

### 相关文档
- [后端系统架构概览](./Backend_System_Architecture.md)
- [数据模型设计文档](./Backend_Data_Models.md)
- [前端对接指南](./Frontend_Integration_Guide.md)
- [后端开发者指南](./Backend_Developer_Guide.md) 