# API与UI组件映射关系文档

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **维护者**: 产品经理AI
- **适用角色**: 前端开发者、接口对接工程师
- **依赖文档**: Backend_API_Reference.md, frontend-requirements.md

## 🎯 映射概述

本文档建立后端**28个API端点**与前端**UI组件**的完整映射关系，确保前后端开发的一致性和可追溯性。

## 📊 **API分类与前端应用分布**

### API端点统计
- **认证相关**: 4个API → 登录组件、权限控制
- **访客管理**: 9个API → 访客管理模块
- **组织管理**: 15个API → 组织管理模块 (5个员工+5个部门+5个站点)
- **配置引擎**: 多个API → 配置中心模块

### 前端应用分布
- **管理端(React)**: 使用全部28个API
- **H5端(Vue)**: 使用6个核心API
- **设备端**: 使用4个签到相关API

---

## 🔐 **一、认证API映射**

### 1.1 用户登录 API
**API端点**: `POST /api/v1/auth/login`

| 前端应用 | 组件路径 | UI组件描述 | 状态管理 |
|----------|----------|------------|----------|
| **管理端** | `src/pages/auth/LoginPage.tsx` | 管理员登录表单页面 | `authSlice.login` |
| **H5端** | `src/pages/auth/LoginPage.vue` | 移动端登录页面 | `useAuthStore.login` |
| **设备端** | `src/pages/auth/DeviceLogin.vue` | 设备管理员登录 | 本地状态 |

#### 组件实现细节

**管理端登录组件**:
```tsx
// src/pages/auth/LoginPage.tsx
interface LoginFormData {
  username: string;
  password: string;
  tenant_id: string;
}

const LoginPage: React.FC = () => {
  const dispatch = useAppDispatch();
  
  const handleLogin = async (values: LoginFormData) => {
    const result = await dispatch(authActions.login(values));
    if (result.success) {
      navigate('/dashboard');
    }
  };

  return (
    <Form onFinish={handleLogin}>
      <Form.Item name="username" rules={[{ required: true }]}>
        <Input placeholder="用户名" />
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true }]}>
        <Input.Password placeholder="密码" />
      </Form.Item>
      <Form.Item name="tenant_id">
        <Select placeholder="选择租户">
          <Option value="default_tenant">默认租户</Option>
        </Select>
      </Form.Item>
      <Button type="primary" htmlType="submit">登录</Button>
    </Form>
  );
};
```

**H5端登录组件**:
```vue
<!-- src/pages/auth/LoginPage.vue -->
<template>
  <van-form @submit="handleLogin">
    <van-field v-model="form.username" label="用户名" required />
    <van-field v-model="form.password" type="password" label="密码" required />
    <van-button type="primary" native-type="submit">登录</van-button>
  </van-form>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const form = reactive({
  username: '',
  password: '',
  tenant_id: 'default_tenant'
});

const handleLogin = async () => {
  await authStore.login(form);
  router.push('/book');
};
</script>
```

### 1.2 Token刷新 API
**API端点**: `POST /api/v1/auth/refresh`

#### 前端映射关系

| 前端应用 | 实现位置 | 触发条件 | 处理方式 |
|----------|----------|----------|----------|
| **管理端** | `src/utils/httpClient.ts` | 401响应拦截 | 自动刷新Token |
| **H5端** | `src/utils/request.ts` | 401响应拦截 | 自动刷新Token |
| **设备端** | `src/utils/api.ts` | 401响应拦截 | 跳转登录页面 |

---

## 👥 **二、访客管理API映射**

### 2.1 创建访客 API
**API端点**: `POST /api/v1/visitors/`

| 前端应用 | 组件路径 | UI组件描述 | 表单字段映射 |
|----------|----------|------------|-------------|
| **管理端** | `src/pages/visitors/CreateVisitorModal.tsx` | 新增访客模态框 | 完整表单字段 |
| **H5端** | `src/pages/book/VisitorBookingPage.vue` | 访客预约主页面 | 核心表单字段 |

#### 表单字段映射详情

