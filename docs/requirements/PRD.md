# 访客管理系统产品需求文档 (PRD) v2.2

## 📋 文档信息
- **版本**: v2.2.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-18
- **维护者**: 产品经理AI
- **适用角色**: 产品经理、开发团队、业务干系人
- **依赖文档**: Backend_API_Reference.md, Configuration_Engine_Guide.md
- **重大更新**: 完善四大核心场景配置需求、门岗前台全流程功能、React生态技术选型

## 🎯 产品概述

### 产品愿景
打造一个**场景化配置驱动**的企业级智能访客管理平台，支持从访客申请到离园的全流程闭环管理，为企业提供安全、高效、智能的访客管理服务。

### 产品定位
- **目标市场**: 中大型企业、园区、政府机构、工业园区
- **核心价值**: 安全防控 + 效率提升 + 智能体验 + 场景化配置
- **竞争优势**: Clean Architecture + 多场景配置引擎 + 全流程闭环

### 技术优势现状评估
- ✅ **多租户架构**: 支持SaaS部署，租户数据完全隔离
- ✅ **基础配置引擎**: 表单配置、工作流配置、业务规则引擎、空间配置
- ⚠️ **场景化配置**: 需要增强，支持四大场景模板和场景间智能路由
- ❌ **全流程覆盖**: 缺乏门岗放行和前台签到功能
- ✅ **高性能**: 28个API端点，响应时间<200ms，支持1000+并发
- ✅ **Clean Architecture + DDD**: 成熟的领域驱动设计架构

## 👥 用户分析 (新增岗位角色)

### 主要用户群体

#### 1. 访客 (Visitor) - 无变化
**用户特征**: 临时性用户，不熟悉企业环境
**核心需求**: 简单的在线预约流程、清晰的访问指引、快速的签到签出体验

#### 2. 员工 (Employee) - 四大业务场景细分
**用户特征**: 日常工作需要接待访客，熟悉企业内部流程
**核心需求场景**:

**场景2.1: 员工邀约已知访客**
- 直接填入访客完整信息(姓名、电话、身份证、来访事由)
- 预设访问权限和访问区域
- 快速审批流程或自动通过
- 访客仅需确认到访时间和查看二维码

**场景2.2: 员工邀约未知访客**  
- 员工创建邀请事件(企业开放日、会议、培训等)
- 生成邀请链接和邀请码，设置填报人数限制
- 访客通过链接填写个人信息后等待审批
- 支持邀请码分享和访客信息批量审核

**场景2.3: 员工批量邀约**
- Excel模板批量导入访客信息
- 访客分组管理和标签分类
- 批量审批流程和统一通知
- 二维码批量生成和分发

#### 3. 管理员 (Admin) - 配置增强
**用户特征**: 负责访客管理规则制定，关注安全和数据分析
**核心需求**:
- **场景配置管理**: 不同业务场景的规则配置
- **多级审批配置**: 复杂组织架构的审批流程设计
- **权限区域配置**: 精细化的访问权限控制

#### 4. 门岗人员 (Security Guard) - 新增 🆕
**用户特征**: 
- 负责园区入口访客身份验证和放行
- 操作平板设备进行快速验证
- 处理异常情况和紧急事件

**核心需求**:
- **快速身份验证**: 二维码扫描、身份证验证、人脸识别
- **权限检查**: 访客区域权限、时间窗口验证
- **入园登记**: 访客证打印、临时通行证发放
- **实时状态**: 园区内访客实时监控

#### 5. 前台人员 (Receptionist) - 新增 🆕
**用户特征**:
- 负责访客到达后的接待和签到服务
- 协调被访人员和会议室资源
- 提供访客服务和问题解答

**核心需求**:
- **到达确认**: 访客签到和身份核验
- **被访人通知**: 实时通知被访人员访客到达
- **会议室协调**: 会议室预定和使用管理
- **访客服务**: 等候区管理、访客引导服务

#### 6. 部门访客负责人 (Department Visitor Manager) - 新增 🆕
**用户特征**:
- 负责本部门低风险访客的快速审批
- 通常为部门主管或指定的访客接待负责人
- 具有本部门访客管理的决策权限

**核心需求**:
- **部门访客审批**: 部门级访客申请的快速审批
- **低风险访客管理**: 常见访客类型的简化审批流程
- **部门权限配置**: 可配置的部门访客接待区域和权限
- **访客接待协调**: 协调部门内员工的访客接待安排

#### 7. 安保人员 (Security) - 角色调整
**更新定位**: 专注于安全监控和应急处理，不再负责日常验证

## 🎯 核心功能需求重构

### 🌟 **四大核心业务场景详细需求**

#### 场景1: 访客自主申请 (最常见场景)
**流程描述**: 访客主动发起访问申请 → 选择被访人/部门 → 等待审批 → 获得访问权限

**表单配置需求**:
```typescript
interface SelfRegistrationForm {
  visitor_info: {
    name: string,          // 必填
    phone: string,         // 必填 + 格式验证
    id_number: string,     // 必填 + 身份证验证
    company?: string,      // 可选
    purpose: string        // 必填，下拉选择
  },
  
  visit_target: {
    target_type: "person" | "department",  // 选择访问类型
    employee_selector?: {                  // 选择具体员工
      search_mode: "name_phone_match",     // 姓名+电话核对
      validation_required: true
    },
    department_selector?: {                // 选择访问部门  
      tree_display: true,
      manager_auto_assign: true            // 自动分配部门负责人审批
    }
  },
  
  visit_details: {
    visit_date: date,      // 智能推荐可用时间
    visit_duration: number,
    visitor_count: number, 
    access_areas: string[] // 基于被访人权限预设
  }
}
```

