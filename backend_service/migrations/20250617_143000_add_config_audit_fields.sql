-- =====================================================
-- 配置引擎审计字段补齐迁移脚本
-- 版本：20250617_143000
-- 目标：为配置引擎表添加缺失的审计字段
-- =====================================================

-- 开始事务
BEGIN;

-- =====================================================
-- 1. 为form_configurations表添加审计字段
-- =====================================================

DO $$ 
BEGIN
    -- 添加is_deleted字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'form_configurations' 
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE form_configurations 
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE '✅ form_configurations表添加is_deleted字段';
    END IF;
    
    -- 添加deleted_at字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'form_configurations' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE form_configurations 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '✅ form_configurations表添加deleted_at字段';
    END IF;
    
    -- 添加deleted_by字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'form_configurations' 
        AND column_name = 'deleted_by'
    ) THEN
        ALTER TABLE form_configurations 
        ADD COLUMN deleted_by VARCHAR(100);
        RAISE NOTICE '✅ form_configurations表添加deleted_by字段';
    END IF;
END $$;

-- =====================================================
-- 2. 为workflow_configurations表添加审计字段
-- =====================================================

DO $$ 
BEGIN
    -- 添加is_deleted字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflow_configurations' 
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE workflow_configurations 
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE '✅ workflow_configurations表添加is_deleted字段';
    END IF;
    
    -- 添加deleted_at字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflow_configurations' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE workflow_configurations 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '✅ workflow_configurations表添加deleted_at字段';
    END IF;
    
    -- 添加deleted_by字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflow_configurations' 
        AND column_name = 'deleted_by'
    ) THEN
        ALTER TABLE workflow_configurations 
        ADD COLUMN deleted_by VARCHAR(100);
        RAISE NOTICE '✅ workflow_configurations表添加deleted_by字段';
    END IF;
END $$;

-- =====================================================
-- 3. 为spatial_configurations表添加审计字段
-- =====================================================

DO $$ 
BEGIN
    -- 添加is_deleted字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'spatial_configurations' 
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE spatial_configurations 
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE '✅ spatial_configurations表添加is_deleted字段';
    END IF;
    
    -- 添加deleted_at字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'spatial_configurations' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE spatial_configurations 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '✅ spatial_configurations表添加deleted_at字段';
    END IF;
    
    -- 添加deleted_by字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'spatial_configurations' 
        AND column_name = 'deleted_by'
    ) THEN
        ALTER TABLE spatial_configurations 
        ADD COLUMN deleted_by VARCHAR(100);
        RAISE NOTICE '✅ spatial_configurations表添加deleted_by字段';
    END IF;
END $$;

-- =====================================================
-- 4. 为business_rules表添加审计字段
-- =====================================================

DO $$ 
BEGIN
    -- 添加is_deleted字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'business_rules' 
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE business_rules 
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE '✅ business_rules表添加is_deleted字段';
    END IF;
    
    -- 添加deleted_at字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'business_rules' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE business_rules 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '✅ business_rules表添加deleted_at字段';
    END IF;
    
    -- 添加deleted_by字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'business_rules' 
        AND column_name = 'deleted_by'
    ) THEN
        ALTER TABLE business_rules 
        ADD COLUMN deleted_by VARCHAR(100);
        RAISE NOTICE '✅ business_rules表添加deleted_by字段';
    END IF;
END $$;

-- =====================================================
-- 5. 为相关子表添加审计字段（如果需要）
-- =====================================================

-- 为spatial_entities表添加审计字段
DO $$ 
BEGIN
    -- 添加is_deleted字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'spatial_entities' 
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE spatial_entities 
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE '✅ spatial_entities表添加is_deleted字段';
    END IF;
    
    -- 添加deleted_at字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'spatial_entities' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE spatial_entities 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '✅ spatial_entities表添加deleted_at字段';
    END IF;
    
    -- 添加deleted_by字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'spatial_entities' 
        AND column_name = 'deleted_by'
    ) THEN
        ALTER TABLE spatial_entities 
        ADD COLUMN deleted_by VARCHAR(100);
        RAISE NOTICE '✅ spatial_entities表添加deleted_by字段';
    END IF;
END $$;

