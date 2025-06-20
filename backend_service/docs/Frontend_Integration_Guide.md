# 前端对接指南

## 📋 文档信息
- **版本**: v3.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-20
- **适用角色**: 前端开发者、全栈开发者

## 🎯 对接概述

本文档为前端开发者提供与访客管理系统后端API的完整集成方案，包括认证处理、API调用、错误处理、状态管理等最佳实践。系统已升级至v3.0.0，新增场景化配置和门岗前台功能，提供156个API端点的完整前端集成指导。

### 支持的前端技术栈
- ✅ **React Admin Dashboard** - 管理端控制台，支持复杂场景化配置界面
- ✅ **React Mobile Portal** - 移动端H5应用，适配门岗前台系统  
- ✅ **React Native App** - 原生移动端应用，门岗验证和移动同步
- ✅ **小程序** - 微信/支付宝小程序，访客自助申请和服务
- ✅ **原生JavaScript** - 设备嵌入式系统，WebView集成和硬件控制

### 新增v3.0功能模块
- 🎯 **场景化配置模块** - 场景模板管理、智能路由、场景执行
- 🚪 **门岗管理模块** - 访客验证、入园登记、离线缓存
- 🏢 **前台管理模块** - 访客签到、主机通知、等候管理
- 📱 **移动端模块** - 数据同步、离线验证、快速操作
- 🔧 **设备管理模块** - 设备注册、状态监控、远程控制
- ❤️ **系统监控模块** - 健康检查、组件状态、性能指标

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

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      if (authService.isAuthenticated()) {
        const user = authService.getCurrentUser()
        setUser(user)
      }
      setLoading(false)
    }
    
    initAuth()
  }, [])

  const login = async (credentials) => {
    const result = await authService.login(credentials)
    if (result.success) {
      setUser(result.data)
    }
    return result
  }

  const logout = () => {
    authService.logout()
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
    throw new Error('useAuth must be used within an AuthProvider')
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

#### 场景管理服务 ⭐ NEW
```javascript
// services/scenarioService.js
import httpClient from '../utils/httpClient'

class ScenarioService {
  // 场景模板管理
  async getScenarioTemplates(params = {}) {
    try {
      const response = await httpClient.client.get('/config/scenarios/templates', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async createScenarioTemplate(templateData) {
    try {
      const response = await httpClient.client.post('/config/scenarios/templates', templateData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 场景实例管理
  async getScenarioInstances(params = {}) {
    try {
      const response = await httpClient.client.get('/config/scenarios/instances', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async createScenarioInstance(instanceData) {
    try {
      const response = await httpClient.client.post('/config/scenarios/instances', instanceData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 场景智能路由
  async routeScenario(routingData) {
    try {
      const response = await httpClient.client.post('/config/scenarios/route', routingData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 场景执行管理
  async getScenarioExecutions(params = {}) {
    try {
      const response = await httpClient.client.get('/config/scenarios/executions', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async cancelScenarioExecution(executionId) {
    try {
      const response = await httpClient.client.post(`/config/scenarios/executions/${executionId}/cancel`)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  handleError(error) {
    return { success: false, error: error.response?.data?.detail || '操作失败' }
  }
}

export default new ScenarioService()
```

#### 门岗管理服务 ⭐ NEW
```javascript
// services/gateService.js
import httpClient from '../utils/httpClient'

class GateService {
  // 获取今日到访访客
  async getTodayArrivals(gateId = '') {
    try {
      const params = gateId ? { gate_id: gateId } : {}
      const response = await httpClient.client.get('/gate/arrivals/today', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 访客身份验证
  async verifyVisitor(visitorId, verificationData) {
    try {
      const response = await httpClient.client.post(`/gate/visitors/${visitorId}/verify`, verificationData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 访客入园登记
  async entryVisitor(visitorId, entryData) {
    try {
      const response = await httpClient.client.post(`/gate/visitors/${visitorId}/entry`, entryData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 获取园区内访客状态
  async getInParkVisitors(gateId = '') {
    try {
      const params = gateId ? { gate_id: gateId } : {}
      const response = await httpClient.client.get('/gate/visitors/in-park', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 获取离线验证缓存
  async getOfflineCache(gateId) {
    try {
      const response = await httpClient.client.get('/gate/cache/today-visitors', {
        params: { gate_id: gateId }
      })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  handleError(error) {
    return { success: false, error: error.response?.data?.detail || '操作失败' }
  }
}

export default new GateService()
```

#### 前台管理服务 ⭐ NEW
```javascript
// services/receptionService.js
import httpClient from '../utils/httpClient'

class ReceptionService {
  // 前台访客签到
  async visitorCheckin(checkinData) {
    try {
      const response = await httpClient.client.post('/reception/visitor-checkin', checkinData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 通知被访人
  async notifyHost(notificationData) {
    try {
      const response = await httpClient.client.post('/reception/notify-host', notificationData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 会议室管理
  async createMeetingRoom(roomData) {
    try {
      const response = await httpClient.client.post('/reception/meeting-rooms', roomData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  async getMeetingRooms(params = {}) {
    try {
      const response = await httpClient.client.get('/reception/meeting-rooms', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 获取等候区域状态
  async getWaitingAreaStatus() {
    try {
      const response = await httpClient.client.get('/reception/waiting-area/status')
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 访客服务反馈
  async submitFeedback(feedbackData) {
    try {
      const response = await httpClient.client.post('/reception/services/feedback', feedbackData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  handleError(error) {
    return { success: false, error: error.response?.data?.detail || '操作失败' }
  }
}

export default new ReceptionService()
```

#### 移动端服务 ⭐ NEW
```javascript
// services/mobileService.js
import httpClient from '../utils/httpClient'

class MobileService {
  // 门岗移动端数据同步
  async syncGateData(deviceId, lastSync = null) {
    try {
      const params = { device_id: deviceId }
      if (lastSync) params.last_sync = lastSync
      
      const response = await httpClient.client.get('/mobile/gate/sync', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 移动端二维码验证
  async verifyQRCode(qrData) {
    try {
      const response = await httpClient.client.post('/mobile/gate/verify-qr', qrData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 移动端快速签到
  async quickCheckin(checkinData) {
    try {
      const response = await httpClient.client.post('/mobile/reception/quick-checkin', checkinData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 获取离线缓存数据
  async getOfflineCache(deviceId) {
    try {
      const response = await httpClient.client.get('/mobile/offline/visitor-cache', {
        params: { device_id: deviceId }
      })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  handleError(error) {
    return { success: false, error: error.response?.data?.detail || '操作失败' }
  }
}

export default new MobileService()
```

#### 设备管理服务 ⭐ NEW
```javascript
// services/deviceService.js
import httpClient from '../utils/httpClient'

class DeviceService {
  // 设备注册
  async registerDevice(deviceData) {
    try {
      const response = await httpClient.client.post('/devices/register', deviceData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 获取设备状态
  async getDeviceStatus(deviceId) {
    try {
      const response = await httpClient.client.get(`/devices/${deviceId}/status`)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 设备远程控制
  async controlDevice(deviceId, controlData) {
    try {
      const response = await httpClient.client.post(`/devices/${deviceId}/control`, controlData)
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  // 获取设备列表
  async getDevices(params = {}) {
    try {
      const response = await httpClient.client.get('/devices/', { params })
      return { success: true, data: response.data }
    } catch (error) {
      return this.handleError(error)
    }
  }

  handleError(error) {
    return { success: false, error: error.response?.data?.detail || '操作失败' }
  }
}

export default new DeviceService()
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

### React移动端组件示例

#### 访客列表组件 (React Hooks)
```jsx
// components/VisitorList.jsx
import React, { useState, useEffect, useMemo } from 'react'
import visitorService from '../services/visitorService'

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

  const totalPages = useMemo(() => 
    Math.ceil(pagination.total / pagination.pageSize),
    [pagination.total, pagination.pageSize]
  )

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
        setPagination(prev => ({ ...prev, total: result.data.total }))
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

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
    setPagination(prev => ({ ...prev, page: 1 }))
  }

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }

  useEffect(() => {
    loadVisitors()
  }, [pagination.page, filters])

  return (
    <div className="visitor-list">
      <div className="filters">
        <select 
          value={filters.status} 
          onChange={(e) => handleFilterChange({ status: e.target.value })}
        >
          <option value="">全部状态</option>
          <option value="pending">待审批</option>
          <option value="approved">已审批</option>
          <option value="checked_in">已签到</option>
          <option value="checked_out">已签出</option>
        </select>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
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
                  <td>{formatDate(visitor.expected_date)}</td>
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
      )}

      <div className="pagination">
        <button 
          disabled={pagination.page === 1}
          onClick={() => handlePageChange(pagination.page - 1)}
        >
          上一页
        </button>
        <span>第 {pagination.page} 页，共 {totalPages} 页</span>
        <button 
          disabled={pagination.page >= totalPages}
          onClick={() => handlePageChange(pagination.page + 1)}
        >
          下一页
        </button>
      </div>
    </div>
  )
}