**H5端预约表单**:
```vue
<!-- src/pages/book/VisitorBookingPage.vue -->
<template>
  <van-form @submit="onSubmit">
    <van-cell-group>
      <!-- API字段: name -->
      <van-field 
        v-model="form.name" 
        label="姓名" 
        placeholder="请输入您的姓名" 
        required 
        :rules="[{ required: true, message: '请输入姓名' }]"
      />
      
      <!-- API字段: phone_number -->
      <van-field 
        v-model="form.phone_number" 
        label="手机号" 
        placeholder="请输入手机号" 
        required 
        :rules="[{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]"
      />
      
      <!-- API字段: email -->
      <van-field 
        v-model="form.email" 
        label="邮箱" 
        placeholder="请输入邮箱地址"
        type="email"
      />
      
      <!-- API字段: identification_no -->
      <van-field 
        v-model="form.identification_no" 
        label="身份证号" 
        placeholder="请输入身份证号"
      />
      
      <!-- API字段: company_name -->
      <van-field 
        v-model="form.company_name" 
        label="公司名称" 
        placeholder="请输入公司名称"
      />
      
      <!-- API字段: purpose -->
      <van-field 
        readonly 
        clickable 
        label="访问目的" 
        :value="purposeText" 
        @click="showPurposePicker = true"
      />
      
      <!-- API字段: expected_date -->
      <van-field 
        readonly 
        clickable 
        label="预约时间" 
        :value="expectedDateText" 
        @click="showDatePicker = true"
      />
      
      <!-- API字段: employee_id -->
      <van-field 
        readonly 
        clickable 
        label="接待员工" 
        :value="employeeText" 
        @click="showEmployeePicker = true"
      />
      
      <!-- API字段: comment -->
      <van-field 
        v-model="form.comment" 
        label="备注" 
        type="textarea" 
        placeholder="请输入访问事由"
      />
    </van-cell-group>
    
    <div class="submit-section">
      <van-button type="primary" size="large" native-type="submit">
        提交预约
      </van-button>
    </div>
  </van-form>
  
  <!-- 访问目的选择器 -->
  <van-popup v-model:show="showPurposePicker">
    <van-picker :columns="purposeOptions" @confirm="onPurposeConfirm" />
  </van-popup>
  
  <!-- 时间选择器 -->
  <van-popup v-model:show="showDatePicker">
    <van-datetime-picker 
      type="datetime" 
      @confirm="onDateConfirm"
      :min-date="new Date()"
    />
  </van-popup>
  
  <!-- 员工选择器 -->
  <van-popup v-model:show="showEmployeePicker">
    <van-picker :columns="employeeOptions" @confirm="onEmployeeConfirm" />
  </van-popup>
</template>

<script setup lang="ts">
// 表单数据结构对应API请求体
interface VisitorForm {
  name: string;
  phone_number: string;
  email: string;
  identification_no: string;
  company_name: string;
  purpose: 'business_meeting' | 'interview' | 'site_visit' | 'delivery' | 'maintenance' | 'other';
  expected_date: string; // ISO格式时间
  employee_id: number;
  comment: string;
}

const form = reactive<VisitorForm>({
  name: '',
  phone_number: '',
  email: '',
  identification_no: '',
  company_name: '',
  purpose: 'business_meeting',
  expected_date: '',
  employee_id: 0,
  comment: ''
});

// API调用处理
const onSubmit = async () => {
  try {
    const response = await apiClient.post('/visitors/', form);
    if (response.success) {
      // 跳转到状态页面
      router.push(`/status?visitor_id=${response.data.id}`);
      showToast('预约提交成功');
    }
  } catch (error) {
    showToast('预约提交失败');
  }
};
</script>
```

### 2.2 获取访客列表 API
**API端点**: `GET /api/v1/visitors/`

| 前端应用 | 组件路径 | UI组件描述 | 查询参数映射 |
|----------|----------|------------|-------------|
| **管理端** | `src/pages/visitors/VisitorListPage.tsx` | 访客列表管理页面 | 完整查询参数 |

