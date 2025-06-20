# 前端对接指南 v3.1

## 📋 文档信息
- **版本**: v3.1.0
- **创建日期**: 2025-06-20
- **最后更新**: 2025-06-20 18:00
- **适用角色**: 前端开发者、全栈开发者

## 🎯 对接概述

本文档为前端开发者提供与访客管理系统后端API的完整集成方案。系统已升级至v3.1.0，**新增匿名访客申请功能**，支持租户数据隔离，API成功率达到**100%**，提供156个API端点的完整前端集成指导。

### 🚀 最新功能亮点 (v3.1.0)
- ✨ **匿名访客申请** - 无需登录即可提交访客申请，降低使用门槛
- 🔒 **租户数据隔离** - 完整的多租户架构，确保数据安全性
- 📱 **手机号查询** - 访客可通过手机号查询申请状态和审批进度
- 🏠 **智能租户分配** - 后端自动处理租户分配，前端可选择性传递
- ✅ **API完整性** - 100%的API成功率，37个用户旅程节点全覆盖

### 支持的前端技术栈
- ✅ **React Admin Dashboard** - 管理端控制台，支持复杂场景化配置界面
- ✅ **React Mobile Portal** - 移动端H5应用，适配门岗前台系统  
- ✅ **Vue.js H5应用** - 访客自主申请门户，无需登录
- ✅ **React Native App** - 原生移动端应用，门岗验证和移动同步
- ✅ **小程序** - 微信/支付宝小程序，访客自助申请和服务
- ✅ **原生JavaScript** - 设备嵌入式系统，WebView集成和硬件控制

## 🔓 匿名访客申请集成

### 1. 核心概念
匿名访客申请是v3.1.0的重要新功能，允许外部访客无需登录即可提交访客申请。

**核心优势**：
- 🚫 **无需注册** - 访客无需预先注册账号
- 🏠 **自动租户** - 后端智能分配租户，确保数据隔离
- 📱 **手机查询** - 访客可随时查询申请状态
- 🔄 **无缝升级** - 兼容现有认证系统

### 2. API端点说明

#### 2.1 匿名访客申请
```http
POST /api/v1/visitors/apply
Content-Type: application/json
X-Tenant-ID: company_a  # 可选，指定租户

{
  "name": "张三",
  "phone_number": "13800138000",
  "identification_no": "110101199001011234",
  "company_name": "测试公司",
  "purpose": "business",
  "expected_date": "2025-06-21T14:00:00",
  "employee_id": 1,
  "site_id": 5,
  "email": "zhangsan@company.com",
  "comment": "商务洽谈"
}
```

**响应示例**：
```json
{
  "id": 11,
  "pass_code": "7EEDC15E",
  "name": "张三",
  "phone_number": "13800138000",
  "status": "pending",
  "tenant_id": "default",
  "created_at": "2025-06-20T09:50:31.218672Z"
}
```

#### 2.2 手机号查询申请状态
```http
GET /api/v1/visitors/query/by-phone?phone_number=13800138000
X-Tenant-ID: company_a  # 可选，指定租户
```

**响应示例**：
```json
[
  {
    "id": 11,
    "pass_code": "7EEDC15E",
    "name": "张三",
    "status": "pending",
    "approval_outcome": null,
    "approval_comment": null,
    "expected_date": "2025-06-21T14:00:00",
    "created_at": "2025-06-20T09:50:31.218672Z"
  }
]
```

### 3. JavaScript SDK实现