export default VisitorList
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

## 🆕 v3.0新功能UI组件

### 场景管理组件 ⭐ NEW

#### 场景模板管理组件
```jsx
// components/ScenarioTemplates.jsx
import React, { useState, useEffect } from 'react'
import scenarioService from '../services/scenarioService'

const ScenarioTemplates = () => {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState(null)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    setLoading(true)
    try {
      const result = await scenarioService.getScenarioTemplates()
      if (result.success) {
        setTemplates(result.data.items || [])
      }
    } catch (error) {
      console.error('加载场景模板失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTemplate = () => {
    setEditingTemplate(null)
    setModalVisible(true)
  }

  const handleEditTemplate = (template) => {
    setEditingTemplate(template)
    setModalVisible(true)
  }

  const handleSaveTemplate = async (templateData) => {
    try {
      const result = editingTemplate
        ? await scenarioService.updateScenarioTemplate(editingTemplate.id, templateData)
        : await scenarioService.createScenarioTemplate(templateData)

      if (result.success) {
        setModalVisible(false)
        loadTemplates()
        // 显示成功消息
      }
    } catch (error) {
      console.error('保存场景模板失败:', error)
    }
  }

  return (
    <div className="scenario-templates">
      <div className="header">
        <h2>场景模板管理</h2>
        <button onClick={handleCreateTemplate} className="btn-primary">
          创建新模板
        </button>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="templates-grid">
          {templates.map(template => (
            <div key={template.id} className="template-card">
              <div className="template-header">
                <h3>{template.template_name}</h3>
                <span className={`status ${template.is_active ? 'active' : 'inactive'}`}>
                  {template.is_active ? '启用' : '禁用'}
                </span>
              </div>
              
              <div className="template-info">
                <p><strong>编码:</strong> {template.template_code}</p>
                <p><strong>分类:</strong> {template.template_category}</p>
                <p><strong>描述:</strong> {template.template_description}</p>
              </div>

              <div className="template-features">
                <h4>场景特性:</h4>
                <ul>
                  {Object.entries(template.scenario_features || {}).map(([key, value]) => (
                    <li key={key}>
                      {key}: {value ? '是' : '否'}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="template-actions">
                <button onClick={() => handleEditTemplate(template)} className="btn-secondary">
                  编辑
                </button>
                <button className="btn-info">查看实例</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {modalVisible && (
        <ScenarioTemplateModal
          template={editingTemplate}
          onSave={handleSaveTemplate}
          onCancel={() => setModalVisible(false)}
        />
      )}
    </div>
  )
}

export default ScenarioTemplates
```

