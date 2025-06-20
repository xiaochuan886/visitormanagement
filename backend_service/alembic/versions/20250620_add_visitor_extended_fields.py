"""添加访客表扩展字段支持门岗前台功能

Revision ID: 20250620_add_visitor_extended_fields
Revises: 20250608_120000_add_configuration_engine
Create Date: 2025-06-20 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250620_000000'
down_revision = '20250608_120000'
branch_labels = None
depends_on = None


def upgrade():
    """添加访客表扩展字段"""
    
    # 添加门岗前台扩展字段到visitors表
    op.add_column('visitors', sa.Column('current_status', sa.String(length=50), nullable=True, 
                                       comment='当前状态: pending, approved, checked_in, in_park, exited'))
    
    op.add_column('visitors', sa.Column('entry_time', sa.DateTime(timezone=True), nullable=True,
                                       comment='实际入园时间'))
    
    op.add_column('visitors', sa.Column('exit_time', sa.DateTime(timezone=True), nullable=True,
                                       comment='实际离园时间'))
    
    op.add_column('visitors', sa.Column('current_location', sa.String(length=200), nullable=True,
                                       comment='当前位置'))
    
    op.add_column('visitors', sa.Column('reception_desk_id', sa.String(length=50), nullable=True,
                                       comment='签到的前台设备ID'))
    
    # 添加时间顺序约束
    op.create_check_constraint(
        'chk_visitors_park_time_order',
        'visitors',
        'exit_time IS NULL OR entry_time IS NULL OR exit_time > entry_time'
    )


def downgrade():
    """移除访客表扩展字段"""
    
    # 删除约束
    op.drop_constraint('chk_visitors_park_time_order', 'visitors', type_='check')
    
    # 删除扩展字段
    op.drop_column('visitors', 'reception_desk_id')
    op.drop_column('visitors', 'current_location')  
    op.drop_column('visitors', 'exit_time')
    op.drop_column('visitors', 'entry_time')
    op.drop_column('visitors', 'current_status') 