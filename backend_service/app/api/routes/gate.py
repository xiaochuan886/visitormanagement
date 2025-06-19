"""
门岗放行系统API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.dto.gate_dto import (
    GateVerificationDTO,
    VisitorEntryDTO,
    GateStatusDTO,
    OfflineVerificationDTO,
    TodayVisitorsCacheDTO,
    EmergencyOpenDTO,
    GateDeviceStatusDTO
)
from app.application.services.security_gate_service import SecurityGateService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant

router = APIRouter()


@router.get("/arrivals/today", response_model=List[TodayVisitorsCacheDTO], summary="今日预期到访访客")
async def get_today_arrivals(
    gate_id: Optional[str] = Query(None, description="门岗ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取今日预期到访的访客列表，用于门岗验证"""
    service = SecurityGateService(db)
    arrivals = await service.get_today_arrivals(tenant_id, gate_id)
    return arrivals


@router.post("/visitors/{visitor_id}/verify", response_model=GateVerificationDTO, summary="访客身份验证")
async def verify_visitor(
    visitor_id: int,
    verification_method: str = Query(..., description="验证方式: qr_code|id_card|face_recognition|manual"),
    gate_id: str = Query(..., description="门岗设备ID"),
    verification_data: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """多重验证访客身份"""
    service = SecurityGateService(db)
    result = await service.verify_visitor_identity(
        visitor_id=visitor_id,
        verification_method=verification_method,
        gate_id=gate_id,
        verification_data=verification_data,
        operator=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.post("/visitors/{visitor_id}/entry", response_model=VisitorEntryDTO, summary="访客入园登记")
async def register_visitor_entry(
    visitor_id: int,
    gate_id: str = Query(..., description="门岗设备ID"),
    entry_photo: Optional[UploadFile] = File(None, description="入园现场照片"),
    vehicle_info: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """登记访客入园信息，打印访客证"""
    service = SecurityGateService(db)
    entry_result = await service.register_visitor_entry(
        visitor_id=visitor_id,
        gate_id=gate_id,
        entry_photo=entry_photo,
        vehicle_info=vehicle_info,
        operator=current_user["sub"],
        tenant_id=tenant_id
    )
    return entry_result


@router.get("/visitors/in-park", response_model=List[dict], summary="园区内访客实时状态")
async def get_visitors_in_park(
    gate_id: Optional[str] = Query(None, description="门岗ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取当前在园区内的访客实时状态"""
    service = SecurityGateService(db)
    visitors = await service.get_visitors_in_park(tenant_id, gate_id)
    return visitors


@router.get("/cache/today-visitors", response_model=dict, summary="今日访客离线缓存数据")
async def get_today_visitors_cache(
    gate_id: str = Query(..., description="门岗设备ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取门岗离线验证所需的今日访客数据"""
    service = SecurityGateService(db)
    cache_data = await service.generate_offline_cache(tenant_id, gate_id)
    return cache_data


@router.post("/offline/verify-sync", summary="离线验证记录同步")
async def sync_offline_verifications(
    offline_records: List[OfflineVerificationDTO],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """同步离线期间的验证记录"""
    service = SecurityGateService(db)
    sync_result = await service.sync_offline_verifications(
        offline_records=offline_records,
        tenant_id=tenant_id
    )
    return sync_result


@router.post("/alerts", summary="安全提醒上报")
async def report_security_alert(
    alert_type: str = Query(..., description="告警类型: blacklist|unauthorized|system_error"),
    gate_id: str = Query(..., description="门岗设备ID"),
    alert_data: dict = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """上报安全告警和异常情况"""
    service = SecurityGateService(db)
    alert_result = await service.report_security_alert(
        alert_type=alert_type,
        gate_id=gate_id,
        alert_data=alert_data,
        reporter=current_user["sub"],
        tenant_id=tenant_id
    )
    return alert_result


@router.post("/emergency/open", summary="紧急开放门禁")
async def emergency_open_gate(
    emergency_data: EmergencyOpenDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """紧急情况下开放门禁系统"""
    service = SecurityGateService(db)
    result = await service.emergency_open_gates(
        emergency_data=emergency_data,
        operator=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.post("/devices/{device_id}/heartbeat", summary="设备健康状态上报")
async def device_heartbeat(
    device_id: str,
    status_data: GateDeviceStatusDTO,
    db: AsyncSession = Depends(get_db)
):
    """门岗设备健康状态心跳上报"""
    service = SecurityGateService(db)
    result = await service.update_device_status(
        device_id=device_id,
        status_data=status_data
    )
    return result


@router.get("/devices/{device_id}/status", response_model=GateDeviceStatusDTO, summary="获取设备状态")
async def get_device_status(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取门岗设备当前状态"""
    service = SecurityGateService(db)
    status = await service.get_device_status(device_id, tenant_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    return status 