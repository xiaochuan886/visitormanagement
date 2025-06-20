"""
前台接待核心服务层
负责访客接待流程、主机通知、会议室管理、访客服务等功能
"""
import asyncio
import json
import logging
from datetime import datetime, date, timedelta, time
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, asc

from app.application.dto.reception_dto import (
    ReceptionCheckinDTO, HostNotificationDTO, WaitingAreaStatusDTO,
    MeetingRoomDTO, VisitorServiceRequestDTO, VisitorFeedbackDTO,
    DailyReceptionStatisticsDTO as ReceptionStatisticsDTO,
    CheckinMethod, CheckinStatus, NotificationChannel, ServiceType
)
from app.application.interfaces.repository import IRepository
from app.infrastructure.cache.redis_client import RedisClient
from app.core.logging import get_logger
from app.domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, 
    ValidationError,
    ConfigurationConflictError
)

logger = get_logger(__name__)


class ReceptionService:
    """前台接待核心服务"""
    
    def __init__(
        self,
        repository: IRepository,
        redis_client: RedisClient
    ):
        self.repository = repository
        self.redis_client = redis_client
        self.logger = logger
        
        # 缓存配置
        self.cache_prefix = "reception_service"
        self.checkin_cache_ttl = 1800  # 30分钟
        self.notification_cache_ttl = 300  # 5分钟
        self.meeting_room_cache_ttl = 3600  # 1小时
        
        # 服务配置
        self.max_waiting_time_minutes = 30
        self.vip_priority_enabled = True
        self.auto_notification_enabled = True
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        pass
    
    # ==================== 访客签到管理 ====================
    
    async def visitor_checkin(
        self,
        visitor_id: int,
        checkin_method: CheckinMethod,
        reception_desk_id: str,
        checkin_data: Optional[Dict[str, Any]] = None,
        operator: str = "",
        tenant_id: str = ""
    ) -> ReceptionCheckinDTO:
        """访客前台签到"""
        try:
            self.logger.info(f"访客前台签到: {visitor_id}, 方式: {checkin_method}")
            
            # 获取访客信息
            visitor = await self._get_visitor_info(visitor_id, tenant_id)
            if not visitor:
                raise ValidationError(f"访客不存在: {visitor_id}")
            
            # 检查签到资格
            eligibility_check = await self._check_checkin_eligibility(visitor, tenant_id)
            if not eligibility_check["eligible"]:
                raise ValidationError(f"签到失败: {eligibility_check['reason']}")
            
            # 处理签到照片
            photo_url = None
            if checkin_data and checkin_data.get("photo"):
                photo_url = await self._process_checkin_photo(checkin_data["photo"], visitor_id)
            
            # 分配等候区域
            waiting_area = await self._assign_waiting_area(visitor, reception_desk_id, tenant_id)
            
            # 创建签到记录
            checkin_record = {
                "visitor_id": visitor_id,
                "checkin_method": checkin_method.value,
                "reception_desk_id": reception_desk_id,
                "checkin_time": datetime.now(),
                "checkin_status": CheckinStatus.COMPLETED.value,
                "photo_url": photo_url,
                "waiting_area_id": waiting_area["area_id"],
                "queue_number": waiting_area["queue_number"],
                "estimated_wait_time": waiting_area["estimated_wait_time"],
                "operator": operator,
                "tenant_id": tenant_id
            }
            
            # 保存签到记录
            created_checkin = await self.repository.create("reception_checkins", checkin_record)
            
            # 发送主机通知
            notification_result = await self._send_host_notification(visitor, checkin_record, tenant_id)
            
            checkin_dto = ReceptionCheckinDTO(**created_checkin)
            self.logger.info(f"访客签到成功: {visitor_id}")
            return checkin_dto
            
        except Exception as e:
            self.logger.error(f"访客签到失败: {visitor_id}, 错误: {str(e)}")
            raise
    
    # ==================== 辅助方法 ====================
    
    async def _get_visitor_info(self, visitor_id: int, tenant_id: str) -> Optional[Dict[str, Any]]:
        """获取访客信息"""
        return await self.repository.get_by_condition(
            "visitors",
            {"id": visitor_id, "tenant_id": tenant_id}
        )
    
    async def _check_checkin_eligibility(
        self, 
        visitor: Dict[str, Any], 
        tenant_id: str
    ) -> Dict[str, Any]:
        """检查签到资格"""
        # 检查访客状态
        if visitor.get("status") != "approved":
            return {"eligible": False, "reason": f"访客状态异常: {visitor.get('status')}"}
        
        # 检查是否已签到
        existing_checkin = await self.repository.get_by_condition(
            "reception_checkins",
            {
                "visitor_id": visitor["id"],
                "tenant_id": tenant_id,
                "checkin_status": ["completed", "waiting"]
            }
        )
        
        if existing_checkin:
            return {"eligible": False, "reason": "访客已签到"}
        
        return {"eligible": True, "reason": ""}
    
    async def _assign_waiting_area(
        self,
        visitor: Dict[str, Any],
        reception_desk_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """分配等候区域"""
        # 获取当前队列号
        current_queue = await self.repository.get_max_value(
            "reception_checkins",
            "queue_number",
            {
                "reception_desk_id": reception_desk_id,
                "tenant_id": tenant_id,
                "checkin_time": {">=": date.today()}
            }
        )
        
        next_queue_number = (current_queue or 0) + 1
        
        # 计算预计等待时间
        waiting_count = await self.repository.count(
            "reception_checkins",
            {
                "reception_desk_id": reception_desk_id,
                "tenant_id": tenant_id,
                "checkin_status": "waiting"
            }
        )
        
        estimated_wait_time = waiting_count * 10  # 每人平均10分钟
        
        return {
            "area_id": f"area_{reception_desk_id}",
            "queue_number": next_queue_number,
            "estimated_wait_time": estimated_wait_time
        }
    
    async def _send_host_notification(
        self,
        visitor: Dict[str, Any],
        checkin_record: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """发送主机通知"""
        try:
            # 获取员工信息
            employee = await self.repository.get_by_condition(
                "employees",
                {"id": visitor.get("employee_id"), "tenant_id": tenant_id}
            )
            
            if not employee:
                return {"sent": False, "reason": "被访员工不存在"}
            
            # 生成通知内容
            notification_content = {
                "visitor_name": visitor["name"],
                "visitor_phone": visitor["phone"],
                "visit_purpose": visitor.get("purpose", ""),
                "checkin_time": checkin_record["checkin_time"].isoformat(),
                "queue_number": checkin_record["queue_number"]
            }
            
            # 这里可以集成真实的通知服务（微信、邮件、短信等）
            # 现在先模拟发送成功
            
            return {"sent": True, "notification_id": f"notif_{visitor['id']}_{int(datetime.now().timestamp())}"}
            
        except Exception as e:
            self.logger.error(f"发送主机通知失败: {str(e)}")
            return {"sent": False, "reason": str(e)}
    
    async def _process_checkin_photo(self, photo_data: Any, visitor_id: int) -> Optional[str]:
        """处理签到照片"""
        try:
            # 这里应该集成文件上传服务
            # 现在先返回模拟URL
            photo_url = f"/uploads/checkin_photos/visitor_{visitor_id}_{int(datetime.now().timestamp())}.jpg"
            return photo_url
        except Exception as e:
            self.logger.error(f"处理签到照片失败: {str(e)}")
            return None
    
    async def get_waiting_area_status(
        self,
        reception_desk_id: str,
        tenant_id: str
    ) -> WaitingAreaStatusDTO:
        """
        获取等候区域状态
        
        Args:
            reception_desk_id: 前台接待台ID
            tenant_id: 租户ID
            
        Returns:
            WaitingAreaStatusDTO: 等候区域状态
        """
        try:
            # 尝试从缓存获取
            cache_key = f"{self.cache_prefix}:waiting_area:{reception_desk_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return WaitingAreaStatusDTO.model_validate_json(cached_data)
            
            # 查询当前等候访客
            waiting_visitors = await self.repository.list_by_conditions(
                "reception_checkins",
                {
                    "reception_desk_id": reception_desk_id,
                    "tenant_id": tenant_id,
                    "checkin_status": "waiting"
                },
                order_by="checkin_time"
            )
            
            # 计算等候统计
            total_waiting = len(waiting_visitors)
            vip_waiting = len([v for v in waiting_visitors if v.get("visitor_info", {}).get("is_vip", False)])
            average_wait_time = await self._calculate_average_wait_time(reception_desk_id, tenant_id)
            
            # 获取区域配置
            area_config = await self._get_waiting_area_config(reception_desk_id, tenant_id)
            
            waiting_status = WaitingAreaStatusDTO(
                reception_desk_id=reception_desk_id,
                total_capacity=area_config.get("capacity", 20),
                current_occupancy=total_waiting,
                occupancy_rate=total_waiting / area_config.get("capacity", 20) * 100,
                waiting_visitors=waiting_visitors,
                vip_visitors_count=vip_waiting,
                average_wait_time_minutes=average_wait_time,
                peak_hour_indicator=await self._is_peak_hour(reception_desk_id, tenant_id),
                comfort_amenities=area_config.get("amenities", []),
                current_queue_number=waiting_visitors[-1]["queue_number"] if waiting_visitors else 0,
                next_available_slot=await self._get_next_available_slot(reception_desk_id, tenant_id),
                area_status="busy" if total_waiting > area_config.get("capacity", 20) * 0.8 else "normal",
                last_updated=datetime.now()
            )
            
            # 缓存结果
            await self.redis_client.setex(
                cache_key,
                self.checkin_cache_ttl,
                waiting_status.model_dump_json()
            )
            
            return waiting_status
            
        except Exception as e:
            self.logger.error(f"获取等候区域状态失败: {reception_desk_id}, 错误: {str(e)}")
            raise
    
    # ==================== 主机通知管理 ====================
    
    async def send_host_notification(
        self,
        visitor_id: int,
        notification_channels: List[NotificationChannel],
        custom_message: Optional[str] = None,
        tenant_id: str = ""
    ) -> HostNotificationDTO:
        """
        发送主机通知
        
        Args:
            visitor_id: 访客ID
            notification_channels: 通知渠道
            custom_message: 自定义消息
            tenant_id: 租户ID
            
        Returns:
            HostNotificationDTO: 通知发送结果
        """
        try:
            self.logger.info(f"发送主机通知: 访客{visitor_id}, 渠道: {notification_channels}")
            
            # 获取访客和员工信息
            visitor = await self._get_visitor_info(visitor_id, tenant_id)
            if not visitor:
                raise ValidationError(f"访客不存在: {visitor_id}")
            
            employee = await self._get_employee_info(visitor.get("employee_id"), tenant_id)
            if not employee:
                raise ValidationError(f"被访员工不存在: {visitor.get('employee_id')}")
            
            # 生成通知内容
            notification_content = await self._generate_notification_content(
                visitor, employee, custom_message
            )
            
            # 执行多渠道通知
            notification_results = []
            for channel in notification_channels:
                result = await self._send_notification_via_channel(
                    channel, employee, notification_content, visitor
                )
                notification_results.append(result)
            
            # 创建通知记录
            notification_record = {
                "notification_id": f"notif_{visitor_id}_{int(datetime.now().timestamp())}",
                "visitor_id": visitor_id,
                "employee_id": employee["id"],
                "notification_channels": [channel.value for channel in notification_channels],
                "notification_content": notification_content,
                "sent_at": datetime.now(),
                "delivery_status": "sent" if any(r["success"] for r in notification_results) else "failed",
                "delivery_results": notification_results,
                "read_status": "unread",
                "tenant_id": tenant_id
            }
            
            await self.repository.create("host_notifications", notification_record)
            
            # 设置确认超时处理
            await self._schedule_confirmation_timeout(notification_record)
            
            notification_dto = HostNotificationDTO(**notification_record)
            
            self.logger.info(f"主机通知发送完成: {visitor_id}, 成功渠道: {len([r for r in notification_results if r['success']])}")
            return notification_dto
            
        except Exception as e:
            self.logger.error(f"主机通知发送失败: {visitor_id}, 错误: {str(e)}")
            raise
    
    async def confirm_host_response(
        self,
        notification_id: str,
        response_action: str,
        response_message: Optional[str] = None,
        estimated_arrival_minutes: Optional[int] = None,
        tenant_id: str = ""
    ) -> Dict[str, Any]:
        """
        确认主机响应
        
        Args:
            notification_id: 通知ID
            response_action: 响应动作 (accept|decline|delay)
            response_message: 响应消息
            estimated_arrival_minutes: 预计到达时间（分钟）
            tenant_id: 租户ID
            
        Returns:
            Dict: 响应处理结果
        """
        try:
            self.logger.info(f"处理主机响应: {notification_id}, 动作: {response_action}")
            
            # 获取通知记录
            notification = await self.repository.get_by_condition(
                "host_notifications",
                {"notification_id": notification_id, "tenant_id": tenant_id}
            )
            
            if not notification:
                raise ValidationError(f"通知记录不存在: {notification_id}")
            
            # 更新通知状态
            response_data = {
                "read_status": "read",
                "response_action": response_action,
                "response_message": response_message,
                "response_time": datetime.now(),
                "estimated_arrival_minutes": estimated_arrival_minutes
            }
            
            await self.repository.update(
                "host_notifications",
                {"notification_id": notification_id, "tenant_id": tenant_id},
                response_data
            )
            
            # 通知访客响应结果
            visitor_notification_result = await self._notify_visitor_response(
                notification["visitor_id"], response_action, response_message, 
                estimated_arrival_minutes, tenant_id
            )
            
            # 根据响应调整等候安排
            if response_action == "accept":
                await self._arrange_meeting(notification, estimated_arrival_minutes, tenant_id)
            elif response_action == "decline":
                await self._handle_meeting_decline(notification, response_message, tenant_id)
            elif response_action == "delay":
                await self._handle_meeting_delay(notification, estimated_arrival_minutes, tenant_id)
            
            result = {
                "notification_id": notification_id,
                "response_processed": True,
                "response_action": response_action,
                "visitor_notified": visitor_notification_result["success"],
                "next_steps": await self._get_next_steps(response_action, notification),
                "updated_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"主机响应处理完成: {notification_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"主机响应处理失败: {notification_id}, 错误: {str(e)}")
            raise
    
    # ==================== 会议室管理 ====================
    
    async def get_available_meeting_rooms(
        self,
        start_time: datetime,
        duration_minutes: int,
        capacity_required: int,
        amenities_required: Optional[List[str]] = None,
        tenant_id: str = ""
    ) -> List[MeetingRoomDTO]:
        """
        获取可用会议室
        
        Args:
            start_time: 开始时间
            duration_minutes: 持续时间（分钟）
            capacity_required: 所需容量
            amenities_required: 所需设备
            tenant_id: 租户ID
            
        Returns:
            List[MeetingRoomDTO]: 可用会议室列表
        """
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # 查询所有会议室
            all_rooms = await self.repository.list_by_conditions(
                "meeting_rooms",
                {
                    "tenant_id": tenant_id,
                    "status": "active",
                    "capacity": {">=": capacity_required}
                }
            )
            
            available_rooms = []
            
            for room in all_rooms:
                # 检查时间冲突
                conflicts = await self.repository.list_by_conditions(
                    "meeting_room_bookings",
                    {
                        "room_id": room["id"],
                        "tenant_id": tenant_id,
                        "status": "confirmed",
                        "start_time": {"<": end_time},
                        "end_time": {">": start_time}
                    }
                )
                
                if conflicts:
                    continue
                
                # 检查设备要求
                if amenities_required:
                    room_amenities = room.get("amenities", [])
                    if not all(amenity in room_amenities for amenity in amenities_required):
                        continue
                
                # 计算推荐指数
                recommendation_score = await self._calculate_room_recommendation_score(
                    room, start_time, duration_minutes, capacity_required
                )
                
                meeting_room_dto = MeetingRoomDTO(
                    room_id=room["id"],
                    room_name=room["name"],
                    location=room["location"],
                    capacity=room["capacity"],
                    amenities=room.get("amenities", []),
                    booking_status="available",
                    current_booking=None,
                    next_booking=await self._get_next_booking(room["id"], start_time, tenant_id),
                    availability_window=await self._get_availability_window(room["id"], start_time, tenant_id),
                    room_features=room.get("features", {}),
                    booking_rules=room.get("booking_rules", {}),
                    real_time_status="vacant",
                    equipment_status=room.get("equipment_status", {}),
                    cleaning_status=room.get("cleaning_status", "clean"),
                    recommendation_score=recommendation_score,
                    estimated_setup_time=room.get("setup_time_minutes", 5)
                )
                
                available_rooms.append(meeting_room_dto)
            
            # 按推荐指数排序
            available_rooms.sort(key=lambda x: x.recommendation_score, reverse=True)
            
            return available_rooms
            
        except Exception as e:
            self.logger.error(f"获取可用会议室失败: {str(e)}")
            return []
    
    async def book_meeting_room(
        self,
        room_id: int,
        visitor_id: int,
        start_time: datetime,
        duration_minutes: int,
        meeting_title: str,
        attendees: List[str],
        operator: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        预订会议室
        
        Args:
            room_id: 会议室ID
            visitor_id: 访客ID
            start_time: 开始时间
            duration_minutes: 持续时间
            meeting_title: 会议标题
            attendees: 参与者列表
            operator: 操作员
            tenant_id: 租户ID
            
        Returns:
            Dict: 预订结果
        """
        try:
            self.logger.info(f"预订会议室: 房间{room_id}, 访客{visitor_id}, 时间{start_time}")
            
            # 验证会议室可用性
            availability = await self.get_available_meeting_rooms(
                start_time, duration_minutes, len(attendees), None, tenant_id
            )
            
            available_room = next((room for room in availability if room.room_id == room_id), None)
            if not available_room:
                raise ValidationError("会议室不可用")
            
            # 创建预订记录
            booking_record = {
                "booking_id": f"booking_{room_id}_{visitor_id}_{int(start_time.timestamp())}",
                "room_id": room_id,
                "visitor_id": visitor_id,
                "start_time": start_time,
                "end_time": start_time + timedelta(minutes=duration_minutes),
                "duration_minutes": duration_minutes,
                "meeting_title": meeting_title,
                "attendees": attendees,
                "booking_status": "confirmed",
                "operator": operator,
                "tenant_id": tenant_id,
                "created_at": datetime.now(),
                "booking_source": "reception_desk"
            }
            
            await self.repository.create("meeting_room_bookings", booking_record)
            
            # 更新会议室状态
            await self.repository.update(
                "meeting_rooms",
                {"id": room_id, "tenant_id": tenant_id},
                {"current_booking_id": booking_record["booking_id"]}
            )
            
            # 发送确认通知
            await self._send_booking_confirmation(booking_record, tenant_id)
            
            # 清除会议室缓存
            await self._clear_meeting_room_cache(room_id)
            
            result = {
                "booking_id": booking_record["booking_id"],
                "room_name": available_room.room_name,
                "booking_confirmed": True,
                "start_time": start_time.isoformat(),
                "end_time": (start_time + timedelta(minutes=duration_minutes)).isoformat(),
                "access_code": await self._generate_room_access_code(room_id, booking_record["booking_id"]),
                "setup_instructions": available_room.room_features.get("setup_instructions", "")
            }
            
            self.logger.info(f"会议室预订成功: {booking_record['booking_id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"会议室预订失败: {str(e)}")
            raise 