#### 场景智能路由组件
```jsx
// components/ScenarioRouter.jsx
import React, { useState } from 'react'
import scenarioService from '../services/scenarioService'

const ScenarioRouter = () => {
  const [routingData, setRoutingData] = useState({
    context: {},
    entity_type: 'visitor',
    entity_id: '',
    auto_execute: false
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleRoute = async () => {
    setLoading(true)
    try {
      const response = await scenarioService.routeScenario(routingData)
      if (response.success) {
        setResult(response.data)
      }
    } catch (error) {
      console.error('场景路由失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const addContextField = () => {
    const key = prompt('请输入上下文字段名:')
    const value = prompt('请输入上下文字段值:')
    if (key && value) {
      setRoutingData(prev => ({
        ...prev,
        context: { ...prev.context, [key]: value }
      }))
    }
  }

  return (
    <div className="scenario-router">
      <h2>场景智能路由</h2>
      
      <div className="routing-form">
        <div className="form-group">
          <label>实体类型:</label>
          <select
            value={routingData.entity_type}
            onChange={(e) => setRoutingData(prev => ({ ...prev, entity_type: e.target.value }))}
          >
            <option value="visitor">访客</option>
            <option value="employee">员工</option>
            <option value="meeting">会议</option>
          </select>
        </div>

        <div className="form-group">
          <label>实体ID:</label>
          <input
            type="text"
            value={routingData.entity_id}
            onChange={(e) => setRoutingData(prev => ({ ...prev, entity_id: e.target.value }))}
            placeholder="请输入实体ID"
          />
        </div>

        <div className="form-group">
          <label>上下文信息:</label>
          <div className="context-fields">
            {Object.entries(routingData.context).map(([key, value]) => (
              <div key={key} className="context-field">
                <span>{key}: {value}</span>
                <button onClick={() => {
                  const newContext = { ...routingData.context }
                  delete newContext[key]
                  setRoutingData(prev => ({ ...prev, context: newContext }))
                }}>删除</button>
              </div>
            ))}
            <button onClick={addContextField} className="btn-secondary">
              添加上下文字段
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={routingData.auto_execute}
              onChange={(e) => setRoutingData(prev => ({ ...prev, auto_execute: e.target.checked }))}
            />
            自动执行匹配的场景
          </label>
        </div>

        <button onClick={handleRoute} disabled={loading} className="btn-primary">
          {loading ? '路由中...' : '开始路由'}
        </button>
      </div>

      {result && (
        <div className="routing-result">
          <h3>路由结果:</h3>
          <div className="matched-scenario">
            <h4>匹配的场景:</h4>
            <p><strong>实例名称:</strong> {result.matched_scenario?.instance_name}</p>
            <p><strong>匹配度:</strong> {(result.matched_scenario?.match_score * 100).toFixed(1)}%</p>
          </div>

          {result.execution_result && (
            <div className="execution-result">
              <h4>执行结果:</h4>
              <p><strong>执行ID:</strong> {result.execution_result.execution_id}</p>
              <p><strong>状态:</strong> {result.execution_result.status}</p>
              <p><strong>进度:</strong> {result.execution_result.steps_completed}/{result.execution_result.steps_total}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ScenarioRouter
```