**工作流配置需求**:
- **个人访问路径**: 访客申请 → 被访员工审批 → 自动通过
- **部门访问路径**: 访客申请 → 部门负责人审批 → 自动通过
- **智能路由**: 根据访客选择自动分配不同审批流程

#### 场景2: 员工邀约已知访客 (快速通道)
**流程描述**: 员工预先知道访客信息 → 直接创建访客记录 → 自动审批 → 通知访客

**表单配置需求**:
```typescript
interface EmployeeInvitationKnownForm {
  inviter_info: {
    employee_id: string,   // 自动获取当前登录员工
    department: string,    // 自动获取
    authorization_level: string // 基于员工级别预设权限
  },
  
  visitor_info: {
    // 员工填写完整访客信息
    name: string,
    phone: string,
    id_number: string,
    company: string,
    position?: string
  },
  
  visit_authorization: {
    access_areas: string[],         // 员工可授权的区域范围
    visit_duration: number,         // 基于员工权限的时长限制
    authorization_type: "temporary" | "long_term", // 授权类型：临时授权/长期授权
    authorization_expiry?: date,    // 长期授权到期时间
    special_permissions?: string[], // 特殊权限申请
    auto_approval_eligible: boolean // 是否符合自动审批条件
  }
}
```

**自动审批规则与黑名单检查**:
- 员工权限级别 >= 3级 且 访客非敏感区域 → 自动通过
- 重复访客(30天内来过) 且 无黑名单记录 → 自动通过  
- 内部会议参与者 → 自动通过
- **黑名单处理策略**(可配置):
  - 策略1: 黑名单访客申请直接拒绝
  - 策略2: 黑名单访客需要安全主管审批
  - 策略3: 黑名单访客仅提示警告但允许通过

#### 场景3: 员工邀约未知访客 (活动邀请)
**流程描述**: 员工创建邀请活动 → 生成邀请链接 → 访客填写信息 → 员工批量审批

**多阶段表单需求**:
```typescript
interface EmployeeInvitationUnknownForm {
  // 阶段1: 员工创建邀请(Employee Actor)
  stage1_invitation_setup: {
    event_info: {
      event_name: string,        // 活动名称
      event_type: "meeting" | "training" | "visit" | "openday",
      event_date_range: {start: date, end: date},
      location: string,
      description: string
    },
    
    invitation_config: {
      max_participants: number,   // 最大邀请人数
      registration_deadline: date,
      approval_mode: "auto" | "manual" | "batch",
      invitation_code: string     // 自动生成邀请码
    },
    
    required_fields: string[],    // 要求访客填写的字段
    access_permissions: AccessConfig
  },
  
  // 阶段2: 访客填写信息(Visitor Actor)  
  stage2_visitor_registration: {
    invitation_code: string,      // 访客输入邀请码
    visitor_info: VisitorInfo,    // 基于阶段1配置的字段
    custom_questions: CustomAnswer[], // 活动特定问题
    agreement_confirmation: boolean   // 协议确认
  },
  
  // 阶段3: 员工批量审批(Employee Actor)
  stage3_batch_approval: {
    registration_list: VisitorRegistration[],
    batch_approval_action: "approve_all" | "approve_selected" | "reject_selected",
    approval_comments?: string,
    notification_settings: NotificationConfig
  }
}
```

#### 场景4: 员工批量邀约 (Excel导入)
**流程描述**: 员工准备Excel访客清单 → 批量导入系统 → 数据验证 → 批量审批 → 统一通知

**Excel模板需求**:
```typescript
interface BatchInvitationExcel {
  template_columns: [
    "访客姓名*", "手机号码*", "身份证号*", "所属公司", 
    "访问日期*", "访问时长", "访问区域", "备注"
  ],
  
  validation_rules: {
    max_rows: 100,           // 单次最多导入100人
    required_fields: ["name", "phone", "id_number", "visit_date"],
    format_validation: {
      phone: "中国大陆手机号",
      id_number: "18位身份证号",  
      visit_date: "YYYY-MM-DD格式"
    }
  },
  
  import_processing: {
    duplicate_check: "同一手机号30天内重复检查",
    blacklist_check: "访客黑名单检查(支持可配置处理策略)",
    permission_check: "员工权限范围检查",
    auto_grouping: "基于访问日期自动分组",
    authorization_type_config: "批量设置临时授权或长期授权"
  }
}
```

### 📊 **配置引擎增强需求**

#### 1. 场景配置管理器 (基于现有配置引擎扩展)

**需求背景**: 现有配置引擎支持表单配置、工作流配置、业务规则配置、空间配置，但各配置相互独立，缺乏场景化整合能力。

**管理后台场景编辑功能**: 
- 租户管理员可在管理后台创建、编辑、删除场景模板
- 支持场景模板预览和测试功能
- 提供场景模板的版本管理和回滚机制
- 支持从预设场景模板快速创建自定义场景

**功能需求**:

