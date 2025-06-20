"""
移动端数据同步核心服务层
负责离线数据同步、增量更新、冲突解决、移动端缓存管理、应急验证等功能
"""
import asyncio
import json
import logging
import hashlib
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, asc

from app.application.dto.mobile_dto import (
    MobileGateSyncDTO, MobileQRVerificationDTO, MobileOfflineSyncDTO as OfflineSyncDTO,
    EmergencyVerificationDTO, MobileDeviceStatusDTO, MobileQuickCheckinDTO as MobileCheckinDTO,
    MobileDeviceType, SyncStatus, NetworkQuality, PhotoQuality, EmergencyType
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


class MobileSyncService:
    """移动端数据同步核心服务"""
    
    def __init__(
        self,
        repository: IRepository,
        redis_client: RedisClient
    ):
        self.repository = repository
        self.redis_client = redis_client
        self.logger = logger
        
        # 缓存配置
        self.cache_prefix = "mobile_sync"
        self.sync_cache_ttl = 3600  # 1小时
        self.offline_data_ttl = 86400  # 24小时
        self.conflict_resolution_ttl = 7200  # 2小时
        
        # 同步配置
        self.max_offline_hours = 24
        self.chunk_size = 100  # 分批同步大小
        self.compression_enabled = True
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        pass
    
    # ==================== 门岗移动端数据同步 ====================
    
    async def sync_gate_mobile_data(
        self,
        device_id: str,
        last_sync: Optional[str] = None,
        tenant_id: str = ""
    ) -> MobileGateSyncDTO:
        """
        门岗移动端数据同步
        
        Args:
            device_id: 移动设备ID
            last_sync: 上次同步时间
            tenant_id: 租户ID
            
        Returns:
            MobileGateSyncDTO: 同步数据包
        """
        try:
            self.logger.info(f"门岗移动端数据同步: 设备{device_id}, 上次同步: {last_sync}")
            
            # 解析上次同步时间
            last_sync_time = None
            if last_sync:
                try:
                    last_sync_time = datetime.fromisoformat(last_sync)
                except ValueError:
                    self.logger.warning(f"无效的同步时间格式: {last_sync}")
            
            if not last_sync_time:
                last_sync_time = datetime.now() - timedelta(days=1)
            
            # 获取设备信息
            device_info = await self._get_mobile_device_info(device_id, tenant_id)
            if not device_info:
                raise ConfigurationNotFoundError(f"移动设备不存在: {device_id}")
            
            # 确定同步日期范围
            sync_date_from = last_sync_time.date()
            sync_date_to = date.today() + timedelta(days=1)  # 包含明天
            
            # 获取增量访客数据
            visitor_data = await self._get_incremental_visitor_data(
                last_sync_time, sync_date_from, sync_date_to, tenant_id
            )
            
            # 获取黑名单更新
            blacklist_data = await self._get_blacklist_updates(last_sync_time, tenant_id)
            
            # 获取门岗配置更新
            gate_config = await self._get_gate_configuration_updates(
                device_info.get("gate_id"), last_sync_time, tenant_id
            )
            
            # 获取验证规则更新
            verification_rules = await self._get_verification_rules_updates(last_sync_time, tenant_id)
            
            # 网络质量评估
            network_quality = await self._assess_network_quality(device_id)
            
            # 组装同步数据
            sync_data = MobileGateSyncDTO(
                sync_id=f"sync_{device_id}_{int(datetime.now().timestamp())}",
                device_id=device_id,
                device_type=MobileDeviceType.MOBILE_TABLET,
                gate_id=device_info.get("gate_id", ""),
                sync_timestamp=datetime.now(),
                last_sync_time=last_sync_time,
                sync_date_from=sync_date_from,
                sync_date_to=sync_date_to,
                today_visitors_count=len(visitor_data["today_visitors"]),
                approved_visitors=visitor_data["approved_visitors"],
                pending_visitors=visitor_data["pending_visitors"],
                blacklist_entries=blacklist_data["entries"],
                blacklist_version=blacklist_data["version"],
                gate_configuration=gate_config,
                verification_rules=verification_rules,
                sync_status=SyncStatus.COMPLETED,
                data_size_kb=0.0,  # 将在后面计算
                compression_ratio=1.0,
                network_quality=network_quality,
                download_speed_kbps=network_quality.value * 100  # 模拟下载速度
            )
            
            # 计算数据大小和压缩
            sync_json = sync_data.model_dump_json()
            original_size = len(sync_json.encode('utf-8'))
            
            if self.compression_enabled:
                compressed_data = await self._compress_sync_data(sync_json)
                compressed_size = len(compressed_data)
                sync_data.compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
                sync_data.data_size_kb = compressed_size / 1024
            else:
                sync_data.data_size_kb = original_size / 1024
            
            # 保存同步记录
            await self._save_sync_record(sync_data, tenant_id)
            
            # 缓存同步数据
            cache_key = f"{self.cache_prefix}:gate_sync:{device_id}"
            await self.redis_client.setex(
                cache_key,
                self.sync_cache_ttl,
                sync_data.model_dump_json()
            )
            
            self.logger.info(f"门岗移动端同步完成: {device_id}, 数据大小: {sync_data.data_size_kb:.2f}KB")
            return sync_data
            
        except Exception as e:
            self.logger.error(f"门岗移动端数据同步失败: {device_id}, 错误: {str(e)}")
            raise
    
    # ==================== 移动端二维码验证 ====================
    
    async def verify_qr_code_mobile(
        self,
        qr_data: str,
        device_id: str,
        gate_id: str,
        operator: str = "",
        tenant_id: str = ""
    ) -> MobileQRVerificationDTO:
        """
        移动端二维码验证
        
        Args:
            qr_data: 二维码数据
            device_id: 移动设备ID
            gate_id: 门岗ID
            operator: 操作员
            tenant_id: 租户ID
            
        Returns:
            MobileQRVerificationDTO: 验证结果
        """
        try:
            self.logger.info(f"移动端二维码验证: 设备{device_id}, 门岗{gate_id}")
            
            # 生成验证ID
            verification_id = f"mobile_qr_{device_id}_{int(datetime.now().timestamp())}"
            
            # 解析二维码数据
            qr_info = await self._parse_qr_code_data(qr_data)
            if not qr_info["valid"]:
                return self._create_failed_qr_verification(
                    verification_id, device_id, gate_id, qr_data, "二维码格式无效", operator
                )
            
            # 查找访客信息
            visitor = await self._find_visitor_by_qr(qr_info["visitor_id"], tenant_id)
            if not visitor:
                return self._create_failed_qr_verification(
                    verification_id, device_id, gate_id, qr_data, "访客不存在", operator
                )
            
            # 执行验证检查
            verification_result = await self._perform_mobile_verification_checks(
                visitor, gate_id, qr_info, tenant_id
            )
            
            # 创建验证记录
            verification_dto = MobileQRVerificationDTO(
                verification_id=verification_id,
                device_id=device_id,
                gate_id=gate_id,
                qr_code_data=qr_data,
                qr_scan_timestamp=datetime.now(),
                qr_image_quality=PhotoQuality.MEDIUM,  # 可以从设备获取
                visitor_id=visitor["id"] if verification_result["success"] else None,
                visitor_name=visitor["name"] if verification_result["success"] else None,
                verification_success=verification_result["success"],
                verification_message=verification_result["message"],
                visitor_phone=visitor.get("phone") if verification_result["success"] else None,
                visit_purpose=visitor.get("purpose") if verification_result["success"] else None,
                employee_name=visitor.get("employee_name") if verification_result["success"] else None,
                access_granted=verification_result["access_granted"],
                access_areas=verification_result.get("access_areas", []),
                access_valid_until=verification_result.get("access_valid_until"),
                blacklist_check_passed=verification_result.get("blacklist_check_passed", True),
                time_window_valid=verification_result.get("time_window_valid", True),
                area_permission_valid=verification_result.get("area_permission_valid", True),
                device_location=await self._get_device_location(device_id),
                network_status=await self._get_device_network_status(device_id),
                operator=operator,
                verification_timestamp=datetime.now(),
                remarks=verification_result.get("remarks")
            )
            
            # 保存验证记录
            await self._save_mobile_verification_record(verification_dto, tenant_id)
            
            # 如果验证成功且在线，同步到主系统
            if verification_result["success"] and await self._is_device_online(device_id):
                await self._sync_verification_to_main_system(verification_dto, tenant_id)
            
            self.logger.info(f"移动端二维码验证完成: {verification_id}, 结果: {verification_result['success']}")
            return verification_dto
            
        except Exception as e:
            self.logger.error(f"移动端二维码验证失败: {device_id}, 错误: {str(e)}")
            raise
    
    # ==================== 离线数据缓存管理 ====================
    
    async def get_mobile_offline_cache(
        self,
        device_type: str,
        device_id: str,
        cache_hours: int = 24,
        tenant_id: str = ""
    ) -> Dict[str, Any]:
        """
        获取移动端离线验证缓存数据
        
        Args:
            device_type: 设备类型
            device_id: 设备ID
            cache_hours: 缓存小时数
            tenant_id: 租户ID
            
        Returns:
            Dict: 离线缓存数据包
        """
        try:
            self.logger.info(f"生成移动端离线缓存: 设备{device_id}, 类型{device_type}, 时长{cache_hours}小时")
            
            # 确定缓存时间范围
            cache_start = datetime.now()
            cache_end = cache_start + timedelta(hours=cache_hours)
            
            # 获取访客数据
            visitor_cache = await self._generate_visitor_offline_cache(
                device_type, device_id, cache_start, cache_end, tenant_id
            )
            
            # 获取验证规则缓存
            rules_cache = await self._generate_rules_offline_cache(tenant_id)
            
            # 获取黑名单缓存
            blacklist_cache = await self._generate_blacklist_offline_cache(tenant_id)
            
            # 获取设备配置缓存
            device_config_cache = await self._generate_device_config_cache(device_id, tenant_id)
            
            # 生成应急联系人信息
            emergency_contacts = await self._get_emergency_contacts_cache(tenant_id)
            
            # 组装离线缓存包
            offline_cache = {
                "cache_id": f"offline_{device_id}_{int(cache_start.timestamp())}",
                "device_id": device_id,
                "device_type": device_type,
                "tenant_id": tenant_id,
                "generated_at": cache_start.isoformat(),
                "expires_at": cache_end.isoformat(),
                "cache_version": "v2.0",
                "data": {
                    "visitors": visitor_cache,
                    "verification_rules": rules_cache,
                    "blacklist": blacklist_cache,
                    "device_config": device_config_cache,
                    "emergency_contacts": emergency_contacts
                },
                "metadata": {
                    "total_visitors": len(visitor_cache),
                    "blacklist_count": len(blacklist_cache),
                    "cache_duration_hours": cache_hours,
                    "last_updated": datetime.now().isoformat(),
                    "cache_size_mb": 0,  # 将在后面计算
                    "sync_strategy": "incremental",
                    "offline_capabilities": [
                        "qr_verification",
                        "visitor_lookup", 
                        "blacklist_check",
                        "emergency_procedures"
                    ]
                }
            }
            
            # 计算缓存大小
            cache_json = json.dumps(offline_cache, default=str)
            offline_cache["metadata"]["cache_size_mb"] = len(cache_json.encode('utf-8')) / (1024 * 1024)
            
            # 存储到Redis
            cache_key = f"{self.cache_prefix}:offline_cache:{device_id}"
            await self.redis_client.setex(
                cache_key,
                self.offline_data_ttl,
                json.dumps(offline_cache, default=str)
            )
            
            self.logger.info(f"移动端离线缓存生成完成: {device_id}, 大小: {offline_cache['metadata']['cache_size_mb']:.2f}MB")
            return offline_cache
            
        except Exception as e:
            self.logger.error(f"生成移动端离线缓存失败: {device_id}, 错误: {str(e)}")
            raise
    
    # ==================== 应急验证处理 ====================
    
    async def process_emergency_verification(
        self,
        emergency_data: EmergencyVerificationDTO,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        处理应急验证
        
        Args:
            emergency_data: 应急验证数据
            tenant_id: 租户ID
            
        Returns:
            Dict: 应急验证处理结果
        """
        try:
            self.logger.warning(f"处理应急验证: {emergency_data.emergency_type}, 设备: {emergency_data.device_id}")
            
            # 验证应急情况合法性
            emergency_validation = await self._validate_emergency_situation(emergency_data, tenant_id)
            if not emergency_validation["valid"]:
                raise ValidationError(f"应急验证无效: {emergency_validation['reason']}")
            
            # 记录应急验证
            emergency_record = {
                **emergency_data.model_dump(),
                "tenant_id": tenant_id,
                "processed_at": datetime.now(),
                "verification_result": "pending",
                "risk_assessment": await self._assess_emergency_risk(emergency_data),
                "auto_approval": await self._check_auto_approval_eligibility(emergency_data, tenant_id)
            }
            
            # 执行风险评估
            risk_assessment = emergency_record["risk_assessment"]
            
            # 根据风险等级决定处理方式
            if risk_assessment["level"] == "low" and emergency_record["auto_approval"]:
                # 低风险自动批准
                approval_result = await self._auto_approve_emergency_verification(emergency_record, tenant_id)
                emergency_record["verification_result"] = "auto_approved"
            elif risk_assessment["level"] in ["medium", "high"]:
                # 中高风险需要人工审批
                approval_result = await self._request_manual_approval(emergency_record, tenant_id)
                emergency_record["verification_result"] = "pending_approval"
            else:
                # 超高风险拒绝
                approval_result = {"approved": False, "reason": "风险等级过高"}
                emergency_record["verification_result"] = "rejected"
            
            # 保存应急记录
            await self.repository.create("emergency_verifications", emergency_record)
            
            # 发送通知
            await self._send_emergency_notifications(emergency_record, tenant_id)
            
            # 如果获得批准，创建临时访问权限
            temporary_access = None
            if approval_result.get("approved"):
                temporary_access = await self._create_temporary_access(emergency_data, tenant_id)
            
            result = {
                "emergency_id": emergency_record["emergency_id"],
                "verification_result": emergency_record["verification_result"],
                "risk_level": risk_assessment["level"],
                "approved": approval_result.get("approved", False),
                "approval_reason": approval_result.get("reason", ""),
                "temporary_access": temporary_access,
                "valid_duration_minutes": emergency_data.access_duration_minutes,
                "restrictions": {
                    "escort_required": emergency_data.escort_required,
                    "restricted_areas": emergency_data.restricted_areas,
                    "monitoring_required": True
                },
                "processed_at": datetime.now().isoformat()
            }
            
            self.logger.warning(f"应急验证处理完成: {emergency_data.emergency_id}, 结果: {result['verification_result']}")
            return result
            
        except Exception as e:
            self.logger.error(f"应急验证处理失败: {emergency_data.emergency_id}, 错误: {str(e)}")
            raise
    
    # ==================== 离线数据同步 ====================
    
    async def sync_offline_data(
        self,
        device_id: str,
        offline_records: List[Dict[str, Any]],
        tenant_id: str
    ) -> OfflineSyncDTO:
        """
        同步离线数据
        
        Args:
            device_id: 设备ID
            offline_records: 离线记录列表
            tenant_id: 租户ID
            
        Returns:
            OfflineSyncDTO: 同步结果
        """
        try:
            self.logger.info(f"开始离线数据同步: 设备{device_id}, 记录数{len(offline_records)}")
            
            sync_results = {
                "successful_syncs": 0,
                "failed_syncs": 0,
                "conflict_resolutions": 0,
                "skipped_records": 0,
                "details": []
            }
            
            for record in offline_records:
                try:
                    # 检查记录完整性
                    if not await self._validate_offline_record(record):
                        sync_results["skipped_records"] += 1
                        continue
                    
                    # 检查是否存在冲突
                    conflict_check = await self._check_data_conflicts(record, tenant_id)
                    
                    if conflict_check["has_conflict"]:
                        # 执行冲突解决
                        resolution_result = await self._resolve_data_conflict(
                            record, conflict_check["conflict_data"], tenant_id
                        )
                        
                        if resolution_result["resolved"]:
                            sync_results["conflict_resolutions"] += 1
                            await self._apply_resolved_record(resolution_result["resolved_record"], tenant_id)
                            sync_results["successful_syncs"] += 1
                        else:
                            sync_results["failed_syncs"] += 1
                    else:
                        # 直接同步记录
                        await self._sync_single_record(record, tenant_id)
                        sync_results["successful_syncs"] += 1
                    
                except Exception as e:
                    sync_results["failed_syncs"] += 1
                    sync_results["details"].append({
                        "record_id": record.get("id", "unknown"),
                        "error": str(e)
                    })
            
            # 创建同步DTO
            sync_dto = OfflineSyncDTO(
                sync_id=f"offline_sync_{device_id}_{int(datetime.now().timestamp())}",
                device_id=device_id,
                sync_timestamp=datetime.now(),
                offline_duration_hours=self._calculate_offline_duration(device_id),
                total_records=len(offline_records),
                successful_syncs=sync_results["successful_syncs"],
                failed_syncs=sync_results["failed_syncs"],
                conflict_resolutions=sync_results["conflict_resolutions"],
                data_integrity_check=await self._verify_data_integrity(device_id, tenant_id),
                sync_strategy="merge_priority",
                last_successful_sync=await self._get_last_successful_sync(device_id, tenant_id),
                network_conditions=await self._get_current_network_conditions(device_id),
                compression_used=self.compression_enabled,
                sync_status=SyncStatus.COMPLETED if sync_results["failed_syncs"] == 0 else SyncStatus.PARTIAL_FAILURE
            )
            
            # 保存同步记录
            await self._save_offline_sync_record(sync_dto, tenant_id)
            
            self.logger.info(f"离线数据同步完成: 设备{device_id}, 成功{sync_results['successful_syncs']}条")
            return sync_dto
            
        except Exception as e:
            self.logger.error(f"离线数据同步失败: {device_id}, 错误: {str(e)}")
            raise
    
    # ==================== 辅助方法 ====================
    
    async def _get_mobile_device_info(self, device_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """获取移动设备信息"""
        return await self.repository.get_by_condition(
            "mobile_devices",
            {"device_id": device_id, "tenant_id": tenant_id}
        )
    
    async def _assess_network_quality(self, device_id: str) -> NetworkQuality:
        """评估网络质量"""
        # 这里可以集成真实的网络质量检测
        # 现在返回模拟值
        return NetworkQuality.GOOD
    
    async def _compress_sync_data(self, data: str) -> bytes:
        """压缩同步数据"""
        # 这里可以使用gzip或其他压缩算法
        # 现在返回模拟压缩结果
        return data.encode('utf-8')
    
    def _calculate_offline_duration(self, device_id: str) -> float:
        """计算离线时长"""
        # 这里应该从设备状态记录计算实际离线时长
        # 现在返回模拟值
        return 2.5  # 2.5小时
    
    async def _validate_offline_record(self, record: Dict[str, Any]) -> bool:
        """验证离线记录"""
        required_fields = ["id", "timestamp", "type", "data"]
        return all(field in record for field in required_fields) 