-- 场景管理系统初始数据
-- 版本: 20250617_150002
-- 描述: 添加预制场景模板和示例数据

-- ===== 预制场景模板 =====

-- 1. 访客登记场景模板
INSERT INTO scenario_templates (
    template_name,
    template_code,
    template_version,
    template_category,
    template_description,
    is_builtin,
    is_template_active,
    scenario_features,
    default_configurations,
    supported_roles,
    trigger_conditions,
    template_tags,
    tenant_id,
    created_by,
    updated_by
) VALUES (
    '标准访客登记',
    'visitor_checkin_standard',
    1,
    'visitor_management',
    '标准的访客登记流程，包含身份验证、信息录入、照片拍摄、访问卡发放等环节',
    true,
    true,
    '{"form_steps": ["identity_verification", "information_input", "photo_capture", "card_issuance"], "required_fields": ["name", "phone", "company", "visit_purpose"], "optional_fields": ["email", "id_number", "vehicle_plate"], "validation_rules": {"phone": "regex", "email": "email_format"}, "photo_required": true, "card_required": true}',
    '{"max_duration": 480, "notification_enabled": true, "approval_required": false, "escort_required": false, "badge_type": "visitor", "access_areas": ["lobby", "meeting_rooms"], "auto_checkout": true}',
    '["receptionist", "security", "admin"]',
    '{"entity_type": "visitor", "action": "checkin", "conditions": [{"field": "visitor_type", "operator": "eq", "value": "standard"}]}',
    '["访客", "登记", "标准", "前台"]',
    'default',
    'system',
    'system'
),
(
    'VIP访客登记',
    'visitor_checkin_vip',
    1,
    'visitor_management',
    'VIP访客专用登记流程，简化步骤并提供专属服务',
    true,
    true,
    '{"form_steps": ["identity_verification", "vip_service_selection"], "required_fields": ["name", "phone", "company"], "optional_fields": ["email", "special_requirements"], "validation_rules": {"phone": "regex"}, "photo_required": false, "card_required": true}',
    '{"max_duration": 720, "notification_enabled": true, "approval_required": false, "escort_required": true, "badge_type": "vip", "access_areas": ["lobby", "meeting_rooms", "executive_floor"], "auto_checkout": false, "priority_service": true}',
    '["receptionist", "vip_service", "admin"]',
    '{"entity_type": "visitor", "action": "checkin", "conditions": [{"field": "visitor_type", "operator": "eq", "value": "vip"}]}',
    '["VIP", "访客", "专属", "高端"]',
    'default',
    'system',
    'system'
),
(
    '员工访客预约',
    'visitor_appointment',
    1,
    'visitor_management',
    '员工为访客创建预约的场景，包含预约信息填写和审批流程',
    true,
    true,
    '{"form_steps": ["appointment_info", "visitor_details", "approval_workflow"], "required_fields": ["visitor_name", "visitor_phone", "visit_date", "visit_time", "visit_purpose", "host_employee"], "optional_fields": ["visitor_company", "visitor_email", "special_requirements"], "validation_rules": {"visit_date": "future_date", "visit_time": "business_hours"}, "approval_required": true}',
    '{"max_duration": 240, "notification_enabled": true, "approval_required": true, "escort_required": false, "advance_notice": 24, "reminder_enabled": true}',
    '["employee", "admin", "manager"]',
    '{"entity_type": "appointment", "action": "create", "conditions": [{"field": "appointment_type", "operator": "eq", "value": "visitor"}]}',
    '["预约", "员工", "访客", "审批"]',
    'default',
    'system',
    'system'
),
(
    '访客离场',
    'visitor_checkout',
    1,
    'visitor_management',
    '访客离场登记流程，包含卡片回收和满意度调查',
    true,
    true,
    '{"form_steps": ["card_return", "satisfaction_survey", "checkout_confirmation"], "required_fields": ["visitor_id"], "optional_fields": ["satisfaction_rating", "feedback_comments"], "card_return_required": true, "survey_optional": true}',
    '{"notification_enabled": true, "feedback_collection": true, "auto_archive": true, "checkout_notification": true}',
    '["receptionist", "security", "admin"]',
    '{"entity_type": "visitor", "action": "checkout", "conditions": [{"field": "status", "operator": "eq", "value": "checked_in"}]}',
    '["访客", "离场", "退卡", "调查"]',
    'default',
    'system',
    'system'
);