#### 查询参数与UI组件映射

**管理端访客列表**:
```tsx
// src/pages/visitors/VisitorListPage.tsx
interface VisitorListQuery {
  skip: number;        // 分页：跳过记录数
  limit: number;       // 分页：每页记录数
  status?: string;     // 筛选：访客状态
  employee_id?: number; // 筛选：接待员工ID
  date_from?: string;  // 筛选：开始日期
  date_to?: string;    // 筛选：结束日期
  search?: string;     // 搜索：姓名或电话
}

const VisitorListPage: React.FC = () => {
  const [query, setQuery] = useState<VisitorListQuery>({
    skip: 0,
    limit: 20
  });
  
  // 筛选器组件
  const FilterForm = () => (
    <Row gutter={16} className="filter-form">
      <Col span={6}>
        {/* API参数: status */}
        <Select 
          placeholder="访客状态" 
          value={query.status}
          onChange={(value) => setQuery({...query, status: value})}
          allowClear
        >
          <Option value="pending">待审批</Option>
          <Option value="approved">已批准</Option>
          <Option value="rejected">已拒绝</Option>
          <Option value="checked_in">已签到</Option>
          <Option value="checked_out">已签出</Option>
        </Select>
      </Col>
      
      <Col span={6}>
        {/* API参数: date_from, date_to */}
        <RangePicker 
          placeholder={['开始日期', '结束日期']}
          onChange={(dates) => {
            setQuery({
              ...query, 
              date_from: dates?.[0]?.format('YYYY-MM-DD'),
              date_to: dates?.[1]?.format('YYYY-MM-DD')
            });
          }}
        />
      </Col>
      
      <Col span={6}>
        {/* API参数: employee_id */}
        <Select 
          placeholder="接待员工" 
          showSearch
          value={query.employee_id}
          onChange={(value) => setQuery({...query, employee_id: value})}
        >
          {employees.map(emp => (
            <Option key={emp.id} value={emp.id}>{emp.name}</Option>
          ))}
        </Select>
      </Col>
      
      <Col span={6}>
        {/* API参数: search (后端搜索姓名/电话) */}
        <Input 
          placeholder="搜索姓名/电话" 
          value={query.search}
          onChange={(e) => setQuery({...query, search: e.target.value})}
          suffix={<SearchOutlined />}
        />
      </Col>
    </Row>
  );
  
  // 表格列定义 - 对应API响应字段
  const columns = [
    { 
      title: '访客姓名', 
      dataIndex: 'name',   // API字段: name
      sorter: true 
    },
    { 
      title: '联系电话', 
      dataIndex: 'phone_number'  // API字段: phone_number
    },
    { 
      title: '公司名称', 
      dataIndex: 'company_name'  // API字段: company_name
    },
    { 
      title: '访问目的', 
      dataIndex: 'purpose',      // API字段: purpose
      render: (purpose: string) => purposeMap[purpose]
    },
    { 
      title: '接待员工', 
      dataIndex: 'employee_name' // API字段: employee.name (关联查询)
    },
    { 
      title: '预约时间', 
      dataIndex: 'expected_date', // API字段: expected_date
      sorter: true,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm')
    },
    { 
      title: '状态', 
      dataIndex: 'status',       // API字段: status
      render: (status: string) => <StatusTag status={status} />
    },
    { 
      title: '操作', 
      render: (record: Visitor) => (
        <Space>
          <Button size="small" onClick={() => handleView(record.id)}>查看</Button>
          <Button size="small" onClick={() => handleEdit(record.id)}>编辑</Button>
        </Space>
      )
    }
  ];
  
  // API调用
  const fetchVisitors = async () => {
    const response = await apiClient.get('/visitors/', { params: query });
    setVisitors(response.data.items);  // API响应: { items: [], total: number }
    setTotal(response.data.total);
  };
  
  return (
    <PageContainer>
      <FilterForm />
      <Table
        columns={columns}
        dataSource={visitors}
        pagination={{
          current: Math.floor(query.skip / query.limit) + 1,
          pageSize: query.limit,
          total: total,
          onChange: (page, pageSize) => {
            setQuery({
              ...query,
              skip: (page - 1) * pageSize!,
              limit: pageSize!
            });
          }
        }}
        onChange={(pagination, filters, sorter) => {
          // 处理排序 - 对应API的sort_by, sort_order参数
          if (sorter && !Array.isArray(sorter)) {
            setQuery({
              ...query,
              sort_by: sorter.field as string,
              sort_order: sorter.order === 'ascend' ? 'asc' : 'desc'
            });
          }
        }}
      />
    </PageContainer>
  );
};
```

