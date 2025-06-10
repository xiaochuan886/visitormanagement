# 访客管理系统 Cursor 规则使用指南

## 概述
本指南将详细说明如何使用为访客管理系统创建的9个Cursor规则文件，以最大化开发效率和代码质量。

## 规则文件结构

```
.cursor/rules/
├── 核心架构规则/
│   ├── visitor-management-core.mdc     # 核心架构标准
│   ├── clean-architecture.mdc         # 清洁架构实现
│   └── security-standards.mdc         # 安全标准规范
├── 业务域规则/
│   ├── visitor-domain.mdc             # 访客业务域
│   ├── auth-domain.mdc                # 认证业务域
│   └── organization-domain.mdc        # 组织管理域
└── 开发场景规则/
    ├── api-development.mdc            # API开发规范
    ├── testing-standards.mdc          # 测试开发标准
    └── performance-optimization.mdc   # 性能优化规范
```

## 使用方式

### 1. Cursor编辑器中的自动激活
当您在Cursor中打开访客管理系统项目时，这些规则会自动加载并影响：
- **代码补全建议** - 根据规则提供符合架构的代码建议
- **错误检测** - 自动检查代码是否符合规范
- **重构建议** - 提供符合Clean Architecture的重构方案
- **性能优化提示** - 根据性能规范给出优化建议

### 2. 手动触发规则应用
在Cursor中可以通过以下方式手动应用规则：
- **Ctrl/Cmd + K** → 选择相关规则文件进行代码生成
- **右键菜单** → "Apply Cursor Rules" 选项
- **Chat功能** → 直接询问关于特定规则的问题

## 不同开发场景的使用指南

### 📋 新功能开发场景

#### 1. 创建新的API端点
**适用规则**: `api-development.mdc` + `clean-architecture.mdc` + `security-standards.mdc`

**使用步骤**:
1. 在Cursor中创建新的路由文件 (如: `new_feature_router.py`)
2. 输入 `@router.` 后，Cursor会根据api-development.mdc规则提供标准的端点模板
3. 系统会自动提示需要的依赖注入参数
4. 根据security-standards.mdc自动添加权限验证

**示例提示词**:
```
"请根据api-development.mdc规则创建一个访客签到的API端点"
```

#### 2. 实现新的业务逻辑
**适用规则**: `visitor-domain.mdc` + `clean-architecture.mdc`

**使用步骤**:
1. 在domain层创建新的实体或值对象
2. Cursor会根据visitor-domain.mdc提供状态管理模式
3. 自动生成符合Clean Architecture的分层结构
4. 提供域事件和验证逻辑的模板

### 🧪 测试开发场景

#### 1. 编写单元测试
**适用规则**: `testing-standards.mdc` + 相关业务域规则

**使用步骤**:
1. 创建测试文件 (`test_*.py`)
2. 输入测试类名，Cursor会提供符合naming convention的模板
3. 自动生成AAA模式的测试方法结构
4. 根据覆盖率要求提示需要测试的分支

**示例提示词**:
```
"按照testing-standards.mdc规则为VisitorService类创建完整的单元测试"
```

#### 2. 集成测试编写
**适用规则**: `testing-standards.mdc` + `api-development.mdc`

**使用步骤**:
1. 创建API集成测试
2. 自动生成httpx.AsyncClient的使用模式
3. 提供多租户测试的模板
4. 根据安全规则添加认证测试

### ⚡ 性能优化场景

#### 1. 数据库查询优化
**适用规则**: `performance-optimization.mdc` + `clean-architecture.mdc`

**使用步骤**:
1. 识别慢查询代码
2. Cursor根据性能规则提供优化建议
3. 自动建议索引创建和查询重构
4. 提供分页和批量处理的实现

**示例提示词**:
```
"根据performance-optimization.mdc规则优化这个访客查询方法的性能"
```

#### 2. 缓存实现
**适用规则**: `performance-optimization.mdc` + `security-standards.mdc`

**使用步骤**:
1. 编写需要缓存的服务方法
2. 自动提供Redis缓存模式的实现
3. 根据安全规则确保缓存数据的租户隔离
4. 生成缓存失效策略

### 🔐 安全功能开发场景

