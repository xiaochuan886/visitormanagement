# 访客管理系统设计系统规范

## 📋 文档信息
- **版本**: v1.0.0
- **创建日期**: 2024-12-27
- **维护者**: UI/UX设计团队
- **适用范围**: 访客管理系统全平台设计
- **技术栈**: React + Ant Design + Tailwind CSS

## 🎨 设计系统概述

### 设计原则
1. **一致性**: 统一的视觉语言和交互模式
2. **可访问性**: 符合WCAG 2.1 AA标准
3. **可扩展性**: 支持多主题和个性化定制
4. **效率性**: 提高设计和开发效率

### 设计系统架构
```
设计系统
├── 设计原则 (Design Principles)
├── 设计令牌 (Design Tokens)
├── 基础组件 (Foundation)
│   ├── 颜色系统 (Colors)
│   ├── 字体系统 (Typography)
│   ├── 间距系统 (Spacing)
│   ├── 图标系统 (Icons)
│   └── 布局栅格 (Grid)
├── UI组件 (Components)
│   ├── 基础组件 (Basic)
│   ├── 表单组件 (Form)
│   ├── 导航组件 (Navigation)
│   ├── 反馈组件 (Feedback)
│   └── 数据展示 (Data Display)
├── 模式规范 (Patterns)
│   ├── 页面布局 (Layout)
│   ├── 导航模式 (Navigation)
│   ├── 表单模式 (Forms)
│   └── 数据模式 (Data)
└── 品牌资产 (Brand Assets)
```

## 🎨 基础设计系统

### 颜色系统 (Color System)

#### 主色调 (Primary Colors)
```css
/* 主品牌色 - 蓝色系 */
--primary-50: #E6F7FF;
--primary-100: #BAE7FF;
--primary-200: #91D5FF;
--primary-300: #69C0FF;
--primary-400: #40A9FF;
--primary-500: #1890FF; /* 主色 */
--primary-600: #096DD9;
--primary-700: #0050B3;
--primary-800: #003A8C;
--primary-900: #002766;

/* 辅助色 - 紫色系 */
--secondary-50: #F9F0FF;
--secondary-100: #EFDBFF;
--secondary-200: #D3ADF7;
--secondary-300: #B37FEB;
--secondary-400: #9254DE;
--secondary-500: #722ED1; /* 辅助色 */
--secondary-600: #531DAB;
--secondary-700: #391085;
--secondary-800: #22075E;
--secondary-900: #120338;
```

#### 功能色彩 (Functional Colors)
```css
/* 成功色 - 绿色系 */
--success-50: #F6FFED;
--success-500: #52C41A;
--success-600: #389E0D;

/* 警告色 - 橙色系 */
--warning-50: #FFF7E6;
--warning-500: #FA8C16;
--warning-600: #D46B08;

/* 错误色 - 红色系 */
--error-50: #FFF2F0;
--error-500: #FF4D4F;
--error-600: #CF1322;

/* 信息色 - 蓝色系 */
--info-50: #E6F7FF;
--info-500: #1890FF;
--info-600: #096DD9;
```

#### 中性色彩 (Neutral Colors)
```css
/* 文字色彩 */
--text-primary: #262626;   /* 主要文字 */
--text-secondary: #595959; /* 次要文字 */
--text-tertiary: #8C8C8C;  /* 辅助文字 */
--text-quaternary: #BFBFBF; /* 提示文字 */

/* 背景色彩 */
--bg-primary: #FFFFFF;     /* 主背景 */
--bg-secondary: #FAFAFA;   /* 次背景 */
--bg-tertiary: #F5F5F5;    /* 三级背景 */
--bg-quaternary: #F0F0F0;  /* 四级背景 */

/* 边框色彩 */
--border-primary: #D9D9D9;   /* 主边框 */
--border-secondary: #E8E8E8; /* 次边框 */
--border-tertiary: #F0F0F0;  /* 三级边框 */
```

### 字体系统 (Typography)

#### 字体族 (Font Family)
```css
/* 主字体 */
--font-family-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                       Roboto, 'Helvetica Neue', Arial, sans-serif;

/* 等宽字体 */
--font-family-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', 
                    Menlo, Courier, monospace;

/* 数字字体 */
--font-family-number: 'Helvetica Neue', Helvetica, Arial, sans-serif;
```