### 门岗管理组件 ⭐ NEW

#### 门岗今日到访组件
```jsx
// components/GateTodayArrivals.jsx
import React, { useState, useEffect } from 'react'
import gateService from '../services/gateService'

const GateTodayArrivals = ({ gateId = 'GATE001' }) => {
  const [arrivals, setArrivals] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadTodayArrivals()
    // 每30秒刷新一次
    const interval = setInterval(loadTodayArrivals, 30000)
    return () => clearInterval(interval)
  }, [gateId])

  const loadTodayArrivals = async () => {
    setLoading(true)
    try {
      const result = await gateService.getTodayArrivals(gateId)
      if (result.success) {
        setArrivals(result.data.arrivals || [])
      }
    } catch (error) {
      console.error('加载今日到访失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyVisitor = async (visitor) => {
    try {
      const verificationData = {
        verification_method: 'manual_entry',
        gate_id: gateId,
        verification_data: {
          manual_verification: true,
          operator_id: 'current_user'
        }
      }

      const result = await gateService.verifyVisitor(visitor.visitor_id, verificationData)
      if (result.success) {
        // 更新访客状态
        loadTodayArrivals()
        alert('验证成功')
      }
    } catch (error) {
      console.error('验证失败:', error)
      alert('验证失败')
    }
  }

  const filteredArrivals = arrivals.filter(visitor =>
    visitor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    visitor.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    visitor.pass_code.includes(searchTerm)
  )

  return (
    <div className="gate-today-arrivals">
      <div className="header">
        <h2>今日到访访客 ({gateId})</h2>
        <div className="search-box">
          <input
            type="text"
            placeholder="搜索访客姓名、公司或通行码..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button onClick={loadTodayArrivals} className="btn-refresh">
          刷新
        </button>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <div className="arrivals-list">
          {filteredArrivals.length === 0 ? (
            <div className="no-data">今日暂无预约访客</div>
          ) : (
            filteredArrivals.map(visitor => (
              <div key={visitor.visitor_id} className="visitor-card">
                <div className="visitor-info">
                  <div className="basic-info">
                    <h3>{visitor.name}</h3>
                    <p className="company">{visitor.company}</p>
                    <p className="pass-code">通行码: {visitor.pass_code}</p>
                    <p className="phone">电话: {visitor.phone_masked}</p>
                  </div>
                  
                  <div className="visit-info">
                    <p><strong>访问时间:</strong> {visitor.visit_time}</p>
                    <p><strong>被访人:</strong> {visitor.host_employee}</p>
                    <p><strong>可访问区域:</strong> {visitor.areas.join(', ')}</p>
                  </div>
                </div>

                <div className="visitor-status">
                  <span className={`status-badge ${visitor.status}`}>
                    {visitor.status === 'approved' ? '已审批' : 
                     visitor.status === 'checked_in' ? '已入园' : '待处理'}
                  </span>
                </div>

                <div className="visitor-actions">
                  {visitor.status === 'approved' && (
                    <button 
                      onClick={() => handleVerifyVisitor(visitor)}
                      className="btn-primary"
                    >
                      验证入园
                    </button>
                  )}
                  <button className="btn-secondary">查看详情</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default GateTodayArrivals
```

