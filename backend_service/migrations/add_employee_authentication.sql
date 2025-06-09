-- 员工认证系统迁移脚本
-- 添加认证相关字段到员工表

-- 1. 添加认证字段
ALTER TABLE employees ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS login_attempts INTEGER DEFAULT 0;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;

-- 2. 确保email唯一性
CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_email_unique ON employees(email) 
WHERE email IS NOT NULL AND NOT is_deleted;

-- 3. 创建角色表
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB,
    tenant_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 审计字段
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by VARCHAR(100)
);

-- 4. 创建员工角色关联表
CREATE TABLE IF NOT EXISTS employee_roles (
    employee_id INTEGER REFERENCES employees(id),
    role_id INTEGER REFERENCES user_roles(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by VARCHAR(100),
    tenant_id VARCHAR(50),
    PRIMARY KEY (employee_id, role_id)
);

-- 5. 插入默认角色
INSERT INTO user_roles (name, description, permissions, tenant_id, created_by) VALUES
('admin', '系统管理员', '["*"]', 'default', 'system'),
('manager', '部门经理', '["visitor:read", "visitor:write", "visitor:approve", "employee:read", "department:read"]', 'default', 'system'),
('employee', '普通员工', '["visitor:read", "visitor:create"]', 'default', 'system'),
('visitor_manager', '访客管理员', '["visitor:*", "department:read", "employee:read"]', 'default', 'system')
ON CONFLICT (name) DO NOTHING;

-- 6. 创建默认管理员（密码: admin123）
-- 先检查是否已存在管理员
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM employees WHERE email = 'admin@company.com') THEN
        INSERT INTO employees (
            name, 
            email, 
            employee_id, 
            password_hash, 
            status, 
            tenant_id, 
            created_by,
            position,
            department_id
        ) VALUES (
            'System Administrator', 
            'admin@company.com', 
            'ADMIN001', 
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqyc3.pNj6SfPnJ8EZXRnKm', -- 'admin123'
            'active', 
            'default', 
            'system',
            'System Administrator',
            NULL
        );
    ELSE
        -- 如果已存在，更新密码
        UPDATE employees 
        SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqyc3.pNj6SfPnJ8EZXRnKm',
            status = 'active'
        WHERE email = 'admin@company.com';
    END IF;
END $$;

-- 7. 分配管理员角色
INSERT INTO employee_roles (employee_id, role_id, granted_by, tenant_id)
SELECT e.id, r.id, 'system', 'default'
FROM employees e, user_roles r
WHERE e.email = 'admin@company.com' AND r.name = 'admin'
ON CONFLICT DO NOTHING;

-- 8. 创建认证相关索引
CREATE INDEX IF NOT EXISTS idx_employees_password_hash ON employees(password_hash) WHERE password_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_last_login ON employees(last_login_at);
CREATE INDEX IF NOT EXISTS idx_user_roles_name ON user_roles(name);
CREATE INDEX IF NOT EXISTS idx_employee_roles_employee ON employee_roles(employee_id);

-- 9. 添加更新时间触发器
CREATE OR REPLACE FUNCTION update_user_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_user_roles_updated_at
    BEFORE UPDATE ON user_roles
    FOR EACH ROW EXECUTE FUNCTION update_user_roles_updated_at();

-- 10. 验证创建结果
DO $$
DECLARE
    admin_count INTEGER;
    role_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO admin_count FROM employees WHERE email = 'admin@company.com' AND password_hash IS NOT NULL;
    SELECT COUNT(*) INTO role_count FROM user_roles;
    
    RAISE NOTICE '管理员账户创建: %', CASE WHEN admin_count > 0 THEN '成功' ELSE '失败' END;
    RAISE NOTICE '角色创建数量: %', role_count;
END $$; 