##### 1.1 场景模板管理
```typescript
interface ScenarioTemplate {
  // 场景基础信息
  scenario_id: string;
  scenario_name: string;
  scenario_type: "self_registration" | "employee_invitation_known" | 
                  "employee_invitation_unknown" | "batch_invitation" | "vip_visit";
  
  // 整合现有配置引擎
  form_configuration: {
    base_form_id: string;           // 基于现有表单配置
    conditional_fields: ConditionalField[];  // 扩展条件字段
    multi_stage_config?: MultiStageConfig;   // 新增多阶段支持
  };
  
  workflow_configuration: {
    base_workflow_id: string;       // 基于现有工作流配置
    scenario_specific_rules: WorkflowRule[];  // 场景特定规则
    approval_matrix: ApprovalMatrix;         // 新增审批矩阵
  };
  
  business_rules: {
    base_rules: string[];           // 继承基础业务规则
    scenario_overrides: BusinessRuleOverride[];  // 场景规则覆盖
    custom_validations: CustomValidation[];      // 自定义验证逻辑
  };
  
  // 新增配置
  access_permissions: {
    authorization_types: ["temporary", "long_term"],
    default_authorization_type: "temporary",
    long_term_expiry_days: number,
    area_restrictions: string[]
  };
  blacklist_handling: {
    strategy: "reject" | "require_security_approval" | "warning_only",
    custom_message: string,
    escalation_roles: string[]
  };
  notification_settings: NotificationConfig;
  ui_customization: UICustomizationConfig;
}
```

##### 1.2 场景特定字段类型 (扩展现有15种字段类型)
```typescript
// 基于现有字段类型，新增场景特定字段
interface ScenarioSpecificFields {
  employee_selector: {
    type: "employee_search",
    validation_mode: "name_phone_match" | "employee_id_match",
    search_scope: "department" | "site" | "all",
    auto_approval_rules: EmployeeBasedApprovalRule[]
  },
  
  department_selector: {
    type: "department_tree", 
    display_mode: "tree" | "dropdown" | "cascader",
    permission_check: "visitor_reception_enabled",
    department_manager_approval: boolean
  },
  
  invitation_batch: {
    type: "batch_invitation_builder",
    max_invitations: number,
    template_fields: string[],
    approval_threshold: number
  },
  
  time_slot_picker: {
    type: "smart_time_picker",
    working_hours_only: boolean,
    advance_booking_limits: TimeLimit,
    conflict_detection: boolean
  }
}
```

##### 1.3 多阶段表单引擎 (扩展现有表单配置)
```typescript
interface MultiStageFormConfig {
  stages: [
    {
      stage_id: "invitation_creation",
      actor_role: "employee", 
      form_config: FormConfiguration,  // 复用现有表单配置
      validation_rules: ValidationRule[],
      next_stage_triggers: StageTrigger[]
    },
    {
      stage_id: "visitor_registration",
      actor_role: "visitor",
      form_config: FormConfiguration,
      conditional_display: ConditionalLogic,  // 基于现有条件逻辑
      submission_limits: SubmissionLimit
    }
  ],
  
  stage_transitions: StageTransition[],
  completion_criteria: CompletionCriteria
}
```

#### 2. 智能审批引擎增强

基于现有工作流配置，增加以下能力：

```typescript
interface EnhancedApprovalEngine {
  // 基于现有工作流配置扩展
  approval_matrix: {
    scenario_based_routing: {
      "self_registration": ["selected_employee", "department_manager"],
      "employee_invitation_known": ["auto_approval"],
      "employee_invitation_unknown": ["inviter", "department_manager"],
      "batch_invitation": ["inviter", "department_manager", "security_manager"]
    },
    
    conditional_approval: {
      visitor_count_threshold: number,
      advance_booking_requirements: TimeRequirement,
      special_area_access: SpecialApprovalRule
    }
  },
  
  // 新增自动审批规则
  auto_approval_conditions: {
    employee_invitation_with_known_info: AutoApprovalRule,
    repeat_visitor_with_history: AutoApprovalRule,
    internal_meeting_participants: AutoApprovalRule
  }
}
```

### 🏢 **全流程访客管理功能**

#### 3. 访客申请阶段 (增强现有功能)

##### 3.1 场景化访客申请
**基于场景1: 访客自主申请**
- 访客类型选择: 个人访问 vs 部门访问
- 被访人搜索: 姓名+电话后台核对
- 被访部门选择: 部门访客负责人自动分配审批
- 智能时间推荐: 基于被访人日程的时间建议

**基于场景2: 员工邀约(已知访客信息)**
- 员工直接填入访客完整信息
- 预设访问权限和区域
- 快速审批或自动通过
- 访客仅需确认到访时间

**基于场景3: 员工邀约(未知访客信息)**
- 员工创建邀请事件(企业开放日、会议等)
- 生成邀请链接，限制填报人数
- 访客填写信息后，邀请人审批
- 支持邀请码分享和批量处理

**基于场景4: 员工批量邀约**
- Excel模板批量导入访客信息
- 批量审批流程
- 访客分组管理
- 统一通知和二维码生成

##### 3.2 智能表单引擎应用
- **条件显示逻辑**: 基于访问目的显示不同字段组合
- **智能验证**: 身份证、电话号码、邮箱格式自动验证
- **自动填充**: 基于历史访客记录的信息预填充
- **实时检查**: 被访人在岗状态、会议室可用性实时验证

#### 4. 门岗放行系统 🆕

##### 4.1 门岗工作台 (iPad应用)
**技术需求**: React Native 或 Web App，支持摄像头调用

**核心功能**:
```typescript
interface SecurityGateWorkstation {
  visitor_verification: {
    qr_code_scanner: "扫描访客预约二维码",
    manual_search: "按姓名/电话搜索访客记录", 
    id_card_reader: "身份证读卡器集成",
    face_recognition: "人脸识别比对(可选)"
  },
  
  access_control_check: {
    area_permissions: "检查访客授权访问区域",
    time_window_validation: "验证访问时间窗口有效性",
    blacklist_check: "访客黑名单检查",
    capacity_limits: "园区/建筑访客容量检查"
  },
  
  entry_processing: {
    visitor_badge_printing: "访客证/临时卡打印",
    vehicle_registration: "车辆信息登记",
    entrance_logging: "入园时间和入口记录",
    photo_capture: "现场拍照留档"
  },
  
  real_time_monitoring: {
    pending_arrivals: "今日预期访客列表",
    current_in_park: "园区内访客实时状态",
    alert_management: "异常访客提醒处理",
    emergency_procedures: "紧急情况处理流程"
  }
}
```