#### 访客验证组件
```jsx
// components/VisitorVerification.jsx
import React, { useState } from 'react'
import gateService from '../services/gateService'

const VisitorVerification = ({ gateId = 'GATE001' }) => {
  const [verificationMethod, setVerificationMethod] = useState('qr_code')
  const [verificationData, setVerificationData] = useState('')
  const [verifyResult, setVerifyResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleVerification = async () => {
    if (!verificationData.trim()) {
      alert('请输入验证数据')
      return
    }

    setLoading(true)
    try {
      let requestData = {
        verification_method: verificationMethod,
        gate_id: gateId,
        verification_data: {}
      }

      // 根据验证方式构造不同的数据
      switch (verificationMethod) {
        case 'qr_code':
          requestData.verification_data.qr_content = verificationData
          requestData.verification_data.scan_timestamp = new Date().toISOString()
          break
        case 'id_card':
          requestData.verification_data.id_card_number = verificationData
          break
        case 'manual_entry':
          requestData.verification_data.visitor_name = verificationData
          break
        default:
          requestData.verification_data.input_data = verificationData
      }

      // 这里需要从输入中解析访客ID，简化示例直接使用固定值
      const visitorId = extractVisitorIdFromInput(verificationData)
      
      const result = await gateService.verifyVisitor(visitorId, requestData)
      setVerifyResult(result)
      
      if (result.success && result.data.verification_result.valid) {
        // 验证成功，可以进行入园登记
        setVerificationData('')
      }
    } catch (error) {
      console.error('验证失败:', error)
      setVerifyResult({ success: false, error: '验证失败' })
    } finally {
      setLoading(false)
    }
  }

  const extractVisitorIdFromInput = (input) => {
    // 简化的访客ID提取逻辑
    // 实际应用中可能需要从二维码或其他数据中解析
    if (input.includes('VISITOR:')) {
      return input.split(':')[1]?.split(':')[0] || '1'
    }
    return '1' // 默认值
  }

  const handleEntry = async () => {
    if (!verifyResult?.data?.visitor_id) return

    try {
      const entryData = {
        gate_id: gateId,
        badge_number: `V${Date.now().toString().slice(-3)}`,
        temperature_check: 36.5,
        health_check_passed: true
      }

      const result = await gateService.entryVisitor(verifyResult.data.visitor_id, entryData)
      if (result.success) {
        alert('入园登记成功')
        setVerifyResult(null)
      }
    } catch (error) {
      console.error('入园登记失败:', error)
    }
  }

  return (
    <div className="visitor-verification">
      <h2>访客身份验证</h2>
      
      <div className="verification-form">
        <div className="form-group">
          <label>验证方式:</label>
          <select
            value={verificationMethod}
            onChange={(e) => setVerificationMethod(e.target.value)}
          >
            <option value="qr_code">二维码扫描</option>
            <option value="id_card">身份证读取</option>
            <option value="face_recognition">人脸识别</option>
            <option value="manual_entry">手动录入</option>
            <option value="sms_otp">短信验证码</option>
          </select>
        </div>

        <div className="form-group">
          <label>验证数据:</label>
          <textarea
            value={verificationData}
            onChange={(e) => setVerificationData(e.target.value)}
            placeholder={
              verificationMethod === 'qr_code' ? '请扫描或输入二维码内容' :
              verificationMethod === 'id_card' ? '请输入身份证号码' :
              verificationMethod === 'manual_entry' ? '请输入访客姓名' :
              '请输入验证数据'
            }
            rows={3}
          />
        </div>

        <button 
          onClick={handleVerification}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? '验证中...' : '开始验证'}
        </button>
      </div>

      {verifyResult && (
        <div className={`verification-result ${verifyResult.success ? 'success' : 'error'}`}>
          <h3>验证结果</h3>
          
          {verifyResult.success ? (
            verifyResult.data.verification_result.valid ? (
              <div className="success-result">
                <p className="status">✅ 验证成功</p>
                <div className="visitor-details">
                  <h4>访客信息:</h4>
                  <p><strong>姓名:</strong> {verifyResult.data.visitor_info.name}</p>
                  <p><strong>公司:</strong> {verifyResult.data.visitor_info.company}</p>
                  <p><strong>访问目的:</strong> {verifyResult.data.visitor_info.visit_purpose}</p>
                  <p><strong>验证方式:</strong> {verifyResult.data.verification_result.verification_method}</p>
                  <p><strong>安全等级:</strong> {verifyResult.data.verification_result.security_level}</p>
                </div>
                
                {verifyResult.data.next_action === 'allow_entry' && (
                  <button onClick={handleEntry} className="btn-success">
                    允许入园
                  </button>
                )}
              </div>
            ) : (
              <div className="failed-result">
                <p className="status">❌ 验证失败</p>
                <p>原因: 访客信息不匹配或无效</p>
              </div>
            )
          ) : (
            <div className="error-result">
              <p className="status">❌ 验证错误</p>
              <p>{verifyResult.error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default VisitorVerification
```

