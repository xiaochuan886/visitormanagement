"""
设备管理核心服务层
负责设备生命周期管理、状态监控、配置管理等核心功能
"""
import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.application.dto.device_dto import (
    DeviceInfoDTO, DeviceStatusDTO, DeviceMaintenanceDTO,
    DeviceConfigurationDTO, DeviceAlertDTO, DeviceUsageStatisticsDTO,
    DeviceOperationRequestDTO, DeviceOperationResponseDTO, DeviceBatchOperationDTO,
    DeviceType, DeviceStatus, ConnectionType, MaintenanceType, DeviceCapability
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


class DeviceService:
    """设备管理核心服务"""
    
    def __init__(
        self,
        repository: IRepository,
        redis_client: RedisClient
    ):
        self.repository = repository
        self.redis_client = redis_client
        self.logger = logger
        
        # 缓存键前缀
        self.cache_prefix = "device_mgmt"
        self.device_cache_ttl = 3600  # 1小时
        self.status_cache_ttl = 300   # 5分钟
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        pass
    
    # ==================== 设备注册和生命周期管理 ====================
    
    async def register_device(
        self,
        device_info: DeviceInfoDTO,
        site_id: int,
        operator: str
    ) -> DeviceInfoDTO:
        """
        注册新设备
        
        Args:
            device_info: 设备信息
            site_id: 站点ID  
            operator: 操作人员
            
        Returns:
            DeviceInfoDTO: 注册后的设备信息
            
        Raises:
            ValidationError: 设备信息验证失败
            ConfigurationConflictError: 设备ID或序列号重复
        """
        try:
            self.logger.info(f"开始注册设备: {device_info.device_name}, 操作人: {operator}")
            
            # 验证设备信息
            await self._validate_device_info(device_info, site_id)
            
            # 检查设备ID和序列号唯一性
            await self._check_device_uniqueness(device_info.device_id, device_info.serial_number)
            
            # 创建设备记录
            device_data = {
                **device_info.model_dump(),
                "site_id": site_id,
                "created_by": operator,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 保存到数据库
            created_device = await self.repository.create("devices", device_data)
            
            # 创建初始状态记录
            initial_status = DeviceStatusDTO(
                device_id=device_info.device_id,
                operational_status=DeviceStatus.OFFLINE,
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                storage_usage_percent=0.0,
                network_status="disconnected",
                response_time_ms=0.0,
                throughput_per_minute=0.0,
                success_rate_percent=0.0,
                reported_by=operator
            )
            
            await self._create_device_status(initial_status)
            
            # 清除相关缓存
            await self._clear_device_cache(device_info.device_id)
            
            self.logger.info(f"设备注册成功: {device_info.device_id}")
            return DeviceInfoDTO(**created_device)
            
        except Exception as e:
            self.logger.error(f"设备注册失败: {str(e)}")
            raise
    
    async def get_device_info(self, device_id: str) -> Optional[DeviceInfoDTO]:
        """
        获取设备信息
        
        Args:
            device_id: 设备ID
            
        Returns:
            Optional[DeviceInfoDTO]: 设备信息，不存在返回None
        """
        try:
            # 尝试从缓存获取
            cache_key = f"{self.cache_prefix}:device_info:{device_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return DeviceInfoDTO.model_validate_json(cached_data)
            
            # 从数据库查询
            device_data = await self.repository.get_by_condition(
                "devices",
                {"device_id": device_id}
            )
            
            if not device_data:
                return None
            
            device_info = DeviceInfoDTO(**device_data)
            
            # 缓存结果
            await self.redis_client.setex(
                cache_key,
                self.device_cache_ttl,
                device_info.model_dump_json()
            )
            
            return device_info
            
        except Exception as e:
            self.logger.error(f"获取设备信息失败: {device_id}, 错误: {str(e)}")
            raise
    
    async def list_devices(
        self,
        site_id: Optional[int] = None,
        device_type: Optional[DeviceType] = None,
        status: Optional[DeviceStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取设备列表
        
        Args:
            site_id: 站点ID筛选
            device_type: 设备类型筛选
            status: 设备状态筛选
            page: 页码
            page_size: 每页大小
            
        Returns:
            Dict: 包含设备列表和分页信息
        """
        try:
            # 构建查询条件
            conditions = {}
            if site_id:
                conditions["site_id"] = site_id
            if device_type:
                conditions["device_type"] = device_type.value
            if status:
                conditions["status"] = status.value
            
            # 查询设备列表
            devices_data = await self.repository.list_with_pagination(
                "devices",
                conditions=conditions,
                page=page,
                page_size=page_size,
                order_by="created_at",
                order_direction="desc"
            )
            
            devices = [DeviceInfoDTO(**device) for device in devices_data["items"]]
            
            # 获取设备状态信息
            for device in devices:
                device_status = await self.get_device_current_status(device.device_id)
                if device_status:
                    device.status = device_status.operational_status
                    device.last_seen = device_status.status_timestamp
            
            return {
                "devices": devices,
                "total": devices_data["total"],
                "page": page,
                "page_size": page_size,
                "pages": devices_data["pages"]
            }
            
        except Exception as e:
            self.logger.error(f"获取设备列表失败: {str(e)}")
            raise
    
    async def update_device_info(
        self,
        device_id: str,
        updates: Dict[str, Any],
        operator: str
    ) -> DeviceInfoDTO:
        """
        更新设备信息
        
        Args:
            device_id: 设备ID
            updates: 更新数据
            operator: 操作人员
            
        Returns:
            DeviceInfoDTO: 更新后的设备信息
            
        Raises:
            ConfigurationNotFoundError: 设备不存在
        """
        try:
            self.logger.info(f"更新设备信息: {device_id}, 操作人: {operator}")
            
            # 检查设备是否存在
            existing_device = await self.get_device_info(device_id)
            if not existing_device:
                raise ConfigurationNotFoundError(f"设备不存在: {device_id}")
            
            # 准备更新数据
            update_data = {
                **updates,
                "updated_at": datetime.now(),
                "updated_by": operator
            }
            
            # 更新数据库
            updated_device = await self.repository.update(
                "devices",
                {"device_id": device_id},
                update_data
            )
            
            # 清除缓存
            await self._clear_device_cache(device_id)
            
            self.logger.info(f"设备信息更新成功: {device_id}")
            return DeviceInfoDTO(**updated_device)
            
        except Exception as e:
            self.logger.error(f"设备信息更新失败: {device_id}, 错误: {str(e)}")
            raise
    
    async def deactivate_device(
        self,
        device_id: str,
        reason: str,
        operator: str
    ) -> bool:
        """
        停用设备
        
        Args:
            device_id: 设备ID
            reason: 停用原因
            operator: 操作人员
            
        Returns:
            bool: 是否成功停用
        """
        try:
            self.logger.info(f"停用设备: {device_id}, 原因: {reason}, 操作人: {operator}")
            
            # 更新设备状态为禁用
            await self.update_device_info(
                device_id,
                {
                    "status": DeviceStatus.DISABLED.value,
                    "notes": f"停用原因: {reason}"
                },
                operator
            )
            
            # 记录设备状态变更
            status_update = DeviceStatusDTO(
                device_id=device_id,
                operational_status=DeviceStatus.DISABLED,
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                storage_usage_percent=0.0,
                network_status="disconnected",
                response_time_ms=0.0,
                throughput_per_minute=0.0,
                success_rate_percent=0.0,
                reported_by=operator
            )
            
            await self._create_device_status(status_update)
            
            self.logger.info(f"设备停用成功: {device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"设备停用失败: {device_id}, 错误: {str(e)}")
            return False
    
    # ==================== 设备状态监控 ====================
    
    async def update_device_status(
        self,
        status_data: DeviceStatusDTO
    ) -> bool:
        """
        更新设备状态
        
        Args:
            status_data: 设备状态数据
            
        Returns:
            bool: 是否更新成功
        """
        try:
            self.logger.debug(f"更新设备状态: {status_data.device_id}")
            
            # 保存状态记录
            await self._create_device_status(status_data)
            
            # 更新设备基础信息中的状态和最后在线时间
            await self.update_device_info(
                status_data.device_id,
                {
                    "status": status_data.operational_status.value,
                    "last_seen": status_data.status_timestamp
                },
                status_data.reported_by
            )
            
            # 检查告警条件
            await self._check_alert_conditions(status_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"更新设备状态失败: {status_data.device_id}, 错误: {str(e)}")
            return False
    
    async def get_device_current_status(self, device_id: str) -> Optional[DeviceStatusDTO]:
        """
        获取设备当前状态
        
        Args:
            device_id: 设备ID
            
        Returns:
            Optional[DeviceStatusDTO]: 设备当前状态
        """
        try:
            # 尝试从缓存获取
            cache_key = f"{self.cache_prefix}:device_status:{device_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                return DeviceStatusDTO.model_validate_json(cached_data)
            
            # 从数据库查询最新状态
            status_data = await self.repository.get_by_condition(
                "device_status",
                {"device_id": device_id},
                order_by="status_timestamp",
                order_direction="desc"
            )
            
            if not status_data:
                return None
            
            status_dto = DeviceStatusDTO(**status_data)
            
            # 缓存结果
            await self.redis_client.setex(
                cache_key,
                self.status_cache_ttl,
                status_dto.model_dump_json()
            )
            
            return status_dto
            
        except Exception as e:
            self.logger.error(f"获取设备状态失败: {device_id}, 错误: {str(e)}")
            return None
    
    async def get_device_status_history(
        self,
        device_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[DeviceStatusDTO]:
        """
        获取设备状态历史
        
        Args:
            device_id: 设备ID
            start_date: 开始时间
            end_date: 结束时间
            
        Returns:
            List[DeviceStatusDTO]: 状态历史列表
        """
        try:
            conditions = {
                "device_id": device_id,
                "status_timestamp": {">=": start_date, "<=": end_date}
            }
            
            status_records = await self.repository.list_by_conditions(
                "device_status",
                conditions,
                order_by="status_timestamp",
                order_direction="asc"
            )
            
            return [DeviceStatusDTO(**record) for record in status_records]
            
        except Exception as e:
            self.logger.error(f"获取设备状态历史失败: {device_id}, 错误: {str(e)}")
            return []
    
    # ==================== 设备配置管理 ====================
    
    async def deploy_device_configuration(
        self,
        config_data: DeviceConfigurationDTO,
        operator: str
    ) -> bool:
        """
        部署设备配置
        
        Args:
            config_data: 配置数据
            operator: 操作人员
            
        Returns:
            bool: 是否部署成功
        """
        try:
            self.logger.info(f"部署设备配置: {config_data.device_id}, 配置: {config_data.configuration_name}")
            
            # 验证配置数据
            await self._validate_device_configuration(config_data)
            
            # 保存配置记录
            config_record = {
                **config_data.model_dump(),
                "deployed_by": operator,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            await self.repository.create("device_configurations", config_record)
            
            # 更新设备配置状态
            await self.update_device_info(
                config_data.device_id,
                {
                    "configuration": config_data.model_dump(),
                    "updated_by": operator
                },
                operator
            )
            
            self.logger.info(f"设备配置部署成功: {config_data.device_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"设备配置部署失败: {config_data.device_id}, 错误: {str(e)}")
            return False
    
    async def get_device_configuration_history(
        self,
        device_id: str
    ) -> List[DeviceConfigurationDTO]:
        """
        获取设备配置历史
        
        Args:
            device_id: 设备ID
            
        Returns:
            List[DeviceConfigurationDTO]: 配置历史列表
        """
        try:
            config_records = await self.repository.list_by_conditions(
                "device_configurations",
                {"device_id": device_id},
                order_by="created_at",
                order_direction="desc"
            )
            
            return [DeviceConfigurationDTO(**record) for record in config_records]
            
        except Exception as e:
            self.logger.error(f"获取设备配置历史失败: {device_id}, 错误: {str(e)}")
            return []
    
    # ==================== 辅助方法 ====================
    
    async def _validate_device_info(self, device_info: DeviceInfoDTO, site_id: int):
        """验证设备信息"""
        # 检查站点是否存在
        site = await self.repository.get_by_id("sites", site_id)
        if not site:
            raise ValidationError(f"站点不存在: {site_id}")
        
        # 验证设备类型和能力匹配
        if not device_info.capabilities:
            raise ValidationError("设备能力不能为空")
    
    async def _check_device_uniqueness(self, device_id: str, serial_number: str):
        """检查设备唯一性"""
        # 检查设备ID
        existing_device = await self.repository.get_by_condition(
            "devices",
            {"device_id": device_id}
        )
        if existing_device:
            raise ConfigurationConflictError(f"设备ID已存在: {device_id}")
        
        # 检查序列号
        existing_serial = await self.repository.get_by_condition(
            "devices",
            {"serial_number": serial_number}
        )
        if existing_serial:
            raise ConfigurationConflictError(f"序列号已存在: {serial_number}")
    
    async def _create_device_status(self, status_data: DeviceStatusDTO):
        """创建设备状态记录"""
        status_record = {
            **status_data.model_dump(),
            "created_at": datetime.now()
        }
        
        await self.repository.create("device_status", status_record)
        
        # 更新缓存
        cache_key = f"{self.cache_prefix}:device_status:{status_data.device_id}"
        await self.redis_client.setex(
            cache_key,
            self.status_cache_ttl,
            status_data.model_dump_json()
        )
    
    async def _validate_device_configuration(self, config_data: DeviceConfigurationDTO):
        """验证设备配置"""
        # 检查设备是否存在
        device = await self.get_device_info(config_data.device_id)
        if not device:
            raise ConfigurationNotFoundError(f"设备不存在: {config_data.device_id}")
        
        # 验证配置格式（可扩展具体验证规则）
        if not config_data.configuration_name:
            raise ValidationError("配置名称不能为空")
    
    async def _check_alert_conditions(self, status_data: DeviceStatusDTO):
        """检查告警条件"""
        alerts = []
        
        # CPU使用率告警
        if status_data.cpu_usage_percent > 90:
            alerts.append({
                "alert_type": "warning",
                "alert_code": "HIGH_CPU_USAGE",
                "title": "CPU使用率过高",
                "message": f"CPU使用率达到 {status_data.cpu_usage_percent}%",
                "severity": "high"
            })
        
        # 内存使用率告警
        if status_data.memory_usage_percent > 90:
            alerts.append({
                "alert_type": "warning", 
                "alert_code": "HIGH_MEMORY_USAGE",
                "title": "内存使用率过高",
                "message": f"内存使用率达到 {status_data.memory_usage_percent}%",
                "severity": "high"
            })
        
        # 网络连接告警
        if status_data.network_status == "disconnected":
            alerts.append({
                "alert_type": "error",
                "alert_code": "NETWORK_DISCONNECTED", 
                "title": "网络连接断开",
                "message": "设备网络连接已断开",
                "severity": "critical"
            })
        
        # 创建告警记录
        for alert_info in alerts:
            alert_dto = DeviceAlertDTO(
                alert_id=f"alert_{status_data.device_id}_{alert_info['alert_code']}_{int(datetime.now().timestamp())}",
                device_id=status_data.device_id,
                **alert_info,
                alert_source="device_monitor",
                alert_status="active",
                impact_level="minor",
                priority=8 if alert_info["severity"] == "critical" else 5
            )
            
            await self._create_device_alert(alert_dto)
    
    async def _create_device_alert(self, alert_data: DeviceAlertDTO):
        """创建设备告警"""
        alert_record = {
            **alert_data.model_dump(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        await self.repository.create("device_alerts", alert_record)
        
        self.logger.warning(f"设备告警: {alert_data.device_id} - {alert_data.title}")
    
    async def _clear_device_cache(self, device_id: str):
        """清除设备相关缓存"""
        cache_keys = [
            f"{self.cache_prefix}:device_info:{device_id}",
            f"{self.cache_prefix}:device_status:{device_id}"
        ]
        
        for cache_key in cache_keys:
            await self.redis_client.delete(cache_key) 