**API需求** (扩展现有API):
- `GET /api/v1/visitors/arrivals/today` - 今日预期到访
- `POST /api/v1/visitors/{visitor_id}/gate-entry` - 门岗入园登记  
- `GET /api/v1/visitors/in-park/real-time` - 园区内访客实时状态
- `POST /api/v1/security/alerts` - 安全提醒上报

##### 4.2 访客验证流程
1. **扫码验证**: 访客出示预约二维码 → 系统验证有效性
2. **身份核验**: 身份证读卡器验证 → 人脸识别比对(可选)
3. **权限检查**: 访问区域权限 → 时间窗口验证 → 特殊要求检查
4. **入园处理**: 访客证打印 → 车辆登记 → 入园记录
5. **状态更新**: 系统状态更新 → 通知前台和被访人

#### 5. 前台签到系统 🆕

##### 5.1 前台工作台 (PC应用)
**技术需求**: React Web应用 + 访客签到一体机

**核心功能**:
```typescript
interface ReceptionWorkstation {
  visitor_reception: {
    arrival_confirmation: "确认访客到达并更新状态",
    host_notification: "一键通知被访人员访客到达",
    waiting_area_management: "等候区座位分配和管理", 
    visitor_information_display: "访客信息展示和核验"
  },
  
  checkin_services: {
    health_screening: "健康码/体温检测记录",
    safety_briefing: "安全须知告知和确认",
    visitor_badge_activation: "访客证激活和权限设置",
    meeting_room_coordination: "会议室预定确认和分配"
  },
  
  host_coordination: {
    host_calling_system: "内部通讯系统呼叫被访人",
    calendar_integration: "被访人日程系统集成",
    meeting_room_booking: "会议室实时预定和变更",
    escort_arrangement: "陪同人员安排和通知"
  },
  
  visitor_services: {
    information_kiosk: "企业信息、地图导航服务",
    feedback_collection: "访客满意度调研",
    complaint_handling: "访客投诉处理流程",
    emergency_assistance: "紧急情况协助处理"
  }
}
```

**API需求** (扩展现有API):
- `POST /api/v1/visitors/{visitor_id}/reception-checkin` - 前台签到
- `GET /api/v1/employees/{employee_id}/availability` - 被访人在岗状态
- `POST /api/v1/notifications/host-arrival` - 通知被访人
- `GET /api/v1/meeting-rooms/availability` - 会议室可用性
- `POST /api/v1/visitor-services/feedback` - 访客反馈收集

##### 5.2 访客签到一体机
**硬件要求**: 触摸屏一体机，支持身份证读取、摄像头、打印机
**软件要求**: Web应用，支持离线缓存

**自助功能**:
- 访客自助签到确认
- 被访人呼叫系统
- 访客证自助打印
- 企业介绍和地图导航
- 访客满意度评价

#### 6. 离园管理系统 (扩展现有功能)

##### 6.1 智能离园检测
- **自动检测**: 基于门禁系统的自动离园记录
- **手动签出**: 前台或门岗手动确认访客离园
- **超时提醒**: 访问时间超时自动提醒和处理
- **区域追踪**: 访客在园区内的位置轨迹记录

##### 6.2 访问记录完善
- **完整访问日志**: 入园时间、签到时间、离园时间
- **访问区域记录**: 访客实际访问的区域和房间
- **异常情况记录**: 超时、区域违规等异常情况
- **满意度反馈**: 访客体验评价和改进建议

## 🏗️ 技术架构需求

### 🏗️ **React生态多端应用架构 (5+2备用方案)**

#### 技术选型统一: React生态
基于React生态构建统一的前端技术栈，确保代码复用和开发效率。包含5个主要应用端和2个移动端备用方案：

#### 1. 管理端 (React + TypeScript + Ant Design Pro)
**用户**: 租户管理员、员工、SaaS管理员
**技术栈**: React 18 + TypeScript + Ant Design Pro + UmiJS
**核心功能**: 
- 访客管理：审批、监控、报表
- 配置中心：四大场景模板配置、表单工作流配置
- 数据分析：访客行为分析、安全报告
- 系统管理：用户权限、组织架构、系统设置

#### 2. 访客端 (React + TypeScript + Ant Design Mobile)
**用户**: 访客  
**技术栈**: React 18 + TypeScript + Ant Design Mobile + 响应式设计
**核心功能**: 
- 四大场景访客申请：自主申请、邀请确认、活动报名、批量确认
- 状态查看：申请进度、审批结果、访问权限
- 二维码展示：入园凭证、实时状态更新
- 访客服务：企业信息、地图导航、满意度反馈

#### 3. 门岗端 (React Native/PWA + TypeScript)
**用户**: 门岗人员
**技术栈**: React Native 或 React PWA + TypeScript + 原生设备API
**核心功能**: 
- 身份验证：二维码扫描、身份证读取、人脸识别
- 权限检查：区域权限、时间窗口、黑名单检查
- 入园放行：访客证打印、车辆登记、入园记录
- 实时监控：今日预期访客、园区内访客状态
- **离线验证**：本地缓存今日访客数据，支持网络断开时的基础验证
**设备**: iPad/Android平板，集成摄像头、身份证读卡器、打印机