-- 为workflow_executions表添加审计字段
DO $$ 
BEGIN
    -- 添加is_deleted字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflow_executions' 
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE workflow_executions 
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE '✅ workflow_executions表添加is_deleted字段';
    END IF;
    
    -- 添加deleted_at字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflow_executions' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE workflow_executions 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '✅ workflow_executions表添加deleted_at字段';
    END IF;
    
    -- 添加deleted_by字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workflow_executions' 
        AND column_name = 'deleted_by'
    ) THEN
        ALTER TABLE workflow_executions 
        ADD COLUMN deleted_by VARCHAR(100);
        RAISE NOTICE '✅ workflow_executions表添加deleted_by字段';
    END IF;
END $$;

-- 为rule_execution_logs表添加审计字段
DO $$ 
BEGIN
    -- 添加is_deleted字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'rule_execution_logs' 
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE rule_execution_logs 
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE '✅ rule_execution_logs表添加is_deleted字段';
    END IF;
    
    -- 添加deleted_at字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'rule_execution_logs' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE rule_execution_logs 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '✅ rule_execution_logs表添加deleted_at字段';
    END IF;
    
    -- 添加deleted_by字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'rule_execution_logs' 
        AND column_name = 'deleted_by'
    ) THEN
        ALTER TABLE rule_execution_logs 
        ADD COLUMN deleted_by VARCHAR(100);
        RAISE NOTICE '✅ rule_execution_logs表添加deleted_by字段';
    END IF;
END $$;

-- =====================================================
-- 6. 创建软删除功能的索引
-- =====================================================

-- 为配置引擎表创建软删除相关索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_form_configurations_tenant_active 
    ON form_configurations(tenant_id, is_active) WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_form_configurations_not_deleted 
    ON form_configurations(is_deleted) WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workflow_configurations_tenant_active 
    ON workflow_configurations(tenant_id, is_active) WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workflow_configurations_not_deleted 
    ON workflow_configurations(is_deleted) WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_spatial_configurations_tenant_active 
    ON spatial_configurations(tenant_id, is_active) WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_spatial_configurations_not_deleted 
    ON spatial_configurations(is_deleted) WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_business_rules_tenant_active 
    ON business_rules(tenant_id, is_active) WHERE is_deleted = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_business_rules_not_deleted 
    ON business_rules(is_deleted) WHERE is_deleted = FALSE;

-- =====================================================
-- 7. 创建软删除触发器函数
-- =====================================================

-- 创建软删除函数
CREATE OR REPLACE FUNCTION soft_delete_record()
RETURNS TRIGGER AS $$
BEGIN
    -- 如果is_deleted从false变为true，设置deleted_at时间
    IF OLD.is_deleted = FALSE AND NEW.is_deleted = TRUE THEN
        NEW.deleted_at = CURRENT_TIMESTAMP;
        -- 如果deleted_by为空，设置默认值
        IF NEW.deleted_by IS NULL THEN
            NEW.deleted_by = COALESCE(NEW.updated_by, 'system');
        END IF;
    -- 如果is_deleted从true变为false，清除删除时间
    ELSIF OLD.is_deleted = TRUE AND NEW.is_deleted = FALSE THEN
        NEW.deleted_at = NULL;
        NEW.deleted_by = NULL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为配置引擎表创建软删除触发器
DO $$
BEGIN
    -- form_configurations表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_form_configurations_soft_delete') THEN
        CREATE TRIGGER trigger_form_configurations_soft_delete
            BEFORE UPDATE ON form_configurations
            FOR EACH ROW EXECUTE FUNCTION soft_delete_record();
        RAISE NOTICE '✅ form_configurations表软删除触发器已创建';
    END IF;
    
    -- workflow_configurations表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_workflow_configurations_soft_delete') THEN
        CREATE TRIGGER trigger_workflow_configurations_soft_delete
            BEFORE UPDATE ON workflow_configurations
            FOR EACH ROW EXECUTE FUNCTION soft_delete_record();
        RAISE NOTICE '✅ workflow_configurations表软删除触发器已创建';
    END IF;
    
    -- spatial_configurations表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_spatial_configurations_soft_delete') THEN
        CREATE TRIGGER trigger_spatial_configurations_soft_delete
            BEFORE UPDATE ON spatial_configurations
            FOR EACH ROW EXECUTE FUNCTION soft_delete_record();
        RAISE NOTICE '✅ spatial_configurations表软删除触发器已创建';
    END IF;
    
    -- business_rules表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trigger_business_rules_soft_delete') THEN
        CREATE TRIGGER trigger_business_rules_soft_delete
            BEFORE UPDATE ON business_rules
            FOR EACH ROW EXECUTE FUNCTION soft_delete_record();
        RAISE NOTICE '✅ business_rules表软删除触发器已创建';
    END IF;