### 2.3 访客审批 API
**API端点**: `PUT /api/v1/visitors/{visitor_id}/approve`, `PUT /api/v1/visitors/{visitor_id}/reject`

| 前端应用 | 组件路径 | UI组件描述 | 操作映射 |
|----------|----------|------------|----------|
| **管理端** | `src/pages/visitors/ApprovalPage.tsx` | 审批中心页面 | 批准/拒绝操作 |

#### 审批组件实现

```tsx
// src/pages/visitors/ApprovalPage.tsx
const ApprovalPage: React.FC = () => {
  const [pendingVisitors, setPendingVisitors] = useState<Visitor[]>([]);
  
  // 批准操作 - 对应 PUT /api/v1/visitors/{visitor_id}/approve
  const handleApprove = async (visitorId: number, comment?: string) => {
    try {
      await apiClient.put(`/visitors/${visitorId}/approve`, {
        approval_comment: comment  // API字段: approval_comment
      });
      
      message.success('访客已批准');
      fetchPendingVisitors(); // 刷新列表
    } catch (error) {
      message.error('批准失败');
    }
  };
  
  // 拒绝操作 - 对应 PUT /api/v1/visitors/{visitor_id}/reject
  const handleReject = async (visitorId: number, comment: string) => {
    try {
      await apiClient.put(`/visitors/${visitorId}/reject`, {
        approval_comment: comment  // API字段: approval_comment
      });
      
      message.success('访客已拒绝');
      fetchPendingVisitors();
    } catch (error) {
      message.error('拒绝失败');
    }
  };
  
  // 审批卡片组件
  const ApprovalCard: React.FC<{ visitor: Visitor }> = ({ visitor }) => (
    <Card className="approval-card">
      <Card.Meta
        avatar={<Avatar src={visitor.avatar} />}
        title={visitor.name}
        description={`${visitor.company_name} | ${visitor.phone_number}`}
      />
      
      <Descriptions size="small" column={2}>
        <Descriptions.Item label="访问目的">
          {purposeMap[visitor.purpose]}
        </Descriptions.Item>
        <Descriptions.Item label="预约时间">
          {dayjs(visitor.expected_date).format('YYYY-MM-DD HH:mm')}
        </Descriptions.Item>
        <Descriptions.Item label="接待员工">
          {visitor.employee_name}
        </Descriptions.Item>
        <Descriptions.Item label="身份证号">
          {visitor.identification_no}
        </Descriptions.Item>
      </Descriptions>
      
      {visitor.comment && (
        <div className="visitor-comment">
          <Text type="secondary">访问事由：</Text>
          <Text>{visitor.comment}</Text>
        </div>
      )}
      
      <div className="approval-actions">
        <Space>
          <Button 
            type="primary" 
            onClick={() => {
              Modal.confirm({
                title: '确认批准访客？',
                content: (
                  <Input.TextArea
                    placeholder="审批意见（可选）"
                    rows={3}
                    onChange={(e) => setApprovalComment(e.target.value)}
                  />
                ),
                onOk: () => handleApprove(visitor.id, approvalComment)
              });
            }}
          >
            批准
          </Button>
          
          <Button 
            danger 
            onClick={() => {
              Modal.confirm({
                title: '确认拒绝访客？',
                content: (
                  <Input.TextArea
                    placeholder="拒绝原因（必填）"
                    rows={3}
                    onChange={(e) => setRejectComment(e.target.value)}
                  />
                ),
                onOk: () => handleReject(visitor.id, rejectComment)
              });
            }}
          >
            拒绝
          </Button>
        </Space>
      </div>
    </Card>
  );
  
  return (
    <PageContainer title="访客审批">
      <Row gutter={[16, 16]}>
        {pendingVisitors.map(visitor => (
          <Col span={8} key={visitor.id}>
            <ApprovalCard visitor={visitor} />
          </Col>
        ))}
      </Row>
    </PageContainer>
  );
};
```

