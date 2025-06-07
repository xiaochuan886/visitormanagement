# 前端开发指南

## 概述

访客管理系统前端采用现代化的前端技术栈，支持多平台部署（Web、移动端、桌面端），提供优秀的用户体验和开发体验。

## 技术栈选型

### 推荐技术栈

#### Web前端 (主推荐)
- **框架**: React 18+ with TypeScript
- **状态管理**: Redux Toolkit + RTK Query
- **UI组件库**: Ant Design 5.x
- **路由**: React Router v6
- **构建工具**: Vite 4+
- **样式方案**: Tailwind CSS + CSS Modules
- **图表库**: Apache ECharts / Chart.js
- **表单处理**: React Hook Form + Zod
- **国际化**: react-i18next

#### 移动端
- **跨平台**: React Native 0.72+
- **导航**: React Navigation v6
- **UI组件**: NativeBase / React Native Elements
- **状态管理**: Redux Toolkit
- **原生功能**: Expo SDK

#### 桌面端
- **框架**: Electron + React
- **打包**: Electron Builder
- **更新**: electron-updater

### 替代技术栈

#### Vue.js 生态
- **框架**: Vue 3 + TypeScript
- **状态管理**: Pinia
- **UI组件库**: Element Plus / Ant Design Vue
- **构建工具**: Vite

#### Angular 生态
- **框架**: Angular 15+
- **状态管理**: NgRx
- **UI组件库**: Angular Material

## 项目结构

### React + TypeScript 项目结构
```
frontend/
├── public/                 # 静态资源
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── components/         # 通用组件
│   │   ├── common/        # 基础组件
│   │   ├── forms/         # 表单组件
│   │   ├── layout/        # 布局组件
│   │   └── charts/        # 图表组件
│   ├── pages/             # 页面组件
│   │   ├── auth/          # 认证页面
│   │   ├── visitors/      # 访客管理
│   │   ├── employees/     # 员工管理
│   │   ├── dashboard/     # 仪表板
│   │   └── settings/      # 系统设置
│   ├── hooks/             # 自定义Hooks
│   ├── services/          # API服务
│   ├── store/             # 状态管理
│   │   ├── slices/        # Redux切片
│   │   └── api/           # RTK Query API
│   ├── types/             # TypeScript类型定义
│   ├── utils/             # 工具函数
│   ├── constants/         # 常量定义
│   ├── styles/            # 样式文件
│   ├── locales/           # 国际化文件
│   ├── App.tsx
│   ├── index.tsx
│   └── vite-env.d.ts
├── tests/                 # 测试文件
├── docs/                  # 文档
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── .eslintrc.js
```

## 核心功能模块

### 1. 认证模块

#### 登录组件
```typescript
// src/pages/auth/LoginPage.tsx
import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAppDispatch } from '@/hooks/redux';
import { loginAsync } from '@/store/slices/authSlice';
import { LoginRequest } from '@/types/auth';

interface LoginFormData {
  username: string;
  password: string;
}

export const LoginPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const [form] = Form.useForm<LoginFormData>();
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (values: LoginFormData) => {
    setLoading(true);
    try {
      const result = await dispatch(loginAsync(values)).unwrap();
      message.success('登录成功');
      // 重定向到仪表板
    } catch (error) {
      message.error('登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card title="访客管理系统" className="w-96">
        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
            />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>
          
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              className="w-full"
            >
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};
```

#### 认证状态管理
```typescript
// src/store/slices/authSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authAPI } from '@/services/authAPI';
import { LoginRequest, LoginResponse, User } from '@/types/auth';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  isAuthenticated: false,
  loading: false,
  error: null,
};

export const loginAsync = createAsyncThunk(
  'auth/login',
  async (credentials: LoginRequest) => {
    const response = await authAPI.login(credentials);
    return response.data;
  }
);

export const refreshTokenAsync = createAsyncThunk(
  'auth/refreshToken',
  async (refreshToken: string) => {
    const response = await authAPI.refreshToken(refreshToken);
    return response.data;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.isAuthenticated = true;
        localStorage.setItem('accessToken', action.payload.access_token);
        localStorage.setItem('refreshToken', action.payload.refresh_token);
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '登录失败';
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
```

### 2. 访客管理模块

