"""finalize_visitor_status_enum

Revision ID: 20250607_210000
Revises: 20250607_203857
Create Date: 2025-06-07 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250607_210000'
down_revision = '20250607_203857'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级：将visitors.status字段从VARCHAR迁移到visitor_status枚举类型"""
    
    # 执行数据一致性检查
    op.execute("""
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
    """)
    
    # 添加临时枚举字段
    op.add_column('visitors', sa.Column('status_enum', postgresql.ENUM('pending', 'approved', 'rejected', 'checked_in', 'checked_out', 'cancelled', 'expired', name='visitor_status'), nullable=True))
    
    # 数据迁移
    op.execute("""
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
    """)
    
    # 验证迁移结果
    op.execute("""
        DO $$
        DECLARE
            varchar_count INTEGER;
            enum_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO varchar_count FROM visitors WHERE status IS NOT NULL;
            SELECT COUNT(*) INTO enum_count FROM visitors WHERE status_enum IS NOT NULL;
            
            IF enum_count != varchar_count THEN
                RAISE EXCEPTION '迁移失败：VARCHAR记录 %，枚举记录 %', varchar_count, enum_count;
            END IF;
            
            RAISE NOTICE '✅ 数据迁移验证通过：% 条记录成功迁移', enum_count;
        END $$;
    """)
    
    # 删除依赖的视图
    op.execute("DROP VIEW IF EXISTS visitor_details CASCADE")
    op.execute("DROP VIEW IF EXISTS department_stats CASCADE")
    op.execute("DROP VIEW IF EXISTS employee_visitor_stats CASCADE")
    
    # 删除旧字段相关的索引
    op.drop_index('idx_visitors_tenant_status', table_name='visitors')
    op.drop_index('idx_visitors_tenant_status_date', table_name='visitors')
    op.drop_index('idx_visitors_employee_status', table_name='visitors')
    op.drop_index('idx_visitors_pending', table_name='visitors')
    
    # 删除旧字段
    op.drop_column('visitors', 'status')
    
    # 重命名新字段
    op.alter_column('visitors', 'status_enum', new_column_name='status')
    
    # 重建优化索引
    op.create_index('idx_visitors_tenant_status', 'visitors', ['tenant_id', 'status'])
    op.create_index('idx_visitors_tenant_status_date', 'visitors', ['tenant_id', 'status', 'expected_date'])
    op.create_index('idx_visitors_employee_status', 'visitors', ['employee_id', 'status'])
    op.create_index('idx_visitors_pending', 'visitors', ['tenant_id', 'created_at'], postgresql_where=sa.text("status = 'pending'"))
    
    # 更新表注释
    op.execute("COMMENT ON COLUMN visitors.status IS '访客状态 - 使用visitor_status枚举类型确保数据一致性'")
    
    # 重建原有视图（使用枚举类型）
    op.execute("""
        CREATE VIEW visitor_details AS
        SELECT v.pass_code,
            v.name,
            v.email,
            v.phone_number,
            v.identification_no,
            v.license_plate_number,
            v.address,
            v.gender,
            v.company_name,
            v.purpose,
            v.comment,
            v.designation_id,
            v.employee_id,
            v.checkin_date,
            v.checkout_date,
            v.expected_date,
            v.expected_time,
            v.avatar,
            v.trip_code,
            v.health_code,
            v.qr_code,
            v.nucleic_acid_test_report,
            v.privacy_policy,
            v.promise,
            v.status,
            v.approved,
            v.approval_outcome,
            v.approval_comment,
            v.site_id,
            v.survey_response_value,
            v.tenant_id,
            v.created_by,
            v.updated_by,
            v.is_deleted,
            v.deleted_at,
            v.deleted_by,
            v.id,
            v.created_at,
            v.updated_at,
            e.name AS host_employee_name,
            e.email AS host_employee_email,
            e.phone_number AS host_employee_phone,
            e."position" AS host_employee_position,
            d.name AS department_name,
            s.name AS site_name,
            s.address AS site_address,
            des.name AS designation_name,
            des.level AS designation_level
        FROM ((((visitors v
            LEFT JOIN employees e ON ((v.employee_id = e.id)))
            LEFT JOIN departments d ON ((e.department_id = d.id)))
            LEFT JOIN sites s ON ((v.site_id = s.id)))
            LEFT JOIN designations des ON ((v.designation_id = des.id)));
    """)
    
    op.execute("""
        CREATE VIEW department_stats AS
        SELECT d.id,
            d.name,
            d.tenant_id,
            s.name AS site_name,
            count(DISTINCT e.id) FILTER (WHERE ((e.status)::text = 'active'::text)) AS active_employee_count,
            count(DISTINCT v.id) FILTER (WHERE (date(v.created_at) = CURRENT_DATE)) AS visitor_count_today,
            count(DISTINCT v.id) FILTER (WHERE (v.status = 'pending'::visitor_status)) AS pending_visitor_count
        FROM (((departments d
            LEFT JOIN sites s ON ((d.site_id = s.id)))
            LEFT JOIN employees e ON ((d.id = e.department_id)))
            LEFT JOIN visitors v ON ((e.id = v.employee_id)))
        GROUP BY d.id, d.name, d.tenant_id, s.name;
    """)
    
    op.execute("""
        CREATE VIEW employee_visitor_stats AS
        SELECT e.id,
            e.name,
            e.employee_id,
            e.tenant_id,
            d.name AS department_name,
            count(v.id) AS total_visitors,
            count(v.id) FILTER (WHERE (v.status = 'pending'::visitor_status)) AS pending_visitors,
            count(v.id) FILTER (WHERE (v.status = 'approved'::visitor_status)) AS approved_visitors,
            count(v.id) FILTER (WHERE (date(v.created_at) = CURRENT_DATE)) AS today_visitors
        FROM ((employees e
            LEFT JOIN departments d ON ((e.department_id = d.id)))
            LEFT JOIN visitors v ON ((e.id = v.employee_id)))
        WHERE ((e.status)::text = 'active'::text)
        GROUP BY e.id, e.name, e.employee_id, e.tenant_id, d.name;
    """)
    
    # 创建状态统计视图
    op.execute("""
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
    """)
    
    op.execute("COMMENT ON VIEW visitor_status_stats IS '访客状态统计视图 - 提供各状态的实时统计数据'")