### 前台管理组件 ⭐ NEW

#### 前台签到组件
```jsx
// components/ReceptionCheckin.jsx
import React, { useState } from 'react'
import receptionService from '../services/receptionService'

const ReceptionCheckin = () => {
  const [checkinData, setCheckinData] = useState({
    visitor_id: '',
    reception_desk_id: 'RECEPTION001',
    checkin_method: 'manual_entry',
    waiting_area_id: 'WAIT_AREA_A',
    services_provided: [],
    special_requirements: []
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [checkinResult, setCheckinResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const availableServices = [
    '身份验证', '访客登记', '等候安排', '会议室预订', 
    '翻译服务', '饮料提供', '资料打印'
  ]

  const handleServiceToggle = (service) => {
    setCheckinData(prev => ({
      ...prev,
      services_provided: prev.services_provided.includes(service)
        ? prev.services_provided.filter(s => s !== service)
        : [...prev.services_provided, service]
    }))
  }

  const handleCheckin = async () => {
    if (!checkinData.visitor_id) {
      alert('请输入访客ID')
      return
    }

    setLoading(true)
    try {
      const result = await receptionService.visitorCheckin(checkinData)
      if (result.success) {
        setCheckinResult(result.data)
        // 重置表单
        setCheckinData(prev => ({ ...prev, visitor_id: '', services_provided: [] }))
        setSearchTerm('')
      }
    } catch (error) {
      console.error('签到失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNotifyHost = async () => {
    if (!checkinResult?.visitor_id) return

    try {
      const notificationData = {
        visitor_id: checkinResult.visitor_id,
        employee_id: 1, // 这里应该从访客信息中获取
        notification_channels: ['wechat', 'email'],
        notification_content: {
          title: '访客到访通知',
          message: `您的访客已在前台完成签到，请前往接待`,
          visitor_info: {
            name: '访客姓名', // 从实际数据获取
            company: '访客公司',
            purpose: '访问目的'
          }
        }
      }

      const result = await receptionService.notifyHost(notificationData)
      if (result.success) {
        alert('通知发送成功')
      }
    } catch (error) {
      console.error('通知发送失败:', error)
    }
  }

  return (
    <div className="reception-checkin">
      <h2>前台访客签到</h2>
      
      <div className="checkin-form">
        <div className="visitor-search">
          <label>搜索访客:</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="输入访客姓名、手机号或通行码搜索"
          />
          <button className="btn-secondary">搜索</button>
        </div>

        <div className="form-group">
          <label>访客ID:</label>
          <input
            type="text"
            value={checkinData.visitor_id}
            onChange={(e) => setCheckinData(prev => ({ ...prev, visitor_id: e.target.value }))}
            placeholder="请输入访客ID"
          />
        </div>

        <div className="form-group">
          <label>签到方式:</label>
          <select
            value={checkinData.checkin_method}
            onChange={(e) => setCheckinData(prev => ({ ...prev, checkin_method: e.target.value }))}
          >
            <option value="qr_scan">二维码扫描</option>
            <option value="face_recognition">人脸识别</option>
            <option value="id_card">身份证</option>
            <option value="manual_entry">手动录入</option>
            <option value="self_service">自助服务</option>
          </select>
        </div>

        <div className="form-group">
          <label>等候区域:</label>
          <select
            value={checkinData.waiting_area_id}
            onChange={(e) => setCheckinData(prev => ({ ...prev, waiting_area_id: e.target.value }))}
          >
            <option value="WAIT_AREA_A">A区等候区</option>
            <option value="WAIT_AREA_B">B区等候区</option>
            <option value="VIP_AREA">VIP等候区</option>
          </select>
        </div>

        <div className="form-group">
          <label>提供的服务:</label>
          <div className="services-grid">
            {availableServices.map(service => (
              <label key={service} className="service-checkbox">
                <input
                  type="checkbox"
                  checked={checkinData.services_provided.includes(service)}
                  onChange={() => handleServiceToggle(service)}
                />
                {service}
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label>特殊需求:</label>
          <textarea
            value={checkinData.special_requirements.join('\n')}
            onChange={(e) => setCheckinData(prev => ({
              ...prev,
              special_requirements: e.target.value.split('\n').filter(req => req.trim())
            }))}
            placeholder="请输入特殊需求，每行一项"
            rows={3}
          />
        </div>

        <button
          onClick={handleCheckin}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? '签到中...' : '完成签到'}
        </button>
      </div>

      {checkinResult && (
        <div className="checkin-result">
          <h3>签到成功</h3>
          <div className="result-info">
            <p><strong>签到ID:</strong> {checkinResult.checkin_id}</p>
            <p><strong>签到时间:</strong> {new Date(checkinResult.checkin_time).toLocaleString()}</p>
            <p><strong>访客胸牌:</strong> {checkinResult.visitor_badge}</p>
            <p><strong>等候区域:</strong> {checkinResult.waiting_area}</p>
            <p><strong>预计等待时间:</strong> {checkinResult.estimated_wait_time}分钟</p>
          </div>

          <div className="next-steps">
            <h4>后续步骤:</h4>
            <ul>
              {checkinResult.next_steps?.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ul>
          </div>

          <div className="result-actions">
            <button onClick={handleNotifyHost} className="btn-info">
              通知被访人
            </button>
            <button className="btn-secondary">打印访客胸牌</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReceptionCheckin
```

