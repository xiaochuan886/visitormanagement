# 访客管理系统 UI 设计规范

## 概述

本文档定义了访客管理系统的UI设计规范，确保所有界面保持一致的视觉风格和用户体验。

## 设计原则

### 1. 一致性 (Consistency)
- 统一的色彩系统
- 一致的组件样式
- 标准化的交互模式

### 2. 简洁性 (Simplicity)
- 清晰的信息层次
- 简化的操作流程
- 直观的界面布局

### 3. 可访问性 (Accessibility)
- 符合WCAG 2.1标准
- 支持键盘导航
- 适当的对比度

### 4. 响应式 (Responsive)
- 适配多种设备尺寸
- 优化触摸交互
- 流畅的动画效果

## 色彩系统

### 主色调
- **主蓝色**: #667eea (渐变起始)
- **次蓝色**: #764ba2 (渐变结束)
- **功能蓝**: #007AFF (iOS风格)
- **微信绿**: #07C160 (小程序风格)

### 状态色彩
- **成功**: #10B981 (绿色)
- **警告**: #F59E0B (橙色)
- **错误**: #EF4444 (红色)
- **信息**: #3B82F6 (蓝色)

### 中性色彩
- **文本主色**: #111827
- **文本次色**: #6B7280
- **边框色**: #E5E7EB
- **背景色**: #F9FAFB

## 字体规范

### 字体族
- **中文**: PingFang SC, Microsoft YaHei, sans-serif
- **英文**: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto
- **代码**: SFMono-Regular, Consolas, monospace

### 字体大小
- **标题1**: 2rem (32px)
- **标题2**: 1.5rem (24px)
- **标题3**: 1.25rem (20px)
- **正文**: 1rem (16px)
- **小字**: 0.875rem (14px)
- **极小**: 0.75rem (12px)

### 字重
- **粗体**: 600
- **中等**: 500
- **常规**: 400

## 间距系统

### 基础间距单位
- **基准**: 4px
- **小间距**: 8px (2 units)
- **中间距**: 16px (4 units)
- **大间距**: 24px (6 units)
- **超大间距**: 32px (8 units)

### 组件间距
- **卡片内边距**: 24px
- **表单项间距**: 16px
- **按钮内边距**: 12px 24px
- **列表项高度**: 64px

## 组件规范

### 按钮
```css
/* 主要按钮 */
.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
}

/* 次要按钮 */
.btn-secondary {
  background: white;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: 8px;
  padding: 12px 24px;
}
```

### 卡片
```css
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 24px;
}
```

### 表单
```css
.form-input {
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}
```

## 图标规范

### 图标库
- **主要**: FontAwesome 6.4.0
- **风格**: 实心 (fas) 为主，线性 (far) 为辅
- **大小**: 16px, 20px, 24px, 32px

### 常用图标
- **用户**: fas fa-user
- **访客**: fas fa-users
- **设置**: fas fa-cog
- **仪表板**: fas fa-tachometer-alt
- **审批**: fas fa-check-circle
- **签到**: fas fa-qrcode

## 布局规范

### 网格系统
- **容器最大宽度**: 1280px
- **列数**: 12列
- **间隙**: 24px
- **断点**:
  - sm: 640px
  - md: 768px
  - lg: 1024px
  - xl: 1280px

### 页面结构
```
┌─────────────────────────────────┐
│           Header (64px)          │
├─────────────┬───────────────────┤
│             │                   │
│  Sidebar    │   Main Content    │
│  (256px)    │                   │
│             │                   │
└─────────────┴───────────────────┘
```

## 移动端规范

### 设备适配
- **iPhone**: 375px × 812px (iPhone 14 Pro)
- **Android**: 360px × 800px (标准尺寸)
- **小程序**: 375px × 812px (微信标准)

### 触摸目标
- **最小尺寸**: 44px × 44px
- **推荐尺寸**: 48px × 48px
- **间距**: 8px

### 导航模式
- **标签栏高度**: 50px (小程序) / 83px (iOS)
- **导航栏高度**: 44px
- **状态栏高度**: 44px

## 动画规范

### 过渡时间
- **快速**: 150ms
- **标准**: 300ms
- **慢速**: 500ms

### 缓动函数
- **标准**: ease-in-out
- **进入**: ease-out
- **退出**: ease-in

### 常用动画
```css
/* 悬停效果 */
.hover-lift {
  transition: transform 0.3s ease;
}
.hover-lift:hover {
  transform: translateY(-4px);
}

/* 淡入效果 */
.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

## 状态设计

### 加载状态
- **骨架屏**: 用于内容加载
- **加载指示器**: 用于操作反馈
- **进度条**: 用于长时间操作

### 空状态
- **无数据**: 友好的插图 + 引导文案
- **错误状态**: 清晰的错误信息 + 解决方案
- **成功状态**: 积极的反馈 + 后续操作

## 平台特定规范

### Web端
- **最小分辨率**: 1024 × 768
- **推荐分辨率**: 1920 × 1080
- **浏览器支持**: Chrome 90+, Firefox 88+, Safari 14+

### iOS App
- **设计规范**: Apple Human Interface Guidelines
- **安全区域**: 考虑刘海和Home指示器
- **系统字体**: SF Pro Display

### 微信小程序
- **设计规范**: 微信小程序设计指南
- **胶囊按钮**: 保留右上角胶囊区域
- **底部安全区**: 考虑iPhone底部安全区

## 可访问性

### 颜色对比
- **正常文本**: 4.5:1
- **大文本**: 3:1
- **非文本元素**: 3:1

### 键盘导航
- **Tab顺序**: 逻辑清晰
- **焦点指示**: 明显可见
- **快捷键**: 常用功能支持

### 屏幕阅读器
- **语义化标签**: 正确使用HTML标签
- **ARIA标签**: 补充必要的无障碍信息
- **替代文本**: 为图片提供描述

## 质量检查

### 设计一致性
- [ ] 色彩使用符合规范
- [ ] 字体大小和字重正确
- [ ] 间距符合网格系统
- [ ] 组件样式统一

### 响应式检查
- [ ] 移动端适配良好
- [ ] 触摸目标大小合适
- [ ] 内容在小屏幕上可读

### 性能优化
- [ ] 图片格式和大小优化
- [ ] CSS和JS文件压缩
- [ ] 字体文件优化加载

### 可访问性检查
- [ ] 颜色对比度达标
- [ ] 键盘导航流畅
- [ ] 屏幕阅读器兼容

## 更新记录

- **v1.0.0** (2024-12-27): 初始版本，定义基础设计规范
- 后续版本将根据用户反馈和业务需求进行迭代更新 