#### 3.1 门岗备用验证方案 (移动端APP/小程序) 🆕
**技术栈**: React Native APP + 微信小程序
**部署场景**:
- **设备故障备用**: 主设备故障时的应急验证方案
- **预算友好方案**: 为预算紧张的租户提供低成本部署选项
- **移动巡查**: 园区多入口或临时入口的移动验证

**核心功能**:
- **二维码扫描验证**: 使用手机摄像头扫描访客二维码
- **离线验证能力**: 预缓存今日访客列表，支持离线验证
- **简化入园登记**: 手动输入关键信息，同步到主系统
- **实时状态同步**: 网络恢复后自动同步验证记录

#### 4. 前台端 (React + TypeScript + Ant Design)
**用户**: 前台人员
**技术栈**: React 18 + TypeScript + Ant Design + 实时通信
**核心功能**: 
- 签到服务：访客到达确认、健康筛查、安全须知
- 被访人通知：实时通知、日程集成、会议室协调
- 访客服务：等候区管理、访客引导、投诉处理
- 协调管理：内部通讯、会议室预定、陪同安排
- **设备监控**：实时监控门岗设备状态，故障时启用备用方案
**设备**: PC工作站 + 双屏显示 + 内部通讯系统

#### 4.1 前台备用验证方案 (移动端APP/小程序) 🆕
**技术栈**: React Native APP + 微信小程序
**使用场景**:
- **多前台协同**: 大型企业多个前台的移动协调
- **临时前台设置**: 活动期间临时前台的快速部署
- **移动接待服务**: 前台人员主动迎接VIP访客时的移动验证

**核心功能**:
- **访客签到验证**: 扫码确认访客到达并更新状态
- **被访人快速通知**: 一键通知被访人员访客已到达
- **访客信息查询**: 快速查询访客详情和访问权限
- **离线应急处理**: 网络异常时的基础接待功能

#### 5. 设备端 (React Web App + PWA)
**用户**: 访客自助使用
**技术栈**: React 18 + TypeScript + PWA + 硬件集成API
**核心功能**: 
- 自助签到：访客到达自助确认、身份验证
- 信息展示：企业介绍、地图导航、通知公告
- 反馈收集：满意度评价、意见建议收集
- 硬件集成：身份证读取、人脸识别、访客证打印
**设备**: 触摸屏一体机(21寸以上)，支持身份证读卡器、摄像头、打印机

### 🔧 **后端增强需求**

#### 1. 场景配置引擎扩展 (基于现有28个API扩展)
**现有基础**: 表单配置、工作流配置、业务规则、空间配置完整API
**扩展需求**:
- 场景模板管理API (增加8个API端点)
- 多阶段表单配置API (增加6个API端点)
- 场景智能路由引擎 (增加4个API端点)
- 条件逻辑增强引擎 (升级现有API)

#### 2. 门岗前台业务API (新增25个API端点)
**门岗系统API**:
- `GET /api/v1/gate/arrivals/today` - 今日预期访客
- `POST /api/v1/gate/visitors/{id}/verify` - 访客身份验证
- `POST /api/v1/gate/visitors/{id}/entry` - 入园登记
- `GET /api/v1/gate/visitors/in-park` - 园区内访客状态
- `GET /api/v1/gate/cache/today-visitors` - 今日访客离线缓存数据 🆕
- `POST /api/v1/gate/offline/verify` - 离线验证记录上传 🆕

**前台系统API**:
- `POST /api/v1/reception/visitors/{id}/checkin` - 前台签到
- `POST /api/v1/reception/hosts/{id}/notify` - 通知被访人
- `GET /api/v1/reception/meeting-rooms/available` - 会议室可用性
- `POST /api/v1/reception/services/feedback` - 访客反馈

**移动端备用方案API**:
- `GET /api/v1/mobile/gate/sync` - 门岗移动端数据同步 🆕
- `POST /api/v1/mobile/gate/verify-qr` - 移动端二维码验证 🆕
- `GET /api/v1/mobile/reception/visitor-info/{qr_code}` - 扫码获取访客信息 🆕
- `POST /api/v1/mobile/reception/quick-checkin` - 移动端快速签到 🆕
- `GET /api/v1/mobile/offline/visitor-cache` - 移动端离线数据缓存 🆕

#### 3. 实时通信系统
- **WebSocket集群**: 支持多端实时状态同步 (门岗↔前台↔管理端)
- **推送通知**: 短信、邮件、企业微信、钉钉集成
- **设备监控**: 门岗和前台设备健康状态监控
- **消息队列**: Redis Stream + Celery分布式任务处理

#### 4. 硬件集成中间件
- **统一硬件抽象层**: 支持多厂商设备集成
- **身份证读卡器**: 支持华虹、德卡、明华等主流厂商
- **人脸识别**: 支持海康威视、大华、商汤等算法
- **打印机控制**: 支持斑马、TSC、佳博等热敏打印机
- **门禁集成**: 支持海康门禁、大华门禁系统对接

## 🔧 **关键场景需求补充**

### 1. 离线支持与网络异常处理 🆕