#### 字体大小 (Font Size)
```css
/* 标题字体 */
--font-size-h1: 32px;  /* 页面标题 */
--font-size-h2: 24px;  /* 区块标题 */
--font-size-h3: 20px;  /* 卡片标题 */
--font-size-h4: 16px;  /* 列表标题 */
--font-size-h5: 14px;  /* 小标题 */

/* 正文字体 */
--font-size-lg: 16px;  /* 大号正文 */
--font-size-base: 14px; /* 基础正文 */
--font-size-sm: 12px;  /* 小号正文 */
--font-size-xs: 10px;  /* 辅助文字 */
```

#### 字重 (Font Weight)
```css
--font-weight-light: 300;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

#### 行高 (Line Height)
```css
--line-height-tight: 1.2;   /* 紧凑行高 */
--line-height-normal: 1.5;  /* 标准行高 */
--line-height-relaxed: 1.7; /* 宽松行高 */
```

### 间距系统 (Spacing System)

#### 间距标准 (Spacing Scale)
```css
/* 基础间距单位 = 4px */
--space-0: 0px;
--space-1: 4px;   /* 0.25rem */
--space-2: 8px;   /* 0.5rem */
--space-3: 12px;  /* 0.75rem */
--space-4: 16px;  /* 1rem */
--space-5: 20px;  /* 1.25rem */
--space-6: 24px;  /* 1.5rem */
--space-8: 32px;  /* 2rem */
--space-10: 40px; /* 2.5rem */
--space-12: 48px; /* 3rem */
--space-16: 64px; /* 4rem */
--space-20: 80px; /* 5rem */
--space-24: 96px; /* 6rem */
```

#### 间距应用 (Spacing Usage)
- **内边距**: 组件内部元素间距
- **外边距**: 组件之间的间距
- **栅格间距**: 布局网格的间距
- **行间距**: 文本行之间的间距

### 圆角系统 (Border Radius)
```css
--radius-none: 0px;
--radius-sm: 2px;     /* 小圆角 */
--radius-base: 4px;   /* 基础圆角 */
--radius-md: 6px;     /* 中等圆角 */
--radius-lg: 8px;     /* 大圆角 */
--radius-xl: 12px;    /* 超大圆角 */
--radius-full: 50%;   /* 完全圆形 */
```

### 阴影系统 (Shadow System)
```css
/* 卡片阴影 */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 
               0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
             0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
             0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
             0 10px 10px -5px rgba(0, 0, 0, 0.04);

/* 特殊阴影 */
--shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
--shadow-focus: 0 0 0 3px rgba(66, 153, 225, 0.5);
```

## 🧩 组件规范

### 按钮组件 (Button)

#### 按钮类型
```typescript
interface ButtonProps {
  type: 'primary' | 'secondary' | 'tertiary' | 'danger' | 'ghost';
  size: 'large' | 'medium' | 'small';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  children: ReactNode;
}
```

#### 按钮样式规范
**主要按钮 (Primary)**:
- 背景色: `--primary-500`
- 文字色: `white`
- 悬浮态: `--primary-600`
- 按下态: `--primary-700`

**次要按钮 (Secondary)**:
- 背景色: `white`
- 边框色: `--primary-500`
- 文字色: `--primary-500`
- 悬浮态: `--primary-50` 背景

**尺寸规范**:
- 大号: 高度 40px，内边距 16px 24px
- 中号: 高度 32px，内边距 12px 16px  
- 小号: 高度 24px，内边距 8px 12px

### 表单组件 (Form)

#### 输入框 (Input)
```css
.input {
  height: 32px;
  padding: 4px 11px;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-base);
  font-size: var(--font-size-base);
  line-height: 1.5;
}

.input:focus {
  border-color: var(--primary-500);
  box-shadow: var(--shadow-focus);
  outline: none;
}

.input:disabled {
  background-color: var(--bg-quaternary);
  color: var(--text-quaternary);
  cursor: not-allowed;
}
```

#### 表单验证状态
**成功状态**:
- 边框色: `--success-500`
- 图标: 绿色对勾

**错误状态**:
- 边框色: `--error-500`
- 图标: 红色感叹号
- 错误信息: 红色文字，12px字号

**警告状态**:
- 边框色: `--warning-500`
- 图标: 橙色感叹号

### 导航组件 (Navigation)

#### 顶部导航栏
```css
.navbar {
  height: 64px;
  background: linear-gradient(135deg, var(--primary-500), var(--secondary-500));
  box-shadow: var(--shadow-base);
  display: flex;
  align-items: center;
  padding: 0 var(--space-6);
}

.navbar-logo {
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-bold);
  color: white;
}

.navbar-menu {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-4);
}
```

#### 侧边导航栏
```css
.sidebar {
  width: 240px;
  min-height: 100vh;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-secondary);
  padding: var(--space-4) 0;
}

