-- =====================================================
-- 访客状态枚举化完善迁移脚本
-- 版本: v1.0
-- 日期: 2025-06-07
-- 描述: 将visitors.status字段从VARCHAR迁移到visitor_status枚举类型
-- =====================================================

BEGIN;

-- 1. 数据一致性检查
DO $$
DECLARE
    invalid_count INTEGER;
BEGIN
    -- 检查是否有无效的状态值
    SELECT COUNT(*) INTO invalid_count
    FROM visitors 
    WHERE status IS NOT NULL 
    AND status NOT IN ('pending', 'approved', 'rejected', 'checked_in', 'checked_out', 'cancelled', 'expired');
    
    IF invalid_count > 0 THEN
        RAISE EXCEPTION '发现 % 条无效状态数据，请先清理数据', invalid_count;
    END IF;
    
    RAISE NOTICE '✅ 数据一致性检查通过，共检查 % 条记录', (SELECT COUNT(*) FROM visitors WHERE status IS NOT NULL);
END $$;

-- 2. 备份当前状态数据
CREATE TEMP TABLE visitors_status_backup AS 
SELECT id, status, created_at 
FROM visitors 
WHERE status IS NOT NULL;

RAISE NOTICE '✅ 已备份 % 条状态记录', (SELECT COUNT(*) FROM visitors_status_backup);

-- 3. 添加临时枚举字段
ALTER TABLE visitors ADD COLUMN status_enum visitor_status;

-- 4. 数据迁移
UPDATE visitors 
SET status_enum = CASE 
    WHEN status = 'pending' THEN 'pending'::visitor_status
    WHEN status = 'approved' THEN 'approved'::visitor_status
    WHEN status = 'rejected' THEN 'rejected'::visitor_status
    WHEN status = 'checked_in' THEN 'checked_in'::visitor_status
    WHEN status = 'checked_out' THEN 'checked_out'::visitor_status
    WHEN status = 'cancelled' THEN 'cancelled'::visitor_status
    WHEN status = 'expired' THEN 'expired'::visitor_status
    ELSE NULL
END
WHERE status IS NOT NULL;

-- 5. 验证迁移结果
DO $$
DECLARE
    migrated_count INTEGER;
    original_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO original_count FROM visitors_status_backup;
    SELECT COUNT(*) INTO migrated_count FROM visitors WHERE status_enum IS NOT NULL;
    
    IF migrated_count != original_count THEN
        RAISE EXCEPTION '迁移失败：原始记录 %，迁移记录 %', original_count, migrated_count;
    END IF;
    
    RAISE NOTICE '✅ 数据迁移验证通过：% 条记录成功迁移', migrated_count;
END $$;

-- 6. 删除旧字段约束和索引
DROP INDEX IF EXISTS idx_visitors_tenant_status;
DROP INDEX IF EXISTS idx_visitors_tenant_status_date;
DROP INDEX IF EXISTS idx_visitors_employee_status;
DROP INDEX IF EXISTS idx_visitors_pending;

-- 7. 删除旧字段
ALTER TABLE visitors DROP COLUMN status;

-- 8. 重命名新字段
ALTER TABLE visitors RENAME COLUMN status_enum TO status;

-- 9. 添加NOT NULL约束（如果需要）
-- ALTER TABLE visitors ALTER COLUMN status SET NOT NULL;

-- 10. 重建优化索引
CREATE INDEX idx_visitors_tenant_status ON visitors(tenant_id, status);
CREATE INDEX idx_visitors_tenant_status_date ON visitors(tenant_id, status, expected_date);
CREATE INDEX idx_visitors_employee_status ON visitors(employee_id, status);
CREATE INDEX idx_visitors_pending ON visitors(tenant_id, created_at) WHERE status = 'pending';

-- 11. 更新表注释
COMMENT ON COLUMN visitors.status IS '访客状态 - 使用visitor_status枚举类型确保数据一致性';

-- 12. 创建状态统计视图
CREATE OR REPLACE VIEW visitor_status_stats AS
SELECT 
    tenant_id,
    status,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE DATE(created_at) = CURRENT_DATE) as today_count,
    COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as week_count,
    COUNT(*) FILTER (WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as month_count
FROM visitors 
WHERE NOT is_deleted 
GROUP BY tenant_id, status
ORDER BY tenant_id, status;

COMMENT ON VIEW visitor_status_stats IS '访客状态统计视图 - 提供各状态的实时统计数据';

-- 13. 验证最终结果
DO $$
DECLARE
    enum_count INTEGER;
    index_count INTEGER;
BEGIN
    -- 检查枚举字段
    SELECT COUNT(*) INTO enum_count
    FROM information_schema.columns 
    WHERE table_name = 'visitors' 
    AND column_name = 'status' 
    AND data_type = 'USER-DEFINED';
    
    IF enum_count != 1 THEN
        RAISE EXCEPTION '枚举字段创建失败';
    END IF;
    
    -- 检查索引
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes 
    WHERE tablename = 'visitors' 
    AND indexname LIKE '%status%';
    
    RAISE NOTICE '✅ 迁移完成验证：枚举字段 %，状态索引 %', enum_count, index_count;
END $$;

COMMIT;

-- 14. 清理临时表
DROP TABLE IF EXISTS visitors_status_backup;

RAISE NOTICE '🎉 访客状态枚举化迁移完成！';
RAISE NOTICE '📊 新增功能：';
RAISE NOTICE '   - visitor_status枚举类型确保数据一致性';
RAISE NOTICE '   - 4个优化索引提升查询性能';
RAISE NOTICE '   - visitor_status_stats统计视图';
RAISE NOTICE '⚠️  请更新应用层代码以使用新的枚举类型'; 