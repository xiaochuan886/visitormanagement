-- 员工认证系统修复迁移脚本
-- 修复已存在的表结构并添加认证功能

-- 1. 添加认证字段到员工表
ALTER TABLE employees ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS username VARCHAR(100);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS login_attempts INTEGER DEFAULT 0;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;

-- 2. 确保email唯一性
DROP INDEX IF EXISTS idx_employees_email_unique;
CREATE UNIQUE INDEX idx_employees_email_unique ON employees(email) 
WHERE email IS NOT NULL AND (is_deleted IS FALSE OR is_deleted IS NULL);

-- 3. 检查并修复user_roles表结构  
ALTER TABLE user_roles ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE user_roles ADD COLUMN IF NOT EXISTS updated_by VARCHAR(100);
ALTER TABLE user_roles ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE user_roles ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE user_roles ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(100);

-- 4. 清理并重新插入默认角色
DELETE FROM user_roles WHERE name IN ('admin', 'manager', 'employee', 'visitor_manager');

INSERT INTO user_roles (name, description, permissions, created_by) VALUES
('admin', '系统管理员', ARRAY['*'], 'system'),
('manager', '部门经理', ARRAY['visitor:read', 'visitor:write', 'visitor:approve', 'employee:read', 'department:read'], 'system'),
('employee', '普通员工', ARRAY['visitor:read', 'visitor:create'], 'system'),
('visitor_manager', '访客管理员', ARRAY['visitor:*', 'department:read', 'employee:read'], 'system');

-- 5. 适配现有employee_roles表结构
-- 表已存在，不需要创建，但需要确保有正确的引用关系

-- 6. 创建或更新默认管理员（密码: admin123）
-- 先删除已存在的测试管理员
DELETE FROM employees WHERE email IN ('admin@company.com', 'admin@example.com');

INSERT INTO employees (
    name, 
    email, 
    username,
    employee_id, 
    password_hash, 
    status, 
    created_by,
    position,
    department_id,
    created_at,
    updated_at
) VALUES (
    'System Administrator', 
    'admin@example.com', 
    'admin',
    'ADMIN001', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqyc3.pNj6SfPnJ8EZXRnKm', -- 'admin123'
    'active', 
    'system',
    'System Administrator',
    NULL,
    NOW(),
    NOW()
);

-- 7. 分配管理员角色
INSERT INTO employee_roles (employee_id, role_id, assigned_by, assigned_at, is_active)
SELECT e.id, r.id, 'system', NOW(), true
FROM employees e, user_roles r
WHERE e.email = 'admin@example.com' AND r.name = 'admin'
ON CONFLICT (employee_id, role_id) DO NOTHING;

-- 8. 创建认证相关索引
CREATE INDEX IF NOT EXISTS idx_employees_password_hash ON employees(password_hash) WHERE password_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_username ON employees(username) WHERE username IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_last_login ON employees(last_login_at);
CREATE INDEX IF NOT EXISTS idx_user_roles_name ON user_roles(name);
CREATE INDEX IF NOT EXISTS idx_employee_roles_employee ON employee_roles(employee_id);

-- 9. 创建用户名唯一索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_username_unique ON employees(username) 
WHERE username IS NOT NULL AND (is_deleted IS FALSE OR is_deleted IS NULL);

-- 10. 验证创建结果
DO $$
DECLARE
    admin_count INTEGER;
    role_count INTEGER;
    password_field_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO admin_count FROM employees WHERE email = 'admin@example.com' AND password_hash IS NOT NULL;
    SELECT COUNT(*) INTO role_count FROM user_roles;
    SELECT COUNT(*) INTO password_field_count FROM information_schema.columns 
    WHERE table_name = 'employees' AND column_name = 'password_hash';
    
    RAISE NOTICE '管理员账户创建: %', CASE WHEN admin_count > 0 THEN '成功' ELSE '失败' END;
    RAISE NOTICE '角色创建数量: %', role_count;
    RAISE NOTICE 'password_hash字段: %', CASE WHEN password_field_count > 0 THEN '存在' ELSE '不存在' END;
END $$; 