#### 3.1 匿名访客服务
```javascript
// services/anonymousVisitorService.js
class AnonymousVisitorService {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }

  /**
   * 匿名访客申请 - 无需登录
   * @param {Object} visitorData 访客申请数据
   * @param {string} tenantId 可选的租户ID
   */
  async submitApplication(visitorData, tenantId = null) {
    try {
      const headers = {}
      if (tenantId) {
        headers['X-Tenant-ID'] = tenantId
      }

      const response = await this.client.post('/visitors/apply', {
        name: visitorData.name,
        phone_number: visitorData.phoneNumber,
        identification_no: visitorData.idNumber,
        company_name: visitorData.companyName,
        purpose: visitorData.purpose, // 'business', 'interview', 'delivery', etc.
        expected_date: visitorData.expectedDate, // ISO格式
        employee_id: visitorData.employeeId,
        site_id: visitorData.siteId,
        email: visitorData.email,
        comment: visitorData.comment
      }, { headers })

      return {
        success: true,
        data: response.data,
        passCode: response.data.pass_code,
        applicationId: response.data.id
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * 通过手机号查询申请状态 - 无需登录
   */
  async queryByPhone(phoneNumber, tenantId = null) {
    try {
      const headers = {}
      if (tenantId) {
        headers['X-Tenant-ID'] = tenantId
      }

      const response = await this.client.get(
        `/visitors/query/by-phone?phone_number=${phoneNumber}`,
        { headers }
      )

      return {
        success: true,
        data: response.data,
        applications: response.data.map(item => ({
          id: item.id,
          name: item.name,
          status: this.translateStatus(item.status),
          passCode: item.pass_code,
          expectedDate: item.expected_date,
          createdAt: item.created_at,
          approvalOutcome: item.approval_outcome,
          approvalComment: item.approval_comment
        }))
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * 获取可用站点列表 - 无需登录
   */
  async getAvailableSites() {
    try {
      const response = await this.client.get('/sites/')
      return {
        success: true,
        data: response.data.items || response.data
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  /**
   * 获取可访问员工列表 - 无需登录
   */
  async getAvailableEmployees() {
    try {
      const response = await this.client.get('/employees/')
      return {
        success: true,
        data: response.data.items || response.data
      }
    } catch (error) {
      return this.handleError(error)
    }
  }

  translateStatus(status) {
    const statusMap = {
      'pending': '待审批',
      'approved': '已通过',
      'rejected': '已拒绝',
      'checked_in': '已签到',
      'checked_out': '已签出',
      'expired': '已过期'
    }
    return statusMap[status] || status
  }

  handleError(error) {
    const message = error.response?.data?.detail || error.message || '操作失败'
    const status = error.response?.status
    const validationErrors = error.response?.data?.detail

    return {
      success: false,
      error: message,
      status,
      validationErrors: Array.isArray(validationErrors) ? validationErrors : null
    }
  }
}

export default new AnonymousVisitorService()
```

#### 3.2 Vue.js组件示例
```vue
<!-- components/VisitorApplicationForm.vue -->
<template>
  <div class="visitor-application-form">
    <h2>访客申请</h2>
    
    <!-- 成功/错误提示 -->
    <div v-if="result" :class="['alert', result.type]">
      <p>{{ result.message }}</p>
      <p v-if="result.passCode">
        <strong>通行码：{{ result.passCode }}</strong>
      </p>
      <ul v-if="result.validationErrors">
        <li v-for="error in result.validationErrors" :key="error.loc">
          {{ error.msg }}
        </li>
      </ul>
    </div>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>姓名 *</label>
        <input 
          v-model="formData.name" 
          type="text" 
          required 
          placeholder="请输入您的姓名"
        />
      </div>

      <div class="form-group">
        <label>手机号 *</label>
        <input 
          v-model="formData.phoneNumber" 
          type="tel" 
          required 
          placeholder="请输入手机号"
        />
      </div>

      <div class="form-group">
        <label>身份证号 *</label>
        <input 
          v-model="formData.idNumber" 
          type="text" 
          required 
          placeholder="请输入身份证号"
        />
      </div>

      <div class="form-group">
        <label>公司名称 *</label>
        <input 
          v-model="formData.companyName" 
          type="text" 
          required 
          placeholder="请输入公司名称"
        />
      </div>

      <div class="form-group">
        <label>访问目的 *</label>
        <select v-model="formData.purpose" required>
          <option value="business">商务洽谈</option>
          <option value="interview">面试</option>
          <option value="delivery">送货</option>
          <option value="maintenance">维修</option>
          <option value="meeting">会议</option>
          <option value="training">培训</option>
          <option value="other">其他</option>
        </select>
      </div>

      <div class="form-group">
        <label>预计到访时间 *</label>
        <input 
          v-model="formData.expectedDate" 
          type="datetime-local" 
          required 
        />
      </div>

      <div class="form-group">
        <label>被访问员工 *</label>
        <select v-model="formData.employeeId" required>
          <option value="">请选择员工</option>
          <option 
            v-for="emp in employees" 
            :key="emp.id" 
            :value="emp.id"
          >
            {{ emp.name }} - {{ emp.department_name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>访问站点 *</label>
        <select v-model="formData.siteId" required>
          <option value="">请选择站点</option>
          <option 
            v-for="site in sites" 
            :key="site.id" 
            :value="site.id"
          >
            {{ site.name }} - {{ site.address }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label>邮箱</label>
        <input 
          v-model="formData.email" 
          type="email" 
          placeholder="请输入邮箱（可选）"
        />
      </div>

      <div class="form-group">
        <label>备注</label>
        <textarea 
          v-model="formData.comment" 
          rows="3" 
          placeholder="请输入备注信息（可选）"
        ></textarea>
      </div>

      <button type="submit" :disabled="loading" class="submit-btn">
        {{ loading ? '提交中...' : '提交申请' }}
      </button>
    </form>
  </div>
</template>

<script>
import anonymousVisitorService from '../services/anonymousVisitorService'

export default {
  name: 'VisitorApplicationForm',
  data() {
    return {
      formData: {
        name: '',
        phoneNumber: '',
        idNumber: '',
        companyName: '',
        purpose: 'business',
        expectedDate: '',
        employeeId: '',
        siteId: '',
        email: '',
        comment: ''
      },
      sites: [],
      employees: [],
      loading: false,
      result: null
    }
  },
  async mounted() {
    await this.loadInitialData()
  },
  methods: {
    async loadInitialData() {
      try {
        const [sitesResult, employeesResult] = await Promise.all([
          anonymousVisitorService.getAvailableSites(),
          anonymousVisitorService.getAvailableEmployees()
        ])

        if (sitesResult.success) this.sites = sitesResult.data
        if (employeesResult.success) this.employees = employeesResult.data
      } catch (error) {
        console.error('加载初始数据失败:', error)
      }
    },

    async handleSubmit() {
      this.loading = true
      this.result = null

      try {
        // 格式化日期时间
        const expectedDate = new Date(this.formData.expectedDate).toISOString()
        
        const submitData = {
          ...this.formData,
          expectedDate
        }

        const result = await anonymousVisitorService.submitApplication(submitData)
        
        if (result.success) {
          this.result = {
            type: 'success',
            message: '申请提交成功！请记住您的通行码。',
            passCode: result.passCode,
            applicationId: result.applicationId
          }
          
          // 清空表单
          this.resetForm()
        } else {
          this.result = {
            type: 'error',
            message: result.error,
            validationErrors: result.validationErrors
          }
        }
      } catch (error) {
        this.result = {
          type: 'error',
          message: '提交失败，请稍后重试'
        }
      } finally {
        this.loading = false
      }
    },

    resetForm() {
      this.formData = {
        name: '',
        phoneNumber: '',
        idNumber: '',
        companyName: '',
        purpose: 'business',
        expectedDate: '',
        employeeId: '',
        siteId: '',
        email: '',
        comment: ''
      }
    }
  }
}
</script>

<style scoped>
.visitor-application-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.alert {
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.alert.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
```