#### 访客列表组件
```typescript
// src/pages/visitors/VisitorListPage.tsx
import React from 'react';
import { Table, Button, Space, Tag, Input, DatePicker, Select } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { useGetVisitorsQuery } from '@/store/api/visitorsAPI';
import { Visitor, VisitorStatus } from '@/types/visitor';
import { VisitorStatusTag } from '@/components/visitors/VisitorStatusTag';

const { RangePicker } = DatePicker;
const { Option } = Select;

export const VisitorListPage: React.FC = () => {
  const [filters, setFilters] = React.useState({
    search: '',
    status: undefined as VisitorStatus | undefined,
    dateRange: undefined as [string, string] | undefined,
  });

  const { data: visitors, isLoading, error } = useGetVisitorsQuery(filters);

  const columns = [
    {
      title: '访客姓名',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Visitor) => (
        <Space>
          <span>{text}</span>
          {record.avatar && (
            <img
              src={record.avatar}
              alt="头像"
              className="w-8 h-8 rounded-full"
            />
          )}
        </Space>
      ),
    },
    {
      title: '联系电话',
      dataIndex: 'phone',
      key: 'phone',
    },
    {
      title: '来访目的',
      dataIndex: 'purpose',
      key: 'purpose',
    },
    {
      title: '接待员工',
      dataIndex: 'host_employee',
      key: 'host_employee',
      render: (employee: any) => employee?.name || '-',
    },
    {
      title: '访问时间',
      dataIndex: 'visit_date',
      key: 'visit_date',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: VisitorStatus) => <VisitorStatusTag status={status} />,
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record: Visitor) => (
        <Space>
          <Button size="small">查看</Button>
          <Button size="small">编辑</Button>
          {record.status === VisitorStatus.PENDING && (
            <Button size="small" type="primary">
              审批
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold">访客管理</h1>
        <Button type="primary" icon={<PlusOutlined />}>
          新增访客
        </Button>
      </div>

      <div className="mb-4 flex gap-4">
        <Input
          placeholder="搜索访客姓名或电话"
          prefix={<SearchOutlined />}
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="w-64"
        />
        
        <Select
          placeholder="选择状态"
          value={filters.status}
          onChange={(status) => setFilters({ ...filters, status })}
          className="w-32"
          allowClear
        >
          <Option value={VisitorStatus.PENDING}>待审批</Option>
          <Option value={VisitorStatus.APPROVED}>已审批</Option>
          <Option value={VisitorStatus.CHECKED_IN}>已签到</Option>
          <Option value={VisitorStatus.CHECKED_OUT}>已签出</Option>
          <Option value={VisitorStatus.REJECTED}>已拒绝</Option>
        </Select>

        <RangePicker
          onChange={(dates) => {
            if (dates) {
              setFilters({
                ...filters,
                dateRange: [dates[0]!.toISOString(), dates[1]!.toISOString()],
              });
            } else {
              setFilters({ ...filters, dateRange: undefined });
            }
          }}
        />
      </div>

      <Table
        columns={columns}
        dataSource={visitors?.items || []}
        loading={isLoading}
        rowKey="id"
        pagination={{
          total: visitors?.total,
          pageSize: visitors?.page_size,
          current: visitors?.page,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条记录`,
        }}
      />
    </div>
  );
};
```

### 3. 仪表板模块

#### 仪表板组件
```typescript
// src/pages/dashboard/DashboardPage.tsx
import React from 'react';
import { Row, Col, Card, Statistic, Progress } from 'antd';
import { UserOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useGetDashboardStatsQuery } from '@/store/api/dashboardAPI';
import { VisitorChart } from '@/components/charts/VisitorChart';
import { RecentVisitors } from '@/components/dashboard/RecentVisitors';

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading } = useGetDashboardStatsQuery();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">仪表板</h1>
      
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日访客"
              value={stats?.today_visitors || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待审批"
              value={stats?.pending_approvals || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已签到"
              value={stats?.checked_in || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="本月总访客"
              value={stats?.month_visitors || 0}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="访客趋势" loading={isLoading}>
            <VisitorChart data={stats?.visitor_trend || []} />
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card title="最近访客" loading={isLoading}>
            <RecentVisitors visitors={stats?.recent_visitors || []} />
          </Card>
        </Col>
      </Row>
    </div>
  );
};
```

## API集成

### RTK Query API配置
```typescript
// src/store/api/baseAPI.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '@/store';

export const baseAPI = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.accessToken;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Visitor', 'Employee', 'Department', 'Site'],
  endpoints: () => ({}),
});
```

### 访客API
```typescript
// src/store/api/visitorsAPI.ts
import { baseAPI } from './baseAPI';
import { Visitor, CreateVisitorRequest, UpdateVisitorRequest } from '@/types/visitor';