### 移动端组件 ⭐ NEW (React Native示例)

#### 移动门岗验证组件
```jsx
// components/mobile/MobileGateVerification.jsx (React Native)
import React, { useState, useEffect } from 'react'
import { View, Text, TouchableOpacity, Alert, TextInput } from 'react-native'
import { Camera } from 'expo-camera'
import mobileService from '../services/mobileService'

const MobileGateVerification = ({ deviceId = 'MOBILE_GATE_001' }) => {
  const [hasPermission, setHasPermission] = useState(null)
  const [scanned, setScanned] = useState(false)
  const [verificationResult, setVerificationResult] = useState(null)
  const [manualInput, setManualInput] = useState('')
  const [mode, setMode] = useState('camera') // 'camera' or 'manual'

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync()
      setHasPermission(status === 'granted')
    })()
  }, [])

  const handleBarCodeScanned = async ({ type, data }) => {
    if (scanned) return
    
    setScanned(true)
    await verifyQRCode(data)
  }

  const verifyQRCode = async (qrContent) => {
    try {
      const qrData = {
        qr_content: qrContent,
        device_id: deviceId,
        location: 'main_gate',
        verification_method: 'mobile_app'
      }

      const result = await mobileService.verifyQRCode(qrData)
      setVerificationResult(result)
      
      if (result.success && result.data.verification_result.valid) {
        Alert.alert('验证成功', `访客 ${result.data.verification_result.visitor_name} 可以入园`)
      } else {
        Alert.alert('验证失败', '访客信息无效或已过期')
      }
    } catch (error) {
      Alert.alert('验证错误', error.message)
    }
  }

  const handleManualVerification = async () => {
    if (!manualInput.trim()) {
      Alert.alert('提示', '请输入验证码')
      return
    }
    
    await verifyQRCode(manualInput)
    setManualInput('')
  }

  if (hasPermission === null) {
    return <Text>请求相机权限中...</Text>
  }
  
  if (hasPermission === false) {
    return <Text>无相机权限</Text>
  }

  return (
    <View style={{ flex: 1 }}>
      <View style={{ flexDirection: 'row', padding: 10 }}>
        <TouchableOpacity
          style={[styles.modeButton, mode === 'camera' && styles.activeModeButton]}
          onPress={() => setMode('camera')}
        >
          <Text>扫码验证</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.modeButton, mode === 'manual' && styles.activeModeButton]}
          onPress={() => setMode('manual')}
        >
          <Text>手动输入</Text>
        </TouchableOpacity>
      </View>

      {mode === 'camera' ? (
        <View style={{ flex: 1 }}>
          <Camera
            style={{ flex: 1 }}
            type={Camera.Constants.Type.back}
            onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
          />
          
          {scanned && (
            <TouchableOpacity
              style={styles.rescanButton}
              onPress={() => setScanned(false)}
            >
              <Text style={styles.rescanButtonText}>重新扫描</Text>
            </TouchableOpacity>
          )}
        </View>
      ) : (
        <View style={styles.manualInputContainer}>
          <TextInput
            style={styles.manualInput}
            value={manualInput}
            onChangeText={setManualInput}
            placeholder="请输入访客通行码或二维码内容"
            multiline
          />
          
          <TouchableOpacity
            style={styles.verifyButton}
            onPress={handleManualVerification}
          >
            <Text style={styles.verifyButtonText}>验证</Text>
          </TouchableOpacity>
        </View>
      )}

      {verificationResult && (
        <View style={styles.resultContainer}>
          {verificationResult.success ? (
            <View style={styles.successResult}>
              <Text style={styles.resultTitle}>✅ 验证成功</Text>
              <Text>访客: {verificationResult.data.verification_result.visitor_name}</Text>
              <Text>公司: {verificationResult.data.verification_result.company}</Text>
              <Text>目的: {verificationResult.data.verification_result.visit_purpose}</Text>
            </View>
          ) : (
            <View style={styles.errorResult}>
              <Text style={styles.resultTitle}>❌ 验证失败</Text>
              <Text>{verificationResult.error}</Text>
            </View>
          )}
        </View>
      )}
    </View>
  )
}

const styles = {
  modeButton: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
    margin: 5,
    borderRadius: 5
  },
  activeModeButton: {
    backgroundColor: '#007bff'
  },
  manualInputContainer: {
    flex: 1,
    padding: 20
  },
  manualInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    height: 100,
    textAlignVertical: 'top',
    marginBottom: 20
  },
  verifyButton: {
    backgroundColor: '#007bff',
    padding: 15,
    alignItems: 'center',
    borderRadius: 5
  },
  verifyButtonText: {
    color: 'white',
    fontWeight: 'bold'
  },
  rescanButton: {
    position: 'absolute',
    bottom: 50,
    alignSelf: 'center',
    backgroundColor: '#007bff',
    padding: 15,
    borderRadius: 5
  },
  rescanButtonText: {
    color: 'white',
    fontWeight: 'bold'
  },
  resultContainer: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#ccc'
  },
  successResult: {
    backgroundColor: '#d4edda',
    padding: 15,
    borderRadius: 5
  },
  errorResult: {
    backgroundColor: '#f8d7da',
    padding: 15,
    borderRadius: 5
  },
  resultTitle: {
    fontWeight: 'bold',
    marginBottom: 10
  }
}

export default MobileGateVerification
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
- **技术栈**: React, React Native, 小程序
- **问题反馈**: 通过项目Issue提交

### 相关文档
- [后端API完整参考手册](./Backend_API_Reference.md)
- [后端系统架构概览](./Backend_System_Architecture.md)
- [后端开发者指南](./Backend_Developer_Guide.md) 