def downgrade() -> None:
    """降级：将visitors.status字段从枚举类型恢复到VARCHAR"""
    
    # 删除状态统计视图
    op.execute("DROP VIEW IF EXISTS visitor_status_stats")
    
    # 删除枚举相关索引
    op.drop_index('idx_visitors_pending', table_name='visitors')
    op.drop_index('idx_visitors_employee_status', table_name='visitors')
    op.drop_index('idx_visitors_tenant_status_date', table_name='visitors')
    op.drop_index('idx_visitors_tenant_status', table_name='visitors')
    
    # 添加临时VARCHAR字段
    op.add_column('visitors', sa.Column('status_varchar', sa.VARCHAR(length=20), nullable=True))
    
    # 数据迁移回VARCHAR
    op.execute("""
        UPDATE visitors 
        SET status_varchar = status::text
        WHERE status IS NOT NULL;
    """)
    
    # 删除枚举字段
    op.drop_column('visitors', 'status')
    
    # 重命名VARCHAR字段
    op.alter_column('visitors', 'status_varchar', new_column_name='status')
    
    # 重建原始索引
    op.create_index('idx_visitors_tenant_status', 'visitors', ['tenant_id', 'status'])
    op.create_index('idx_visitors_tenant_status_date', 'visitors', ['tenant_id', 'status', 'expected_date'])
    op.create_index('idx_visitors_employee_status', 'visitors', ['employee_id', 'status'])
    op.create_index('idx_visitors_pending', 'visitors', ['tenant_id', 'created_at'], postgresql_where=sa.text("status = 'pending'"))
    
    # 恢复原始注释
    op.execute("COMMENT ON COLUMN visitors.status IS '访客状态'") 