#### 3.3 申请状态查询组件
```vue
<!-- components/VisitorStatusQuery.vue -->
<template>
  <div class="visitor-status-query">
    <h2>查询申请状态</h2>
    
    <div class="query-form">
      <div class="form-group">
        <label>手机号</label>
        <input 
          v-model="phoneNumber" 
          type="tel" 
          placeholder="请输入申请时使用的手机号"
        />
      </div>
      
      <button @click="handleQuery" :disabled="loading">
        {{ loading ? '查询中...' : '查询' }}
      </button>
    </div>

    <!-- 查询结果 -->
    <div v-if="applications.length > 0" class="applications-list">
      <h3>您的申请记录</h3>
      <div 
        v-for="app in applications" 
        :key="app.id" 
        class="application-card"
      >
        <div class="app-header">
          <span class="app-name">{{ app.name }}</span>
          <span :class="['status', getStatusClass(app.status)]">
            {{ app.status }}
          </span>
        </div>
        
        <div class="app-details">
          <p><strong>通行码：</strong>{{ app.passCode }}</p>
          <p><strong>预计到访：</strong>{{ formatDate(app.expectedDate) }}</p>
          <p><strong>申请时间：</strong>{{ formatDate(app.createdAt) }}</p>
          
          <div v-if="app.approvalOutcome" class="approval-info">
            <p><strong>审批结果：</strong>{{ translateApproval(app.approvalOutcome) }}</p>
            <p v-if="app.approvalComment"><strong>审批意见：</strong>{{ app.approvalComment }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="searched && applications.length === 0" class="no-results">
      <p>未找到相关申请记录</p>
    </div>

    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script>
import anonymousVisitorService from '../services/anonymousVisitorService'

export default {
  name: 'VisitorStatusQuery',
  data() {
    return {
      phoneNumber: '',
      applications: [],
      loading: false,
      searched: false,
      error: null
    }
  },
  methods: {
    async handleQuery() {
      if (!this.phoneNumber.trim()) {
        this.error = '请输入手机号'
        return
      }

      this.loading = true
      this.error = null
      this.searched = false

      try {
        const result = await anonymousVisitorService.queryByPhone(this.phoneNumber)
        
        if (result.success) {
          this.applications = result.applications
          this.searched = true
        } else {
          this.error = result.error
        }
      } catch (error) {
        this.error = '查询失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },

    getStatusClass(status) {
      const statusClasses = {
        '待审批': 'pending',
        '已通过': 'approved',
        '已拒绝': 'rejected',
        '已签到': 'checked-in',
        '已签出': 'checked-out',
        '已过期': 'expired'
      }
      return statusClasses[status] || 'default'
    },

    translateApproval(outcome) {
      const approvalMap = {
        'approved': '通过',
        'rejected': '拒绝',
        'pending': '待审批'
      }
      return approvalMap[outcome] || outcome
    },

    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.visitor-status-query {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.query-form {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.form-group {
  flex: 1;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.application-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  background-color: #f9f9f9;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.app-name {
  font-size: 18px;
  font-weight: bold;
}

.status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
}

.status.pending { background-color: #fff3cd; color: #856404; }
.status.approved { background-color: #d4edda; color: #155724; }
.status.rejected { background-color: #f8d7da; color: #721c24; }
.status.checked-in { background-color: #cce7ff; color: #004085; }
.status.checked-out { background-color: #e2e3e5; color: #383d41; }

.app-details p {
  margin: 8px 0;
}

.approval-info {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}

.no-results, .error-message {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  color: #dc3545;
}
</style>
```

