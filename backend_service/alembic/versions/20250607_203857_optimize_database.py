"""optimize_database

Revision ID: 20250607_203857
Revises: 
Create Date: 2025-06-07 20:38:57.000000

数据库优化迁移：
- 创建枚举类型
- 添加检查约束
- 创建性能优化索引
- 添加触发器和视图
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250607_203857'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """执行数据库优化升级"""
    
    # 1. 创建枚举类型
    visitor_status_enum = postgresql.ENUM(
        'pending', 'approved', 'rejected', 'checked_in', 
        'checked_out', 'cancelled', 'expired',
        name='visitor_status'
    )
    visitor_status_enum.create(op.get_bind(), checkfirst=True)
    
    approval_action_enum = postgresql.ENUM(
        'approve', 'reject', 'modify', 'cancel',
        name='approval_action'
    )
    approval_action_enum.create(op.get_bind(), checkfirst=True)
    
    # 2. 添加检查约束
    # 站点表约束
    op.create_check_constraint(
        'chk_sites_status',
        'sites',
        "status IN ('active', 'inactive', 'maintenance')"
    )
    op.create_check_constraint(
        'chk_sites_email',
        'sites',
        "email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
    )
    
    # 部门表约束
    op.create_check_constraint(
        'chk_departments_email',
        'departments',
        "email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
    )
    op.create_check_constraint(
        'chk_departments_no_self_parent',
        'departments',
        'parent_id != id'
    )
    
    # 职位表约束
    op.create_check_constraint(
        'chk_designations_level',
        'designations',
        'level >= 1 AND level <= 10'
    )
    
    # 员工表约束
    op.create_check_constraint(
        'chk_employees_status',
        'employees',
        "status IN ('active', 'inactive', 'terminated', 'on_leave')"
    )
    op.create_check_constraint(
        'chk_employees_email',
        'employees',
        "email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
    )
    op.create_check_constraint(
        'chk_employees_gender',
        'employees',
        "gender IS NULL OR gender IN ('male', 'female', 'other')"
    )
    op.create_check_constraint(
        'chk_employees_no_self_manager',
        'employees',
        'manager_id != id'
    )
    op.create_check_constraint(
        'chk_employees_salary',
        'employees',
        'salary IS NULL OR salary >= 0'
    )
    
    # 访客表约束
    op.create_check_constraint(
        'chk_visitors_checkout_after_checkin',
        'visitors',
        'checkout_date IS NULL OR checkin_date IS NULL OR checkout_date > checkin_date'
    )
    op.create_check_constraint(
        'chk_visitors_email',
        'visitors',
        "email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
    )
    op.create_check_constraint(
        'chk_visitors_gender',
        'visitors',
        "gender IS NULL OR gender IN ('male', 'female', 'other')"
    )
    op.create_check_constraint(
        'chk_visitors_survey_score',
        'visitors',
        'survey_response_value IS NULL OR (survey_response_value >= 1 AND survey_response_value <= 10)'
    )
    
    # 3. 创建性能优化索引
    # 站点表索引
    op.create_index('idx_sites_tenant_status', 'sites', ['tenant_id', 'status'])
    op.create_index('idx_sites_location', 'sites', ['latitude', 'longitude'], 
                   postgresql_where=sa.text('latitude IS NOT NULL AND longitude IS NOT NULL'))
    
    # 部门表索引
    op.create_index('idx_departments_tenant_site', 'departments', ['tenant_id', 'site_id'])
    op.create_index('idx_departments_parent', 'departments', ['parent_id'], 
                   postgresql_where=sa.text('parent_id IS NOT NULL'))
    op.create_index('idx_departments_manager', 'departments', ['manager_id'], 
                   postgresql_where=sa.text('manager_id IS NOT NULL'))
    
    # 职位表索引
    op.create_index('idx_designations_tenant_site', 'designations', ['tenant_id', 'site_id'])
    op.create_index('idx_designations_level', 'designations', ['level'])
    
    # 员工表索引
    op.create_index('idx_employees_tenant_dept', 'employees', ['tenant_id', 'department_id'])
    op.create_index('idx_employees_manager', 'employees', ['manager_id'], 
                   postgresql_where=sa.text('manager_id IS NOT NULL'))
    op.create_index('idx_employees_status_active', 'employees', ['status'], 
                   postgresql_where=sa.text("status = 'active'"))
    op.create_index('idx_employees_email_search', 'employees', ['email'], 
                   postgresql_where=sa.text('email IS NOT NULL'))
    op.create_index('idx_employees_name_search', 'employees', [sa.text('lower(name)')])
    
    # 访客表索引
    op.create_index('idx_visitors_tenant_status', 'visitors', ['tenant_id', 'status'])
    op.create_index('idx_visitors_employee_date', 'visitors', ['employee_id', 'expected_date'])
    op.create_index('idx_visitors_phone_search', 'visitors', ['phone_number'], 
                   postgresql_where=sa.text('phone_number IS NOT NULL'))
    op.create_index('idx_visitors_checkin_date', 'visitors', ['checkin_date'], 
                   postgresql_where=sa.text('checkin_date IS NOT NULL'))
    op.create_index('idx_visitors_name_search', 'visitors', [sa.text('lower(name)')])
    op.create_index('idx_visitors_company_search', 'visitors', ['company_name'], 
                   postgresql_where=sa.text('company_name IS NOT NULL'))
    op.create_index('idx_visitors_tenant_status_date', 'visitors', ['tenant_id', 'status', 'expected_date'])
    
    # 部分索引优化
    op.create_index('idx_visitors_pending', 'visitors', ['tenant_id', 'created_at'], 
                   postgresql_where=sa.text("status = 'pending'"))
    # 移除有问题的索引，改为简单的复合索引
    op.create_index('idx_visitors_employee_status', 'visitors', ['employee_id', 'status'])
    
    # 访客历史表索引
    op.create_index('idx_visitor_histories_visitor', 'visitor_histories', ['visitor_id'])
    op.create_index('idx_visitor_histories_tenant_time', 'visitor_histories', ['tenant_id', sa.text('action_time DESC')])
    op.create_index('idx_visitor_histories_action', 'visitor_histories', ['action'])
    
    # 审批历史表索引
    op.create_index('idx_approval_histories_visitor', 'approval_histories', ['visitor_id'])
    op.create_index('idx_approval_histories_approver', 'approval_histories', ['approver_id'], 
                   postgresql_where=sa.text('approver_id IS NOT NULL'))
    op.create_index('idx_approval_histories_tenant_date', 'approval_histories', ['tenant_id', sa.text('approval_date DESC')])
    
    # 签到点表索引
    op.create_index('idx_checkin_points_tenant_site', 'checkin_points', ['tenant_id', 'site_id'])
    op.create_index('idx_checkin_points_active', 'checkin_points', ['is_active'], 
                   postgresql_where=sa.text('is_active = TRUE'))
    
    # 同行人员表索引
    op.create_index('idx_companions_visitor', 'companions', ['visitor_id'])
    
    # 4. 创建触发器函数
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
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
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_phone(phone TEXT)
        RETURNS BOOLEAN AS $$
        BEGIN
            RETURN phone IS NULL OR phone ~ '^[0-9+\\-\\s()]{10,20}$';
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_id_card(id_card TEXT)
        RETURNS BOOLEAN AS $$
        BEGIN
            RETURN id_card IS NULL OR id_card ~ '^[0-9X]{15,18}$';
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # 5. 创建触发器
    trigger_tables = [
        'sites', 'departments', 'designations', 
        'employees', 'visitors', 'checkin_points'
    ]
    
    for table in trigger_tables:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at 
                BEFORE UPDATE ON {table} 
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)
    
    # 访客状态自动更新触发器
    op.execute("""
        CREATE TRIGGER auto_update_visitor_status_trigger
            BEFORE UPDATE ON visitors
            FOR EACH ROW EXECUTE FUNCTION auto_update_visitor_status();
    """)
    
    # 6. 创建优化视图
    op.execute("""
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
    """)
    
    op.execute("""
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
    """)
    
    op.execute("""
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
    """)
    
    # 7. 添加表注释
    op.execute("COMMENT ON TABLE sites IS '站点表 - 存储组织的物理位置信息'")
    op.execute("COMMENT ON TABLE departments IS '部门表 - 组织架构管理'")
    op.execute("COMMENT ON TABLE designations IS '职位表 - 定义组织内的职位信息'")
    op.execute("COMMENT ON TABLE employees IS '员工表 - 存储员工基本信息和组织关系'")
    op.execute("COMMENT ON TABLE visitors IS '访客表 - 存储访客信息和访问记录'")
    op.execute("COMMENT ON TABLE visitor_histories IS '访客历史表 - 记录访客状态变更和操作日志'")
    op.execute("COMMENT ON TABLE approval_histories IS '审批历史表 - 记录访客审批流程'")
    op.execute("COMMENT ON TABLE checkin_points IS '签到点表 - 定义访客签到签出位置'")
    op.execute("COMMENT ON TABLE companions IS '同行人员表 - 记录访客的同行人员信息'")
    
    # 关键字段注释
    op.execute("COMMENT ON COLUMN sites.code IS '站点编码 - 全局唯一标识'")
    op.execute("COMMENT ON COLUMN sites.working_hours_start IS '工作时间开始 - HH:MM格式'")
    op.execute("COMMENT ON COLUMN departments.parent_id IS '上级部门ID - 支持层级结构'")
    op.execute("COMMENT ON COLUMN designations.level IS '职位级别 - 1-10，数字越大级别越高'")
    op.execute("COMMENT ON COLUMN employees.employee_id IS '员工工号 - 全局唯一标识'")
    op.execute("COMMENT ON COLUMN employees.manager_id IS '上级员工ID - 支持组织层级'")
    op.execute("COMMENT ON COLUMN visitors.status IS '访客状态 - 使用枚举类型确保数据一致性'")


def downgrade():
    """回滚数据库优化"""
    
    # 删除视图
    op.execute("DROP VIEW IF EXISTS visitor_details")
    op.execute("DROP VIEW IF EXISTS department_stats")
    op.execute("DROP VIEW IF EXISTS employee_visitor_stats")
    
    # 删除触发器
    trigger_tables = [
        'sites', 'departments', 'designations', 
        'employees', 'visitors', 'checkin_points'
    ]
    
    for table in trigger_tables:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    op.execute("DROP TRIGGER IF EXISTS auto_update_visitor_status_trigger ON visitors")
    
    # 删除触发器函数
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    op.execute("DROP FUNCTION IF EXISTS auto_update_visitor_status()")
    op.execute("DROP FUNCTION IF EXISTS validate_phone(TEXT)")
    op.execute("DROP FUNCTION IF EXISTS validate_id_card(TEXT)")
    
    # 删除索引
    indexes_to_drop = [
        'idx_sites_tenant_status', 'idx_sites_location',
        'idx_departments_tenant_site', 'idx_departments_parent', 'idx_departments_manager',
        'idx_designations_tenant_site', 'idx_designations_level',
        'idx_employees_tenant_dept', 'idx_employees_manager', 'idx_employees_status_active',
        'idx_employees_email_search', 'idx_employees_name_search',
        'idx_visitors_tenant_status', 'idx_visitors_employee_date', 'idx_visitors_phone_search',
        'idx_visitors_checkin_date', 'idx_visitors_name_search', 'idx_visitors_company_search',
        'idx_visitors_tenant_status_date', 'idx_visitors_pending', 'idx_visitors_employee_status',
        'idx_visitor_histories_visitor', 'idx_visitor_histories_tenant_time', 'idx_visitor_histories_action',
        'idx_approval_histories_visitor', 'idx_approval_histories_approver', 'idx_approval_histories_tenant_date',
        'idx_checkin_points_tenant_site', 'idx_checkin_points_active',
        'idx_companions_visitor'
    ]
    
    for index_name in indexes_to_drop:
        op.drop_index(index_name, if_exists=True)
    
    # 删除检查约束
    constraints_to_drop = [
        ('chk_sites_status', 'sites'),
        ('chk_sites_email', 'sites'),
        ('chk_departments_email', 'departments'),
        ('chk_departments_no_self_parent', 'departments'),
        ('chk_designations_level', 'designations'),
        ('chk_employees_status', 'employees'),
        ('chk_employees_email', 'employees'),
        ('chk_employees_gender', 'employees'),
        ('chk_employees_no_self_manager', 'employees'),
        ('chk_employees_salary', 'employees'),
        ('chk_visitors_checkout_after_checkin', 'visitors'),
        ('chk_visitors_email', 'visitors'),
        ('chk_visitors_gender', 'visitors'),
        ('chk_visitors_survey_score', 'visitors')
    ]
    
    for constraint_name, table_name in constraints_to_drop:
        op.drop_constraint(constraint_name, table_name, type_='check')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS visitor_status")
    op.execute("DROP TYPE IF EXISTS approval_action") 