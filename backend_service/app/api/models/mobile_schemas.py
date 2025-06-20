"""
移动端同步系统 Schema 定义
包含移动端数据同步、离线验证、应急处理等相关数据传输对象
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.api.models.base_response import BaseResponseModel


# 枚举定义
class SyncType(str, Enum):
    """同步类型枚举"""
    FULL_SYNC = "full_sync"
    INCREMENTAL_SYNC = "incremental_sync"
    EMERGENCY_SYNC = "emergency_sync"
    MANUAL_SYNC = "manual_sync"


class SyncStatus(str, Enum):
    """同步状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class NetworkQuality(str, Enum):
    """网络质量枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    POOR = "poor"
    OFFLINE = "offline"


# 移动端数据同步 Schema
class MobileSyncRequestSchema(BaseModel):
    """移动端数据同步请求Schema"""
    device_id: str = Field(..., description="设备ID")
    sync_type: SyncType = Field(..., description="同步类型")
    data_types: List[str] = Field(..., description="数据类型列表")
    last_sync_time: Optional[datetime] = Field(None, description="上次同步时间")
    force_sync: bool = Field(False, description="是否强制同步")
    network_quality: NetworkQuality = Field(NetworkQuality.GOOD, description="网络质量")
    compression_enabled: bool = Field(True, description="是否启用压缩")
    batch_size: int = Field(100, description="批次大小", ge=1, le=1000)


class MobileSyncResponseSchema(BaseResponseModel):
    """移动端数据同步响应Schema"""
    sync_id: str = Field(..., description="同步ID")
    device_id: str = Field(..., description="设备ID")
    sync_status: SyncStatus = Field(..., description="同步状态")
    sync_data: Dict[str, Any] = Field(..., description="同步数据")
    data_count: int = Field(..., description="数据条数")
    sync_time: datetime = Field(..., description="同步时间")
    next_sync_time: Optional[datetime] = Field(None, description="下次同步时间")
    compression_ratio: Optional[float] = Field(None, description="压缩比例")


# 离线验证上传 Schema
class OfflineVerificationUploadRequestSchema(BaseModel):
    """离线验证上传请求Schema"""
    device_id: str = Field(..., description="设备ID")
    verifications: List[Dict[str, Any]] = Field(..., description="离线验证列表")
    upload_priority: int = Field(1, description="上传优先级", ge=1, le=5)


class OfflineVerificationUploadResponseSchema(BaseResponseModel):
    """离线验证上传响应Schema"""
    upload_id: str = Field(..., description="上传ID")
    processed_count: int = Field(..., description="处理数量")
    success_count: int = Field(..., description="成功数量")
    failure_count: int = Field(..., description="失败数量")
    duplicate_count: int = Field(..., description="重复数量")
    conflicts: List[Dict[str, Any]] = Field(default=[], description="冲突记录")
    upload_time: datetime = Field(..., description="上传时间")


# 二维码验证 Schema
class MobileQRVerificationRequestSchema(BaseModel):
    """移动端二维码验证请求Schema"""
    device_id: str = Field(..., description="设备ID")
    qr_code: str = Field(..., description="二维码内容")
    scan_location: Optional[Dict[str, float]] = Field(None, description="扫描位置")
    offline_mode: bool = Field(False, description="是否离线模式")


class MobileQRVerificationResponseSchema(BaseResponseModel):
    """移动端二维码验证响应Schema"""
    verification_id: str = Field(..., description="验证ID")
    visitor_info: Optional[Dict[str, Any]] = Field(None, description="访客信息")
    access_granted: bool = Field(..., description="是否允许通行")
    verification_time: datetime = Field(..., description="验证时间")
    offline_cached: bool = Field(False, description="是否离线缓存")


# 应急验证处理 Schema
class EmergencyVerificationMobileRequestSchema(BaseModel):
    """移动端应急验证请求Schema"""
    device_id: str = Field(..., description="设备ID")
    emergency_type: str = Field(..., description="应急类型")
    reason: str = Field(..., description="应急原因")
    affected_functions: List[str] = Field(..., description="受影响功能")
    operation_type: str = Field(..., description="操作类型")
    operator: str = Field(..., description="操作员")


class EmergencyVerificationMobileResponseSchema(BaseResponseModel):
    """移动端应急验证响应Schema"""
    emergency_id: str = Field(..., description="应急处理ID")
    device_id: str = Field(..., description="设备ID")
    emergency_status: str = Field(..., description="应急状态")
    activated_at: datetime = Field(..., description="激活时间")
    emergency_procedures: List[str] = Field(..., description="应急程序")


# 数据冲突解决 Schema
class DataConflictResolutionRequestSchema(BaseModel):
    """数据冲突解决请求Schema"""
    device_id: str = Field(..., description="设备ID")
    conflicts: List[Dict[str, Any]] = Field(..., description="冲突列表")
    resolution_strategy: str = Field("manual", description="解决策略")


class DataConflictResolutionResponseSchema(BaseResponseModel):
    """数据冲突解决响应Schema"""
    resolution_id: str = Field(..., description="解决方案ID")
    resolved_conflicts: int = Field(..., description="已解决冲突数")
    pending_conflicts: int = Field(..., description="待处理冲突数")
    resolution_results: List[Dict[str, Any]] = Field(..., description="解决结果")


# 移动端状态同步 Schema
class MobileStatusSyncRequestSchema(BaseModel):
    """移动端状态同步请求Schema"""
    device_id: str = Field(..., description="设备ID")
    device_status: Dict[str, Any] = Field(..., description="设备状态")
    location_info: Optional[Dict[str, float]] = Field(None, description="位置信息")
    battery_level: Optional[int] = Field(None, description="电池电量", ge=0, le=100)


class MobileStatusSyncResponseSchema(BaseResponseModel):
    """移动端状态同步响应Schema"""
    device_id: str = Field(..., description="设备ID")
    sync_time: datetime = Field(..., description="同步时间")
    server_instructions: List[str] = Field(default=[], description="服务器指令")
    config_updates: Dict[str, Any] = Field(default={}, description="配置更新")


# 缓存管理 Schema
class CacheManagementRequestSchema(BaseModel):
    """缓存管理请求Schema"""
    device_id: str = Field(..., description="设备ID")
    operation: str = Field(..., description="操作类型")
    cache_types: List[str] = Field(..., description="缓存类型")


class CacheManagementResponseSchema(BaseResponseModel):
    """缓存管理响应Schema"""
    device_id: str = Field(..., description="设备ID")
    operation_result: Dict[str, str] = Field(..., description="操作结果")
    cache_info: Dict[str, Any] = Field(..., description="缓存信息")
    operation_time: datetime = Field(..., description="操作时间") 