-- ===== 示例场景实例 =====

-- 获取刚插入的模板ID (使用CTE方式)
WITH template_ids AS (
    SELECT 
        id,
        template_code
    FROM scenario_templates 
    WHERE template_code IN ('visitor_checkin_standard', 'visitor_checkin_vip', 'visitor_appointment', 'visitor_checkout')
    AND is_builtin = true
)

-- 插入场景实例
INSERT INTO scenario_instances (
    instance_name,
    instance_code,
    template_id,
    instance_status,
    priority_level,
    custom_configurations,
    routing_rules,
    trigger_conditions,
    auto_routing_enabled,
    applicable_sites,
    applicable_departments,
    applicable_roles,
    effective_from,
    tenant_id,
    created_by,
    updated_by
)
SELECT 
    CASE 
        WHEN t.template_code = 'visitor_checkin_standard' THEN '前台标准登记'
        WHEN t.template_code = 'visitor_checkin_vip' THEN 'VIP接待登记'
        WHEN t.template_code = 'visitor_appointment' THEN '访客预约管理'
        WHEN t.template_code = 'visitor_checkout' THEN '访客离场处理'
    END as instance_name,
    CASE 
        WHEN t.template_code = 'visitor_checkin_standard' THEN 'front_desk_standard'
        WHEN t.template_code = 'visitor_checkin_vip' THEN 'vip_reception'
        WHEN t.template_code = 'visitor_appointment' THEN 'appointment_mgmt'
        WHEN t.template_code = 'visitor_checkout' THEN 'checkout_process'
    END as instance_code,
    t.id as template_id,
    'active' as instance_status,
    CASE 
        WHEN t.template_code = 'visitor_checkin_vip' THEN 10
        WHEN t.template_code = 'visitor_checkin_standard' THEN 8
        WHEN t.template_code = 'visitor_appointment' THEN 6
        WHEN t.template_code = 'visitor_checkout' THEN 5
    END as priority_level,
    CASE 
        WHEN t.template_code = 'visitor_checkin_standard' THEN '{"business_hours": {"start": "08:00", "end": "18:00"}, "weekend_enabled": false}'
        WHEN t.template_code = 'visitor_checkin_vip' THEN '{"business_hours": {"start": "07:00", "end": "22:00"}, "weekend_enabled": true, "dedicated_staff": true}'
        WHEN t.template_code = 'visitor_appointment' THEN '{"advance_booking_days": 30, "max_daily_appointments": 50}'
        WHEN t.template_code = 'visitor_checkout' THEN '{"auto_checkout_hours": 8, "feedback_required": false}'
    END::jsonb as custom_configurations,
    CASE 
        WHEN t.template_code = 'visitor_checkin_standard' THEN '{"conditions": [{"field": "visitor_type", "operator": "eq", "value": "standard"}, {"field": "time", "operator": "between", "value": ["08:00", "18:00"]}], "priority": 80}'
        WHEN t.template_code = 'visitor_checkin_vip' THEN '{"conditions": [{"field": "visitor_type", "operator": "eq", "value": "vip"}], "priority": 100}'
        WHEN t.template_code = 'visitor_appointment' THEN '{"conditions": [{"field": "action", "operator": "eq", "value": "create_appointment"}], "priority": 60}'
        WHEN t.template_code = 'visitor_checkout' THEN '{"conditions": [{"field": "action", "operator": "eq", "value": "checkout"}], "priority": 50}'
    END::jsonb as routing_rules,
    CASE 
        WHEN t.template_code = 'visitor_checkin_standard' THEN '{"entity_type": "visitor", "action": "checkin", "visitor_type": "standard"}'
        WHEN t.template_code = 'visitor_checkin_vip' THEN '{"entity_type": "visitor", "action": "checkin", "visitor_type": "vip"}'
        WHEN t.template_code = 'visitor_appointment' THEN '{"entity_type": "appointment", "action": "create"}'
        WHEN t.template_code = 'visitor_checkout' THEN '{"entity_type": "visitor", "action": "checkout"}'
    END::jsonb as trigger_conditions,
    true as auto_routing_enabled,
    '["headquarters", "branch_office"]'::jsonb as applicable_sites,
    CASE 
        WHEN t.template_code = 'visitor_checkin_standard' THEN '["reception", "security"]'
        WHEN t.template_code = 'visitor_checkin_vip' THEN '["vip_service", "executive_reception"]'
        WHEN t.template_code = 'visitor_appointment' THEN '["all_departments"]'
        WHEN t.template_code = 'visitor_checkout' THEN '["reception", "security"]'
    END::jsonb as applicable_departments,
    CASE 
        WHEN t.template_code = 'visitor_checkin_standard' THEN '["receptionist", "security_guard"]'
        WHEN t.template_code = 'visitor_checkin_vip' THEN '["vip_receptionist", "concierge"]'
        WHEN t.template_code = 'visitor_appointment' THEN '["employee", "manager", "admin"]'
        WHEN t.template_code = 'visitor_checkout' THEN '["receptionist", "security_guard"]'
    END::jsonb as applicable_roles,
    NOW() as effective_from,
    'default' as tenant_id,
    'system' as created_by,
    'system' as updated_by
