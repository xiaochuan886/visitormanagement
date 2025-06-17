"""add_configuration_engine

Revision ID: 20250608_120000
Revises: 20250607_210000
Create Date: 2025-06-08 12:00:00.000000

添加通用化配置引擎数据库表结构：
- 表单配置引擎（form_configurations, form_field_configurations）
- 空间层级管理（spatial_configurations, spatial_entities）
- 工作流配置引擎（workflow_configurations, workflow_executions）
- 业务规则引擎（business_rules, rule_execution_logs）
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250608_120000'
down_revision = '20250607_210000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级：添加配置引擎数据库表结构"""
    
    # ===== 1. 表单配置引擎 =====
    
    # 表单配置主表
    op.create_table(
        'form_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('form_type', sa.String(50), nullable=False),
        sa.Column('form_name', sa.String(100), nullable=False),
        sa.Column('form_version', sa.Integer, default=1, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_default', sa.Boolean, default=False, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('form_schema', postgresql.JSONB),  # 完整表单结构
        sa.Column('ui_schema', postgresql.JSONB),    # UI渲染配置
        sa.Column('validation_schema', postgresql.JSONB),  # 验证规则
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100)),
        sa.Column('updated_by', sa.String(100)),
        
        # 约束
        sa.CheckConstraint("form_type IN ('visitor_registration', 'approval_form', 'employee_form', 'site_form', 'department_form')", name='chk_form_type'),
        sa.CheckConstraint("form_version >= 1", name='chk_form_version'),
        sa.UniqueConstraint('tenant_id', 'form_type', 'form_version', name='uq_form_config_version')
    )
    
    # 表单字段配置表（详细字段配置）
    op.create_table(
        'form_field_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('form_config_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('form_configurations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_key', sa.String(100), nullable=False),
        sa.Column('field_label', sa.String(200), nullable=False),
        sa.Column('field_type', sa.String(50), nullable=False),
        sa.Column('field_order', sa.Integer, nullable=False),
        sa.Column('is_required', sa.Boolean, default=False, nullable=False),
        sa.Column('is_readonly', sa.Boolean, default=False, nullable=False),
        sa.Column('is_visible', sa.Boolean, default=True, nullable=False),
        sa.Column('validation_rules', postgresql.JSONB),
        sa.Column('field_options', postgresql.JSONB),
        sa.Column('conditional_logic', postgresql.JSONB),
        sa.Column('default_value', sa.Text),
        sa.Column('placeholder_text', sa.String(200)),
        sa.Column('help_text', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # 约束
        sa.CheckConstraint("field_type IN ('text', 'textarea', 'select', 'multiselect', 'radio', 'checkbox', 'date', 'datetime', 'time', 'file', 'number', 'email', 'phone', 'url')", name='chk_field_type'),
        sa.CheckConstraint("field_order >= 0", name='chk_field_order'),
        sa.UniqueConstraint('form_config_id', 'field_key', name='uq_form_field_key')
    )
    
    # ===== 2. 空间层级管理 =====
    
    # 空间配置表
    op.create_table(
        'spatial_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('config_name', sa.String(100), nullable=False),
        sa.Column('spatial_levels', postgresql.JSONB, nullable=False),  # ["site", "building", "floor", "zone", "room"]
        sa.Column('level_settings', postgresql.JSONB, nullable=False),  # 各层级的设置
        sa.Column('access_control_settings', postgresql.JSONB),         # 访问控制配置
        sa.Column('device_integration_settings', postgresql.JSONB),     # 设备集成配置
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_default', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100)),
        sa.Column('updated_by', sa.String(100)),
        
        # 约束
        sa.UniqueConstraint('tenant_id', 'config_name', name='uq_spatial_config_name')
    )
    
    # 通用空间实体表
    op.create_table(
        'spatial_entities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('spatial_config_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_configurations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),  # site, building, floor, zone, room
        sa.Column('entity_level', sa.Integer, nullable=False),     # 0=site, 1=building, 2=floor, etc.
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_entities.id', ondelete='CASCADE')),
        sa.Column('entity_code', sa.String(100), nullable=False),
        sa.Column('entity_name', sa.String(200), nullable=False),
        sa.Column('display_order', sa.Integer, default=0, nullable=False),
        sa.Column('entity_attributes', postgresql.JSONB),         # 自定义属性
        sa.Column('access_control_rules', postgresql.JSONB),      # 访问控制规则
        sa.Column('device_integrations', postgresql.JSONB),       # 设备集成配置
        sa.Column('location_data', postgresql.JSONB),             # 位置信息（经纬度、楼层图等）
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100)),
        sa.Column('updated_by', sa.String(100)),
        
        # 约束
        sa.CheckConstraint("entity_type IN ('site', 'building', 'floor', 'zone', 'room', 'area', 'workstation')", name='chk_entity_type'),
        sa.CheckConstraint("entity_level >= 0 AND entity_level <= 10", name='chk_entity_level'),
        sa.CheckConstraint("display_order >= 0", name='chk_display_order'),
        sa.UniqueConstraint('tenant_id', 'spatial_config_id', 'entity_code', name='uq_spatial_entity_code')
    )
    
    # ===== 3. 工作流配置引擎 =====
    
    # 工作流配置表
    op.create_table(
        'workflow_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('workflow_name', sa.String(100), nullable=False),
        sa.Column('workflow_type', sa.String(50), nullable=False),
        sa.Column('workflow_version', sa.Integer, default=1, nullable=False),
        sa.Column('trigger_conditions', postgresql.JSONB, nullable=False),  # 触发条件
        sa.Column('workflow_steps', postgresql.JSONB, nullable=False),      # 工作流步骤定义
        sa.Column('failure_handling', postgresql.JSONB),                    # 失败处理策略
        sa.Column('timeout_settings', postgresql.JSONB),                    # 超时设置
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('priority_level', sa.Integer, default=1, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100)),
        sa.Column('updated_by', sa.String(100)),
        
        # 约束
        sa.CheckConstraint("workflow_type IN ('visitor_approval', 'device_control', 'notification', 'data_sync', 'security_check')", name='chk_workflow_type'),
        sa.CheckConstraint("workflow_version >= 1", name='chk_workflow_version'),
        sa.CheckConstraint("priority_level >= 1 AND priority_level <= 10", name='chk_priority_level'),
        sa.UniqueConstraint('tenant_id', 'workflow_name', 'workflow_version', name='uq_workflow_version')
    )
    
    # 工作流执行历史表
    op.create_table(
        'workflow_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('workflow_config_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workflow_configurations.id'), nullable=False),
        sa.Column('target_entity_type', sa.String(50), nullable=False),    # visitor, employee, etc.
        sa.Column('target_entity_id', sa.String(100), nullable=False),
        sa.Column('execution_status', sa.String(50), nullable=False),      # pending, running, completed, failed, cancelled
        sa.Column('current_step', sa.Integer, default=0, nullable=False),
        sa.Column('execution_data', postgresql.JSONB),                     # 执行过程数据
        sa.Column('step_results', postgresql.JSONB),                       # 各步骤执行结果
        sa.Column('context_data', postgresql.JSONB),                       # 上下文数据
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('last_executed_at', sa.DateTime(timezone=True)),
        sa.Column('error_details', sa.Text),
        sa.Column('retry_count', sa.Integer, default=0, nullable=False),
        
        # 约束
        sa.CheckConstraint("execution_status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')", name='chk_execution_status'),
        sa.CheckConstraint("current_step >= 0", name='chk_current_step'),
        sa.CheckConstraint("retry_count >= 0", name='chk_retry_count')
    )
    
    # ===== 4. 业务规则引擎 =====
    
    # 业务规则配置表
    op.create_table(
        'business_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('rule_name', sa.String(100), nullable=False),
        sa.Column('rule_category', sa.String(50), nullable=False),
        sa.Column('rule_version', sa.Integer, default=1, nullable=False),
        sa.Column('rule_conditions', postgresql.JSONB, nullable=False),    # 规则条件
        sa.Column('rule_actions', postgresql.JSONB, nullable=False),       # 规则动作
        sa.Column('rule_priority', sa.Integer, default=1, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('effective_from', sa.DateTime(timezone=True)),
        sa.Column('effective_until', sa.DateTime(timezone=True)),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100)),
        sa.Column('updated_by', sa.String(100)),
        
        # 约束
        sa.CheckConstraint("rule_category IN ('validation', 'automation', 'security', 'notification', 'access_control', 'data_processing')", name='chk_rule_category'),
        sa.CheckConstraint("rule_version >= 1", name='chk_rule_version'),
        sa.CheckConstraint("rule_priority >= 1 AND rule_priority <= 100", name='chk_rule_priority'),
        sa.CheckConstraint("effective_until IS NULL OR effective_until > effective_from", name='chk_rule_effective_dates'),
        sa.UniqueConstraint('tenant_id', 'rule_name', 'rule_version', name='uq_rule_version')
    )
    
    # 规则执行日志表
    op.create_table(
        'rule_execution_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('business_rules.id'), nullable=False),
        sa.Column('target_entity_type', sa.String(50), nullable=False),
        sa.Column('target_entity_id', sa.String(100), nullable=False),
        sa.Column('execution_result', sa.String(50), nullable=False),      # success, failed, skipped, error
        sa.Column('execution_details', postgresql.JSONB),
        sa.Column('input_data', postgresql.JSONB),                        # 输入数据
        sa.Column('output_data', postgresql.JSONB),                       # 输出数据
        sa.Column('execution_time_ms', sa.Integer),                       # 执行时间（毫秒）
        sa.Column('error_message', sa.Text),
        sa.Column('execution_time', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # 约束
        sa.CheckConstraint("execution_result IN ('success', 'failed', 'skipped', 'error', 'timeout')", name='chk_execution_result'),
        sa.CheckConstraint("execution_time_ms IS NULL OR execution_time_ms >= 0", name='chk_execution_time_ms')
    )
    
    # ===== 5. 创建性能优化索引 =====
    
    # 表单配置索引
    op.create_index('idx_form_configs_tenant_type', 'form_configurations', ['tenant_id', 'form_type'])
    op.create_index('idx_form_configs_active', 'form_configurations', ['is_active'], postgresql_where=sa.text('is_active = TRUE'))
    op.create_index('idx_form_configs_default', 'form_configurations', ['tenant_id', 'form_type', 'is_default'], postgresql_where=sa.text('is_default = TRUE'))
    
    op.create_index('idx_form_fields_config', 'form_field_configurations', ['form_config_id', 'field_order'])
    op.create_index('idx_form_fields_visible', 'form_field_configurations', ['form_config_id'], postgresql_where=sa.text('is_visible = TRUE'))
    
    # 空间配置索引
    op.create_index('idx_spatial_configs_tenant', 'spatial_configurations', ['tenant_id'])
    op.create_index('idx_spatial_configs_active', 'spatial_configurations', ['is_active'], postgresql_where=sa.text('is_active = TRUE'))
    
    op.create_index('idx_spatial_entities_tenant_config', 'spatial_entities', ['tenant_id', 'spatial_config_id'])
    op.create_index('idx_spatial_entities_parent', 'spatial_entities', ['parent_id'], postgresql_where=sa.text('parent_id IS NOT NULL'))
    op.create_index('idx_spatial_entities_level_order', 'spatial_entities', ['entity_level', 'display_order'])
    op.create_index('idx_spatial_entities_type_active', 'spatial_entities', ['entity_type'], postgresql_where=sa.text('is_active = TRUE'))
    
    # 工作流配置索引
    op.create_index('idx_workflow_configs_tenant_type', 'workflow_configurations', ['tenant_id', 'workflow_type'])
    op.create_index('idx_workflow_configs_active', 'workflow_configurations', ['is_active'], postgresql_where=sa.text('is_active = TRUE'))
    
    op.create_index('idx_workflow_executions_tenant_status', 'workflow_executions', ['tenant_id', 'execution_status'])
    op.create_index('idx_workflow_executions_config', 'workflow_executions', ['workflow_config_id', 'started_at'])
    op.create_index('idx_workflow_executions_entity', 'workflow_executions', ['target_entity_type', 'target_entity_id'])
    op.create_index('idx_workflow_executions_pending', 'workflow_executions', ['started_at'], postgresql_where=sa.text("execution_status IN ('pending', 'running')"))
    
    # 业务规则索引
    op.create_index('idx_business_rules_tenant_category', 'business_rules', ['tenant_id', 'rule_category'])
    op.create_index('idx_business_rules_active', 'business_rules', ['is_active', 'rule_priority'], postgresql_where=sa.text('is_active = TRUE'))
    op.create_index('idx_business_rules_effective', 'business_rules', ['effective_from', 'effective_until'], postgresql_where=sa.text('is_active = TRUE'))
    
    op.create_index('idx_rule_logs_tenant_time', 'rule_execution_logs', ['tenant_id', sa.text('execution_time DESC')])
    op.create_index('idx_rule_logs_rule', 'rule_execution_logs', ['rule_id', 'execution_time'])
    op.create_index('idx_rule_logs_entity', 'rule_execution_logs', ['target_entity_type', 'target_entity_id'])
    op.create_index('idx_rule_logs_result', 'rule_execution_logs', ['execution_result'])
    
    # ===== 6. 创建触发器函数 =====
    
    # 更新时间戳触发器（如果不存在）
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # 为配置表添加更新时间戳触发器
    for table_name in ['form_configurations', 'spatial_configurations', 
                       'spatial_entities', 'workflow_configurations', 'business_rules']:
        op.execute(f"""
            CREATE TRIGGER trigger_update_{table_name}_updated_at
                BEFORE UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """)
    
    # 配置版本管理触发器
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_config_version()
        RETURNS TRIGGER AS $$
        BEGIN
            -- 确保同一租户下同一类型只有一个默认配置
            IF NEW.is_default = TRUE THEN
                UPDATE form_configurations 
                SET is_default = FALSE 
                WHERE tenant_id = NEW.tenant_id 
                AND form_type = NEW.form_type 
                AND id != NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_validate_form_config_default
            BEFORE INSERT OR UPDATE ON form_configurations
            FOR EACH ROW
            EXECUTE FUNCTION validate_config_version();
    """)
    
    # ===== 7. 添加表注释 =====
    op.execute("COMMENT ON TABLE form_configurations IS '表单配置主表 - 存储各种表单的配置信息'")
    op.execute("COMMENT ON TABLE form_field_configurations IS '表单字段配置表 - 存储表单字段的详细配置'")
    op.execute("COMMENT ON TABLE spatial_configurations IS '空间配置表 - 定义空间层级结构配置'")
    op.execute("COMMENT ON TABLE spatial_entities IS '空间实体表 - 存储具体的空间实体（站点、楼栋、楼层等）'")
    op.execute("COMMENT ON TABLE workflow_configurations IS '工作流配置表 - 定义各种业务流程'")
    op.execute("COMMENT ON TABLE workflow_executions IS '工作流执行记录表 - 记录工作流的执行过程和结果'")
    op.execute("COMMENT ON TABLE business_rules IS '业务规则配置表 - 定义各种业务规则'")
    op.execute("COMMENT ON TABLE rule_execution_logs IS '规则执行日志表 - 记录业务规则的执行过程'")
    
    print("✅ 配置引擎数据库表结构创建完成")


def downgrade() -> None:
    """降级：删除配置引擎数据库表结构"""
    
    # 删除触发器
    for table_name in ['form_configurations', 'spatial_configurations', 
                       'spatial_entities', 'workflow_configurations', 'business_rules']:
        op.execute(f"DROP TRIGGER IF EXISTS trigger_update_{table_name}_updated_at ON {table_name}")
    
    op.execute("DROP TRIGGER IF EXISTS trigger_validate_form_config_default ON form_configurations")
    
    # 删除触发器函数
    op.execute("DROP FUNCTION IF EXISTS validate_config_version()")
    
    # 删除索引（会随表自动删除，这里列出便于参考）
    # 业务规则相关表
    op.drop_table('rule_execution_logs')
    op.drop_table('business_rules')
    
    # 工作流相关表
    op.drop_table('workflow_executions')
    op.drop_table('workflow_configurations')
    
    # 空间管理相关表
    op.drop_table('spatial_entities')
    op.drop_table('spatial_configurations')
    
    # 表单配置相关表
    op.drop_table('form_field_configurations')
    op.drop_table('form_configurations')
    
    print("✅ 配置引擎数据库表结构删除完成")