export const visitorsAPI = baseAPI.injectEndpoints({
  endpoints: (builder) => ({
    getVisitors: builder.query<{
      items: Visitor[];
      total: number;
      page: number;
      page_size: number;
    }, {
      search?: string;
      status?: string;
      page?: number;
      page_size?: number;
    }>({
      query: (params) => ({
        url: '/visitors',
        params,
      }),
      providesTags: ['Visitor'],
    }),
    
    getVisitor: builder.query<Visitor, string>({
      query: (id) => `/visitors/${id}`,
      providesTags: (result, error, id) => [{ type: 'Visitor', id }],
    }),
    
    createVisitor: builder.mutation<Visitor, CreateVisitorRequest>({
      query: (visitor) => ({
        url: '/visitors',
        method: 'POST',
        body: visitor,
      }),
      invalidatesTags: ['Visitor'],
    }),
    
    updateVisitor: builder.mutation<Visitor, { id: string; visitor: UpdateVisitorRequest }>({
      query: ({ id, visitor }) => ({
        url: `/visitors/${id}`,
        method: 'PUT',
        body: visitor,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Visitor', id }],
    }),
    
    approveVisitor: builder.mutation<Visitor, { id: string; notes?: string }>({
      query: ({ id, notes }) => ({
        url: `/visitors/${id}/approve`,
        method: 'POST',
        body: { notes },
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Visitor', id }],
    }),
  }),
});

export const {
  useGetVisitorsQuery,
  useGetVisitorQuery,
  useCreateVisitorMutation,
  useUpdateVisitorMutation,
  useApproveVisitorMutation,
} = visitorsAPI;
```

## 样式和主题

### Tailwind CSS配置
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false, // 避免与Ant Design冲突
  },
};
```

### Ant Design主题定制
```typescript
// src/styles/theme.ts
import { theme } from 'antd';

export const customTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    borderRadius: 6,
    fontSize: 14,
  },
  components: {
    Button: {
      borderRadius: 6,
    },
    Card: {
      borderRadius: 8,
    },
  },
};
```

## 国际化

### i18n配置
```typescript
// src/locales/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zhCN from './zh-CN.json';
import enUS from './en-US.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      'zh-CN': { translation: zhCN },
      'en-US': { translation: enUS },
    },
    lng: 'zh-CN',
    fallbackLng: 'zh-CN',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
```

### 语言文件示例
```json
// src/locales/zh-CN.json
{
  "common": {
    "save": "保存",
    "cancel": "取消",
    "delete": "删除",
    "edit": "编辑",
    "view": "查看",
    "search": "搜索",
    "loading": "加载中...",
    "noData": "暂无数据"
  },
  "visitor": {
    "title": "访客管理",
    "name": "访客姓名",
    "phone": "联系电话",
    "purpose": "来访目的",
    "hostEmployee": "接待员工",
    "visitDate": "访问时间",
    "status": {
      "pending": "待审批",
      "approved": "已审批",
      "checkedIn": "已签到",
      "checkedOut": "已签出",
      "rejected": "已拒绝"
    }
  }
}
```

## 测试策略

### 单元测试
```typescript
// src/components/__tests__/VisitorStatusTag.test.tsx
import { render, screen } from '@testing-library/react';
import { VisitorStatusTag } from '../visitors/VisitorStatusTag';
import { VisitorStatus } from '@/types/visitor';

describe('VisitorStatusTag', () => {
  it('renders pending status correctly', () => {
    render(<VisitorStatusTag status={VisitorStatus.PENDING} />);
    expect(screen.getByText('待审批')).toBeInTheDocument();
  });

  it('renders approved status correctly', () => {
    render(<VisitorStatusTag status={VisitorStatus.APPROVED} />);
    expect(screen.getByText('已审批')).toBeInTheDocument();
  });
});
```

### 集成测试
```typescript
// src/pages/__tests__/VisitorListPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from '@/store';
import { VisitorListPage } from '../visitors/VisitorListPage';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <Provider store={store}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </Provider>
  );
};

describe('VisitorListPage', () => {
  it('renders visitor list correctly', async () => {
    renderWithProviders(<VisitorListPage />);
    
    expect(screen.getByText('访客管理')).toBeInTheDocument();
    expect(screen.getByText('新增访客')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByRole('table')).toBeInTheDocument();
    });
  });
});
```

## 性能优化

### 代码分割
```typescript
// src/routes/index.tsx
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Spin } from 'antd';

const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage'));
const VisitorListPage = lazy(() => import('@/pages/visitors/VisitorListPage'));
const EmployeeListPage = lazy(() => import('@/pages/employees/EmployeeListPage'));

const LoadingSpinner = () => (
  <div className="flex justify-center items-center h-64">
    <Spin size="large" />
  </div>
);

export const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/visitors" element={<VisitorListPage />} />
        <Route path="/employees" element={<EmployeeListPage />} />
      </Routes>
    </Suspense>
  );
};
```

### 虚拟滚动
```typescript
// src/components/VirtualTable.tsx
import { FixedSizeList as List } from 'react-window';
import { Table } from 'antd';

interface VirtualTableProps {
  data: any[];
  height: number;
  itemHeight: number;
  columns: any[];
}

export const VirtualTable: React.FC<VirtualTableProps> = ({
  data,
  height,
  itemHeight,
  columns,
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      {/* 渲染表格行 */}
    </div>
  );

  return (
    <List
      height={height}
      itemCount={data.length}
      itemSize={itemHeight}
    >
      {Row}
    </List>
  );
};
```

## 部署配置

### Vite构建配置
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          antd: ['antd'],
          charts: ['echarts'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### Docker配置
```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx配置
```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # 处理前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

本前端开发指南提供了完整的前端开发框架和最佳实践，确保团队能够高效开发出高质量的前端应用。 