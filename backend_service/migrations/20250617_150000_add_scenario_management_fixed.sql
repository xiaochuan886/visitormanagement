-- 场景管理系统数据库迁移 (修复版本)
-- 版本: 20250617_150000
-- 描述: 添加动态场景管理系统表结构

-- ===== 第一部分：创建表 =====

-- 1. 场景模板表
CREATE TABLE IF NOT EXISTS scenario_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(100) NOT NULL,
    template_code VARCHAR(50) NOT NULL,
    template_version INTEGER DEFAULT 1 NOT NULL,
    template_category VARCHAR(50) NOT NULL,
    template_description TEXT,
    
    -- 预制模板标识
    is_builtin BOOLEAN DEFAULT FALSE NOT NULL,
    is_template_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- 场景特征定义
    scenario_features JSONB NOT NULL,
    default_configurations JSONB NOT NULL,
    
    -- 模板元数据
    supported_roles JSONB,
    trigger_conditions JSONB,
    template_tags JSONB,
    
    -- 使用统计
    usage_count INTEGER DEFAULT 0 NOT NULL,
    last_used_at TIMESTAMPTZ,
    
    -- 审计字段 (继承 TenantModel)
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    deleted_by VARCHAR(100),
    tenant_id VARCHAR(50) DEFAULT 'default' NOT NULL,
    
    -- 约束
    CONSTRAINT chk_template_category CHECK (template_category IN ('visitor_management', 'employee_management', 'event_management', 'security_management', 'custom')),
    CONSTRAINT chk_template_version CHECK (template_version >= 1),
    CONSTRAINT chk_usage_count CHECK (usage_count >= 0)
);

-- 2. 场景实例表
CREATE TABLE IF NOT EXISTS scenario_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_name VARCHAR(100) NOT NULL,
    instance_code VARCHAR(50) NOT NULL,
    
    -- 模板关联
    template_id UUID NOT NULL REFERENCES scenario_templates(id),
    
    -- 实例状态
    instance_status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    priority_level INTEGER DEFAULT 1 NOT NULL,
    
    -- 场景配置（覆盖模板默认配置）
    custom_configurations JSONB,
    form_config_overrides JSONB,
    workflow_config_overrides JSONB,
    business_rule_overrides JSONB,
    spatial_config_overrides JSONB,
    
    -- 路由和触发
    routing_rules JSONB NOT NULL,
    trigger_conditions JSONB NOT NULL,
    auto_routing_enabled BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- 使用范围
    applicable_sites JSONB,
    applicable_departments JSONB,
    applicable_roles JSONB,
    
    -- 时间有效性
    effective_from TIMESTAMPTZ,
    effective_until TIMESTAMPTZ,
    
    -- 统计和分析
    execution_count INTEGER DEFAULT 0 NOT NULL,
    success_count INTEGER DEFAULT 0 NOT NULL,
    last_executed_at TIMESTAMPTZ,
    average_execution_time FLOAT,
    
    -- 审计字段
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    deleted_by VARCHAR(100),
    tenant_id VARCHAR(50) DEFAULT 'default' NOT NULL,
    
    -- 约束
    CONSTRAINT chk_instance_status CHECK (instance_status IN ('draft', 'active', 'inactive', 'archived', 'testing')),
    CONSTRAINT chk_priority_level CHECK (priority_level >= 1 AND priority_level <= 10),
    CONSTRAINT chk_execution_count CHECK (execution_count >= 0),
    CONSTRAINT chk_success_count CHECK (success_count >= 0),
    CONSTRAINT chk_success_rate CHECK (success_count <= execution_count),
    CONSTRAINT chk_instance_effective_dates CHECK (effective_until IS NULL OR effective_until > effective_from),
    CONSTRAINT chk_execution_time CHECK (average_execution_time IS NULL OR average_execution_time >= 0)
);