### 2.4 访客签到/签出 API
**API端点**: `POST /api/v1/visitors/{visitor_id}/checkin`, `POST /api/v1/visitors/{visitor_id}/checkout`

| 前端应用 | 组件路径 | UI组件描述 | 扫码处理 |
|----------|----------|------------|----------|
| **设备端** | `src/pages/kiosk/CheckinPage.vue` | 签到设备主页面 | 二维码扫描处理 |
| **H5端** | `src/pages/checkin/SelfCheckin.vue` | 访客自助签到 | 通行码输入 |

#### 设备端签到组件

```vue
<!-- src/pages/kiosk/CheckinPage.vue -->
<template>
  <div class="kiosk-checkin">
    <header class="kiosk-header">
      <h1>访客签到系统</h1>
      <div class="current-time">{{ currentTime }}</div>
    </header>
    
    <main class="kiosk-main">
      <!-- 二维码扫描区域 -->
      <div class="scan-area" v-if="!isProcessing">
        <QRScanner 
          @scan="handleQRScan" 
          :camera-width="400"
          :camera-height="300"
        />
        <p class="scan-instruction">请扫描您的访客二维码进行签到</p>
      </div>
      
      <!-- 处理中状态 -->
      <div class="processing" v-if="isProcessing">
        <van-loading size="48px" />
        <p>正在处理签到...</p>
      </div>
      
      <!-- 签到成功显示 -->
      <div class="success-result" v-if="checkinResult">
        <van-icon name="success" size="64px" color="#52c41a" />
        <h2>签到成功！</h2>
        <div class="visitor-info">
          <p><strong>访客姓名：</strong>{{ checkinResult.visitor_name }}</p>
          <p><strong>接待员工：</strong>{{ checkinResult.employee_name }}</p>
          <p><strong>签到时间：</strong>{{ checkinResult.checkin_time }}</p>
        </div>
        <van-button @click="resetPage" type="primary" size="large">
          继续扫码
        </van-button>
      </div>
      
      <!-- 手动输入通行码 -->
      <div class="manual-input">
        <van-button @click="showManualInput = true" size="large">
          手动输入通行码
        </van-button>
      </div>
    </main>
    
    <!-- 手动输入弹窗 -->
    <van-popup v-model:show="showManualInput" position="center">
      <div class="manual-input-form">
        <h3>输入访客通行码</h3>
        <van-field 
          v-model="manualPassCode" 
          placeholder="请输入通行码"
          maxlength="20"
        />
        <div class="form-actions">
          <van-button @click="handleManualCheckin" type="primary">
            确认签到
          </van-button>
          <van-button @click="showManualInput = false">
            取消
          </van-button>
        </div>
      </div>
    </van-popup>
    
    <footer class="kiosk-footer">
      <van-button @click="showHelp = true">需要帮助？</van-button>
    </footer>
  </div>
</template>

<script setup lang="ts">
interface CheckinResult {
  visitor_id: number;
  visitor_name: string;
  employee_name: string;
  checkin_time: string;
  status: string;
}

// 二维码扫描处理
const handleQRScan = async (passCode: string) => {
  try {
    isProcessing.value = true;
    
    // 1. 先根据通行码查找访客
    const visitorResponse = await apiClient.get('/visitors/', {
      params: { pass_code: passCode }
    });
    
    if (!visitorResponse.data.items.length) {
      showToast('无效的通行码');
      return;
    }
    
    const visitor = visitorResponse.data.items[0];
    
    // 2. 执行签到操作 - 对应 POST /api/v1/visitors/{visitor_id}/checkin
    const checkinResponse = await apiClient.post(`/visitors/${visitor.id}/checkin`, {
      device_id: deviceId,           // 设备ID
      checkin_method: 'qr_code',     // 签到方式
      location: 'main_entrance'      // 签到位置
    });
    
    // 3. 显示签到结果
    checkinResult.value = {
      visitor_id: visitor.id,
      visitor_name: visitor.name,
      employee_name: visitor.employee_name,
      checkin_time: checkinResponse.data.checkin_date,
      status: checkinResponse.data.status
    };
    
    showSuccessSound(); // 播放成功提示音
    
  } catch (error) {
    showToast('签到失败，请联系管理员');
  } finally {
    isProcessing.value = false;
  }
};

// 手动输入通行码签到
const handleManualCheckin = async () => {
  if (!manualPassCode.value) {
    showToast('请输入通行码');
    return;
  }
  
  await handleQRScan(manualPassCode.value);
  showManualInput.value = false;
  manualPassCode.value = '';
};

// 签出处理 (类似签到逻辑)
const handleCheckout = async (visitorId: number) => {
  try {
    // 对应 POST /api/v1/visitors/{visitor_id}/checkout
    const response = await apiClient.post(`/visitors/${visitorId}/checkout`, {
      device_id: deviceId,
      checkout_method: 'qr_code',
      location: 'main_entrance'
    });
    
    showToast('签出成功');
  } catch (error) {
    showToast('签出失败');
  }
};
</script>
```

