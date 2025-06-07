-- 添加员工表缺失字段
-- 执行前请备份数据库

BEGIN;

-- 添加新字段
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS position VARCHAR(100);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS manager_id INTEGER;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS hire_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS birth_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS address VARCHAR(200);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_contact VARCHAR(100);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_phone VARCHAR(20);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS salary FLOAT;

-- 为现有员工设置默认的employee_id（如果为空）
UPDATE employees 
SET employee_id = 'EMP' || LPAD(id::text, 6, '0') 
WHERE employee_id IS NULL OR employee_id = '';

-- 添加约束
ALTER TABLE employees ADD CONSTRAINT IF NOT EXISTS employees_employee_id_unique UNIQUE (employee_id);
ALTER TABLE employees ADD CONSTRAINT IF NOT EXISTS employees_manager_id_fkey 
    FOREIGN KEY (manager_id) REFERENCES employees (id);

-- 设置employee_id为非空
ALTER TABLE employees ALTER COLUMN employee_id SET NOT NULL;

COMMIT; 