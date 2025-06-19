-- 场景管理系统索引和触发器
-- 版本: 20250617_150001
-- 描述: 为场景管理系统表添加索引和触发器

-- ===== 第二部分：创建索引 =====

-- 场景模板表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_tenant ON scenario_templates(tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_active ON scenario_templates(is_template_active, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_category ON scenario_templates(template_category, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_code ON scenario_templates(template_code, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_builtin ON scenario_templates(is_builtin, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_usage ON scenario_templates(usage_count DESC, last_used_at DESC, tenant_id) WHERE NOT is_deleted;

-- 场景实例表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_tenant ON scenario_instances(tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_template ON scenario_instances(template_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_status ON scenario_instances(instance_status, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_code ON scenario_instances(instance_code, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_priority ON scenario_instances(priority_level DESC, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_effective ON scenario_instances(effective_from, effective_until, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_auto_routing ON scenario_instances(auto_routing_enabled, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_execution_stats ON scenario_instances(execution_count DESC, success_count DESC, tenant_id) WHERE NOT is_deleted;

-- 场景执行表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_tenant ON scenario_executions(tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_instance ON scenario_executions(scenario_instance_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_status ON scenario_executions(execution_status, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_type ON scenario_executions(execution_type, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_trigger_user ON scenario_executions(trigger_user_id, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_target ON scenario_executions(target_entity_type, target_entity_id, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_started ON scenario_executions(started_at DESC, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_completed ON scenario_executions(completed_at DESC, tenant_id) WHERE completed_at IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_trigger_source ON scenario_executions(trigger_source, tenant_id);

-- 场景路由规则表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_routing_rules_tenant ON scenario_routing_rules(tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_routing_rules_active ON scenario_routing_rules(is_active, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_routing_rules_priority ON scenario_routing_rules(rule_priority ASC, tenant_id) WHERE NOT is_deleted AND is_active;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_routing_rules_effective ON scenario_routing_rules(effective_from, effective_until, tenant_id) WHERE NOT is_deleted AND is_active;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_routing_rules_match_strategy ON scenario_routing_rules(match_strategy, tenant_id) WHERE NOT is_deleted AND is_active;

-- 场景分析表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_analytics_tenant ON scenario_analytics(tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_analytics_instance ON scenario_analytics(scenario_instance_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_analytics_date ON scenario_analytics(analytics_date DESC, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_analytics_period ON scenario_analytics(period_type, analytics_date DESC, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_analytics_instance_period ON scenario_analytics(scenario_instance_id, period_type, analytics_date DESC);

-- ===== 第三部分：复合索引 =====

-- 场景模板复合索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_category_active ON scenario_templates(template_category, is_template_active, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_code_version ON scenario_templates(template_code, template_version DESC, tenant_id) WHERE NOT is_deleted;

-- 场景实例复合索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_template_status ON scenario_instances(template_id, instance_status) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_status_priority ON scenario_instances(instance_status, priority_level DESC, tenant_id) WHERE NOT is_deleted;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_effective_status ON scenario_instances(effective_from, effective_until, instance_status, tenant_id) WHERE NOT is_deleted;

-- 场景执行复合索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_instance_status ON scenario_executions(scenario_instance_id, execution_status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_instance_started ON scenario_executions(scenario_instance_id, started_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_target_status ON scenario_executions(target_entity_type, target_entity_id, execution_status, tenant_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_executions_user_status ON scenario_executions(trigger_user_id, execution_status, tenant_id);

-- ===== 第四部分：唯一约束 =====

-- 场景模板唯一约束
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_templates_code_version_unique ON scenario_templates(template_code, template_version, tenant_id) WHERE NOT is_deleted;

-- 场景实例唯一约束
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_instances_code_unique ON scenario_instances(instance_code, tenant_id) WHERE NOT is_deleted;

-- 场景路由规则唯一约束
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_routing_rules_name_unique ON scenario_routing_rules(rule_name, tenant_id) WHERE NOT is_deleted;

-- 场景分析唯一约束
CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_scenario_analytics_instance_date_period_unique ON scenario_analytics(scenario_instance_id, analytics_date, period_type);

-- ===== 第五部分：触发器 =====

-- 场景模板触发器：更新 updated_at
CREATE OR REPLACE FUNCTION update_scenario_templates_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_scenario_templates_updated_at ON scenario_templates;
CREATE TRIGGER trigger_scenario_templates_updated_at
    BEFORE UPDATE ON scenario_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_templates_timestamp();

-- 场景实例触发器：更新 updated_at
CREATE OR REPLACE FUNCTION update_scenario_instances_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_scenario_instances_updated_at ON scenario_instances;
CREATE TRIGGER trigger_scenario_instances_updated_at
    BEFORE UPDATE ON scenario_instances
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_instances_timestamp();

-- 场景执行触发器：更新 updated_at
CREATE OR REPLACE FUNCTION update_scenario_executions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_scenario_executions_updated_at ON scenario_executions;
CREATE TRIGGER trigger_scenario_executions_updated_at
    BEFORE UPDATE ON scenario_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_executions_timestamp();

-- 场景路由规则触发器：更新 updated_at
CREATE OR REPLACE FUNCTION update_scenario_routing_rules_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_scenario_routing_rules_updated_at ON scenario_routing_rules;
CREATE TRIGGER trigger_scenario_routing_rules_updated_at
    BEFORE UPDATE ON scenario_routing_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_routing_rules_timestamp();

-- 场景分析触发器：更新 updated_at
CREATE OR REPLACE FUNCTION update_scenario_analytics_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_scenario_analytics_updated_at ON scenario_analytics;
CREATE TRIGGER trigger_scenario_analytics_updated_at
    BEFORE UPDATE ON scenario_analytics
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_analytics_timestamp();

-- ===== 第六部分：统计触发器 =====

-- 场景模板使用统计触发器
CREATE OR REPLACE FUNCTION update_scenario_template_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE scenario_templates 
    SET usage_count = usage_count + 1,
        last_used_at = NOW()
    WHERE id = NEW.template_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_scenario_template_usage_count ON scenario_instances;
CREATE TRIGGER trigger_scenario_template_usage_count
    AFTER INSERT ON scenario_instances
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_template_usage();

-- 场景实例执行统计触发器
CREATE OR REPLACE FUNCTION update_scenario_instance_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE scenario_instances 
        SET execution_count = execution_count + 1,
            last_executed_at = NOW()
        WHERE id = NEW.scenario_instance_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' AND OLD.execution_status != NEW.execution_status THEN
        IF NEW.execution_status = 'completed' THEN
            UPDATE scenario_instances 
            SET success_count = success_count + 1,
                average_execution_time = COALESCE(
                    (average_execution_time * (success_count) + COALESCE(NEW.execution_duration, 0)) / (success_count + 1),
                    NEW.execution_duration
                )
            WHERE id = NEW.scenario_instance_id;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_scenario_execution_stats_insert ON scenario_executions;
CREATE TRIGGER trigger_scenario_execution_stats_insert
    AFTER INSERT ON scenario_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_instance_stats();

DROP TRIGGER IF EXISTS trigger_scenario_execution_stats_update ON scenario_executions;
CREATE TRIGGER trigger_scenario_execution_stats_update
    AFTER UPDATE ON scenario_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_scenario_instance_stats();

-- 场景路由规则匹配统计触发器
CREATE OR REPLACE FUNCTION update_routing_rule_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.trigger_context ? 'matched_routing_rules' THEN
        UPDATE scenario_routing_rules 
        SET matched_count = matched_count + 1,
            last_matched_at = NOW()
        WHERE id = ANY(
            SELECT jsonb_array_elements_text(NEW.trigger_context->'matched_routing_rules')::UUID
        );
        
        IF NEW.execution_status = 'completed' THEN
            UPDATE scenario_routing_rules 
            SET success_count = success_count + 1
            WHERE id = ANY(
                SELECT jsonb_array_elements_text(NEW.trigger_context->'matched_routing_rules')::UUID
            );
        END IF;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_routing_rule_stats ON scenario_executions;
CREATE TRIGGER trigger_routing_rule_stats
    AFTER INSERT OR UPDATE ON scenario_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_routing_rule_stats(); 