---

## 🏢 **三、组织管理API映射**

### 3.1 员工管理API群
**API端点**: 
- `GET /api/v1/employees/` (获取员工列表)
- `POST /api/v1/employees/` (创建员工)
- `GET /api/v1/employees/{employee_id}` (获取员工详情)
- `PUT /api/v1/employees/{employee_id}` (更新员工)
- `DELETE /api/v1/employees/{employee_id}` (删除员工)

| API端点 | 前端组件 | UI操作 | 组件路径 |
|---------|----------|---------|----------|
| `GET /employees/` | 员工列表表格 | 列表展示、筛选、搜索 | `EmployeeListPage.tsx` |
| `POST /employees/` | 新增员工模态框 | 表单提交 | `CreateEmployeeModal.tsx` |
| `GET /employees/{id}` | 员工详情抽屉 | 查看详情 | `EmployeeDetailDrawer.tsx` |
| `PUT /employees/{id}` | 编辑员工模态框 | 表单更新 | `EditEmployeeModal.tsx` |
| `DELETE /employees/{id}` | 删除确认对话框 | 删除操作 | `EmployeeListPage.tsx` |

#### 员工管理页面实现

```tsx
// src/pages/organization/EmployeeListPage.tsx
const EmployeeListPage: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 获取员工列表 - GET /api/v1/employees/
  const fetchEmployees = async (params: EmployeeQuery = {}) => {
    setLoading(true);
    try {
      const response = await apiClient.get('/employees/', { params });
      setEmployees(response.data.items);
    } finally {
      setLoading(false);
    }
  };
  
  // 删除员工 - DELETE /api/v1/employees/{employee_id}
  const handleDelete = (employee: Employee) => {
    Modal.confirm({
      title: `确认删除员工 ${employee.name}？`,
      content: '删除后将无法恢复，该员工的访客记录将保留',
      onOk: async () => {
        try {
          await apiClient.delete(`/employees/${employee.id}`);
          message.success('删除成功');
          fetchEmployees();
        } catch (error) {
          message.error('删除失败');
        }
      }
    });
  };
  
  const columns = [
    { title: '姓名', dataIndex: 'name' },
    { title: '工号', dataIndex: 'employee_id' },
    { title: '邮箱', dataIndex: 'email' },
    { title: '部门', dataIndex: 'department_name' },
    { title: '职位', dataIndex: 'position' },
    { title: '状态', dataIndex: 'status', render: (status: string) => <StatusTag status={status} /> },
    {
      title: '操作',
      render: (record: Employee) => (
        <Space>
          <Button size="small" onClick={() => handleView(record)}>查看</Button>
          <Button size="small" onClick={() => handleEdit(record)}>编辑</Button>
          <Button size="small" danger onClick={() => handleDelete(record)}>删除</Button>
        </Space>
      )
    }
  ];
  
  return (
    <PageContainer
      title="员工管理"
      extra={<Button type="primary" onClick={() => setCreateModalVisible(true)}>新增员工</Button>}
    >
      <Table
        columns={columns}
        dataSource={employees}
        loading={loading}
        pagination={{ pageSize: 20 }}
      />
      
      {/* 新增员工模态框 */}
      <CreateEmployeeModal 
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onSuccess={() => {
          fetchEmployees();
          setCreateModalVisible(false);
        }}
      />
    </PageContainer>
  );
};
```