-- 3. 场景执行表
CREATE TABLE IF NOT EXISTS scenario_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_instance_id UUID NOT NULL REFERENCES scenario_instances(id),
    
    -- 执行信息
    execution_status VARCHAR(50) NOT NULL,
    execution_type VARCHAR(50) NOT NULL,
    
    -- 触发信息
    trigger_source VARCHAR(50),
    trigger_user_id VARCHAR(100),
    trigger_context JSONB,
    
    -- 目标实体
    target_entity_type VARCHAR(50) NOT NULL,
    target_entity_id VARCHAR(100) NOT NULL,
    target_entity_data JSONB,
    
    -- 执行过程
    execution_steps JSONB,
    current_step VARCHAR(100),
    execution_data JSONB,
    step_results JSONB,
    
    -- 时间信息
    started_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMPTZ,
    execution_duration FLOAT,
    
    -- 结果信息
    execution_result JSONB,
    error_details TEXT,
    retry_count INTEGER DEFAULT 0 NOT NULL,
    
    -- 审计字段
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    tenant_id VARCHAR(50) DEFAULT 'default' NOT NULL,
    
    -- 约束
    CONSTRAINT chk_scenario_execution_status CHECK (execution_status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')),
    CONSTRAINT chk_execution_type CHECK (execution_type IN ('manual', 'automatic', 'scheduled', 'triggered', 'test')),
    CONSTRAINT chk_trigger_source CHECK (trigger_source IN ('api', 'ui', 'system', 'workflow', 'scheduler', 'webhook')),
    CONSTRAINT chk_execution_duration CHECK (execution_duration IS NULL OR execution_duration >= 0),
    CONSTRAINT chk_retry_count CHECK (retry_count >= 0)
);

-- 4. 场景路由规则表
CREATE TABLE IF NOT EXISTS scenario_routing_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(100) NOT NULL,
    rule_description TEXT,
    
    -- 路由规则配置
    rule_priority INTEGER DEFAULT 1 NOT NULL,
    rule_conditions JSONB NOT NULL,
    target_scenario_ids JSONB NOT NULL,
    
    -- 条件匹配设置
    condition_logic VARCHAR(20) DEFAULT 'AND' NOT NULL,
    match_strategy VARCHAR(50) DEFAULT 'first_match' NOT NULL,
    
    -- 规则状态
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    effective_from TIMESTAMPTZ,
    effective_until TIMESTAMPTZ,
    
    -- 使用统计
    matched_count INTEGER DEFAULT 0 NOT NULL,
    success_count INTEGER DEFAULT 0 NOT NULL,
    last_matched_at TIMESTAMPTZ,
    
    -- 审计字段
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    deleted_by VARCHAR(100),
    tenant_id VARCHAR(50) DEFAULT 'default' NOT NULL,
    
    -- 约束
    CONSTRAINT chk_routing_rule_priority CHECK (rule_priority >= 1 AND rule_priority <= 100),
    CONSTRAINT chk_condition_logic CHECK (condition_logic IN ('AND', 'OR')),
    CONSTRAINT chk_match_strategy CHECK (match_strategy IN ('first_match', 'best_match', 'all_match', 'weighted_match')),
    CONSTRAINT chk_matched_count CHECK (matched_count >= 0),
    CONSTRAINT chk_routing_success_count CHECK (success_count >= 0),
    CONSTRAINT chk_routing_success_rate CHECK (success_count <= matched_count),
    CONSTRAINT chk_routing_effective_dates CHECK (effective_until IS NULL OR effective_until > effective_from)
);

-- 5. 场景分析表
CREATE TABLE IF NOT EXISTS scenario_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_instance_id UUID NOT NULL REFERENCES scenario_instances(id),
    
    -- 统计周期
    analytics_date TIMESTAMPTZ NOT NULL,
    period_type VARCHAR(20) NOT NULL,
    
    -- 执行统计
    total_executions INTEGER DEFAULT 0 NOT NULL,
    successful_executions INTEGER DEFAULT 0 NOT NULL,
    failed_executions INTEGER DEFAULT 0 NOT NULL,
    
    -- 性能统计
    avg_execution_time FLOAT DEFAULT 0.0 NOT NULL,
    min_execution_time FLOAT,
    max_execution_time FLOAT,
    
    -- 用户统计
    unique_users INTEGER DEFAULT 0 NOT NULL,
    user_distribution JSONB,
    
    -- 时间分布
    hourly_distribution JSONB,
    daily_trend JSONB,
    
    -- 业务指标
    business_metrics JSONB,
    
    -- 审计字段
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    tenant_id VARCHAR(50) DEFAULT 'default' NOT NULL,
    
    -- 约束
    CONSTRAINT chk_period_type CHECK (period_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    CONSTRAINT chk_total_executions CHECK (total_executions >= 0),
    CONSTRAINT chk_successful_executions CHECK (successful_executions >= 0),
    CONSTRAINT chk_failed_executions CHECK (failed_executions >= 0),
    CONSTRAINT chk_execution_sum CHECK (successful_executions + failed_executions <= total_executions),
    CONSTRAINT chk_avg_execution_time CHECK (avg_execution_time >= 0),
    CONSTRAINT chk_unique_users CHECK (unique_users >= 0)
); 