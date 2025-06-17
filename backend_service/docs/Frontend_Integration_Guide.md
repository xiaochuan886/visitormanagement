# 前端对接指南

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **适用角色**: 前端开发者、全栈开发者

## 🎯 对接概述

本文档为前端开发者提供与访客管理系统后端API的完整集成方案，包括认证处理、API调用、错误处理、状态管理等最佳实践。

### 支持的前端技术栈
- ✅ **React** - 管理端推荐
- ✅ **Vue.js** - H5端推荐  
- ✅ **小程序** - 微信/支付宝小程序
- ✅ **移动端** - React Native/Flutter
- ✅ **原生JavaScript** - 通用支持

## 🚀 快速开始

### 1. 基础配置

#### API基础配置
```javascript
// config/api.js
const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 30000,
  RETRY_TIMES: 3
}

// API响应状态
const API_STATUS = {
  SUCCESS: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  VALIDATION_ERROR: 422,
  SERVER_ERROR: 500
}

export { API_CONFIG, API_STATUS }
```

#### HTTP客户端封装
```javascript
// utils/httpClient.js
import axios from 'axios'
import { API_CONFIG } from '../config/api'

class HttpClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        const tenantId = this.getTenantId()
        if (tenantId) {
          config.headers['X-Tenant-ID'] = tenantId
        }

        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        // Token过期自动刷新
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          try {
            await this.refreshToken()
            return this.client(originalRequest)
          } catch (refreshError) {
            this.handleAuthError()
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  getToken() {
    return localStorage.getItem('access_token')
  }

  getTenantId() {
    return localStorage.getItem('tenant_id') || 'default_tenant'
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) throw new Error('No refresh token')

    const response = await axios.post(`${API_CONFIG.BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken
    })

    const { access_token } = response.data
    localStorage.setItem('access_token', access_token)
    return access_token
  }

  handleAuthError() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
  }
}

export default new HttpClient()
```

### 2. 认证管理

#### 登录服务
```javascript
// services/authService.js
import httpClient from '../utils/httpClient'

class AuthService {
  async login(credentials) {
    try {
      const response = await httpClient.client.post('/auth/login', credentials)
      const { access_token, refresh_token, user_info } = response.data
      
      // 保存令牌和用户信息
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user_info', JSON.stringify(user_info))
      localStorage.setItem('tenant_id', user_info.tenant_id)
      
      return { success: true, data: user_info }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || '登录失败' 
      }
    }
  }

  async logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
    localStorage.removeItem('tenant_id')
  }

  getCurrentUser() {
    const userInfo = localStorage.getItem('user_info')
    return userInfo ? JSON.parse(userInfo) : null
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  }
}