END $$;

-- =====================================================
-- 8. 更新表注释
-- =====================================================

COMMENT ON COLUMN form_configurations.is_deleted IS '软删除标记 - FALSE为正常，TRUE为已删除';
COMMENT ON COLUMN form_configurations.deleted_at IS '删除时间 - 软删除时自动设置';
COMMENT ON COLUMN form_configurations.deleted_by IS '删除操作人 - 记录软删除操作者';

COMMENT ON COLUMN workflow_configurations.is_deleted IS '软删除标记 - FALSE为正常，TRUE为已删除';
COMMENT ON COLUMN workflow_configurations.deleted_at IS '删除时间 - 软删除时自动设置';
COMMENT ON COLUMN workflow_configurations.deleted_by IS '删除操作人 - 记录软删除操作者';

COMMENT ON COLUMN spatial_configurations.is_deleted IS '软删除标记 - FALSE为正常，TRUE为已删除';
COMMENT ON COLUMN spatial_configurations.deleted_at IS '删除时间 - 软删除时自动设置';
COMMENT ON COLUMN spatial_configurations.deleted_by IS '删除操作人 - 记录软删除操作者';

COMMENT ON COLUMN business_rules.is_deleted IS '软删除标记 - FALSE为正常，TRUE为已删除';
COMMENT ON COLUMN business_rules.deleted_at IS '删除时间 - 软删除时自动设置';
COMMENT ON COLUMN business_rules.deleted_by IS '删除操作人 - 记录软删除操作者';

-- =====================================================
-- 9. 更新统计信息
-- =====================================================

ANALYZE form_configurations;
ANALYZE workflow_configurations;
ANALYZE spatial_configurations;
ANALYZE business_rules;
ANALYZE spatial_entities;
ANALYZE workflow_executions;
ANALYZE rule_execution_logs;

-- =====================================================
-- 10. 输出迁移结果
-- =====================================================

DO $$ 
BEGIN
    RAISE NOTICE '🎉 配置引擎审计字段补齐迁移完成！';
    RAISE NOTICE '✅ 已为4个核心配置引擎表添加审计字段：';
    RAISE NOTICE '   - form_configurations (表单配置)';
    RAISE NOTICE '   - workflow_configurations (工作流配置)';
    RAISE NOTICE '   - spatial_configurations (空间配置)';
    RAISE NOTICE '   - business_rules (业务规则)';
    RAISE NOTICE '✅ 已为3个相关子表添加审计字段：';
    RAISE NOTICE '   - spatial_entities (空间实体)';
    RAISE NOTICE '   - workflow_executions (工作流执行)';
    RAISE NOTICE '   - rule_execution_logs (规则执行日志)';
    RAISE NOTICE '✅ 已创建软删除功能相关索引和触发器';
    RAISE NOTICE '✅ 现在配置引擎完全支持软删除和审计追踪功能';
    RAISE NOTICE '📋 下一步：重启服务以应用新的数据库结构';
END $$;

-- 提交事务
COMMIT;

-- =====================================================
-- 11. 验证迁移结果（可选执行）
-- =====================================================

-- 验证所有表都有审计字段
SELECT 
    t.table_name,
    COUNT(CASE WHEN c.column_name = 'is_deleted' THEN 1 END) as has_is_deleted,
    COUNT(CASE WHEN c.column_name = 'deleted_at' THEN 1 END) as has_deleted_at,
    COUNT(CASE WHEN c.column_name = 'deleted_by' THEN 1 END) as has_deleted_by
FROM information_schema.tables t
LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE t.table_name IN (
    'form_configurations', 'workflow_configurations', 
    'spatial_configurations', 'business_rules',
    'spatial_entities', 'workflow_executions', 'rule_execution_logs'
)
AND t.table_schema = 'public'
GROUP BY t.table_name
ORDER BY t.table_name; 