#### 1.1 设备端离线能力
**门岗离线验证**:
```typescript
interface OfflineGateSystem {
  cache_management: {
    today_visitors: "预缓存当日所有预期访客信息",
    blacklist_cache: "缓存黑名单数据，离线时进行基础检查",
    cache_update_strategy: "每2小时或网络恢复时自动更新缓存",
    cache_expiry: "缓存数据24小时后自动过期"
  },
  
  offline_verification: {
    qr_code_validation: "基于本地缓存验证二维码有效性",
    basic_permission_check: "检查访客基础权限和时间窗口",
    offline_entry_log: "本地记录入园信息，网络恢复后同步",
    fallback_mode: "网络断开超过30分钟自动进入离线模式"
  },
  
  sync_strategy: {
    network_recovery_detection: "自动检测网络连接恢复",
    incremental_sync: "增量同步离线期间的验证记录",
    conflict_resolution: "处理离线记录与服务器数据的冲突",
    sync_priority: "优先同步安全相关和异常记录"
  }
}
```

#### 1.2 移动端离线支持
**APP/小程序离线功能**:
- **数据预缓存**: 工作开始时自动下载今日访客数据
- **离线验证**: 基于本地缓存进行二维码验证
- **本地存储**: 使用SQLite存储离线验证记录
- **智能同步**: 网络恢复时自动上传离线记录

### 2. 访客数据隐私保护增强 🆕

#### 2.1 数据脱敏展示
```typescript
interface DataMaskingRules {
  phone_masking: "139****8888", // 手机号中间4位脱敏
  id_number_masking: "1234**********5678", // 身份证号中间脱敏
  sensitive_data_access_log: "记录谁在何时查看了完整信息",
  role_based_masking: "根据用户角色决定脱敏程度"
}
```

#### 2.2 数据保留策略
- **访客离园后**: 7天内删除身份证照片和人脸识别数据
- **访问记录**: 仅保留访问时间、目的地等非敏感统计信息
- **审计日志**: 敏感数据访问日志保留1年
- **数据导出**: 支持访客申请删除个人数据

### 3. 设备健康监控与故障自愈 🆕

#### 3.1 实时设备监控
```typescript
interface DeviceHealthMonitoring {
  hardware_status: {
    camera_status: "摄像头连接状态和图像质量检测",
    printer_status: "打印机纸张状态和打印队列监控",
    card_reader_status: "身份证读卡器连接和读取功能检测",
    network_status: "网络连接质量和延迟监控"
  },
  
  auto_recovery: {
    device_restart: "设备无响应时自动重启相关服务",
    fallback_mode: "主设备故障时自动切换到手机验证",
    alert_escalation: "故障超过5分钟自动通知IT运维",
    performance_degradation: "设备性能下降时主动优化"
  }
}
```

### 4. 紧急情况处理机制 🆕

#### 4.1 紧急疏散模式
- **一键启动**: 管理员可一键启动紧急疏散模式
- **自动门禁开放**: 所有门禁自动开启，便于人员疏散
- **访客位置统计**: 实时统计园区内访客数量和大概分布
- **紧急通知**: 自动发送紧急通知给所有园区内人员

### 5. 访客体验优化细节 🆕

#### 5.1 智能等候时间预估
```typescript
interface VisitorExperienceOptimization {
  waiting_time_estimation: {
    queue_analysis: "基于当前等候队列长度预估等候时间",
    historical_data: "结合历史数据优化预估准确性",
    real_time_update: "等候时间动态更新并通知访客"
  },
  
  location_guidance: {
    simple_route: "从门岗到目的地的简单文字路线指引",
    landmark_navigation: "基于显著建筑物的导航指引",
    qr_code_map: "访客证包含简单地图二维码"
  },
  
  rejection_reason_clarity: {
    detailed_feedback: "申请被拒绝时提供明确具体的原因",
    improvement_suggestions: "提供如何改进申请的建议",
    appeal_process: "提供申诉渠道和联系方式"
  }
}
```

### 6. 访客分组与批量操作增强 🆕

#### 6.1 智能分组管理
- **自动分组规则**: 基于访问日期、来访公司、访问目的自动分组
- **分组权限管理**: 不同分组配置不同的访问区域和时间限制
- **分组通知模板**: 支持按分组发送定制化的通知内容
- **分组状态管理**: 批量更新分组内所有访客的状态

### 7. 多语言支持（国际化）🆕

#### 7.1 前端国际化
```typescript
interface InternationalizationSupport {
  supported_languages: ["zh-CN", "en-US"], // 中英文双语
  visitor_interface: "访客申请界面支持语言切换",
  device_interface: "门岗和前台设备支持双语显示",
  notification_templates: "邮件和短信通知模板多语言支持",
  error_messages: "错误提示和系统消息双语支持"
}
```

### 8. 预约时间冲突智能处理 🆕

#### 8.1 智能时间协调
- **冲突检测**: 自动检测被访人的时间冲突并提前预警
- **时间推荐**: 基于被访人空闲时间智能推荐可用时段
- **会议室协调**: 需要会议室时自动检查可用性并预订
- **日程集成**: 支持与企业内部日历系统的基础集成

## 📊 功能优先级规划

### 🔴 **P0 (必须实现 - 核心MVP)**
1. **四大场景配置**: 自主申请、已知邀约、未知邀约、批量邀约场景模板
2. **管理端核心功能**: React + Ant Design Pro，访客审批、基础配置管理
3. **访客端应用**: React + Ant Design Mobile，四场景申请流程、二维码展示
4. **门岗端基础功能**: React PWA，二维码验证、访客查询、入园登记
5. **移动端备用验证**: React Native APP + 微信小程序，设备故障时的应急验证 🆕
6. **基础离线支持**: 今日访客数据缓存，网络异常时的基础验证功能 🆕