export default new AuthService()
```

#### React认证Hook
```javascript
// hooks/useAuth.js
import { useState, useEffect, useContext, createContext } from 'react'
import authService from '../services/authService'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const currentUser = authService.getCurrentUser()
    setUser(currentUser)
    setLoading(false)
  }, [])

  const login = async (credentials) => {
    const result = await authService.login(credentials)
    if (result.success) {
      setUser(result.data)
    }
    return result
  }

  const logout = async () => {
    await authService.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
```

### 3. API服务封装

#### 访客管理服务
```javascript
// services/visitorService.js
import httpClient from '../utils/httpClient'

class VisitorService {
  async getVisitors(params = {}) {
    try {
      const response = await httpClient.client.get('/visitors/', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async getVisitor(id) {
    try {
      const response = await httpClient.client.get(`/visitors/${id}`)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async createVisitor(visitorData) {
    try {
      const response = await httpClient.client.post('/visitors/', visitorData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async updateVisitor(id, updates) {
    try {
      const response = await httpClient.client.put(`/visitors/${id}`, updates)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async deleteVisitor(id) {
    try {
      await httpClient.client.delete(`/visitors/${id}`)
      return { success: true }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async approveVisitor(id, approval) {
    try {
      const response = await httpClient.client.post(`/visitors/${id}/approve`, approval)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async checkinVisitor(id, checkinData) {
    try {
      const response = await httpClient.client.post(`/visitors/${id}/checkin`, checkinData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async checkoutVisitor(id, checkoutData) {
    try {
      const response = await httpClient.client.post(`/visitors/${id}/checkout`, checkoutData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  handleError(error) {
    const message = error.response?.data?.detail || error.message || '操作失败'
    const status = error.response?.status
    const errorCode = error.response?.data?.error_code
    
    return { 
      success: false, 
      error: message,
      status,
      errorCode
    }
  }
}

export default new VisitorService()
```

#### 配置引擎服务
```javascript
// services/configService.js
import httpClient from '../utils/httpClient'

class ConfigService {
  // 表单配置
  async getFormConfigs(params = {}) {
    try {
      const response = await httpClient.client.get('/config/forms/', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async createFormConfig(formData) {
    try {
      const response = await httpClient.client.post('/config/forms/', formData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 工作流配置
  async getWorkflowConfigs(params = {}) {
    try {
      const response = await httpClient.client.get('/config/workflows/', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 空间配置
  async getSpatialConfigs(params = {}) {
    try {
      const response = await httpClient.client.get('/config/spatial/', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 业务规则
  async getBusinessRules(params = {}) {
    try {
      const response = await httpClient.client.get('/config/rules/', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  handleError(error) {
    const message = error.response?.data?.detail || error.message || '操作失败'
    return { success: false, error: message }
  }
}

export default new ConfigService()
```

## 🎨 UI组件示例

### React组件示例

#### 访客列表组件
```jsx
// components/VisitorList.jsx
import React, { useState, useEffect } from 'react'
import visitorService from '../services/visitorService'
import { useAuth } from '../hooks/useAuth'

const VisitorList = () => {
  const [visitors, setVisitors] = useState([])
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0
  })
  const [filters, setFilters] = useState({
    status: '',
    dateFrom: '',
    dateTo: ''
  })

  const { user } = useAuth()

  useEffect(() => {
    loadVisitors()
  }, [pagination.page, filters])

  const loadVisitors = async () => {
    setLoading(true)
    try {
      const params = {
        skip: (pagination.page - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...filters
      }

      const result = await visitorService.getVisitors(params)
      if (result.success) {
        setVisitors(result.data.items)
        setPagination(prev => ({
          ...prev,
          total: result.data.total
        }))
      }
    } catch (error) {
      console.error('加载访客列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (visitorId, outcome) => {
    try {
      const result = await visitorService.approveVisitor(visitorId, {
        outcome,
        comment: outcome === 'approved' ? '同意访问' : '拒绝访问'
      })

      if (result.success) {
        loadVisitors() // 重新加载列表
      }
    } catch (error) {
      console.error('审批失败:', error)
    }
  }

  const handleCheckin = async (visitorId) => {
    try {
      const result = await visitorService.checkinVisitor(visitorId, {
        checkin_point: 'main_entrance',
        comment: '访客已到达'
      })

      if (result.success) {
        loadVisitors()
      }
    } catch (error) {
      console.error('签到失败:', error)
    }
  }

  if (loading) {
    return <div>加载中...</div>
  }

  return (
    <div className="visitor-list">
      <div className="filters">
        <select 
          value={filters.status} 
          onChange={e => setFilters({...filters, status: e.target.value})}
        >
          <option value="">全部状态</option>
          <option value="pending">待审批</option>
          <option value="approved">已审批</option>
          <option value="checked_in">已签到</option>
          <option value="checked_out">已签出</option>
        </select>
      </div>

      <div className="visitor-table">
        <table>
          <thead>
            <tr>
              <th>访客姓名</th>
              <th>联系电话</th>
              <th>访问目的</th>
              <th>状态</th>
              <th>预约时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {visitors.map(visitor => (
              <tr key={visitor.id}>
                <td>{visitor.name}</td>
                <td>{visitor.phone_number}</td>
                <td>{visitor.purpose}</td>
                <td>{getStatusText(visitor.status)}</td>
                <td>{new Date(visitor.expected_date).toLocaleString()}</td>
                <td>
                  {visitor.status === 'pending' && (
                    <>
                      <button onClick={() => handleApprove(visitor.id, 'approved')}>
                        同意
                      </button>
                      <button onClick={() => handleApprove(visitor.id, 'rejected')}>
                        拒绝
                      </button>
                    </>
                  )}
                  {visitor.status === 'approved' && (
                    <button onClick={() => handleCheckin(visitor.id)}>
                      签到
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button 
          disabled={pagination.page === 1}
          onClick={() => setPagination(prev => ({...prev, page: prev.page - 1}))}
        >
          上一页
        </button>
        <span>第 {pagination.page} 页，共 {Math.ceil(pagination.total / pagination.pageSize)} 页</span>
        <button 
          disabled={pagination.page * pagination.pageSize >= pagination.total}
          onClick={() => setPagination(prev => ({...prev, page: prev.page + 1}))}
        >
          下一页
        </button>
      </div>
    </div>
  )
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审批',
    approved: '已审批',
    rejected: '已拒绝',
    checked_in: '已签到',
    checked_out: '已签出',
    cancelled: '已取消',
    expired: '已过期'
  }
  return statusMap[status] || status
}

export default VisitorList
```

#### 访客创建表单
```jsx
// components/VisitorForm.jsx
import React, { useState, useEffect } from 'react'
import visitorService from '../services/visitorService'
import employeeService from '../services/employeeService'

const VisitorForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    email: '',
    identification_no: '',
    company_name: '',
    purpose: 'business_meeting',
    expected_date: '',
    employee_id: '',
    comment: ''
  })
  
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    loadEmployees()
  }, [])

  const loadEmployees = async () => {
    const result = await employeeService.getEmployees()
    if (result.success) {
      setEmployees(result.data.items)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // 清除字段错误
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.name.trim()) {
      newErrors.name = '请输入访客姓名'
    }
    
    if (!formData.phone_number.trim()) {
      newErrors.phone_number = '请输入联系电话'
    } else if (!/^1[3-9]\d{9}$/.test(formData.phone_number)) {
      newErrors.phone_number = '请输入正确的手机号码'
    }
    
    if (!formData.expected_date) {
      newErrors.expected_date = '请选择预约时间'
    }
    
    if (!formData.employee_id) {
      newErrors.employee_id = '请选择接待员工'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    try {
      const result = await visitorService.createVisitor(formData)
      if (result.success) {
        onSubmit?.(result.data)
      } else {
        alert(result.error)
      }
    } catch (error) {
      alert('创建失败: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="visitor-form">
      <div className="form-group">
        <label>访客姓名 *</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={errors.name ? 'error' : ''}
        />
        {errors.name && <span className="error-text">{errors.name}</span>}
      </div>

      <div className="form-group">
        <label>联系电话 *</label>
        <input
          type="tel"
          name="phone_number"
          value={formData.phone_number}
          onChange={handleChange}
          className={errors.phone_number ? 'error' : ''}
        />
        {errors.phone_number && <span className="error-text">{errors.phone_number}</span>}
      </div>

      <div className="form-group">
        <label>邮箱地址</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label>身份证号</label>
        <input
          type="text"
          name="identification_no"
          value={formData.identification_no}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label>公司名称</label>
        <input
          type="text"
          name="company_name"
          value={formData.company_name}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label>访问目的 *</label>
        <select
          name="purpose"
          value={formData.purpose}
          onChange={handleChange}
        >
          <option value="business_meeting">商务会议</option>
          <option value="interview">面试</option>
          <option value="site_visit">参观访问</option>
          <option value="delivery">送货</option>
          <option value="maintenance">维护</option>
          <option value="other">其他</option>
        </select>
      </div>

      <div className="form-group">
        <label>预约时间 *</label>
        <input
          type="datetime-local"
          name="expected_date"
          value={formData.expected_date}
          onChange={handleChange}
          className={errors.expected_date ? 'error' : ''}
        />
        {errors.expected_date && <span className="error-text">{errors.expected_date}</span>}
      </div>

      <div className="form-group">
        <label>接待员工 *</label>
        <select
          name="employee_id"
          value={formData.employee_id}
          onChange={handleChange}
          className={errors.employee_id ? 'error' : ''}
        >
          <option value="">请选择接待员工</option>
          {employees.map(employee => (
            <option key={employee.id} value={employee.id}>
              {employee.name} - {employee.department?.name}
            </option>
          ))}
        </select>
        {errors.employee_id && <span className="error-text">{errors.employee_id}</span>}
      </div>

      <div className="form-group">
        <label>备注信息</label>
        <textarea
          name="comment"
          value={formData.comment}
          onChange={handleChange}
          rows={3}
        />
      </div>

      <div className="form-actions">
        <button type="button" onClick={onCancel}>
          取消
        </button>
        <button type="submit" disabled={loading}>
          {loading ? '创建中...' : '创建访客'}
        </button>
      </div>
    </form>
  )
}

export default VisitorForm
```

### Vue.js组件示例

#### 访客列表组件 (Vue 3)
```vue
<!-- components/VisitorList.vue -->
<template>
  <div class="visitor-list">
    <div class="filters">
      <select v-model="filters.status" @change="loadVisitors">
        <option value="">全部状态</option>
        <option value="pending">待审批</option>
        <option value="approved">已审批</option>
        <option value="checked_in">已签到</option>
        <option value="checked_out">已签出</option>
      </select>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="visitor-table">
      <table>
        <thead>
          <tr>
            <th>访客姓名</th>
            <th>联系电话</th>
            <th>访问目的</th>
            <th>状态</th>
            <th>预约时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="visitor in visitors" :key="visitor.id">
            <td>{{ visitor.name }}</td>
            <td>{{ visitor.phone_number }}</td>
            <td>{{ visitor.purpose }}</td>
            <td>{{ getStatusText(visitor.status) }}</td>
            <td>{{ formatDate(visitor.expected_date) }}</td>
            <td>
              <template v-if="visitor.status === 'pending'">
                <button @click="handleApprove(visitor.id, 'approved')">
                  同意
                </button>
                <button @click="handleApprove(visitor.id, 'rejected')">
                  拒绝
                </button>
              </template>
              <template v-if="visitor.status === 'approved'">
                <button @click="handleCheckin(visitor.id)">
                  签到
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button 
        :disabled="pagination.page === 1"
        @click="pagination.page--; loadVisitors()"
      >
        上一页
      </button>
      <span>第 {{ pagination.page }} 页，共 {{ totalPages }} 页</span>
      <button 
        :disabled="pagination.page >= totalPages"
        @click="pagination.page++; loadVisitors()"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import visitorService from '../services/visitorService'

const visitors = ref([])
const loading = ref(false)
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})
const filters = reactive({
  status: '',
  dateFrom: '',
  dateTo: ''
})

const totalPages = computed(() => 
  Math.ceil(pagination.total / pagination.pageSize)
)

const loadVisitors = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...filters
    }

    const result = await visitorService.getVisitors(params)
    if (result.success) {
      visitors.value = result.data.items
      pagination.total = result.data.total
    }
  } catch (error) {
    console.error('加载访客列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleApprove = async (visitorId, outcome) => {
  try {
    const result = await visitorService.approveVisitor(visitorId, {
      outcome,
      comment: outcome === 'approved' ? '同意访问' : '拒绝访问'
    })

    if (result.success) {
      await loadVisitors()
    }
  } catch (error) {
    console.error('审批失败:', error)
  }
}

const handleCheckin = async (visitorId) => {
  try {
    const result = await visitorService.checkinVisitor(visitorId, {
      checkin_point: 'main_entrance',
      comment: '访客已到达'
    })

    if (result.success) {
      await loadVisitors()
    }
  } catch (error) {
    console.error('签到失败:', error)
  }
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '待审批',
    approved: '已审批',
    rejected: '已拒绝',
    checked_in: '已签到',
    checked_out: '已签出',
    cancelled: '已取消',
    expired: '已过期'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadVisitors()
})
</script>
```

## 🛠️ 最佳实践

### 1. 错误处理策略

#### 统一错误处理
```javascript
// utils/errorHandler.js
class ErrorHandler {
  static handle(error, context = '') {
    console.error(`${context} 错误:`, error)

    // 网络错误
    if (!error.response) {
      return {
        message: '网络连接失败，请检查网络设置',
        type: 'network'
      }
    }

    const { status, data } = error.response

    // 根据状态码处理
    switch (status) {
      case 400:
        return {
          message: data.detail || '请求参数错误',
          type: 'validation'
        }
      case 401:
        return {
          message: '登录已过期，请重新登录',
          type: 'auth'
        }
      case 403:
        return {
          message: '没有权限执行此操作',
          type: 'permission'
        }
      case 404:
        return {
          message: '请求的资源不存在',
          type: 'notfound'
        }
      case 422:
        return {
          message: this.formatValidationErrors(data),
          type: 'validation'
        }
      case 500:
        return {
          message: '服务器内部错误，请稍后重试',
          type: 'server'
        }
      default:
        return {
          message: data.detail || '未知错误',
          type: 'unknown'
        }
    }
  }

  static formatValidationErrors(data) {
    if (data.detail && Array.isArray(data.detail)) {
      return data.detail.map(err => err.msg).join(', ')
    }
    return data.detail || '数据验证失败'
  }
}

export default ErrorHandler
```

### 2. 状态管理

#### Redux/Zustand状态管理
```javascript
// stores/visitorStore.js (Zustand示例)
import { create } from 'zustand'
import visitorService from '../services/visitorService'

const useVisitorStore = create((set, get) => ({
  // 状态
  visitors: [],
  currentVisitor: null,
  loading: false,
  pagination: {
    page: 1,
    pageSize: 20,
    total: 0
  },
  filters: {
    status: '',
    dateFrom: '',
    dateTo: ''
  },

  // 操作
  setLoading: (loading) => set({ loading }),
  
  setFilters: (filters) => set({ filters }),
  
  setPagination: (pagination) => set((state) => ({
    pagination: { ...state.pagination, ...pagination }
  })),

  loadVisitors: async () => {
    const { pagination, filters } = get()
    set({ loading: true })
    
    try {
      const params = {
        skip: (pagination.page - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...filters
      }

      const result = await visitorService.getVisitors(params)
      if (result.success) {
        set({
          visitors: result.data.items,
          pagination: {
            ...pagination,
            total: result.data.total
          }
        })
      }
    } catch (error) {
      console.error('加载访客失败:', error)
    } finally {
      set({ loading: false })
    }
  },

  approveVisitor: async (id, outcome) => {
    try {
      const result = await visitorService.approveVisitor(id, {
        outcome,
        comment: outcome === 'approved' ? '同意访问' : '拒绝访问'
      })

      if (result.success) {
        // 更新本地状态
        set((state) => ({
          visitors: state.visitors.map(visitor =>
            visitor.id === id ? { ...visitor, status: outcome } : visitor
          )
        }))
        return { success: true }
      }
      return result
    } catch (error) {
      return { success: false, error: error.message }
    }
  }
}))

export default useVisitorStore
```

### 3. 缓存策略

#### API响应缓存
```javascript
// utils/cache.js
class CacheManager {
  constructor() {
    this.cache = new Map()
    this.timeouts = new Map()
  }

  set(key, data, ttl = 300000) { // 默认5分钟
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    })

    // 设置自动清除
    if (this.timeouts.has(key)) {
      clearTimeout(this.timeouts.get(key))
    }

    const timeout = setTimeout(() => {
      this.delete(key)
    }, ttl)

    this.timeouts.set(key, timeout)
  }

  get(key) {
    const cached = this.cache.get(key)
    if (!cached) return null

    const { data, timestamp, ttl } = cached
    if (Date.now() - timestamp > ttl) {
      this.delete(key)
      return null
    }

    return data
  }

  delete(key) {
    this.cache.delete(key)
    if (this.timeouts.has(key)) {
      clearTimeout(this.timeouts.get(key))
      this.timeouts.delete(key)
    }
  }

  clear() {
    this.cache.clear()
    this.timeouts.forEach(timeout => clearTimeout(timeout))
    this.timeouts.clear()
  }
}

const cache = new CacheManager()

// 带缓存的API调用包装器
export const withCache = (apiCall, cacheKey, ttl) => {
  return async (...args) => {
    const key = `${cacheKey}_${JSON.stringify(args)}`
    
    // 尝试从缓存获取
    const cached = cache.get(key)
    if (cached) {
      return cached
    }

    // 调用API
    const result = await apiCall(...args)
    
    // 缓存成功响应
    if (result.success) {
      cache.set(key, result, ttl)
    }

    return result
  }
}

export default cache
```

### 4. 性能优化

#### 虚拟滚动 (大数据量列表)
```javascript
// hooks/useVirtualList.js
import { useMemo, useState, useEffect } from 'react'

const useVirtualList = (items, itemHeight, containerHeight) => {
  const [scrollTop, setScrollTop] = useState(0)

  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight)
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    )

    return {
      startIndex,
      endIndex,
      items: items.slice(startIndex, endIndex),
      offsetY: startIndex * itemHeight
    }
  }, [items, itemHeight, containerHeight, scrollTop])

  const totalHeight = items.length * itemHeight

  return {
    visibleItems,
    totalHeight,
    setScrollTop
  }
}

export default useVirtualList
```

#### 防抖搜索
```javascript
// hooks/useDebounce.js
import { useState, useEffect } from 'react'

const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

// 使用示例
const SearchComponent = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const debouncedSearchTerm = useDebounce(searchTerm, 500)

  useEffect(() => {
    if (debouncedSearchTerm) {
      // 执行搜索
      searchVisitors(debouncedSearchTerm)
    }
  }, [debouncedSearchTerm])

  return (
    <input
      type="text"
      value={searchTerm}
      onChange={e => setSearchTerm(e.target.value)}
      placeholder="搜索访客..."
    />
  )
}
```

## 📱 移动端集成

### 微信小程序示例
```javascript
// utils/request.js (微信小程序)
class WxRequest {
  constructor() {
    this.baseUrl = 'https://api.yourcompany.com/api/v1'
    this.token = wx.getStorageSync('access_token')
  }

  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: this.baseUrl + options.url,
        method: options.method || 'GET',
        data: options.data,
        header: {
          'Content-Type': 'application/json',
          'Authorization': this.token ? `Bearer ${this.token}` : '',
          ...options.header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else if (res.statusCode === 401) {
            // Token过期，跳转登录
            wx.removeStorageSync('access_token')
            wx.redirectTo({ url: '/pages/login/login' })
            reject(new Error('登录已过期'))
          } else {
            reject(new Error(res.data.detail || '请求失败'))
          }
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  }

  get(url, data) {
    return this.request({ url, method: 'GET', data })
  }

  post(url, data) {
    return this.request({ url, method: 'POST', data })
  }
}

export default new WxRequest()
```

## 🔄 实时功能

### WebSocket连接
```javascript
// utils/websocket.js
class WebSocketManager {
  constructor(url) {
    this.url = url
    this.ws = null
    this.reconnectInterval = 5000
    this.maxReconnectAttempts = 5
    this.reconnectAttempts = 0
    this.listeners = new Map()
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url)
      
      this.ws.onopen = () => {
        console.log('WebSocket连接已建立')
        this.reconnectAttempts = 0
        this.authenticate()
      }

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      }

      this.ws.onclose = () => {
        console.log('WebSocket连接已关闭')
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error)
    }
  }

  authenticate() {
    const token = localStorage.getItem('access_token')
    if (token) {
      this.send({
        type: 'authenticate',
        token
      })
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  subscribe(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)
  }

  unsubscribe(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback)
    }
  }

  handleMessage(data) {
    const { type, payload } = data
    if (this.listeners.has(type)) {
      this.listeners.get(type).forEach(callback => {
        callback(payload)
      })
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect()
      }, this.reconnectInterval)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
    }
  }
}

// 使用示例
const wsManager = new WebSocketManager('ws://localhost:8000/ws')

// 监听访客状态变化
wsManager.subscribe('visitor_status_changed', (data) => {
  console.log('访客状态变化:', data)
  // 更新UI
})

export default wsManager
```

## 📚 常见问题

### Q1: Token过期如何处理？
**A**: 使用请求拦截器自动检测401响应，调用刷新Token接口，重新发送原请求。

### Q2: 如何处理网络异常？
**A**: 实现重试机制，指数退避策略，用户友好的错误提示。

### Q3: 大数据量列表如何优化？
**A**: 使用虚拟滚动、分页加载、搜索过滤等技术。

### Q4: 如何实现离线功能？
**A**: 使用Service Worker缓存API响应，IndexedDB存储数据。

---

## 📞 技术支持

### 前端集成支持
- **负责人**: 前端开发团队
- **技术栈**: React, Vue.js, 小程序
- **问题反馈**: 通过项目Issue提交

### 相关文档
- [后端API完整参考手册](./Backend_API_Reference.md)
- [后端系统架构概览](./Backend_System_Architecture.md)
- [后端开发者指南](./Backend_Developer_Guide.md) 