#### 1. 认证授权实现
**适用规则**: `auth-domain.mdc` + `security-standards.mdc`

**使用步骤**:
1. 创建认证相关的服务类
2. 自动提供JWT token管理的实现
3. 根据RBAC规则生成权限检查逻辑
4. 提供多租户隔离的认证流程

#### 2. 数据验证实现
**适用规则**: `visitor-domain.mdc` + `security-standards.mdc`

**使用步骤**:
1. 创建Pydantic模型
2. 自动添加中国手机号、身份证等验证规则
3. 提供输入清理和SQL注入防护
4. 生成审计日志记录

## Chat功能使用技巧

### 1. 架构咨询
**提示词模板**:
```
"根据clean-architecture.mdc规则，这个类应该放在哪一层？"
"按照visitor-management-core.mdc的要求，如何实现多租户隔离？"
```

### 2. 代码审查
**提示词模板**:
```
"请根据所有规则检查这段代码是否符合规范"
"这个API实现是否满足api-development.mdc的要求？"
```

### 3. 重构建议
**提示词模板**:
```
"如何重构这个方法以符合performance-optimization.mdc的性能要求？"
"按照security-standards.mdc重构这个认证逻辑"
```

## 规则组合使用策略

### 1. 全栈功能开发
**规则组合**: 核心架构 + 业务域 + 开发场景
- 从clean-architecture.mdc确定分层结构
- 用相关业务域规则实现业务逻辑
- 按api-development.mdc实现API层
- 用testing-standards.mdc编写测试

### 2. 性能调优项目
**规则组合**: performance-optimization.mdc + visitor-management-core.mdc
- 使用性能基准进行问题识别
- 应用优化策略和最佳实践
- 验证改进效果

### 3. 安全加固项目
**规则组合**: security-standards.mdc + auth-domain.mdc
- 全面应用安全规范
- 强化认证授权流程
- 实现安全审计机制

## 团队协作最佳实践

### 1. 规则遵循检查清单
在代码审查时，使用以下检查清单：
- [ ] 是否符合Clean Architecture分层要求？
- [ ] 是否实现了多租户隔离？
- [ ] API是否包含适当的错误处理？
- [ ] 是否有对应的单元测试？
- [ ] 性能是否满足基准要求？
- [ ] 安全验证是否完整？

### 2. 规则更新流程
1. **提出更新需求** - 基于实际使用经验
2. **团队讨论** - 评估影响和必要性  
3. **更新规则文件** - 修改对应的.mdc文件
4. **团队培训** - 确保所有人了解新规则
5. **应用验证** - 在实际项目中验证效果

### 3. 新成员入职
1. **规则文档学习** - 阅读所有规则文件
2. **实践练习** - 使用规则完成小任务
3. **代码审查参与** - 观察规则在实际中的应用
4. **问题反馈** - 提出使用中的疑问和建议

## 故障排除

### 1. 规则不生效
**可能原因**:
- `.cursor/rules/` 目录不在项目根目录
- 规则文件语法错误
- Cursor需要重启

**解决方案**:
- 检查文件位置和语法
- 重启Cursor编辑器
- 检查mdc引用语法是否正确

### 2. 规则冲突
**可能原因**:
- 不同规则文件之间存在矛盾
- 规则过于严格导致无法实现

**解决方案**:
- 检查规则依赖关系
- 调整规则优先级
- 根据实际需求微调规则

### 3. 性能影响
**可能原因**:
- 规则过于复杂
- 实时检查过于频繁

**解决方案**:
- 简化复杂规则
- 调整检查频率
- 选择性启用规则

## 持续改进

### 1. 规则效果评估
定期评估规则使用效果：
- **代码质量指标** - 缺陷率、技术债务
- **开发效率指标** - 开发速度、代码复用率
- **团队满意度** - 开发体验、学习曲线

### 2. 规则优化建议
- 收集团队反馈和使用痛点
- 分析实际项目中的规则应用情况
- 根据技术栈更新调整规则内容
- 定期review和精简不必要的规则

## 总结
通过合理使用这些Cursor规则，可以显著提升访客管理系统的开发效率和代码质量。关键是要理解每个规则的适用场景，并在实际开发中灵活组合使用。 