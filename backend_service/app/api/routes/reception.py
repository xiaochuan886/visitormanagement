"""
前台签到系统API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.dto.reception_dto import (
    ReceptionCheckinDTO,
    HostNotificationDTO,
    MeetingRoomDTO,
    MeetingRoomBookingDTO,
    VisitorFeedbackDTO,
    VisitorServiceRequestDTO,
    ReceptionVisitorInfoDTO,
    HostAvailabilityDTO
)
from app.application.services.reception_service import ReceptionService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant

router = APIRouter()


@router.post("/visitors/{visitor_id}/checkin", response_model=ReceptionCheckinDTO, summary="前台签到服务")
async def reception_checkin(
    visitor_id: int,
    checkin_data: ReceptionCheckinDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """访客在前台完成签到，包含健康检查、安全须知等"""
    service = ReceptionService(db)
    result = await service.process_visitor_checkin(
        visitor_id=visitor_id,
        checkin_data=checkin_data,
        receptionist=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.post("/hosts/{employee_id}/notify", response_model=HostNotificationDTO, summary="通知被访人")
async def notify_host_arrival(
    employee_id: int,
    notification_data: HostNotificationDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """实时通知被访员工访客已到达"""
    service = ReceptionService(db)
    result = await service.notify_host_of_arrival(
        employee_id=employee_id,
        notification_data=notification_data,
        sender=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.get("/employees/{employee_id}/availability", response_model=HostAvailabilityDTO, summary="被访人在岗状态")
async def get_employee_availability(
    employee_id: int,
    check_calendar: bool = Query(True, description="是否检查日程"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取被访员工的在岗状态和可用性"""
    service = ReceptionService(db)
    availability = await service.check_employee_availability(
        employee_id=employee_id,
        check_calendar=check_calendar,
        tenant_id=tenant_id
    )
    return availability


@router.get("/meeting-rooms/available", response_model=List[MeetingRoomDTO], summary="可用会议室查询")
async def get_available_meeting_rooms(
    date: str = Query(..., description="日期 YYYY-MM-DD"),
    start_time: str = Query(..., description="开始时间 HH:MM"),
    duration: int = Query(..., description="持续时长（分钟）"),
    capacity: Optional[int] = Query(None, description="最少容纳人数"),
    equipment: Optional[str] = Query(None, description="设备需求"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """查询可用的会议室"""
    service = ReceptionService(db)
    rooms = await service.get_available_meeting_rooms(
        date=date,
        start_time=start_time,
        duration=duration,
        capacity=capacity,
        equipment=equipment,
        tenant_id=tenant_id
    )
    return rooms


@router.post("/meeting-rooms/{room_id}/book", response_model=MeetingRoomBookingDTO, summary="预定会议室")
async def book_meeting_room(
    room_id: int,
    booking_data: MeetingRoomBookingDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """为访客预定会议室"""
    service = ReceptionService(db)
    booking = await service.book_meeting_room(
        room_id=room_id,
        booking_data=booking_data,
        booker=current_user["sub"],
        tenant_id=tenant_id
    )
    return booking


@router.get("/visitors/{visitor_id}/info", response_model=ReceptionVisitorInfoDTO, summary="访客详细信息")
async def get_visitor_reception_info(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取访客的详细信息，用于前台接待"""
    service = ReceptionService(db)
    visitor_info = await service.get_visitor_reception_info(
        visitor_id=visitor_id,
        tenant_id=tenant_id
    )
    if not visitor_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客信息不存在"
        )
    return visitor_info


@router.post("/services/feedback", summary="访客反馈收集")
async def collect_visitor_feedback(
    feedback_data: VisitorFeedbackDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """收集访客的满意度反馈和建议"""
    service = ReceptionService(db)
    result = await service.collect_visitor_feedback(
        feedback_data=feedback_data,
        collector=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.post("/services/request", summary="访客服务请求")
async def handle_visitor_service_request(
    service_request: VisitorServiceRequestDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """处理访客的各类服务请求"""
    service = ReceptionService(db)
    result = await service.handle_visitor_service_request(
        service_request=service_request,
        handler=current_user["sub"],
        tenant_id=tenant_id
    )
    return result


@router.get("/waiting-area/status", summary="等候区状态")
async def get_waiting_area_status(
    area_id: Optional[str] = Query(None, description="等候区ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取等候区的当前状态和座位情况"""
    service = ReceptionService(db)
    status_info = await service.get_waiting_area_status(
        area_id=area_id,
        tenant_id=tenant_id
    )
    return status_info


@router.post("/waiting-area/assign", summary="分配等候座位")
async def assign_waiting_seat(
    visitor_id: int,
    area_id: str = Query(..., description="等候区ID"),
    seat_preference: Optional[str] = Query(None, description="座位偏好"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """为访客分配等候区座位"""
    service = ReceptionService(db)
    assignment = await service.assign_waiting_seat(
        visitor_id=visitor_id,
        area_id=area_id,
        seat_preference=seat_preference,
        assigner=current_user["sub"],
        tenant_id=tenant_id
    )
    return assignment


@router.get("/statistics/daily", summary="前台日报统计")
async def get_daily_reception_statistics(
    date: str = Query(..., description="统计日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取前台接待的日报统计数据"""
    service = ReceptionService(db)
    statistics = await service.get_daily_reception_statistics(
        date=date,
        tenant_id=tenant_id
    )
    return statistics 