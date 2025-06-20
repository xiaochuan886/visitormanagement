"""
设备管理路由
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database.connection import get_db
from app.api.dependencies.auth import get_current_user
from app.application.services.device_service import DeviceService
from app.application.dto.device_dto import (
    DeviceInfoDTO as DeviceRegistrationDTO,
    DeviceConfigurationDTO as DeviceConfigUpdateDTO,
    DeviceStatusDTO as DeviceStatusUpdateDTO,
    DeviceMaintenanceDTO,
    DeviceInfoDTO as DeviceResponseDTO,
    DeviceInfoDTO as DeviceListResponseDTO,
    DeviceStatusDTO as DeviceStatusLogResponseDTO,
    DeviceStatusDTO as DeviceMonitoringDTO,
    DeviceAlertDTO as DeviceAlertConfigDTO,
    DeviceUsageStatisticsDTO as DeviceUsageStatsDTO,
    DeviceType,
    DeviceStatus
)
from app.domain.exceptions.config_exceptions import ValidationError

router = APIRouter(prefix="/devices", tags=["设备管理"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="注册新设备",
    description="在系统中注册新的访客管理设备"
)
async def register_device(
    device_data: DeviceRegistrationDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """注册新设备"""
    try:
        device_service = DeviceService(db)
        device = await device_service.register_device(
            device_data=device_data,
            operator=current_user.get("username", "unknown")
        )
        
        return {
            "success": True,
            "message": "设备注册成功",
            "data": device
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设备注册失败: {str(e)}")


@router.get(
    "",
    summary="获取设备列表",
    description="获取设备列表，支持筛选和分页"
)
async def list_devices(
    device_type: Optional[DeviceType] = Query(None, description="设备类型筛选"),
    status: Optional[DeviceStatus] = Query(None, description="设备状态筛选"),
    site_id: Optional[int] = Query(None, description="站点ID筛选"),
    zone: Optional[str] = Query(None, description="区域筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取设备列表"""
    try:
        device_service = DeviceService(db)
        result = await device_service.list_devices(
            device_type=device_type,
            status=status,
            site_id=site_id,
            zone=zone,
            page=page,
            size=size,
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "获取设备列表成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备列表失败: {str(e)}")


@router.get(
    "/{device_id}",
    summary="获取设备详情",
    description="根据设备ID获取设备详细信息"
)
async def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取设备详情"""
    try:
        device_service = DeviceService(db)
        device = await device_service.get_device(
            device_id=device_id,
            tenant_id=current_user.get("tenant_id")
        )
        
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")
        
        return {
            "success": True,
            "message": "获取设备信息成功",
            "data": device
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备信息失败: {str(e)}")


@router.get(
    "/{device_id}/status",
    summary="获取设备状态",
    description="获取设备的实时状态信息"
)
async def get_device_status(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取设备状态"""
    try:
        device_service = DeviceService(db)
        status_info = await device_service.get_device_status(
            device_id=device_id,
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "获取设备状态成功",
            "data": status_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备状态失败: {str(e)}")


@router.put(
    "/{device_id}/config",
    summary="更新设备配置",
    description="更新设备的配置信息"
)
async def update_device_config(
    device_id: str,
    config_data: DeviceConfigUpdateDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新设备配置"""
    try:
        device_service = DeviceService(db)
        device = await device_service.update_device_config(
            device_id=device_id,
            config_data=config_data,
            operator=current_user.get("username"),
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "设备配置更新成功",
            "data": device
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{device_id}/status",
    summary="更新设备状态",
    description="更新设备的运行状态和健康指标"
)
async def update_device_status(
    device_id: str,
    status_data: DeviceStatusUpdateDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新设备状态"""
    try:
        device_service = DeviceService(db)
        result = await device_service.update_device_status(
            device_id=device_id,
            status_data=status_data,
            operator=current_user.get("username"),
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "设备状态更新成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设备状态更新失败: {str(e)}")


@router.get(
    "/{device_id}/status-logs",
    summary="获取设备状态日志",
    description="获取设备的状态变更历史记录"
)
async def get_device_status_logs(
    device_id: str,
    start_time: Optional[str] = Query(None, description="开始时间 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间 (ISO格式)"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取设备状态日志"""
    try:
        device_service = DeviceService(db)
        result = await device_service.get_device_status_logs(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            page=page,
            size=size,
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "获取设备状态日志成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备状态日志失败: {str(e)}")


@router.post(
    "/{device_id}/maintenance",
    summary="记录设备维护",
    description="记录设备维护活动和结果"
)
async def record_device_maintenance(
    device_id: str,
    maintenance_data: DeviceMaintenanceDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """记录设备维护"""
    try:
        device_service = DeviceService(db)
        result = await device_service.record_maintenance(
            device_id=device_id,
            maintenance_data=maintenance_data,
            operator=current_user.get("username"),
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "设备维护记录成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{device_id}/monitoring",
    summary="获取设备监控数据",
    description="获取设备的实时监控指标和告警信息"
)
async def get_device_monitoring(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取设备监控数据"""
    try:
        device_service = DeviceService(db)
        monitoring_data = await device_service.get_device_monitoring(
            device_id=device_id,
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "获取设备监控数据成功",
            "data": monitoring_data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备监控数据失败: {str(e)}")


@router.put(
    "/{device_id}/alert-config",
    summary="配置设备告警",
    description="配置设备的告警规则和通知设置"
)
async def configure_device_alerts(
    device_id: str,
    alert_config: DeviceAlertConfigDTO,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """配置设备告警"""
    try:
        device_service = DeviceService(db)
        result = await device_service.configure_device_alerts(
            device_id=device_id,
            alert_config=alert_config,
            operator=current_user.get("username"),
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "设备告警配置成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{device_id}/usage-stats",
    summary="获取设备使用统计",
    description="获取设备的使用情况统计和性能分析"
)
async def get_device_usage_stats(
    device_id: str,
    start_date: Optional[str] = Query(None, description="统计开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="统计结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取设备使用统计"""
    try:
        device_service = DeviceService(db)
        stats = await device_service.get_device_usage_stats(
            device_id=device_id,
            start_date=start_date,
            end_date=end_date,
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "success": True,
            "message": "获取设备使用统计成功",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设备使用统计失败: {str(e)}")