"""
门岗和前台功能数据库迁移脚本
Migration Version: 003
Created: 2024-12-19

新增表：
- devices: 设备管理
- device_status_logs: 设备状态日志
- visitor_verifications: 访客验证记录
- visitor_entries: 访客入园记录
- reception_checkins: 前台签到记录
- host_notifications: 主机通知记录
- meeting_rooms: 会议室管理
- meeting_room_bookings: 会议室预订记录
- offline_verifications: 离线验证记录
- security_alerts: 安全告警记录
- emergency_operations: 应急操作记录
- mobile_sync_records: 移动端同步记录

修改表：
- visitors: 添加门岗和前台相关字段
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """执行迁移升级"""
    
    # 1. 创建新的枚举类型
    device_type_enum = postgresql.ENUM(
        'gate_terminal', 'reception_kiosk', 'mobile_tablet', 'access_control',
        'camera_system', 'printer', 'id_scanner', 'face_recognition', 'qr_scanner',
        name='device_type'
    )
    device_type_enum.create(op.get_bind())
    
    device_status_enum = postgresql.ENUM(
        'online', 'offline', 'maintenance', 'error', 'disabled',
        name='device_status'
    )
    device_status_enum.create(op.get_bind())
    
    verification_method_enum = postgresql.ENUM(
        'qr_code', 'id_card', 'face_recognition', 'manual', 'phone_otp',
        name='verification_method'
    )
    verification_method_enum.create(op.get_bind())
    
    verification_status_enum = postgresql.ENUM(
        'success', 'failed', 'pending', 'blacklist', 'expired',
        name='verification_status'
    )
    verification_status_enum.create(op.get_bind())
    
    checkin_method_enum = postgresql.ENUM(
        'qr_code', 'manual', 'face_recognition', 'id_card', 'self_service',
        name='checkin_method'
    )
    checkin_method_enum.create(op.get_bind())
    
    notification_channel_enum = postgresql.ENUM(
        'wechat', 'email', 'sms', 'phone_call', 'system_notification',
        name='notification_channel'
    )
    notification_channel_enum.create(op.get_bind())
    
    # 2. 创建devices表
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('device_id', sa.String(length=50), nullable=False),
        sa.Column('device_name', sa.String(length=100), nullable=False),
        sa.Column('device_type', device_type_enum, nullable=False),
        sa.Column('device_model', sa.String(length=100), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('site_id', sa.Integer(), nullable=True),
        sa.Column('zone', sa.String(length=100), nullable=True),
        sa.Column('floor', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('mac_address', sa.String(length=17), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('status', device_status_enum, nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_maintenance', sa.DateTime(timezone=True), nullable=True),
        sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('firmware_version', sa.String(length=50), nullable=True),
        sa.Column('software_version', sa.String(length=50), nullable=True),
        sa.Column('admin_user', sa.String(length=100), nullable=True),
        sa.Column('installation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('warranty_expire', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.CheckConstraint('port IS NULL OR (port >= 1 AND port <= 65535)', name='chk_devices_port'),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id')
    )
    op.create_index(op.f('ix_devices_tenant_id'), 'devices', ['tenant_id'], unique=False)
    
    # 3. 创建device_status_logs表
    op.create_table(
        'device_status_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('device_id', sa.String(length=50), nullable=False),
        sa.Column('status_before', device_status_enum, nullable=True),
        sa.Column('status_after', device_status_enum, nullable=False),
        sa.Column('cpu_usage', sa.Float(), nullable=True),
        sa.Column('memory_usage', sa.Float(), nullable=True),
        sa.Column('disk_usage', sa.Float(), nullable=True),
        sa.Column('network_latency', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('change_reason', sa.String(length=200), nullable=True),
        sa.Column('operator', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('status_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint('cpu_usage IS NULL OR (cpu_usage >= 0 AND cpu_usage <= 100)', name='chk_cpu_usage'),
        sa.CheckConstraint('memory_usage IS NULL OR (memory_usage >= 0 AND memory_usage <= 100)', name='chk_memory_usage'),
        sa.CheckConstraint('disk_usage IS NULL OR (disk_usage >= 0 AND disk_usage <= 100)', name='chk_disk_usage'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_device_status_logs_tenant_id'), 'device_status_logs', ['tenant_id'], unique=False)
    
    # 4. 创建visitor_verifications表
    op.create_table(
        'visitor_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('verification_id', sa.String(length=100), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=50), nullable=False),
        sa.Column('verification_method', verification_method_enum, nullable=False),
        sa.Column('verification_status', verification_status_enum, nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('verification_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('blacklist_check', sa.Boolean(), nullable=True),
        sa.Column('time_window_valid', sa.Boolean(), nullable=True),
        sa.Column('area_permission_valid', sa.Boolean(), nullable=True),
        sa.Column('access_granted', sa.Boolean(), nullable=True),
        sa.Column('access_areas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('operator', sa.String(length=100), nullable=True),
        sa.Column('verification_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 100', name='chk_confidence_score'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('verification_id')
    )
    op.create_index(op.f('ix_visitor_verifications_tenant_id'), 'visitor_verifications', ['tenant_id'], unique=False)
    
    # 5. 创建visitor_entries表
    op.create_table(
        'visitor_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('entry_id', sa.String(length=100), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('gate_id', sa.String(length=50), nullable=False),
        sa.Column('entry_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('exit_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('entry_photo_url', sa.String(length=500), nullable=True),
        sa.Column('exit_photo_url', sa.String(length=500), nullable=True),
        sa.Column('badge_number', sa.String(length=50), nullable=True),
        sa.Column('badge_type', sa.String(length=50), nullable=True),
        sa.Column('badge_issued', sa.Boolean(), nullable=True),
        sa.Column('badge_returned', sa.Boolean(), nullable=True),
        sa.Column('vehicle_plate', sa.String(length=20), nullable=True),
        sa.Column('vehicle_type', sa.String(length=50), nullable=True),
        sa.Column('parking_spot', sa.String(length=50), nullable=True),
        sa.Column('vehicle_photo_url', sa.String(length=500), nullable=True),
        sa.Column('access_areas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('access_valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('escort_required', sa.Boolean(), nullable=True),
        sa.Column('temperature_check', sa.Float(), nullable=True),
        sa.Column('health_code_status', sa.String(length=20), nullable=True),
        sa.Column('health_check_passed', sa.Boolean(), nullable=True),
        sa.Column('operator', sa.String(length=100), nullable=True),
        sa.Column('entry_status', sa.String(length=50), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['gate_id'], ['devices.device_id'], ),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('entry_id')
    )
    op.create_index(op.f('ix_visitor_entries_tenant_id'), 'visitor_entries', ['tenant_id'], unique=False)
    
    # 6. 创建reception_checkins表
    op.create_table(
        'reception_checkins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('checkin_id', sa.String(length=100), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('reception_desk_id', sa.String(length=50), nullable=False),
        sa.Column('checkin_method', checkin_method_enum, nullable=False),
        sa.Column('checkin_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('checkin_status', sa.String(length=50), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('waiting_area_id', sa.String(length=100), nullable=True),
        sa.Column('queue_number', sa.Integer(), nullable=True),
        sa.Column('estimated_wait_time', sa.Integer(), nullable=True),
        sa.Column('actual_wait_time', sa.Integer(), nullable=True),
        sa.Column('called_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('receptionist', sa.String(length=100), nullable=True),
        sa.Column('services_provided', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('visitor_satisfaction', sa.Integer(), nullable=True),
        sa.Column('service_notes', sa.Text(), nullable=True),
        sa.Column('operator', sa.String(length=100), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.CheckConstraint('queue_number IS NULL OR queue_number > 0', name='chk_queue_number'),
        sa.CheckConstraint('estimated_wait_time IS NULL OR estimated_wait_time >= 0', name='chk_estimated_wait'),
        sa.CheckConstraint('visitor_satisfaction IS NULL OR (visitor_satisfaction >= 1 AND visitor_satisfaction <= 5)', name='chk_satisfaction'),
        sa.ForeignKeyConstraint(['reception_desk_id'], ['devices.device_id'], ),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('checkin_id')
    )
    op.create_index(op.f('ix_reception_checkins_tenant_id'), 'reception_checkins', ['tenant_id'], unique=False)
    
    # 7. 创建host_notifications表
    op.create_table(
        'host_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('notification_id', sa.String(length=100), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('notification_channels', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notification_content', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('delivery_status', sa.String(length=50), nullable=True),
        sa.Column('delivery_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('read_status', sa.String(length=50), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_action', sa.String(length=50), nullable=True),
        sa.Column('response_message', sa.Text(), nullable=True),
        sa.Column('response_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_arrival_minutes', sa.Integer(), nullable=True),
        sa.Column('timeout_minutes', sa.Integer(), nullable=True),
        sa.Column('auto_processed', sa.Boolean(), nullable=True),
        sa.Column('auto_process_action', sa.String(length=50), nullable=True),
        sa.CheckConstraint('estimated_arrival_minutes IS NULL OR estimated_arrival_minutes > 0', name='chk_arrival_minutes'),
        sa.CheckConstraint('timeout_minutes > 0', name='chk_timeout_minutes'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('notification_id')
    )
    op.create_index(op.f('ix_host_notifications_tenant_id'), 'host_notifications', ['tenant_id'], unique=False)
    
    # 8. 创建meeting_rooms表
    op.create_table(
        'meeting_rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('room_name', sa.String(length=100), nullable=False),
        sa.Column('room_code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('site_id', sa.Integer(), nullable=True),
        sa.Column('floor', sa.String(length=50), nullable=True),
        sa.Column('building', sa.String(length=100), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('area_sqm', sa.Float(), nullable=True),
        sa.Column('amenities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('av_equipment', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('furniture', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('booking_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('advance_booking_days', sa.Integer(), nullable=True),
        sa.Column('max_booking_hours', sa.Integer(), nullable=True),
        sa.Column('min_booking_minutes', sa.Integer(), nullable=True),
        sa.Column('room_status', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('room_manager', sa.String(length=100), nullable=True),
        sa.Column('hourly_rate', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.CheckConstraint('capacity > 0', name='chk_room_capacity'),
        sa.CheckConstraint('area_sqm IS NULL OR area_sqm > 0', name='chk_room_area'),
        sa.CheckConstraint('advance_booking_days > 0', name='chk_advance_booking'),
        sa.CheckConstraint('hourly_rate IS NULL OR hourly_rate >= 0', name='chk_hourly_rate'),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_code')
    )
    op.create_index(op.f('ix_meeting_rooms_tenant_id'), 'meeting_rooms', ['tenant_id'], unique=False)
    
    # 9. 创建meeting_room_bookings表
    op.create_table(
        'meeting_room_bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('booking_id', sa.String(length=100), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=True),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('meeting_title', sa.String(length=200), nullable=True),
        sa.Column('meeting_purpose', sa.Text(), nullable=True),
        sa.Column('attendee_count', sa.Integer(), nullable=True),
        sa.Column('attendees', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('booking_status', sa.String(length=50), nullable=True),
        sa.Column('booking_source', sa.String(length=50), nullable=True),
        sa.Column('equipment_needs', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('catering_request', sa.Text(), nullable=True),
        sa.Column('special_requirements', sa.Text(), nullable=True),
        sa.Column('booking_fee', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('payment_status', sa.String(length=50), nullable=True),
        sa.Column('booked_by', sa.String(length=100), nullable=True),
        sa.Column('booking_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_by', sa.String(length=100), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.CheckConstraint('end_time > start_time', name='chk_booking_time_order'),
        sa.CheckConstraint('duration_minutes > 0', name='chk_booking_duration'),
        sa.CheckConstraint('attendee_count IS NULL OR attendee_count > 0', name='chk_attendee_count'),
        sa.CheckConstraint('booking_fee IS NULL OR booking_fee >= 0', name='chk_booking_fee'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['meeting_rooms.id'], ),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_id')
    )
    op.create_index(op.f('ix_meeting_room_bookings_tenant_id'), 'meeting_room_bookings', ['tenant_id'], unique=False)
    
    # 10. 创建offline_verifications表
    op.create_table(
        'offline_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('offline_id', sa.String(length=100), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=50), nullable=False),
        sa.Column('verification_method', verification_method_enum, nullable=False),
        sa.Column('verification_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('offline_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('device_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('sync_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_attempts', sa.Integer(), nullable=True),
        sa.Column('sync_error', sa.Text(), nullable=True),
        sa.Column('verification_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('access_granted', sa.Boolean(), nullable=True),
        sa.Column('operator', sa.String(length=100), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.CheckConstraint('sync_attempts >= 0', name='chk_sync_attempts'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ),
        sa.ForeignKeyConstraint(['visitor_id'], ['visitors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('offline_id')
    )
    op.create_index(op.f('ix_offline_verifications_tenant_id'), 'offline_verifications', ['tenant_id'], unique=False)
    
    # 11. 创建security_alerts表
    op.create_table(
        'security_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('alert_id', sa.String(length=100), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('alert_level', sa.String(length=20), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('device_id', sa.String(length=50), nullable=True),
        sa.Column('alert_title', sa.String(length=200), nullable=False),
        sa.Column('alert_message', sa.Text(), nullable=True),
        sa.Column('alert_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('acknowledged_by', sa.String(length=100), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(length=100), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('auto_response_enabled', sa.Boolean(), nullable=True),
        sa.Column('auto_response_executed', sa.Boolean(), nullable=True),
        sa.Column('auto_response_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=True),
        sa.Column('notification_channels', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('escalation_level', sa.Integer(), nullable=True),
        sa.Column('alert_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alert_id')
    )
    op.create_index(op.f('ix_security_alerts_tenant_id'), 'security_alerts', ['tenant_id'], unique=False)
    
    # 12. 创建emergency_operations表
    op.create_table(
        'emergency_operations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('emergency_id', sa.String(length=100), nullable=False),
        sa.Column('emergency_type', sa.String(length=50), nullable=False),
        sa.Column('emergency_reason', sa.Text(), nullable=False),
        sa.Column('emergency_description', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('affected_areas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('affected_devices', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('gate_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('operation_type', sa.String(length=50), nullable=False),
        sa.Column('operation_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('auto_recovery_minutes', sa.Integer(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('operator', sa.String(length=100), nullable=False),
        sa.Column('authorization_level', sa.String(length=50), nullable=True),
        sa.Column('approver', sa.String(length=100), nullable=True),
        sa.Column('approval_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_status', sa.String(length=50), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('recovery_executed', sa.Boolean(), nullable=True),
        sa.Column('recovery_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('incident_report', sa.Text(), nullable=True),
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        sa.Column('follow_up_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint('auto_recovery_minutes >= 0', name='chk_auto_recovery'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('emergency_id')
    )
    op.create_index(op.f('ix_emergency_operations_tenant_id'), 'emergency_operations', ['tenant_id'], unique=False)
    
    # 13. 创建mobile_sync_records表
    op.create_table(
        'mobile_sync_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('sync_id', sa.String(length=100), nullable=False),
        sa.Column('device_id', sa.String(length=50), nullable=False),
        sa.Column('sync_type', sa.String(length=50), nullable=False),
        sa.Column('sync_direction', sa.String(length=20), nullable=True),
        sa.Column('sync_start_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('sync_end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_sync_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_date_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_date_to', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('successful_records', sa.Integer(), nullable=True),
        sa.Column('failed_records', sa.Integer(), nullable=True),
        sa.Column('data_size_kb', sa.Float(), nullable=True),
        sa.Column('compression_ratio', sa.Float(), nullable=True),
        sa.Column('transfer_time_seconds', sa.Float(), nullable=True),
        sa.Column('network_quality', sa.String(length=20), nullable=True),
        sa.Column('download_speed_kbps', sa.Float(), nullable=True),
        sa.Column('upload_speed_kbps', sa.Float(), nullable=True),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sync_conflicts', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint('total_records >= 0', name='chk_total_records'),
        sa.CheckConstraint('successful_records >= 0', name='chk_successful_records'),
        sa.CheckConstraint('failed_records >= 0', name='chk_failed_records'),
        sa.CheckConstraint('successful_records + failed_records <= total_records', name='chk_records_sum'),
        sa.CheckConstraint('data_size_kb >= 0', name='chk_data_size'),
        sa.CheckConstraint('compression_ratio > 0', name='chk_compression_ratio'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sync_id')
    )
    op.create_index(op.f('ix_mobile_sync_records_tenant_id'), 'mobile_sync_records', ['tenant_id'], unique=False)
    
    # 14. 修改visitors表，添加新字段
    op.add_column('visitors', sa.Column('current_status', sa.String(length=50), nullable=True))
    op.add_column('visitors', sa.Column('entry_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('visitors', sa.Column('exit_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('visitors', sa.Column('current_location', sa.String(length=200), nullable=True))
    op.add_column('visitors', sa.Column('reception_desk_id', sa.String(length=50), nullable=True))
    
    # 添加新的约束
    op.create_check_constraint(
        'chk_visitors_park_time_order',
        'visitors',
        'exit_time IS NULL OR entry_time IS NULL OR exit_time > entry_time'
    )


def downgrade():
    """执行迁移回滚"""
    
    # 1. 删除visitors表新增字段
    op.drop_constraint('chk_visitors_park_time_order', 'visitors', type_='check')
    op.drop_column('visitors', 'reception_desk_id')
    op.drop_column('visitors', 'current_location')
    op.drop_column('visitors', 'exit_time')
    op.drop_column('visitors', 'entry_time')
    op.drop_column('visitors', 'current_status')
    
    # 2. 删除新增的表（逆序删除）
    op.drop_table('mobile_sync_records')
    op.drop_table('emergency_operations')
    op.drop_table('security_alerts')
    op.drop_table('offline_verifications')
    op.drop_table('meeting_room_bookings')
    op.drop_table('meeting_rooms')
    op.drop_table('host_notifications')
    op.drop_table('reception_checkins')
    op.drop_table('visitor_entries')
    op.drop_table('visitor_verifications')
    op.drop_table('device_status_logs')
    op.drop_table('devices')
    
    # 3. 删除枚举类型
    sa.Enum(name='notification_channel').drop(op.get_bind())
    sa.Enum(name='checkin_method').drop(op.get_bind())
    sa.Enum(name='verification_status').drop(op.get_bind())
    sa.Enum(name='verification_method').drop(op.get_bind())
    sa.Enum(name='device_status').drop(op.get_bind())
    sa.Enum(name='device_type').drop(op.get_bind()) 