---

## ⚙️ **四、配置引擎API映射**

### 4.1 表单配置API群
**API端点**: 表单配置相关多个API

| 功能模块 | API端点 | 前端组件 | UI描述 |
|----------|---------|----------|---------|
| 表单列表 | `GET /api/v1/form-configs/` | `FormConfigListPage.tsx` | 表单配置列表页面 |
| 表单设计器 | `POST /api/v1/form-configs/` | `FormDesigner.tsx` | 拖拽式表单设计器 |
| 字段配置 | `PUT /api/v1/form-configs/{id}/fields` | `FieldConfigPanel.tsx` | 字段属性配置面板 |
| 表单预览 | `GET /api/v1/form-configs/{id}/preview` | `FormPreview.tsx` | 表单预览组件 |

#### 表单设计器组件实现

```tsx
// src/pages/config/FormDesigner.tsx
const FormDesigner: React.FC = () => {
  const [formConfig, setFormConfig] = useState<FormConfig>({
    form_name: '',
    form_type: 'visitor_registration',
    description: '',
    form_fields: []
  });
  
  // 保存表单配置 - POST /api/v1/form-configs/
  const handleSaveForm = async () => {
    try {
      const response = await apiClient.post('/form-configs/', formConfig);
      message.success('表单保存成功');
      router.push('/config/forms');
    } catch (error) {
      message.error('保存失败');
    }
  };
  
  // 字段类型组件库
  const FieldTypeComponents = {
    text: TextFieldComponent,
    textarea: TextareaFieldComponent,
    number: NumberFieldComponent,
    email: EmailFieldComponent,
    phone: PhoneFieldComponent,
    date: DateFieldComponent,
    datetime: DatetimeFieldComponent,
    select: SelectFieldComponent,
    multiselect: MultiselectFieldComponent,
    radio: RadioFieldComponent,
    checkbox: CheckboxFieldComponent,
    file: FileFieldComponent,
    image: ImageFieldComponent
  };
  
  return (
    <div className="form-designer">
      <div className="designer-header">
        <Input 
          placeholder="表单名称"
          value={formConfig.form_name}
          onChange={(e) => setFormConfig({...formConfig, form_name: e.target.value})}
        />
        <Button type="primary" onClick={handleSaveForm}>保存表单</Button>
      </div>
      
      <div className="designer-body">
        {/* 字段库 */}
        <div className="field-library">
          <h4>字段库</h4>
          {Object.keys(FieldTypeComponents).map(fieldType => (
            <DraggableFieldItem 
              key={fieldType} 
              fieldType={fieldType}
              onDragEnd={handleFieldDrop}
            />
          ))}
        </div>
        
        {/* 表单画布 */}
        <div className="form-canvas">
          <h4>表单设计</h4>
          <DropZone onDrop={handleFieldDrop}>
            {formConfig.form_fields.map((field, index) => (
              <FormFieldComponent
                key={field.field_key}
                field={field}
                index={index}
                onEdit={() => handleEditField(field)}
                onDelete={() => handleDeleteField(field.field_key)}
              />
            ))}
          </DropZone>
        </div>
        
        {/* 属性配置面板 */}
        <div className="property-panel">
          <h4>字段属性</h4>
          {selectedField && (
            <FieldConfigPanel 
              field={selectedField}
              onChange={handleFieldConfigChange}
            />
          )}
        </div>
      </div>
    </div>
  );
};
```