### 🟡 **P1 (重要功能 - 完整体验)**  
1. **前台签到系统**: React Web，签到服务、被访人通知、会议室协调
2. **多阶段表单引擎**: 支持员工创建邀请→访客填写信息的两阶段流程
3. **设备端自助服务**: React PWA，访客自助签到、信息展示
4. **实时通信系统**: WebSocket实时状态同步、消息通知
5. **数据隐私保护**: 敏感信息脱敏展示、访问审计日志 🆕
6. **设备健康监控**: 硬件状态监控、故障自动切换 🆕

### 🟢 **P2 (优化功能 - 高级特性)**
1. **硬件深度集成**: 身份证读卡器、人脸识别、打印机控制
2. **访客体验优化**: 等候时间预估、路线指引、智能客服 🆕
3. **多语言支持**: 中英文双语界面、通知模板国际化 🆕
4. **智能时间协调**: 冲突检测、时间推荐、会议室智能预订 🆕
5. **紧急情况处理**: 紧急疏散模式、访客位置统计 🆕
6. **企业生态集成**: 企业微信、钉钉、飞书深度集成

### 📈 **开发优先级说明**
**阶段1 (4-6周)**: 完成P0功能，实现基本的四场景访客管理闭环 + 移动端备用方案
**阶段2 (3-4周)**: 完成P1功能，实现完整的门岗-前台-管理端协同 + 数据隐私保护
**阶段3 (4-6周)**: 完成P2功能，实现智能化和生态化的高级特性 + 用户体验优化

### 💡 **成本效益分析**
**移动端备用方案价值**:
- **降低部署成本**: 预算紧张的租户可先使用手机APP，后续升级专用设备
- **提升系统可靠性**: 设备故障时零中断的备用验证方案
- **扩展部署灵活性**: 支持临时入口、移动巡查等灵活场景
- **快速响应能力**: 紧急情况下可快速增加验证点

## 🎯 成功指标

### 业务关键指标 (KPI)
- **四场景申请成功率**: >95%，各场景申请流程完成率
- **访客申请到入园时长**: <5分钟 (自主申请场景)，<2分钟 (已知邀约场景)
- **门岗验证平均时长**: <30秒 (二维码验证)，<60秒 (身份证+人脸验证)
- **移动端备用验证成功率**: >90% (设备故障时的应急验证) 🆕
- **访客满意度评分**: >4.5/5.0 (基于前台服务和整体体验)
- **配置变更生效时间**: <1分钟 (场景模板配置实时生效)
- **离线模式可用率**: >99% (网络异常时的基础功能可用性) 🆕

### 技术性能指标 (SLA)
- **API响应时间**: <200ms (95%请求)，<500ms (99%请求)
- **系统可用性**: 99.9% (月度统计，允许43分钟故障时间)
- **并发处理能力**: 支持1000+并发访客申请，5000+并发查询
- **多端数据同步**: <3秒 (门岗↔前台↔管理端状态同步)
- **硬件集成响应**: <2秒 (身份证读取)，<5秒 (人脸识别)

### 配置引擎性能指标
- **场景模板配置复杂度**: 支持10+条件分支，20+字段配置
- **表单渲染性能**: <500ms (复杂表单加载)，<200ms (简单表单)
- **工作流执行效率**: <1秒 (简单审批)，<5秒 (复杂多级审批)
- **规则引擎响应**: <100ms (业务规则验证和执行)

## 📋 附录

### A. 后端配置引擎能力评估对比

#### A.1 现有配置引擎优势
```typescript
// 现有15种字段类型，支持丰富的表单配置
interface ExistingFieldTypes {
  basic_types: ["text", "number", "email", "phone", "textarea"],
  selection_types: ["select", "multi_select", "radio", "checkbox"],
  date_types: ["date", "datetime", "time", "date_range"],
  file_types: ["file_upload", "image_upload"],
  complex_types: ["cascader", "tree_select"]
}

// 现有工作流引擎，支持复杂审批流程
interface ExistingWorkflowEngine {
  step_types: ["approval", "notification", "condition", "timer"],
  condition_logic: "支持复杂条件表达式",
  parallel_processing: "支持并行审批分支",
  timeout_handling: "超时自动处理机制"
}

// 现有业务规则引擎，支持动态规则配置
interface ExistingBusinessRules {
  rule_types: ["validation", "calculation", "action_trigger"],
  condition_expressions: "支持复杂逻辑表达式",
  priority_management: "规则优先级管理",
  dynamic_execution: "运行时规则动态加载"
}
```

#### A.2 场景化配置缺口分析
```typescript
// 需要补充的场景整合能力
interface ScenarioIntegrationGaps {
  scenario_template_management: {
    current_status: "❌ 不存在",
    required_capability: "场景模板CRUD和版本管理",
    implementation_effort: "中等 (复用现有配置模式)"
  },
  
  intelligent_routing: {
    current_status: "❌ 不存在", 
    required_capability: "基于条件的场景自动选择",
    implementation_effort: "较低 (基于现有规则引擎)"
  },
  
  multi_stage_forms: {
    current_status: "⚠️ 部分支持",
    required_capability: "不同角色的分阶段表单填写",
    implementation_effort: "中等 (扩展现有表单引擎)"
  },
  
  context_preservation: {
    current_status: "❌ 不存在",
    required_capability: "访客申请全流程上下文保持",
    implementation_effort: "较低 (数据模型扩展)"
  }
}
```

### B. React生态技术栈选型对比

#### B.1 管理端技术选型 (React + Ant Design Pro)
```typescript
interface AdminPlatformTechStack {
  advantages: [
    "Ant Design Pro提供完整的中后台解决方案",
    "丰富的业务组件库，减少重复开发",
    "TypeScript支持，提高代码质量",
    "UmiJS构建工具链成熟稳定"
  ],
  
  key_dependencies: {
    "react": "^18.2.0",
    "antd": "^5.12.0", 
    "@ant-design/pro-components": "^2.6.0",
    "umi": "^4.0.0",
    "typescript": "^5.0.0"
  },
  
  estimated_development: "6-8周完成核心功能"
}
```

