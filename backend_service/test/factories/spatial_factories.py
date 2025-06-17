"""
空间配置测试数据工厂

提供空间层次结构、空间实体的测试数据生成。
"""

import factory
from factory import LazyAttribute, LazyFunction, Sequence
from datetime import datetime
import uuid
import json

from app.infrastructure.database.models import (
    SpatialConfigurationModel as SpatialConfiguration,
)
from app.domain.enums.spatial_enums import (
    SpatialType,
    AccessControlType,
    OperatingStatus,
    AccessLevelType,
    TimeRestrictionType,
    SecurityLevel,
)
from app.domain.enums.config_enums import (
    ConfigurationStatus,
)


class SpatialHierarchyFactory(factory.Factory):
    """空间层次结构测试数据工厂"""
    
    class Meta:
        model = SpatialConfiguration
    
    # 基础字段
    id = LazyFunction(lambda: str(uuid.uuid4()))
    tenant_id = "test-tenant"
    name = LazyAttribute(lambda obj: f"test_spatial_{obj.id[:8]}")
    description = "这是一个测试空间配置"
    
    # 空间配置
    spatial_type = SpatialType.BUILDING
    access_control_type = AccessControlType.RESTRICTED
    operating_status = OperatingStatus.OPERATIONAL
    status = ConfigurationStatus.ACTIVE
    
    # 空间层次配置
    hierarchy_config = LazyFunction(lambda: {
        "levels": [
            {
                "level": 1,
                "type": "site",
                "name_pattern": "园区{number}",
                "capacity": 1000
            },
            {
                "level": 2,
                "type": "building",
                "name_pattern": "建筑{letter}",
                "capacity": 200
            },
            {
                "level": 3,
                "type": "floor",
                "name_pattern": "{number}楼",
                "capacity": 50
            },
            {
                "level": 4,
                "type": "room",
                "name_pattern": "房间{number}",
                "capacity": 10
            }
        ],
        "max_depth": 4,
        "auto_numbering": True
    })
    
    # 访问控制配置
    access_control_config = LazyFunction(lambda: {
        "default_access_level": "level_1",
        "time_restrictions": {
            "business_hours": {
                "start": "08:00",
                "end": "18:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            },
            "weekend_hours": {
                "start": "09:00",
                "end": "17:00",
                "days": ["saturday", "sunday"]
            }
        },
        "access_rules": [
            {
                "role": "employee",
                "areas": ["all"],
                "restrictions": ["business_hours"]
            },
            {
                "role": "visitor",
                "areas": ["public", "meeting_rooms"],
                "restrictions": ["business_hours", "escort_required"]
            }
        ]
    })
    
    # 空间属性配置
    spatial_properties = LazyFunction(lambda: {
        "coordinate_system": "building_local",
        "measurement_unit": "meters",
        "floor_height": 3.5,
        "security_zones": [
            {
                "zone_id": "public",
                "security_level": "public",
                "areas": ["lobby", "reception", "cafe"]
            },
            {
                "zone_id": "restricted",
                "security_level": "internal",
                "areas": ["offices", "meeting_rooms"]
            },
            {
                "zone_id": "secure",
                "security_level": "confidential",
                "areas": ["server_room", "executive_floor"]
            }
        ]
    })
    
    # 设备集成配置
    device_integration = LazyFunction(lambda: {
        "supported_devices": [
            "access_card_reader",
            "biometric_scanner",
            "camera",
            "motion_sensor"
        ],
        "device_placement_rules": {
            "entrance": ["access_card_reader", "camera"],
            "restricted_area": ["biometric_scanner", "motion_sensor"],
            "emergency_exit": ["motion_sensor", "camera"]
        },
        "integration_protocols": ["TCP/IP", "RS485", "Wiegand"]
    })
    
    # 时间字段
    created_at = LazyFunction(datetime.now)
    updated_at = LazyFunction(datetime.now)
    created_by = "test_user"
    updated_by = "test_user"
    
    @classmethod
    def create_office_building_hierarchy(cls, tenant_id="test-tenant"):
        """创建办公楼空间层次结构"""
        return cls(
            tenant_id=tenant_id,
            name="office_building_hierarchy",
            description="标准办公楼空间层次结构",
            spatial_type=SpatialType.BUILDING,
            access_control_type=AccessControlType.RESTRICTED,
            hierarchy_config={
                "levels": [
                    {
                        "level": 1,
                        "type": "building",
                        "name_pattern": "办公楼{letter}",
                        "capacity": 500,
                        "attributes": {
                            "total_floors": 20,
                            "elevator_count": 4,
                            "staircase_count": 2
                        }
                    },
                    {
                        "level": 2,
                        "type": "floor",
                        "name_pattern": "{number}楼",
                        "capacity": 50,
                        "attributes": {
                            "floor_area": 800,
                            "ceiling_height": 3.5,
                            "fire_exits": 2
                        }
                    },
                    {
                        "level": 3,
                        "type": "zone",
                        "name_pattern": "{floor_number}-{zone_letter}区",
                        "capacity": 20,
                        "attributes": {
                            "zone_type": "office_area",
                            "workstation_count": 20,
                            "meeting_rooms": 2
                        }
                    },
                    {
                        "level": 4,
                        "type": "room",
                        "name_pattern": "房间{number}",
                        "capacity": 8,
                        "attributes": {
                            "room_area": 25,
                            "window_count": 1,
                            "power_outlets": 6
                        }
                    }
                ],
                "naming_rules": {
                    "building_letters": ["A", "B", "C", "D"],
                    "floor_range": [1, 20],
                    "zone_letters": ["A", "B", "C", "D"],
                    "room_numbering": "sequential"
                }
            },
            access_control_config={
                "default_access_level": "level_2",
                "time_restrictions": {
                    "business_hours": {
                        "start": "07:00",
                        "end": "19:00",
                        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                    },
                    "maintenance_hours": {
                        "start": "19:00", 
                        "end": "07:00",
                        "days": ["all"],
                        "access_roles": ["maintenance", "security"]
                    }
                },
                "security_zones": [
                    {
                        "floors": [1, 2],
                        "access_level": "level_1",
                        "description": "公共区域和接待区"
                    },
                    {
                        "floors": [3, 18],
                        "access_level": "level_2", 
                        "description": "办公区域"
                    },
                    {
                        "floors": [19, 20],
                        "access_level": "level_3",
                        "description": "高管区域"
                    }
                ]
            }
        )
    
    @classmethod
    def create_industrial_facility_hierarchy(cls, tenant_id="test-tenant"):
        """创建工业设施空间层次结构"""
        return cls(
            tenant_id=tenant_id,
            name="industrial_facility_hierarchy",
            description="工业设施空间层次结构",
            spatial_type=SpatialType.SITE,
            access_control_type=AccessControlType.PRIVATE,
            hierarchy_config={
                "levels": [
                    {
                        "level": 1,
                        "type": "site",
                        "name_pattern": "厂区{number}",
                        "capacity": 2000,
                        "attributes": {
                            "site_area": 50000,
                            "security_perimeter": True,
                            "emergency_services": ["fire", "medical", "security"]
                        }
                    },
                    {
                        "level": 2,
                        "type": "zone",
                        "name_pattern": "生产区{letter}",
                        "capacity": 200,
                        "attributes": {
                            "hazard_level": "medium",
                            "ppe_required": True,
                            "environmental_monitoring": True
                        }
                    },
                    {
                        "level": 3,
                        "type": "area",
                        "name_pattern": "作业区{number}",
                        "capacity": 50,
                        "attributes": {
                            "equipment_density": "high",
                            "noise_level": "high",
                            "safety_equipment": ["eyewash", "shower", "extinguisher"]
                        }
                    },
                    {
                        "level": 4,
                        "type": "workstation",
                        "name_pattern": "工位{number}",
                        "capacity": 5,
                        "attributes": {
                            "machinery_type": "cnc",
                            "safety_interlocks": True,
                            "monitoring_sensors": ["vibration", "temperature", "pressure"]
                        }
                    }
                ],
                "safety_protocols": {
                    "mandatory_training": ["safety_basics", "hazmat", "emergency_procedures"],
                    "certification_required": ["crane_operation", "confined_space"],
                    "escort_requirements": {
                        "visitors": "always",
                        "contractors": "hazardous_areas_only",
                        "employees": "none"
                    }
                }
            }
        )

# 技术债务说明：
# 1. 枚举SpatialStatus不存在，使用OperatingStatus替代
# 2. EntityType枚举不存在，使用SpatialType替代  
# 3. SpatialEntityFactory已移除，模型关系需要简化
# 4. 某些字段名可能与实际数据库模型不完全匹配 