---

## 📊 **五、API错误处理映射**

### 5.1 统一错误处理

| 状态码 | 错误类型 | 前端处理方式 | UI反馈 |
|--------|----------|-------------|--------|
| 400 | 请求参数错误 | 表单验证提示 | 字段级错误提示 |
| 401 | 认证失败 | 自动跳转登录 | 登录页面 |
| 403 | 权限不足 | 权限提示 | 权限不足页面 |
| 404 | 资源不存在 | 404页面 | 资源不存在提示 |
| 422 | 数据验证失败 | 表单验证 | 字段验证错误 |
| 500 | 服务器错误 | 全局错误提示 | 系统异常提示 |

### 5.2 错误处理组件

```tsx
// src/utils/errorHandler.ts
export const handleApiError = (error: AxiosError) => {
  const { status, data } = error.response || {};
  
  switch (status) {
    case 400:
      // 字段级错误处理
      if (data?.field_errors) {
        return { type: 'field', errors: data.field_errors };
      }
      break;
      
    case 401:
      // 认证失败处理
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      break;
      
    case 403:
      message.error('权限不足，请联系管理员');
      break;
      
    case 422:
      // 数据验证错误
      message.error(data?.detail || '数据验证失败');
      break;
      
    default:
      message.error('系统异常，请稍后重试');
  }
};
```

---

## 📋 **六、性能优化映射**

### 6.1 API调用优化策略

| 优化策略 | 应用场景 | 实现方式 | 性能提升 |
|----------|----------|----------|----------|
| **请求缓存** | 员工列表、部门列表 | React Query / SWR | 减少重复请求 |
| **分页加载** | 访客列表 | 虚拟滚动 | 大数据量处理 |
| **防抖搜索** | 实时搜索 | useDebounce Hook | 减少API调用 |
| **乐观更新** | 状态切换 | 本地状态预更新 | 提升用户体验 |

### 6.2 缓存策略实现

```tsx
// src/hooks/useVisitorList.ts
export const useVisitorList = (query: VisitorQuery) => {
  return useQuery({
    queryKey: ['visitors', query],
    queryFn: () => apiClient.get('/visitors/', { params: query }),
    staleTime: 5 * 60 * 1000, // 5分钟缓存
    cacheTime: 10 * 60 * 1000 // 10分钟保存
  });
};
```

---

## 🎯 **七、测试用例映射**

### 7.1 API测试覆盖

| API分类 | 测试用例数 | 覆盖率要求 | 自动化程度 |
|---------|------------|------------|------------|
| **认证API** | 12个 | 100% | 完全自动化 |
| **访客管理** | 36个 | 95% | 完全自动化 |
| **组织管理** | 45个 | 90% | 半自动化 |
| **配置引擎** | 24个 | 85% | 手动测试为主 |

### 7.2 前端组件测试

```tsx
// src/pages/visitors/VisitorListPage.test.tsx
describe('VisitorListPage', () => {
  test('should fetch visitors on mount', async () => {
    const mockVisitors = [/* mock data */];
    apiClient.get = jest.fn().mockResolvedValue({ data: { items: mockVisitors } });
    
    render(<VisitorListPage />);
    
    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith('/visitors/', expect.any(Object));
    });
  });
  
  test('should handle filter changes', async () => {
    render(<VisitorListPage />);
    
    const statusFilter = screen.getByPlaceholderText('访客状态');
    fireEvent.change(statusFilter, { target: { value: 'pending' } });
    
    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith(
        '/visitors/', 
        { params: expect.objectContaining({ status: 'pending' }) }
      );
    });
  });
});
```

---

## 📞 **联系信息**

**API对接负责人**: 全栈开发工程师  
**前端负责人**: 前端架构师  
**测试负责人**: 测试工程师  
**文档状态**: API映射关系完成，等待实现验证  

---
*本文档确保了前后端开发的一致性，为高质量的系统交付提供了详细的技术指导* 