#### B.2 访客端技术选型 (React + Ant Design Mobile)
```typescript
interface VisitorAppTechStack {
  advantages: [
    "Ant Design Mobile专为移动端优化",
    "组件丰富，支持触摸交互",
    "PWA支持，可作为小程序使用",
    "与管理端技术栈统一，组件可复用"
  ],
  
  key_dependencies: {
    "react": "^18.2.0",
    "antd-mobile": "^5.34.0",
    "react-router-dom": "^6.8.0", 
    "axios": "^1.6.0",
    "qrcode.js": "^1.0.0"
  },
  
  estimated_development: "4-5周完成四大场景"
}
```

#### B.3 门岗端技术选型 (React PWA vs React Native)
```typescript
interface SecurityGateTechStack {
  pwa_option: {
    advantages: [
      "开发成本低，Web技术栈统一",
      "跨平台兼容，iPad和Android平板通用", 
      "硬件API通过Capacitor或Cordova调用",
      "部署简单，无需应用商店审核"
    ],
    disadvantages: [
      "硬件集成能力相对受限",
      "性能不如原生应用",
      "某些高级硬件功能需要插件"
    ]
  },
  
  react_native_option: {
    advantages: [
      "原生性能，硬件集成能力强",
      "摄像头、蓝牙等设备API完整支持",
      "用户体验接近原生应用",
      "可发布到应用商店"
    ],
    disadvantages: [
      "开发成本较高",
      "需要分别适配iOS和Android",
      "依赖原生模块，升级维护复杂"
    ]
  },
  
  recommendation: "初期采用PWA方案，后期根据需要升级为React Native"
}
```

### C. 场景配置最佳实践建议

#### C.1 场景模板设计原则
1. **基于现有配置引擎**: 最大化复用现有表单、工作流、业务规则配置
2. **场景间解耦**: 每个场景模板独立配置，互不影响
3. **租户级定制**: 每个租户可自定义场景模板，支持继承和覆盖
4. **版本管理**: 场景模板支持版本控制，配置变更可回滚

#### C.2 场景路由策略
```typescript
interface ScenarioRoutingStrategy {
  routing_algorithm: {
    step1: "收集访客申请上下文信息",
    step2: "评估可用场景模板匹配度",
    step3: "基于评分算法选择最佳场景",
    step4: "绑定场景配置到访客申请实例"
  },
  
  fallback_mechanism: {
    primary: "智能路由选择",
    secondary: "用户手动选择场景类型", 
    tertiary: "默认通用场景模板"
  }
}
```

### D. 实施建议与风险评估

#### D.1 技术实施建议
1. **迭代开发**: 分阶段实施，先完成P0核心功能，再逐步完善
2. **架构复用**: 基于现有Clean Architecture + DDD架构扩展，保持技术连续性
3. **测试策略**: 重点测试场景切换逻辑和多端数据同步
4. **性能优化**: 关注配置引擎性能，使用Redis缓存热点配置

#### D.2 主要风险与应对
```typescript
interface RiskAssessment {
  technical_risks: {
    "配置引擎复杂度": {
      risk_level: "中等",
      mitigation: "基于现有引擎扩展，避免重写"
    },
    "多端数据同步": {
      risk_level: "中等", 
      mitigation: "使用WebSocket + Redis实现可靠同步"
    },
    "硬件集成兼容性": {
      risk_level: "高",
      mitigation: "采用硬件抽象层，支持多厂商设备"
    }
  },
  
  business_risks: {
    "用户接受度": {
      risk_level: "低",
      mitigation: "基于现有成熟功能扩展，用户学习成本低"
    },
    "部署复杂度": {
      risk_level: "中等",
      mitigation: "提供Docker容器化部署方案"
    }
  }
}
```

---

**文档版本**: v2.2.0 | **最后更新**: 2025-06-18  
**下一步**: 基于此PRD开始详细的技术方案设计和开发计划制定

## 📝 **PRD更新总结**

### **v2.2版本主要更新内容**
1. ✅ **完善四大核心场景**: 详细定义自主申请、已知邀约、未知邀约、批量邀约的完整流程
2. ✅ **新增用户角色**: 门岗人员、前台人员、部门访客负责人三个关键角色
3. ✅ **移动端备用方案**: React Native APP + 微信小程序的冗余验证机制
4. ✅ **关键场景需求补充**: 8个重要的遗漏需求识别和详细定义
5. ✅ **技术架构完善**: React生态统一技术栈，5+2端应用架构
6. ✅ **API接口扩展**: 从28个API扩展到53个API，覆盖全业务流程

### **核心创新点**
- **场景化配置驱动**: 基于现有配置引擎的场景模板管理
- **移动端备用验证**: 解决设备故障和预算限制的双重问题  
- **离线优先设计**: 网络异常时的基础功能保障
- **数据隐私保护**: 符合数据保护要求的敏感信息处理

### **商业价值**
- **降低部署门槛**: 移动端方案让小型企业也能快速部署
- **提升系统可靠性**: 多重备用机制确保业务连续性
- **增强用户体验**: 八大场景优化提升访客满意度
- **数据合规保障**: 内置隐私保护机制满足法规要求

---

**PRD更新完成** ✅ | **文档完整性**: 已包含所有核心需求和技术架构 | **可执行性**: 具备开发实施的完整指导