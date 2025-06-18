# 前端功能需求规格文档

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **维护者**: 产品经理AI
- **适用角色**: 前端开发者、UI/UX设计师、测试工程师
- **依赖文档**: PRD.md, Backend_API_Reference.md, Frontend_Integration_Guide.md

## 🎯 前端应用概述

访客管理系统包含**3个前端应用**，分别服务于不同的用户场景：

1. **管理端 (React)** - 企业管理人员使用的Web管理平台
2. **H5端 (Vue.js)** - 访客使用的移动端预约平台  
3. **设备端 (Web App)** - 现场签到设备使用的操作界面

## 🎨 设计系统规范

### 视觉风格
- **设计语言**: 现代简约风格，注重功能性和易用性
- **主色调**: 企业蓝 (#1890FF)，辅色绿色 (#52C41A)，警告色橙色 (#FA8C16)
- **字体**: 中文使用PingFang SC，英文使用San Francisco/Roboto
- **间距**: 8px基础间距，倍数间距系统

### 组件规范
- **管理端**: Ant Design 5.x组件库
- **H5端**: Vant 4.x组件库
- **设备端**: 自定义组件，针对触控优化

## 📱 **一、管理端 (React) 详细设计**

### 技术栈确认
```json
{
  "framework": "React 18.2+",
  "language": "TypeScript 5.0+",
  "ui_library": "Ant Design 5.x",
  "routing": "React Router v6",
  "state_management": "Redux Toolkit + RTK Query",
  "http_client": "Axios",
  "build_tool": "Vite",
  "styling": "Less + CSS Modules"
}
```

### 页面架构设计

#### 1.1 布局组件设计
**文件路径**: `src/layouts/MainLayout.tsx`

**布局结构**:
```tsx
<Layout>
  <Header>
    <Logo />
    <UserProfile />
    <NotificationCenter />
  </Header>
  <Layout>
    <Sider>
      <Navigation />
    </Sider>
    <Content>
      <Breadcrumb />
      <PageContent />
    </Content>
  </Layout>
</Layout>
```

**响应式断点**:
- Desktop: ≥1200px - 完整侧边栏
- Tablet: 768px-1199px - 收缩侧边栏
- Mobile: <768px - 抽屉式侧边栏

#### 1.2 导航菜单设计
**功能模块菜单**:
```typescript
const menuItems = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: '仪表板',
    path: '/dashboard'
  },
  {
    key: 'visitors',
    icon: <UserOutlined />,
    label: '访客管理',
    children: [
      { key: 'visitor-list', label: '访客列表', path: '/visitors/list' },
      { key: 'visitor-approval', label: '审批中心', path: '/visitors/approval' },
      { key: 'visitor-checkin', label: '签到管理', path: '/visitors/checkin' }
    ]
  },
  {
    key: 'organization',
    icon: <TeamOutlined />,
    label: '组织管理',
    children: [
      { key: 'employees', label: '员工管理', path: '/organization/employees' },
      { key: 'departments', label: '部门管理', path: '/organization/departments' },
      { key: 'sites', label: '站点管理', path: '/organization/sites' }
    ]
  },
  {
    key: 'config',
    icon: <SettingOutlined />,
    label: '配置中心',
    children: [
      { key: 'forms', label: '表单配置', path: '/config/forms' },
      { key: 'workflows', label: '工作流配置', path: '/config/workflows' },
      { key: 'spatial', label: '空间配置', path: '/config/spatial' },
      { key: 'rules', label: '业务规则', path: '/config/rules' }
    ]
  }
]
```

### 核心页面设计

#### 1.3 仪表板页面 (`/dashboard`)
**对应API**: `GET /api/v1/dashboard/stats`

**功能需求**:
- 访客统计卡片：今日访客、待审批、已签到、异常访客
- 实时访客动态列表 
- 访客状态分布饼图
- 近7天访客趋势图

**UI组件结构**:
```tsx
<Dashboard>
  <Row gutter={16}>
    <Col span={6}><StatCard title="今日访客" value={stats.todayVisitors} /></Col>
    <Col span={6}><StatCard title="待审批" value={stats.pendingApproval} /></Col>
    <Col span={6}><StatCard title="已签到" value={stats.checkedIn} /></Col>
    <Col span={6}><StatCard title="异常访客" value={stats.abnormal} /></Col>
  </Row>
  <Row gutter={16}>
    <Col span={12}><VisitorTrendChart data={stats.trendData} /></Col>
    <Col span={12}><VisitorStatusPieChart data={stats.statusData} /></Col>
  </Row>
  <VisitorRealtimeList />
</Dashboard>
```

#### 1.4 访客列表页面 (`/visitors/list`)
**对应API**: `GET /api/v1/visitors/`

**核心功能**:
- 访客数据表格（支持排序、分页）
- 高级筛选器
- 批量操作
- 快速搜索
- 数据导出

**筛选器设计**:
```tsx
<FilterForm>
  <Row gutter={16}>
    <Col span={6}>
      <Select placeholder="访客状态">
        <Option value="pending">待审批</Option>
        <Option value="approved">已批准</Option>
        <Option value="checked_in">已签到</Option>
        <Option value="checked_out">已签出</Option>
      </Select>
    </Col>
    <Col span={6}>
      <RangePicker placeholder={['开始日期', '结束日期']} />
    </Col>
    <Col span={6}>
      <Select placeholder="接待员工" showSearch />
    </Col>
    <Col span={6}>
      <Input placeholder="搜索姓名/电话" />
    </Col>
  </Row>
</FilterForm>
```

**表格列设计**:
```typescript
const columns = [
  { title: '访客姓名', dataIndex: 'name', sorter: true },
  { title: '联系电话', dataIndex: 'phone_number' },
  { title: '公司名称', dataIndex: 'company_name' },
  { title: '访问目的', dataIndex: 'purpose', render: (purpose) => purposeMap[purpose] },
  { title: '接待员工', dataIndex: 'employee_name' },
  { title: '预约时间', dataIndex: 'expected_date', sorter: true },
  { title: '状态', dataIndex: 'status', render: (status) => <StatusTag status={status} /> },
  { title: '操作', render: (record) => <ActionButtons record={record} /> }
]
```

#### 1.5 访客审批页面 (`/visitors/approval`)
**对应API**: `PUT /api/v1/visitors/{visitor_id}/approve`, `PUT /api/v1/visitors/{visitor_id}/reject`

**核心功能**:
- 待审批访客列表
- 访客详情查看
- 一键批准/拒绝
- 批量审批
- 审批意见编辑

**审批卡片设计**:
```tsx
<ApprovalCard>
  <Card.Meta
    avatar={<Avatar src={visitor.avatar} />}
    title={visitor.name}
    description={`${visitor.company_name} | ${visitor.phone_number}`}
  />
  <Descriptions size="small">
    <Descriptions.Item label="访问目的">{visitor.purpose}</Descriptions.Item>
    <Descriptions.Item label="预约时间">{visitor.expected_date}</Descriptions.Item>
    <Descriptions.Item label="接待员工">{visitor.employee_name}</Descriptions.Item>
  </Descriptions>
  <Space>
    <Button type="primary" onClick={() => approve(visitor.id)}>批准</Button>
    <Button danger onClick={() => reject(visitor.id)}>拒绝</Button>
  </Space>
</ApprovalCard>
```

#### 1.6 员工管理页面 (`/organization/employees`)
**对应API**: 员工管理相关5个API接口

**核心功能**:
- 员工列表展示
- 员工信息CRUD
- 部门分配
- 角色权限设置
- 员工状态管理

#### 1.7 配置中心页面群
**表单配置页面** (`/config/forms`):
- 拖拽式表单设计器
- 字段属性配置面板
- 表单预览功能
- 表单版本管理

**工作流配置页面** (`/config/workflows`):
- 可视化流程设计器
- 审批节点配置
- 条件分支设置
- 流程测试功能

## 📱 **二、H5端 (Vue.js) 详细设计**

### 技术栈确认
```json
{
  "framework": "Vue 3.3+",
  "language": "TypeScript 5.0+",
  "ui_library": "Vant 4.x",
  "routing": "Vue Router v4",
  "state_management": "Pinia",
  "http_client": "Axios",
  "build_tool": "Vite",
  "styling": "SCSS"
}
```

### 页面设计

#### 2.1 访客预约页面 (`/book`)
**对应API**: `POST /api/v1/visitors/`

**页面流程**:
1. 访客信息填写
2. 预约时间选择
3. 接待员工选择
4. 信息确认提交
5. 预约成功反馈

**表单设计**:
```vue
<van-form @submit="onSubmit">
  <van-cell-group>
    <van-field v-model="form.name" label="姓名" placeholder="请输入您的姓名" required />
    <van-field v-model="form.phone_number" label="手机号" placeholder="请输入手机号" required />
    <van-field v-model="form.company_name" label="公司名称" placeholder="请输入公司名称" />
    <van-field v-model="form.identification_no" label="身份证号" placeholder="请输入身份证号" />
    
    <van-field readonly clickable label="访问目的" :value="purposeText" @click="showPurposePicker = true" />
    
    <van-field readonly clickable label="预约时间" :value="expectedDateText" @click="showDatePicker = true" />
    
    <van-field readonly clickable label="接待员工" :value="employeeText" @click="showEmployeePicker = true" />
    
    <van-field v-model="form.comment" label="备注" type="textarea" placeholder="请输入访问事由" />
  </van-cell-group>
  
  <div class="submit-section">
    <van-button type="primary" size="large" native-type="submit">提交预约</van-button>
  </div>
</van-form>
```

#### 2.2 预约状态页面 (`/status`)
**对应API**: `GET /api/v1/visitors/{visitor_id}`

**功能需求**:
- 预约状态展示
- 二维码显示（已批准后）
- 预约信息查看
- 取消预约功能

**状态展示设计**:
```vue
<div class="status-page">
  <van-steps :active="currentStep">
    <van-step>预约提交</van-step>
    <van-step>等待审批</van-step>
    <van-step>审批通过</van-step>
    <van-step>访问完成</van-step>
  </van-steps>
  
  <div class="qr-code-section" v-if="visitor.status === 'approved'">
    <h3>访客通行码</h3>
    <QRCode :value="visitor.pass_code" size="200" />
    <p>请出示此二维码进行签到</p>
  </div>
  
  <van-cell-group title="预约信息">
    <van-cell title="访客姓名" :value="visitor.name" />
    <van-cell title="预约时间" :value="visitor.expected_date" />
    <van-cell title="接待员工" :value="visitor.employee_name" />
    <van-cell title="当前状态" :value="statusText" />
  </van-cell-group>
</div>
```

#### 2.3 访客签到页面 (`/checkin`)
**对应API**: `POST /api/v1/visitors/{visitor_id}/checkin`

**功能需求**:
- 二维码扫描
- 手动输入通行码
- 签到成功确认
- 访客信息展示

## 🖥️ **三、设备端 (Web App) 详细设计**

### 技术栈确认
```json
{
  "framework": "Vue 3.3+ / React 18+",
  "language": "TypeScript",
  "ui_library": "自定义组件库",
  "optimization": "触控优化、大字体、高对比度",
  "offline": "Service Worker离线支持"
}
```

### 设备端特殊设计要求

#### 3.1 签到主页面
**对应API**: 签到/签出相关API

**界面要求**:
- 大按钮设计（最小44px触控目标）
- 高对比度配色方案
- 简化操作流程
- 语音提示支持

**页面布局**:
```vue
<div class="kiosk-layout">
  <header class="kiosk-header">
    <h1>访客签到系统</h1>
    <div class="time-display">{{ currentTime }}</div>
  </header>
  
  <main class="kiosk-main">
    <div class="scan-section">
      <QRScanner @scan="handleScan" />
      <p class="instruction">请扫描您的访客二维码</p>
    </div>
    
    <div class="manual-input">
      <van-button size="large" @click="showManualInput = true">
        手动输入通行码
      </van-button>
    </div>
  </main>
  
  <footer class="kiosk-footer">
    <van-button type="default" @click="showHelp = true">需要帮助？</van-button>
  </footer>
</div>
```

## 🔄 **四、API集成规范**

### 4.1 HTTP客户端封装
所有前端应用使用统一的API客户端：

```typescript
// utils/apiClient.ts
class ApiClient {
  private baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1'
  
  constructor() {
    this.setupInterceptors()
  }
  
  async get<T>(url: string, params?: any): Promise<ApiResponse<T>> {
    // 实现GET请求
  }
  
  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    // 实现POST请求
  }
  
  // 其他HTTP方法...
}
```

### 4.2 状态管理规范

#### React (Redux Toolkit)
```typescript
// store/visitorSlice.ts
export const visitorSlice = createSlice({
  name: 'visitor',
  initialState,
  reducers: {
    setVisitors: (state, action) => {
      state.visitors = action.payload
    },
    updateVisitorStatus: (state, action) => {
      const { visitorId, status } = action.payload
      const visitor = state.visitors.find(v => v.id === visitorId)
      if (visitor) visitor.status = status
    }
  }
})
```

#### Vue (Pinia)
```typescript
// stores/visitor.ts
export const useVisitorStore = defineStore('visitor', {
  state: () => ({
    visitors: [] as Visitor[],
    currentVisitor: null as Visitor | null
  }),
  
  actions: {
    async fetchVisitors() {
      const response = await apiClient.get('/visitors')
      this.visitors = response.data
    }
  }
})
```

## 🎨 **五、UI/UX设计规范**

### 5.1 交互设计原则
- **一致性**: 相同操作在不同页面保持一致的交互方式
- **反馈性**: 每个用户操作都要有明确的视觉反馈
- **容错性**: 重要操作需要二次确认，支持撤销操作
- **无障碍**: 支持键盘导航和屏幕阅读器

### 5.2 响应式设计断点
```css
/* 设计断点定义 */
$mobile: 576px;
$tablet: 768px;
$desktop: 1024px;
$large-desktop: 1440px;

/* 媒体查询示例 */
@media (max-width: $tablet) {
  .visitor-table {
    .table-actions {
      flex-direction: column;
    }
  }
}
```

### 5.3 动画和过渡
- **页面切换**: 300ms滑动过渡
- **模态框**: 200ms淡入淡出
- **加载状态**: Skeleton屏幕和Loading动画
- **状态变化**: 颜色渐变过渡150ms

## 📋 **六、开发规范**

### 6.1 组件命名规范
- **页面组件**: PascalCase + Page后缀，如`VisitorListPage`
- **业务组件**: PascalCase，如`VisitorCard`
- **基础组件**: PascalCase + 前缀，如`BaseButton`

### 6.2 文件组织结构
```
src/
├── components/          # 通用组件
│   ├── base/           # 基础组件
│   ├── business/       # 业务组件
│   └── layout/         # 布局组件
├── pages/              # 页面组件
├── hooks/              # 自定义Hooks
├── stores/             # 状态管理
├── utils/              # 工具函数
├── services/           # API服务
├── types/              # TypeScript类型定义
└── assets/             # 静态资源
```

### 6.3 代码质量标准
- **TypeScript**: 严格模式，100%类型覆盖
- **ESLint**: 使用Vue/React官方推荐配置
- **Prettier**: 统一代码格式化
- **测试覆盖率**: 单元测试覆盖率>80%

## 🚀 **七、部署和构建**

### 7.1 构建配置
- **环境区分**: development、testing、production
- **代码分割**: 路由级别的代码分割
- **资源优化**: 图片压缩、CSS/JS压缩
- **缓存策略**: 静态资源长期缓存

### 7.2 部署方案
- **管理端**: Nginx静态部署
- **H5端**: CDN + Nginx部署
- **设备端**: 本地部署或内网访问

## 📊 **八、性能指标**

### 8.1 加载性能目标
- **首屏加载**: <2s (3G网络)
- **页面切换**: <300ms
- **API响应**: <500ms
- **资源大小**: 初始包<1MB

### 8.2 用户体验指标
- **可用性**: 99.9%
- **错误率**: <0.1%
- **用户满意度**: >90%
- **任务完成率**: >95%

---

## 📞 **联系信息**

**前端负责人**: 前端架构师  
**UI/UX负责人**: 设计师  
**文档状态**: 需求规格完成，等待开发排期  
**更新频率**: 需求变更时及时同步

---
*本文档是前端开发的详细指导，包含了所有必要的技术实现细节和设计规范* 