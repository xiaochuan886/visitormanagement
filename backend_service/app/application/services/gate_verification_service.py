"""
门岗验证核心服务层（增强版）
负责门岗身份验证、设备集成、离线缓存、应急处理等核心功能
"""
import asyncio
import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, asc

from app.application.dto.gate_dto import (
    GateVerificationDTO, VisitorEntryDTO, GateStatusDTO,
    OfflineVerificationDTO, TodayVisitorsCacheDTO, EmergencyOpenDTO,
    GateDeviceStatusDTO, MultiVerificationRequestDTO, FusionVerificationResultDTO,
    VerificationMethod, VerificationStatus, GateAccessLevel
)
from app.application.dto.device_dto import DeviceInfoDTO, DeviceStatusDTO
from app.application.services.device_service import DeviceService
from app.application.interfaces.repository import IRepository
from app.infrastructure.cache.redis_client import RedisClient
from app.core.logging import get_logger
from app.domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, 
    ValidationError,
    ConfigurationConflictError
)

logger = get_logger(__name__)


class GateVerificationService:
    """门岗验证核心服务（增强版）"""
    
    def __init__(
        self,
        repository: IRepository,
        redis_client: RedisClient,
        device_service: DeviceService
    ):
        self.repository = repository
        self.redis_client = redis_client
        self.device_service = device_service
        self.logger = logger
        
        # 缓存配置
        self.cache_prefix = "gate_verification"
        self.visitor_cache_ttl = 3600  # 1小时
        self.verification_cache_ttl = 1800  # 30分钟
        self.offline_cache_ttl = 86400  # 24小时
        
        # 验证规则配置
        self.max_verification_attempts = 3
        self.verification_timeout_minutes = 5
        self.blacklist_check_enabled = True
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        pass
    
    # ==================== 多重身份验证 ====================
    
    async def verify_visitor_identity(
        self,
        visitor_id: int,
        verification_method: VerificationMethod,
        gate_id: str,
        verification_data: Optional[Dict[str, Any]] = None,
        operator: str = "",
        tenant_id: str = ""
    ) -> GateVerificationDTO:
        """
        访客身份验证（单一方法）
        
        Args:
            visitor_id: 访客ID
            verification_method: 验证方式
            gate_id: 门岗设备ID
            verification_data: 验证数据
            operator: 操作员
            tenant_id: 租户ID
            
        Returns:
            GateVerificationDTO: 验证结果
        """
        try:
            self.logger.info(f"开始访客身份验证: {visitor_id}, 方法: {verification_method}, 门岗: {gate_id}")
            
            # 检查设备状态
            await self._check_gate_device_status(gate_id)
            
            # 获取访客信息
            visitor = await self._get_visitor_info(visitor_id, tenant_id)
            if not visitor:
                raise ValidationError(f"访客不存在: {visitor_id}")
            
            # 预验证检查
            pre_check_result = await self._pre_verification_checks(visitor, gate_id, tenant_id)
            if not pre_check_result["passed"]:
                return self._create_failed_verification(
                    visitor_id, visitor, verification_method, gate_id, 
                    pre_check_result["reason"], operator
                )
            
            # 执行具体验证
            verification_result = await self._execute_verification(
                verification_method, visitor, verification_data, gate_id
            )
            
            # 后验证处理
            verification_dto = await self._post_verification_processing(
                verification_result, visitor, verification_method, gate_id, operator, tenant_id
            )
            
            # 记录验证日志
            await self._log_verification_attempt(verification_dto, tenant_id)
            
            self.logger.info(f"访客验证完成: {visitor_id}, 结果: {verification_dto.verification_status}")
            return verification_dto
            
        except Exception as e:
            self.logger.error(f"访客身份验证失败: {visitor_id}, 错误: {str(e)}")
            raise
    
    async def multi_factor_verification(
        self,
        request: MultiVerificationRequestDTO,
        tenant_id: str
    ) -> FusionVerificationResultDTO:
        """
        多重身份验证（融合验证）
        
        Args:
            request: 多重验证请求
            tenant_id: 租户ID
            
        Returns:
            FusionVerificationResultDTO: 融合验证结果
        """
        try:
            self.logger.info(f"开始多重身份验证: 访客{request.visitor_id}, 门岗{request.gate_id}")
            
            # 获取访客信息
            visitor = await self._get_visitor_info(request.visitor_id, tenant_id)
            if not visitor:
                raise ValidationError(f"访客不存在: {request.visitor_id}")
            
            # 执行各种验证方法
            method_results = []
            
            # 主要验证方法
            primary_result = await self._execute_single_verification(
                request.primary_method, visitor, request, request.gate_id
            )
            method_results.append({
                "method": request.primary_method.value,
                "weight": 0.6,
                "result": primary_result
            })
            
            # 辅助验证方法
            for method in request.secondary_methods:
                secondary_result = await self._execute_single_verification(
                    method, visitor, request, request.gate_id
                )
                method_results.append({
                    "method": method.value,
                    "weight": 0.4 / len(request.secondary_methods),
                    "result": secondary_result
                })
            
            # 融合决策
            fusion_result = await self._fusion_decision_making(
                method_results, request, visitor
            )
            
            # 保存融合验证记录
            await self._save_fusion_verification(fusion_result, tenant_id)
            
            self.logger.info(f"多重验证完成: {request.visitor_id}, 总体状态: {fusion_result.overall_status}")
            return fusion_result
            
        except Exception as e:
            self.logger.error(f"多重身份验证失败: {request.visitor_id}, 错误: {str(e)}")
            raise
    
    # ==================== 访客入园管理 ====================
    
    async def register_visitor_entry(
        self,
        visitor_id: int,
        gate_id: str,
        entry_photo: Optional[Any] = None,
        vehicle_info: Optional[Dict[str, Any]] = None,
        operator: str = "",
        tenant_id: str = ""
    ) -> VisitorEntryDTO:
        """
        访客入园登记
        
        Args:
            visitor_id: 访客ID
            gate_id: 门岗设备ID
            entry_photo: 入园照片
            vehicle_info: 车辆信息
            operator: 操作员
            tenant_id: 租户ID
            
        Returns:
            VisitorEntryDTO: 入园记录
        """
        try:
            self.logger.info(f"访客入园登记: {visitor_id}, 门岗: {gate_id}")
            
            # 验证访客权限
            visitor = await self._get_visitor_info(visitor_id, tenant_id)
            if not visitor or visitor.get("status") != "approved":
                raise ValidationError("访客未获得入园权限")
            
            # 检查是否已经在园区内
            in_park_status = await self._check_visitor_in_park_status(visitor_id, tenant_id)
            if in_park_status:
                raise ValidationError("访客已在园区内，请勿重复入园")
            
            # 处理入园照片
            entry_photo_url = None
            if entry_photo:
                entry_photo_url = await self._process_entry_photo(entry_photo, visitor_id)
            
            # 生成访客证
            badge_info = await self._generate_visitor_badge(visitor, gate_id)
            
            # 创建入园记录
            entry_record = {
                "visitor_id": visitor_id,
                "gate_id": gate_id,
                "entry_time": datetime.now(),
                "entry_photo_url": entry_photo_url,
                "vehicle_info": vehicle_info or {},
                "badge_info": badge_info,
                "operator": operator,
                "tenant_id": tenant_id,
                "status": "entered"
            }
            
            # 保存到数据库
            created_entry = await self.repository.create("visitor_entries", entry_record)
            
            # 更新访客状态为"已入园"
            await self.repository.update(
                "visitors",
                {"id": visitor_id, "tenant_id": tenant_id},
                {"current_status": "in_park", "entry_time": datetime.now()}
            )
            
            # 发送入园通知
            await self._send_entry_notification(visitor, entry_record)
            
            # 清除相关缓存
            await self._clear_visitor_cache(visitor_id, tenant_id)
            
            entry_dto = VisitorEntryDTO(**created_entry)
            self.logger.info(f"访客入园登记成功: {visitor_id}")
            return entry_dto
            
        except Exception as e:
            self.logger.error(f"访客入园登记失败: {visitor_id}, 错误: {str(e)}")
            raise
    
    # ==================== 今日访客缓存 ====================
    
    async def get_today_arrivals(
        self,
        tenant_id: str,
        gate_id: Optional[str] = None
    ) -> List[TodayVisitorsCacheDTO]:
        """
        获取今日预期到访访客
        
        Args:
            tenant_id: 租户ID
            gate_id: 门岗ID（可选）
            
        Returns:
            List[TodayVisitorsCacheDTO]: 今日访客列表
        """
        try:
            # 尝试从缓存获取
            cache_key = f"{self.cache_prefix}:today_arrivals:{tenant_id}:{gate_id or 'all'}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                cached_list = json.loads(cached_data)
                return [TodayVisitorsCacheDTO(**item) for item in cached_list]
            
            # 从数据库查询今日访客
            today = date.today()
            conditions = {
                "tenant_id": tenant_id,
                "visit_date": today,
                "status": "approved"
            }
            
            if gate_id:
                conditions["assigned_gate_id"] = gate_id
            
            visitors = await self.repository.list_by_conditions(
                "visitors",
                conditions,
                order_by="expected_arrival_time"
            )
            
            # 转换为DTO
            today_arrivals = []
            for visitor in visitors:
                arrival_dto = TodayVisitorsCacheDTO(
                    visitor_id=visitor["id"],
                    visitor_name=visitor["name"],
                    visitor_phone=visitor["phone"],
                    company_name=visitor.get("company", ""),
                    employee_name=visitor.get("employee_name", ""),
                    visit_purpose=visitor.get("purpose", ""),
                    expected_arrival_time=visitor.get("expected_arrival_time"),
                    visit_areas=visitor.get("visit_areas", []),
                    special_requirements=visitor.get("special_requirements", []),
                    qr_code_data=visitor.get("qr_code", ""),
                    verification_methods=visitor.get("verification_methods", ["qr_code"]),
                    access_level=GateAccessLevel.STANDARD,
                    cache_timestamp=datetime.now()
                )
                today_arrivals.append(arrival_dto)
            
            # 缓存结果
            cache_data = [arrival.model_dump() for arrival in today_arrivals]
            await self.redis_client.setex(
                cache_key,
                self.visitor_cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
            return today_arrivals
            
        except Exception as e:
            self.logger.error(f"获取今日访客失败: {str(e)}")
            return []
    
    async def generate_offline_cache(
        self,
        tenant_id: str,
        gate_id: str
    ) -> Dict[str, Any]:
        """
        生成门岗离线验证缓存数据
        
        Args:
            tenant_id: 租户ID
            gate_id: 门岗设备ID
            
        Returns:
            Dict: 离线缓存数据
        """
        try:
            self.logger.info(f"生成离线缓存: 租户{tenant_id}, 门岗{gate_id}")
            
            # 获取今日访客数据
            today_visitors = await self.get_today_arrivals(tenant_id, gate_id)
            
            # 获取黑名单数据
            blacklist = await self._get_blacklist_data(tenant_id)
            
            # 获取门岗配置
            gate_config = await self._get_gate_configuration(gate_id, tenant_id)
            
            # 获取验证规则
            verification_rules = await self._get_verification_rules(tenant_id)
            
            # 组装缓存数据
            cache_data = {
                "cache_id": f"offline_{gate_id}_{int(datetime.now().timestamp())}",
                "gate_id": gate_id,
                "tenant_id": tenant_id,
                "generated_at": datetime.now().isoformat(),
                "cache_version": "v1.0",
                "data": {
                    "today_visitors": [visitor.model_dump() for visitor in today_visitors],
                    "blacklist": blacklist,
                    "gate_config": gate_config,
                    "verification_rules": verification_rules,
                    "emergency_contacts": await self._get_emergency_contacts(tenant_id)
                },
                "metadata": {
                    "total_visitors": len(today_visitors),
                    "blacklist_count": len(blacklist),
                    "cache_size_kb": 0,  # 将在后面计算
                    "expiry_time": (datetime.now() + timedelta(hours=24)).isoformat()
                }
            }
            
            # 计算缓存大小
            cache_json = json.dumps(cache_data, default=str)
            cache_data["metadata"]["cache_size_kb"] = len(cache_json.encode('utf-8')) / 1024
            
            # 存储到Redis缓存
            cache_key = f"{self.cache_prefix}:offline_cache:{gate_id}"
            await self.redis_client.setex(
                cache_key,
                self.offline_cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
            self.logger.info(f"离线缓存生成成功: {gate_id}, 大小: {cache_data['metadata']['cache_size_kb']:.2f}KB")
            return cache_data
            
        except Exception as e:
            self.logger.error(f"生成离线缓存失败: {gate_id}, 错误: {str(e)}")
            raise
    
    # ==================== 离线验证同步 ====================
    
    async def sync_offline_verifications(
        self,
        offline_records: List[OfflineVerificationDTO],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        同步离线验证记录
        
        Args:
            offline_records: 离线验证记录列表
            tenant_id: 租户ID
            
        Returns:
            Dict: 同步结果统计
        """
        try:
            self.logger.info(f"开始同步离线验证记录: {len(offline_records)}条")
            
            sync_results = {
                "total_records": len(offline_records),
                "successful_syncs": 0,
                "failed_syncs": 0,
                "duplicate_records": 0,
                "validation_errors": 0,
                "details": []
            }
            
            for record in offline_records:
                try:
                    # 检查记录是否已存在
                    existing_record = await self.repository.get_by_condition(
                        "offline_verifications",
                        {"offline_id": record.offline_id, "tenant_id": tenant_id}
                    )
                    
                    if existing_record:
                        sync_results["duplicate_records"] += 1
                        sync_results["details"].append({
                            "offline_id": record.offline_id,
                            "status": "duplicate",
                            "message": "记录已存在"
                        })
                        continue
                    
                    # 验证记录合法性
                    validation_result = await self._validate_offline_record(record, tenant_id)
                    if not validation_result["valid"]:
                        sync_results["validation_errors"] += 1
                        sync_results["details"].append({
                            "offline_id": record.offline_id,
                            "status": "validation_error",
                            "message": validation_result["error"]
                        })
                        continue
                    
                    # 保存离线记录
                    record_data = {
                        **record.model_dump(),
                        "tenant_id": tenant_id,
                        "sync_time": datetime.now(),
                        "sync_status": "synced"
                    }
                    
                    await self.repository.create("offline_verifications", record_data)
                    
                    # 如果是成功的验证，同步到主验证记录
                    if record.verification_data.get("status") == "success":
                        await self._sync_to_main_verification(record, tenant_id)
                    
                    sync_results["successful_syncs"] += 1
                    sync_results["details"].append({
                        "offline_id": record.offline_id,
                        "status": "success",
                        "message": "同步成功"
                    })
                    
                except Exception as e:
                    sync_results["failed_syncs"] += 1
                    sync_results["details"].append({
                        "offline_id": record.offline_id,
                        "status": "error",
                        "message": str(e)
                    })
                    self.logger.error(f"同步离线记录失败: {record.offline_id}, 错误: {str(e)}")
            
            self.logger.info(f"离线验证同步完成: 成功{sync_results['successful_syncs']}条, 失败{sync_results['failed_syncs']}条")
            return sync_results
            
        except Exception as e:
            self.logger.error(f"离线验证同步失败: {str(e)}")
            raise
    
    # ==================== 应急处理 ====================
    
    async def emergency_open_gates(
        self,
        emergency_data: EmergencyOpenDTO,
        operator: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        紧急开放门禁
        
        Args:
            emergency_data: 紧急开放数据
            operator: 操作员
            tenant_id: 租户ID
            
        Returns:
            Dict: 应急处理结果
        """
        try:
            self.logger.warning(f"执行紧急开放门禁: {emergency_data.emergency_type}, 操作员: {operator}")
            
            # 验证操作员权限
            operator_permissions = await self._check_emergency_permissions(operator, tenant_id)
            if not operator_permissions["authorized"]:
                raise ValidationError("操作员无紧急开放权限")
            
            # 记录紧急操作
            emergency_record = {
                **emergency_data.model_dump(),
                "operator": operator,
                "tenant_id": tenant_id,
                "executed_at": datetime.now(),
                "authorization_level": operator_permissions["level"],
                "approval_required": emergency_data.requires_approval
            }
            
            await self.repository.create("emergency_operations", emergency_record)
            
            # 执行门禁开放
            affected_gates = []
            if emergency_data.gate_ids:
                # 指定门岗
                for gate_id in emergency_data.gate_ids:
                    result = await self._execute_emergency_gate_open(gate_id, emergency_data)
                    affected_gates.append(result)
            else:
                # 全部门岗
                all_gates = await self._get_all_gates(tenant_id)
                for gate in all_gates:
                    result = await self._execute_emergency_gate_open(gate["id"], emergency_data)
                    affected_gates.append(result)
            
            # 发送紧急通知
            await self._send_emergency_notifications(emergency_data, operator, affected_gates, tenant_id)
            
            # 设置自动恢复
            if emergency_data.auto_recovery_minutes > 0:
                await self._schedule_emergency_recovery(
                    emergency_data, affected_gates, emergency_data.auto_recovery_minutes
                )
            
            result = {
                "emergency_id": emergency_record["emergency_id"],
                "affected_gates": affected_gates,
                "operation_time": datetime.now().isoformat(),
                "operator": operator,
                "auto_recovery_scheduled": emergency_data.auto_recovery_minutes > 0,
                "recovery_time": (datetime.now() + timedelta(minutes=emergency_data.auto_recovery_minutes)).isoformat() if emergency_data.auto_recovery_minutes > 0 else None
            }
            
            self.logger.warning(f"紧急开放执行完成: 影响{len(affected_gates)}个门岗")
            return result
            
        except Exception as e:
            self.logger.error(f"紧急开放执行失败: {str(e)}")
            raise
    
    async def report_security_alert(
        self,
        alert_type: str,
        gate_id: str,
        alert_data: Dict[str, Any],
        reporter: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        上报安全告警
        
        Args:
            alert_type: 告警类型
            gate_id: 门岗设备ID
            alert_data: 告警数据
            reporter: 报告人
            tenant_id: 租户ID
            
        Returns:
            Dict: 告警处理结果
        """
        try:
            self.logger.warning(f"收到安全告警: {alert_type}, 门岗: {gate_id}")
            
            # 生成告警ID
            alert_id = f"alert_{gate_id}_{alert_type}_{int(datetime.now().timestamp())}"
            
            # 确定告警级别和处理策略
            alert_config = await self._get_alert_configuration(alert_type, tenant_id)
            
            # 创建告警记录
            alert_record = {
                "alert_id": alert_id,
                "alert_type": alert_type,
                "gate_id": gate_id,
                "alert_data": alert_data,
                "reporter": reporter,
                "tenant_id": tenant_id,
                "alert_level": alert_config["level"],
                "auto_response_enabled": alert_config["auto_response"],
                "created_at": datetime.now(),
                "status": "active"
            }
            
            await self.repository.create("security_alerts", alert_record)
            
            # 执行自动响应
            auto_response_result = None
            if alert_config["auto_response"]:
                auto_response_result = await self._execute_auto_response(alert_record)
            
            # 发送告警通知
            await self._send_alert_notifications(alert_record, tenant_id)
            
            # 如果是严重告警，触发应急流程
            if alert_config["level"] == "critical":
                await self._trigger_emergency_procedures(alert_record, tenant_id)
            
            result = {
                "alert_id": alert_id,
                "alert_level": alert_config["level"],
                "auto_response_executed": auto_response_result is not None,
                "auto_response_result": auto_response_result,
                "notification_sent": True,
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.warning(f"安全告警处理完成: {alert_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"安全告警处理失败: {str(e)}")
            raise
    
    # ==================== 设备状态管理 ====================
    
    async def get_device_status(
        self,
        device_id: str,
        tenant_id: str
    ) -> Optional[GateDeviceStatusDTO]:
        """
        获取门岗设备状态
        
        Args:
            device_id: 设备ID
            tenant_id: 租户ID
            
        Returns:
            Optional[GateDeviceStatusDTO]: 设备状态信息
        """
        try:
            # 从设备服务获取基础状态
            device_status = await self.device_service.get_device_current_status(device_id)
            if not device_status:
                return None
            
            # 获取门岗特定状态
            gate_specific_status = await self._get_gate_specific_status(device_id, tenant_id)
            
            # 组合状态信息
            gate_device_status = GateDeviceStatusDTO(
                device_id=device_id,
                device_status=device_status.operational_status,
                network_status=device_status.network_status,
                last_heartbeat=device_status.status_timestamp,
                current_visitor_count=gate_specific_status.get("current_visitor_count", 0),
                today_verification_count=gate_specific_status.get("today_verification_count", 0),
                success_rate_today=gate_specific_status.get("success_rate_today", 0.0),
                error_count_today=gate_specific_status.get("error_count_today", 0),
                maintenance_status=gate_specific_status.get("maintenance_status", "normal"),
                capabilities=gate_specific_status.get("capabilities", []),
                configuration_version=gate_specific_status.get("configuration_version", "1.0"),
                firmware_version=gate_specific_status.get("firmware_version", "unknown"),
                offline_cache_status=gate_specific_status.get("offline_cache_status", "valid"),
                emergency_mode_active=gate_specific_status.get("emergency_mode_active", False)
            )
            
            return gate_device_status
            
        except Exception as e:
            self.logger.error(f"获取设备状态失败: {device_id}, 错误: {str(e)}")
            return None
    
    async def get_visitors_in_park(
        self,
        tenant_id: str,
        gate_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取园区内访客实时状态
        
        Args:
            tenant_id: 租户ID
            gate_id: 门岗ID（可选）
            
        Returns:
            List[Dict]: 园区内访客列表
        """
        try:
            conditions = {
                "tenant_id": tenant_id,
                "current_status": "in_park"
            }
            
            if gate_id:
                conditions["entry_gate_id"] = gate_id
            
            visitors_in_park = await self.repository.list_by_conditions(
                "visitors",
                conditions,
                order_by="entry_time",
                order_direction="desc"
            )
            
            # 增强访客信息
            enhanced_visitors = []
            for visitor in visitors_in_park:
                enhanced_visitor = {
                    **visitor,
                    "duration_in_park": self._calculate_park_duration(visitor.get("entry_time")),
                    "current_location": await self._get_visitor_current_location(visitor["id"], tenant_id),
                    "access_logs": await self._get_recent_access_logs(visitor["id"], tenant_id)
                }
                enhanced_visitors.append(enhanced_visitor)
            
            return enhanced_visitors
            
        except Exception as e:
            self.logger.error(f"获取园区内访客失败: {str(e)}")
            return []
    
    # ==================== 辅助方法 ====================
    
    async def _check_gate_device_status(self, gate_id: str):
        """检查门岗设备状态"""
        device_info = await self.device_service.get_device_info(gate_id)
        if not device_info:
            raise ConfigurationNotFoundError(f"门岗设备不存在: {gate_id}")
        
        if device_info.status not in ["online", "standby"]:
            raise ValidationError(f"门岗设备状态异常: {device_info.status}")
    
    async def _get_visitor_info(self, visitor_id: int, tenant_id: str) -> Optional[Dict[str, Any]]:
        """获取访客信息"""
        return await self.repository.get_by_condition(
            "visitors",
            {"id": visitor_id, "tenant_id": tenant_id}
        )
    
    async def _pre_verification_checks(
        self, 
        visitor: Dict[str, Any], 
        gate_id: str, 
        tenant_id: str
    ) -> Dict[str, Any]:
        """预验证检查"""
        checks = {"passed": True, "reason": ""}
        
        # 黑名单检查
        if self.blacklist_check_enabled:
            is_blacklisted = await self._check_blacklist(visitor["phone"], tenant_id)
            if is_blacklisted:
                checks = {"passed": False, "reason": "访客在黑名单中"}
                return checks
        
        # 时间窗口检查
        current_time = datetime.now().time()
        visit_start = visitor.get("visit_start_time")
        visit_end = visitor.get("visit_end_time")
        
        if visit_start and visit_end:
            if not (visit_start <= current_time <= visit_end):
                checks = {"passed": False, "reason": "不在访问时间窗口内"}
                return checks
        
        # 访客状态检查
        if visitor.get("status") != "approved":
            checks = {"passed": False, "reason": f"访客状态异常: {visitor.get('status')}"}
            return checks
        
        return checks
    
    def _calculate_park_duration(self, entry_time) -> str:
        """计算在园时长"""
        if not entry_time:
            return "未知"
        
        if isinstance(entry_time, str):
            entry_time = datetime.fromisoformat(entry_time)
        
        duration = datetime.now() - entry_time
        hours = duration.total_seconds() // 3600
        minutes = (duration.total_seconds() % 3600) // 60
        
        return f"{int(hours)}小时{int(minutes)}分钟"
    
    async def _clear_visitor_cache(self, visitor_id: int, tenant_id: str):
        """清除访客相关缓存"""
        cache_keys = [
            f"{self.cache_prefix}:visitor_info:{visitor_id}",
            f"{self.cache_prefix}:today_arrivals:{tenant_id}:*"
        ]
        
        for cache_key in cache_keys:
            if "*" in cache_key:
                # 删除匹配的所有键
                keys = await self.redis_client.keys(cache_key)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                await self.redis_client.delete(cache_key) 