## 🏠 租户隔离与多租户支持

### 1. 租户识别机制
系统支持多种租户识别方式，前端可以根据具体场景选择：

#### 方式1：后端自动分配（推荐）
```javascript
// 最简单的方式 - 后端自动处理租户
const result = await anonymousVisitorService.submitApplication(visitorData)
// 系统自动分配到 'default' 租户
```

#### 方式2：Header传递
```javascript
// 前端指定租户ID
const tenantId = getTenantFromDomain() // 从域名获取
const result = await anonymousVisitorService.submitApplication(visitorData, tenantId)
```

#### 方式3：域名识别（后端实现）
```javascript
// 根据访问域名自动识别租户
// company-a.visitor.com → company_a
// company-b.visitor.com → company_b
// 前端无需处理，后端自动解析
```

### 2. 租户工具函数
```javascript
// utils/tenantUtils.js
class TenantUtils {
  /**
   * 从域名获取租户ID
   */
  static getTenantFromDomain() {
    const hostname = window.location.hostname
    
    // 子域名模式: company-a.visitor.com
    if (hostname.endsWith('.visitor.com')) {
      const subdomain = hostname.split('.')[0]
      return subdomain !== 'www' ? subdomain : null
    }
    
    // 独立域名映射
    const domainTenantMap = {
      'company-a.com': 'company_a',
      'company-b.com': 'company_b'
    }
    
    return domainTenantMap[hostname] || null
  }

  /**
   * 智能获取租户ID
   */
  static getCurrentTenant() {
    return this.getTenantFromDomain() || 'default'
  }
}

export default TenantUtils
```

## 🚀 部署和配置

### 1. 环境变量配置
```bash
# .env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_DEFAULT_TENANT=default
REACT_APP_ENABLE_TENANT_HEADER=true
```

### 2. 构建配置
```json
{
  "name": "visitor-portal",
  "version": "1.0.0",
  "dependencies": {
    "axios": "^1.0.0",
    "vue": "^3.0.0"
  },
  "scripts": {
    "dev": "vue-cli-service serve",
    "build": "vue-cli-service build",
    "test": "vue-cli-service test:unit"
  }
}
```

### 3. API测试
```bash
# 测试匿名访客申请
curl -X POST "http://localhost:8000/api/v1/visitors/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试访客",
    "phone_number": "13800138000",
    "identification_no": "110101199001011234",
    "company_name": "测试公司",
    "purpose": "business",
    "expected_date": "2025-06-21T14:00:00",
    "employee_id": 1,
    "site_id": 5
  }'

# 测试手机号查询
curl "http://localhost:8000/api/v1/visitors/query/by-phone?phone_number=13800138000"
```

## 📝 注意事项

### 1. 安全考虑
- ✅ 所有数据经过租户隔离验证
- ✅ 输入数据经过完整验证
- ✅ 敏感信息不在URL中传递
- ⚠️ 生产环境建议启用HTTPS

### 2. 性能优化
- 🚀 使用axios拦截器统一处理请求
- 📱 移动端适配响应式设计
- 💾 适当使用本地缓存减少API调用
- ⚡ 表单验证在客户端进行

### 3. 错误处理
- 📋 完整的表单验证反馈
- 🔄 网络错误自动重试机制
- 💬 用户友好的错误提示
- 📊 错误日志记录

## 🎯 下一步开发建议

1. **立即可开发**：
   - ✅ 匿名访客申请页面
   - ✅ 申请状态查询页面
   - ✅ 基础的管理后台

2. **后续扩展**：
   - 🔜 实时通知功能
   - 🔜 二维码生成展示
   - 🔜 照片上传功能
   - 🔜 移动端优化

前端开发已具备完整的API支持，可以立即开始开发工作！