-- =====================================================
-- 访客管理系统数据库优化脚本
-- 版本: v2.0
-- 创建日期: 2025-06-07
-- 说明: 基于实际DDL分析的性能优化和数据完整性增强
-- =====================================================

-- 开始事务
BEGIN;

-- =====================================================
-- 1. 创建枚举类型
-- =====================================================

-- 创建访客状态枚举（如果不存在）
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'visitor_status') THEN
        CREATE TYPE visitor_status AS ENUM (
            'pending',      -- 待审批
            'approved',     -- 已审批
            'rejected',     -- 已拒绝
            'checked_in',   -- 已签到
            'checked_out',  -- 已签出
            'cancelled',    -- 已取消
            'expired'       -- 已过期
        );
    END IF;
END $$;

-- 创建审批动作枚举（如果不存在）
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'approval_action') THEN
        CREATE TYPE approval_action AS ENUM (
            'approve',   -- 审批通过
            'reject',    -- 审批拒绝
            'modify',    -- 修改信息
            'cancel'     -- 取消申请
        );
    END IF;
END $$;

-- =====================================================
-- 2. 添加检查约束
-- =====================================================

-- 站点表约束
DO $$ 
BEGIN
    -- 站点状态约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_sites_status') THEN
        ALTER TABLE sites ADD CONSTRAINT chk_sites_status 
            CHECK (status IN ('active', 'inactive', 'maintenance'));
    END IF;
    
    -- 站点邮箱格式约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_sites_email') THEN
        ALTER TABLE sites ADD CONSTRAINT chk_sites_email 
            CHECK (email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
    END IF;
END $$;

-- 部门表约束
DO $$ 
BEGIN
    -- 部门邮箱格式约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_departments_email') THEN
        ALTER TABLE departments ADD CONSTRAINT chk_departments_email 
            CHECK (email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
    END IF;
    
    -- 防止自引用约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_departments_no_self_parent') THEN
        ALTER TABLE departments ADD CONSTRAINT chk_departments_no_self_parent 
            CHECK (parent_id != id);
    END IF;
END $$;

-- 职位表约束
DO $$ 
BEGIN
    -- 职位级别约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_designations_level') THEN
        ALTER TABLE designations ADD CONSTRAINT chk_designations_level 
            CHECK (level >= 1 AND level <= 10);
    END IF;
END $$;

-- 员工表约束
DO $$ 
BEGIN
    -- 员工状态约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_employees_status') THEN
        ALTER TABLE employees ADD CONSTRAINT chk_employees_status 
            CHECK (status IN ('active', 'inactive', 'terminated', 'on_leave'));
    END IF;
    
    -- 员工邮箱格式约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_employees_email') THEN
        ALTER TABLE employees ADD CONSTRAINT chk_employees_email 
            CHECK (email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
    END IF;
    
    -- 性别约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_employees_gender') THEN
        ALTER TABLE employees ADD CONSTRAINT chk_employees_gender 
            CHECK (gender IS NULL OR gender IN ('male', 'female', 'other'));
    END IF;
    
    -- 防止自引用管理者约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_employees_no_self_manager') THEN
        ALTER TABLE employees ADD CONSTRAINT chk_employees_no_self_manager 
            CHECK (manager_id != id);
    END IF;
    
    -- 薪资非负约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_employees_salary') THEN
        ALTER TABLE employees ADD CONSTRAINT chk_employees_salary 
            CHECK (salary IS NULL OR salary >= 0);
    END IF;
END $$;

-- 访客表约束
DO $$ 
BEGIN
    -- 签出时间晚于签到时间约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_visitors_checkout_after_checkin') THEN
        ALTER TABLE visitors ADD CONSTRAINT chk_visitors_checkout_after_checkin 
            CHECK (checkout_date IS NULL OR checkin_date IS NULL OR checkout_date > checkin_date);
    END IF;
    
    -- 访客邮箱格式约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_visitors_email') THEN
        ALTER TABLE visitors ADD CONSTRAINT chk_visitors_email 
            CHECK (email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
    END IF;
    
    -- 性别约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_visitors_gender') THEN
        ALTER TABLE visitors ADD CONSTRAINT chk_visitors_gender 
            CHECK (gender IS NULL OR gender IN ('male', 'female', 'other'));
    END IF;
    
    -- 调查问卷得分约束
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_visitors_survey_score') THEN
        ALTER TABLE visitors ADD CONSTRAINT chk_visitors_survey_score 
            CHECK (survey_response_value IS NULL OR (survey_response_value >= 1 AND survey_response_value <= 10));
    END IF;
END $$;

-- =====================================================
-- 3. 创建性能优化索引
-- =====================================================

-- 站点表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sites_tenant_status 
    ON sites(tenant_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sites_location 
    ON sites(latitude, longitude) WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

-- 部门表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_departments_tenant_site 
    ON departments(tenant_id, site_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_departments_parent 
    ON departments(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_departments_manager 
    ON departments(manager_id) WHERE manager_id IS NOT NULL;

-- 职位表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_designations_tenant_site 
    ON designations(tenant_id, site_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_designations_level 
    ON designations(level);

-- 员工表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employees_tenant_dept 
    ON employees(tenant_id, department_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employees_manager 
    ON employees(manager_id) WHERE manager_id IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employees_status_active 
    ON employees(status) WHERE status = 'active';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employees_email_search 
    ON employees(email) WHERE email IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employees_name_search 
    ON employees(lower(name));

-- 访客表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_tenant_status 
    ON visitors(tenant_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_employee_date 
    ON visitors(employee_id, expected_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_phone_search 
    ON visitors(phone_number) WHERE phone_number IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_checkin_date 
    ON visitors(checkin_date) WHERE checkin_date IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_name_search 
    ON visitors(lower(name));
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_company_search 
    ON visitors(company_name) WHERE company_name IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_tenant_status_date 
    ON visitors(tenant_id, status, expected_date);

-- 部分索引优化
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_pending 
    ON visitors(tenant_id, created_at) WHERE status = 'pending';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitors_today 
    ON visitors(employee_id, status) WHERE DATE(created_at) = CURRENT_DATE;

-- 访客历史表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitor_histories_visitor 
    ON visitor_histories(visitor_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitor_histories_tenant_time 
    ON visitor_histories(tenant_id, action_time DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_visitor_histories_action 
    ON visitor_histories(action);

-- 审批历史表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approval_histories_visitor 
    ON approval_histories(visitor_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approval_histories_approver 
    ON approval_histories(approver_id) WHERE approver_id IS NOT NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_approval_histories_tenant_date 
    ON approval_histories(tenant_id, approval_date DESC);

-- 签到点表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkin_points_tenant_site 
    ON checkin_points(tenant_id, site_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_checkin_points_active 
    ON checkin_points(is_active) WHERE is_active = TRUE;

-- 同行人员表索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companions_visitor 
    ON companions(visitor_id);

-- =====================================================
-- 4. 创建触发器函数
-- =====================================================

-- 更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 访客状态自动更新函数
CREATE OR REPLACE FUNCTION auto_update_visitor_status()
RETURNS TRIGGER AS $$
BEGIN
    -- 签到时自动更新状态
    IF NEW.checkin_date IS NOT NULL AND (OLD.checkin_date IS NULL OR OLD.checkin_date != NEW.checkin_date) THEN
        NEW.status = 'checked_in';
    END IF;
    
    -- 签出时自动更新状态
    IF NEW.checkout_date IS NOT NULL AND (OLD.checkout_date IS NULL OR OLD.checkout_date != NEW.checkout_date) THEN
        NEW.status = 'checked_out';
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 数据验证函数
CREATE OR REPLACE FUNCTION validate_phone(phone TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN phone IS NULL OR phone ~ '^[0-9+\-\s()]{10,20}$';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validate_id_card(id_card TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN id_card IS NULL OR id_card ~ '^[0-9X]{15,18}$';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 5. 创建触发器
-- =====================================================

-- 为所有需要的表添加更新时间触发器
DO $$ 
BEGIN
    -- 站点表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_sites_updated_at') THEN
        CREATE TRIGGER update_sites_updated_at 
            BEFORE UPDATE ON sites 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 部门表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_departments_updated_at') THEN
        CREATE TRIGGER update_departments_updated_at 
            BEFORE UPDATE ON departments 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 职位表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_designations_updated_at') THEN
        CREATE TRIGGER update_designations_updated_at 
            BEFORE UPDATE ON designations 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 员工表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_employees_updated_at') THEN
        CREATE TRIGGER update_employees_updated_at 
            BEFORE UPDATE ON employees 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 访客表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_visitors_updated_at') THEN
        CREATE TRIGGER update_visitors_updated_at 
            BEFORE UPDATE ON visitors 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 签到点表
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_checkin_points_updated_at') THEN
        CREATE TRIGGER update_checkin_points_updated_at 
            BEFORE UPDATE ON checkin_points 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    -- 访客状态自动更新触发器
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'auto_update_visitor_status_trigger') THEN
        CREATE TRIGGER auto_update_visitor_status_trigger
            BEFORE UPDATE ON visitors
            FOR EACH ROW EXECUTE FUNCTION auto_update_visitor_status();
    END IF;
END $$;

-- =====================================================
-- 6. 创建优化视图
-- =====================================================

-- 访客详情视图
CREATE OR REPLACE VIEW visitor_details AS
SELECT 
    v.*,
    e.name as host_employee_name,
    e.email as host_employee_email,
    e.phone_number as host_employee_phone,
    e.position as host_employee_position,
    d.name as department_name,
    s.name as site_name,
    s.address as site_address,
    des.name as designation_name,
    des.level as designation_level
FROM visitors v
LEFT JOIN employees e ON v.employee_id = e.id
LEFT JOIN departments d ON e.department_id = d.id
LEFT JOIN sites s ON v.site_id = s.id
LEFT JOIN designations des ON v.designation_id = des.id;

-- 部门统计视图
CREATE OR REPLACE VIEW department_stats AS
SELECT 
    d.id,
    d.name,
    d.tenant_id,
    s.name as site_name,
    COUNT(DISTINCT e.id) FILTER (WHERE e.status = 'active') as active_employee_count,
    COUNT(DISTINCT v.id) FILTER (WHERE DATE(v.created_at) = CURRENT_DATE) as visitor_count_today,
    COUNT(DISTINCT v.id) FILTER (WHERE v.status = 'pending') as pending_visitor_count
FROM departments d
LEFT JOIN sites s ON d.site_id = s.id
LEFT JOIN employees e ON d.id = e.department_id
LEFT JOIN visitors v ON e.id = v.employee_id
GROUP BY d.id, d.name, d.tenant_id, s.name;

-- 员工访客统计视图
CREATE OR REPLACE VIEW employee_visitor_stats AS
SELECT 
    e.id,
    e.name,
    e.employee_id,
    e.tenant_id,
    d.name as department_name,
    COUNT(v.id) as total_visitors,
    COUNT(v.id) FILTER (WHERE v.status = 'pending') as pending_visitors,
    COUNT(v.id) FILTER (WHERE v.status = 'approved') as approved_visitors,
    COUNT(v.id) FILTER (WHERE DATE(v.created_at) = CURRENT_DATE) as today_visitors
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
LEFT JOIN visitors v ON e.id = v.employee_id
WHERE e.status = 'active'
GROUP BY e.id, e.name, e.employee_id, e.tenant_id, d.name;

-- =====================================================
-- 7. 添加表注释
-- =====================================================

-- 表注释
COMMENT ON TABLE sites IS '站点表 - 存储组织的物理位置信息';
COMMENT ON TABLE departments IS '部门表 - 组织架构管理';
COMMENT ON TABLE designations IS '职位表 - 定义组织内的职位信息';
COMMENT ON TABLE employees IS '员工表 - 存储员工基本信息和组织关系';
COMMENT ON TABLE visitors IS '访客表 - 存储访客信息和访问记录';
COMMENT ON TABLE visitor_histories IS '访客历史表 - 记录访客状态变更和操作日志';
COMMENT ON TABLE approval_histories IS '审批历史表 - 记录访客审批流程';
COMMENT ON TABLE checkin_points IS '签到点表 - 定义访客签到签出位置';
COMMENT ON TABLE companions IS '同行人员表 - 记录访客的同行人员信息';

-- 关键字段注释
COMMENT ON COLUMN sites.code IS '站点编码 - 全局唯一标识';
COMMENT ON COLUMN sites.working_hours_start IS '工作时间开始 - HH:MM格式';
COMMENT ON COLUMN departments.parent_id IS '上级部门ID - 支持层级结构';
COMMENT ON COLUMN designations.level IS '职位级别 - 1-10，数字越大级别越高';
COMMENT ON COLUMN employees.employee_id IS '员工工号 - 全局唯一标识';
COMMENT ON COLUMN employees.manager_id IS '上级员工ID - 支持组织层级';
COMMENT ON COLUMN visitors.status IS '访客状态 - 使用枚举类型确保数据一致性';

-- =====================================================
-- 8. 创建统计信息收集
-- =====================================================

-- 更新表统计信息
ANALYZE sites;
ANALYZE departments;
ANALYZE designations;
ANALYZE employees;
ANALYZE visitors;
ANALYZE visitor_histories;
ANALYZE approval_histories;
ANALYZE checkin_points;
ANALYZE companions;

-- =====================================================
-- 9. 输出优化结果
-- =====================================================

-- 显示优化完成信息
DO $$ 
BEGIN
    RAISE NOTICE '数据库优化完成！';
    RAISE NOTICE '- 已创建枚举类型: visitor_status, approval_action';
    RAISE NOTICE '- 已添加 % 个检查约束', (
        SELECT COUNT(*) FROM pg_constraint 
        WHERE conname LIKE 'chk_%' 
        AND conrelid IN (
            SELECT oid FROM pg_class 
            WHERE relname IN ('sites', 'departments', 'designations', 'employees', 'visitors')
        )
    );
    RAISE NOTICE '- 已创建 % 个性能优化索引', (
        SELECT COUNT(*) FROM pg_indexes 
        WHERE indexname LIKE 'idx_%'
        AND tablename IN ('sites', 'departments', 'designations', 'employees', 'visitors', 'visitor_histories', 'approval_histories', 'checkin_points', 'companions')
    );
    RAISE NOTICE '- 已创建触发器和优化视图';
    RAISE NOTICE '- 已更新表统计信息';
END $$;

-- 提交事务
COMMIT;

-- =====================================================
-- 10. 验证脚本（可选执行）
-- =====================================================

-- 验证约束是否正确创建
SELECT 
    conname as constraint_name,
    conrelid::regclass as table_name,
    contype as constraint_type
FROM pg_constraint 
WHERE conname LIKE 'chk_%'
ORDER BY conrelid::regclass, conname;

-- 验证索引是否正确创建
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE indexname LIKE 'idx_%'
AND tablename IN ('sites', 'departments', 'designations', 'employees', 'visitors', 'visitor_histories', 'approval_histories', 'checkin_points', 'companions')
ORDER BY tablename, indexname;

-- 验证触发器是否正确创建
SELECT 
    tgname as trigger_name,
    tgrelid::regclass as table_name,
    proname as function_name
FROM pg_trigger t
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE tgname LIKE '%update%'
ORDER BY tgrelid::regclass, tgname; 