FROM template_ids t;

-- ===== 路由规则 =====

INSERT INTO scenario_routing_rules (
    rule_name,
    rule_description,
    rule_priority,
    rule_conditions,
    target_scenario_ids,
    condition_logic,
    match_strategy,
    is_active,
    effective_from,
    tenant_id,
    created_by,
    updated_by
) 
SELECT 
    'VIP访客优先路由',
    '当检测到VIP访客时，优先路由到VIP接待流程',
    100,
    '[{"field": "visitor_type", "operator": "eq", "value": "vip"}, {"field": "action", "operator": "eq", "value": "checkin"}]'::jsonb,
    jsonb_build_array(si.id),
    'AND',
    'first_match',
    true,
    NOW(),
    'default',
    'system',
    'system'
FROM scenario_instances si 
JOIN scenario_templates st ON si.template_id = st.id 
WHERE st.template_code = 'visitor_checkin_vip'

UNION ALL

SELECT 
    '标准访客路由',
    '标准访客登记的默认路由规则',
    80,
    '[{"field": "visitor_type", "operator": "eq", "value": "standard"}, {"field": "action", "operator": "eq", "value": "checkin"}]'::jsonb,
    jsonb_build_array(si.id),
    'AND',
    'first_match',
    true,
    NOW(),
    'default',
    'system',
    'system'
FROM scenario_instances si 
JOIN scenario_templates st ON si.template_id = st.id 
WHERE st.template_code = 'visitor_checkin_standard'

UNION ALL

SELECT 
    '预约创建路由',
    '访客预约创建的路由规则',
    60,
    '[{"field": "action", "operator": "eq", "value": "create_appointment"}]'::jsonb,
    jsonb_build_array(si.id),
    'AND',
    'first_match',
    true,
    NOW(),
    'default',
    'system',
    'system'
FROM scenario_instances si 
JOIN scenario_templates st ON si.template_id = st.id 
WHERE st.template_code = 'visitor_appointment'

UNION ALL

SELECT 
    '访客离场路由',
    '访客离场处理的路由规则',
    50,
    '[{"field": "action", "operator": "eq", "value": "checkout"}]'::jsonb,
    jsonb_build_array(si.id),
    'AND',
    'first_match',
    true,
    NOW(),
    'default',
    'system',
    'system'
FROM scenario_instances si 
JOIN scenario_templates st ON si.template_id = st.id 
WHERE st.template_code = 'visitor_checkout';

-- ===== 初始分析数据 =====

-- 为每个场景实例创建今日的分析记录
INSERT INTO scenario_analytics (
    scenario_instance_id,
    analytics_date,
    period_type,
    total_executions,
    successful_executions,
    failed_executions,
    avg_execution_time,
    unique_users,
    user_distribution,
    hourly_distribution,
    business_metrics,
    tenant_id
)
SELECT 
    si.id,
    CURRENT_DATE,
    'daily',
    0,
    0,
    0,
    0.0,
    0,
    '{}'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb,
    'default'
FROM scenario_instances si;

-- 添加注释
COMMENT ON TABLE scenario_templates IS '场景模板表：存储可重用的场景配置模板';
COMMENT ON TABLE scenario_instances IS '场景实例表：基于模板创建的具体场景实例';
COMMENT ON TABLE scenario_executions IS '场景执行表：记录场景的具体执行过程和结果';
COMMENT ON TABLE scenario_routing_rules IS '场景路由规则表：定义场景的自动路由逻辑';
COMMENT ON TABLE scenario_analytics IS '场景分析表：存储场景执行的统计分析数据'; 