.sidebar-collapsed {
  width: 64px;
}

.sidebar-item {
  height: 40px;
  padding: 0 var(--space-4);
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.sidebar-item:hover {
  background-color: var(--bg-secondary);
}

.sidebar-item.active {
  background-color: var(--primary-50);
  color: var(--primary-500);
  border-right: 3px solid var(--primary-500);
}
```

## 📱 响应式设计规范

### 断点系统 (Breakpoints)
```css
/* 断点定义 */
--breakpoint-xs: 0px;      /* 手机竖屏 */
--breakpoint-sm: 576px;    /* 手机横屏 */
--breakpoint-md: 768px;    /* 平板竖屏 */
--breakpoint-lg: 992px;    /* 平板横屏/小型桌面 */
--breakpoint-xl: 1200px;   /* 桌面 */
--breakpoint-xxl: 1600px;  /* 大屏桌面 */
```

### 栅格系统 (Grid System)
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -12px;
}

.col {
  padding: 0 12px;
  flex: 1;
}

/* 响应式列宽 */
.col-xs-12 { width: 100%; }
.col-sm-6 { width: 50%; }
.col-md-4 { width: 33.333%; }
.col-lg-3 { width: 25%; }
```

### 移动端适配
- **触摸目标**: 最小 44px × 44px
- **文字大小**: 最小 14px，推荐 16px
- **间距调整**: 移动端间距增加 25%
- **导航模式**: 底部标签栏 + 汉堡菜单

## 🎯 交互设计规范

### 动画规范 (Animation)
```css
/* 动画时长 */
--duration-fast: 150ms;
--duration-base: 250ms;
--duration-slow: 350ms;

/* 缓动函数 */
--ease-out: cubic-bezier(0.215, 0.61, 0.355, 1);
--ease-in: cubic-bezier(0.55, 0.055, 0.675, 0.19);
--ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1);

/* 常用动画 */
.fade-in {
  animation: fadeIn var(--duration-base) var(--ease-out);
}

.slide-up {
  animation: slideUp var(--duration-base) var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
```

### 状态反馈
- **加载状态**: 显示加载动画或骨架屏
- **空状态**: 提供友好的空状态插图和文案
- **错误状态**: 清晰的错误信息和恢复建议
- **成功状态**: 及时的成功反馈和下一步引导

### 微交互设计
- **悬浮反馈**: 鼠标悬浮时的视觉变化
- **点击反馈**: 按钮按下时的视觉反应
- **拖拽反馈**: 拖拽过程中的视觉提示
- **操作确认**: 危险操作的二次确认

## 🎨 主题系统

### 亮色主题 (Light Theme)
```css
[data-theme="light"] {
  --bg-app: #ffffff;
  --text-primary: #262626;
  --border-color: #d9d9d9;
}
```

### 暗色主题 (Dark Theme)
```css
[data-theme="dark"] {
  --bg-app: #141414;
  --text-primary: #ffffff;
  --border-color: #434343;
}
```

### 主题切换
- 提供主题切换组件
- 保存用户主题偏好
- 支持系统主题跟随
- 平滑的主题切换动画

## 📏 设计令牌 (Design Tokens)

### 令牌结构
```json
{
  "color": {
    "primary": {
      "50": "#E6F7FF",
      "500": "#1890FF",
      "900": "#002766"
    }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px"
  },
  "typography": {
    "fontSize": {
      "sm": "12px",
      "base": "14px",
      "lg": "16px"
    }
  }
}
```

### 令牌管理
- **版本控制**: 令牌变更版本管理
- **同步机制**: 设计和开发令牌同步
- **文档化**: 每个令牌的使用说明
- **验证工具**: 令牌使用规范检查

## 🔧 工具与流程

### 设计工具
- **Figma**: 主要设计工具，组件库管理
- **Sketch**: 辅助设计工具，资源输出
- **Abstract**: 设计版本控制
- **Zeplin**: 设计交付和标注

### 开发集成
- **Storybook**: 组件库文档和演示
- **Chromatic**: 组件视觉回归测试
- **Design Tokens**: 令牌管理和同步
- **Linting**: 设计系统使用规范检查

### 质量保证
- **设计评审**: 定期设计系统评审
- **可用性测试**: 组件可用性验证
- **性能监控**: 组件性能影响评估
- **维护计划**: 定期更新和优化

---

*本设计系统规范将确保访客管理系统在各个平台上保持一致的用户体验，提高设计和开发效率，同时支持系统的可扩展性和维护性。* 