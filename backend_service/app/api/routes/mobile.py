"""
移动端备用验证方案API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.dto.mobile_dto import (
    MobileQRVerificationDTO as MobileVerificationDTO,
    MobileQuickCheckinDTO as MobileCheckinDTO,
    MobileOfflineSyncDTO as OfflineSyncDTO,
    MobileQRVerificationDTO as QRCodeVerificationDTO,
    MobileDeviceStatusDTO,
    EmergencyVerificationDTO
)
from app.application.services.mobile_sync_service import MobileSyncService as MobileVerificationService
from app.api.dependencies.auth import get_current_user, get_mobile_user
from app.api.dependencies.tenant import get_current_tenant

router = APIRouter()


@router.get("/gate/sync", summary="门岗移动端数据同步")
async def sync_gate_mobile_data(
    device_id: str = Query(..., description="移动设备ID"),
    last_sync: Optional[str] = Query(None, description="上次同步时间"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """门岗移动端获取同步数据"""
    service = MobileVerificationService(db)
    sync_data = await service.sync_gate_mobile_data(
        device_id=device_id,
        last_sync=last_sync,
        tenant_id=tenant_id
    )
    return sync_data


@router.post("/gate/verify-qr", response_model=MobileVerificationDTO, summary="移动端二维码验证")
async def verify_qr_code_mobile(
    qr_data: QRCodeVerificationDTO,
    device_id: str = Query(..., description="移动设备ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """移动端二维码验证功能"""
    service = MobileVerificationService(db)
    result = await service.verify_qr_code_mobile(
        qr_data=qr_data,
        device_id=device_id,
        operator=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.get("/reception/visitor-info/{qr_code}", response_model=dict, summary="扫码获取访客信息")
async def get_visitor_info_by_qr(
    qr_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """前台移动端扫码获取访客详细信息"""
    service = MobileVerificationService(db)
    visitor_info = await service.get_visitor_info_by_qr(
        qr_code=qr_code,
        tenant_id=tenant_id
    )
    if not visitor_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客信息不存在或二维码无效"
        )
    return visitor_info


@router.post("/reception/quick-checkin", response_model=MobileCheckinDTO, summary="移动端快速签到")
async def mobile_quick_checkin(
    checkin_data: MobileCheckinDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """前台移动端快速签到功能"""
    service = MobileVerificationService(db)
    result = await service.mobile_quick_checkin(
        checkin_data=checkin_data,
        operator=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.get("/offline/visitor-cache", summary="移动端离线数据缓存")
async def get_mobile_offline_cache(
    device_type: str = Query(..., description="设备类型: gate|reception"),
    device_id: str = Query(..., description="设备ID"),
    cache_hours: int = Query(24, description="缓存小时数"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取移动端离线验证所需的缓存数据"""
    service = MobileVerificationService(db)
    cache_data = await service.get_mobile_offline_cache(
        device_type=device_type,
        device_id=device_id,
        cache_hours=cache_hours,
        tenant_id=tenant_id
    )
    return cache_data


@router.post("/offline/sync", summary="离线数据同步上传")
async def sync_offline_data(
    sync_data: OfflineSyncDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """上传移动端离线期间的操作记录"""
    service = MobileVerificationService(db)
    sync_result = await service.sync_offline_data(
        sync_data=sync_data,
        tenant_id=tenant_id
    )
    return sync_result


@router.post("/emergency/verify", response_model=EmergencyVerificationDTO, summary="应急验证")
async def emergency_verification(
    visitor_name: str = Query(..., description="访客姓名"),
    visitor_phone: str = Query(..., description="访客电话"),
    emergency_reason: str = Query(..., description="应急原因"),
    device_id: str = Query(..., description="设备ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """应急情况下的访客验证"""
    service = MobileVerificationService(db)
    result = await service.emergency_verification(
        visitor_name=visitor_name,
        visitor_phone=visitor_phone,
        emergency_reason=emergency_reason,
        device_id=device_id,
        operator=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.post("/devices/{device_id}/status", summary="移动设备状态上报")
async def update_mobile_device_status(
    device_id: str,
    status_data: MobileDeviceStatusDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user)
):
    """移动设备状态和位置信息上报"""
    service = MobileVerificationService(db)
    result = await service.update_mobile_device_status(
        device_id=device_id,
        status_data=status_data,
        operator=current_user["sub"]
    )
    return result


@router.get("/devices/{device_id}/config", summary="获取移动设备配置")
async def get_mobile_device_config(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取移动设备的配置信息"""
    service = MobileVerificationService(db)
    config = await service.get_mobile_device_config(
        device_id=device_id,
        tenant_id=tenant_id
    )
    return config


@router.post("/photo/upload", summary="现场照片上传")
async def upload_verification_photo(
    visitor_id: int = Query(..., description="访客ID"),
    photo_type: str = Query(..., description="照片类型: entry|verification|emergency"),
    device_id: str = Query(..., description="设备ID"),
    photo: UploadFile = File(..., description="照片文件"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """上传验证过程中的现场照片"""
    service = MobileVerificationService(db)
    result = await service.upload_verification_photo(
        visitor_id=visitor_id,
        photo_type=photo_type,
        device_id=device_id,
        photo=photo,
        uploader=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.get("/statistics/mobile-usage", summary="移动端使用统计")
async def get_mobile_usage_statistics(
    device_id: Optional[str] = Query(None, description="设备ID"),
    date_from: str = Query(..., description="开始日期"),
    date_to: str = Query(..., description="结束日期"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取移动端使用统计数据"""
    service = MobileVerificationService(db)
    statistics = await service.get_mobile_usage_statistics(
        device_id=device_id,
        date_from=date_from,
        date_to=date_to,
        tenant_id=tenant_id
    )
    return statistics


@router.post("/feedback/device", summary="设备使用反馈")
async def submit_device_feedback(
    device_id: str = Query(..., description="设备ID"),
    feedback_type: str = Query(..., description="反馈类型: bug|suggestion|praise"),
    feedback_content: str = Query(..., description="反馈内容"),
    contact_info: Optional[str] = Query(None, description="联系方式"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_mobile_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """提交移动设备使用反馈"""
    service = MobileVerificationService(db)
    result = await service.submit_device_feedback(
        device_id=device_id,
        feedback_type=feedback_type,
        feedback_content=feedback_content,
        contact_info=contact_info,
        submitter=current_user["sub"],
        tenant_id=tenant_id
    )
    return result 