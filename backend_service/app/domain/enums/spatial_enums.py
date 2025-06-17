"""
空间管理相关枚举定义
定义空间管理系统中使用的各种枚举类型
"""
from enum import Enum


class SpatialType(str, Enum):
    """空间实体类型枚举"""
    SITE = "site"                    # 站点/园区
    BUILDING = "building"            # 建筑/楼栋
    FLOOR = "floor"                  # 楼层
    ZONE = "zone"                    # 区域/分区
    ROOM = "room"                    # 房间
    AREA = "area"                    # 功能区域
    WORKSTATION = "workstation"      # 工位
    PARKING = "parking"              # 停车位
    CORRIDOR = "corridor"            # 走廊
    ENTRANCE = "entrance"            # 入口
    EXIT = "exit"                    # 出口
    ELEVATOR = "elevator"            # 电梯
    STAIRCASE = "staircase"         # 楼梯


class AccessControlType(str, Enum):
    """访问控制类型枚举"""
    PUBLIC = "public"                # 公共区域（无限制）
    RESTRICTED = "restricted"        # 受限区域（需要权限）
    PRIVATE = "private"              # 私人区域（严格限制）
    EMERGENCY_ONLY = "emergency_only"  # 仅应急访问
    MAINTENANCE_ONLY = "maintenance_only"  # 仅维护访问
    VIP_ONLY = "vip_only"           # 仅VIP访问
    EMPLOYEE_ONLY = "employee_only"  # 仅员工访问
    VISITOR_ALLOWED = "visitor_allowed"  # 允许访客
    ESCORT_REQUIRED = "escort_required"  # 需要陪同


class DeviceType(str, Enum):
    """设备类型枚举"""
    ACCESS_CARD_READER = "access_card_reader"    # 门禁读卡器
    BIOMETRIC_SCANNER = "biometric_scanner"      # 生物识别扫描器
    CAMERA = "camera"                            # 摄像头
    MOTION_SENSOR = "motion_sensor"              # 运动传感器
    TEMPERATURE_SENSOR = "temperature_sensor"    # 温度传感器
    SMOKE_DETECTOR = "smoke_detector"            # 烟雾探测器
    ALARM = "alarm"                              # 报警器
    ELECTRONIC_LOCK = "electronic_lock"          # 电子锁
    TURNSTILE = "turnstile"                     # 旋转门/闸机
    ELEVATOR_CONTROLLER = "elevator_controller"  # 电梯控制器
    LIGHTING_CONTROLLER = "lighting_controller"  # 照明控制器
    HVAC_CONTROLLER = "hvac_controller"         # 空调控制器


class LocationDataType(str, Enum):
    """位置数据类型枚举"""
    GPS_COORDINATES = "gps_coordinates"          # GPS坐标
    BUILDING_COORDINATES = "building_coordinates"  # 建筑内坐标
    FLOOR_PLAN_POSITION = "floor_plan_position"  # 平面图位置
    RELATIVE_POSITION = "relative_position"      # 相对位置
    QR_CODE_LOCATION = "qr_code_location"       # 二维码位置标识
    BEACON_POSITION = "beacon_position"          # 信标位置


class SpatialCapabilityType(str, Enum):
    """空间能力类型枚举"""
    CAPACITY_MANAGEMENT = "capacity_management"    # 容量管理
    ACCESS_CONTROL = "access_control"             # 访问控制
    ENVIRONMENTAL_MONITORING = "environmental_monitoring"  # 环境监控
    EMERGENCY_MANAGEMENT = "emergency_management"  # 应急管理
    ASSET_TRACKING = "asset_tracking"             # 资产跟踪
    VISITOR_GUIDANCE = "visitor_guidance"         # 访客引导
    ENERGY_MANAGEMENT = "energy_management"       # 能源管理
    SECURITY_SURVEILLANCE = "security_surveillance"  # 安全监控


class OperatingStatus(str, Enum):
    """运营状态枚举"""
    OPERATIONAL = "operational"      # 正常运营
    MAINTENANCE = "maintenance"      # 维护中
    CLOSED = "closed"               # 关闭
    EMERGENCY = "emergency"         # 应急状态
    RESTRICTED = "restricted"       # 受限状态
    RESERVED = "reserved"           # 预留状态
    OUT_OF_SERVICE = "out_of_service"  # 停止服务


class AccessLevelType(str, Enum):
    """访问级别类型枚举"""
    LEVEL_0 = "level_0"             # 公共级别
    LEVEL_1 = "level_1"             # 基础级别
    LEVEL_2 = "level_2"             # 标准级别
    LEVEL_3 = "level_3"             # 高级级别
    LEVEL_4 = "level_4"             # 机密级别
    LEVEL_5 = "level_5"             # 绝密级别


class TimeRestrictionType(str, Enum):
    """时间限制类型枚举"""
    NO_RESTRICTION = "no_restriction"        # 无时间限制
    BUSINESS_HOURS = "business_hours"        # 营业时间
    SPECIFIC_HOURS = "specific_hours"        # 特定时间段
    APPOINTMENT_ONLY = "appointment_only"    # 仅预约时间
    EMERGENCY_ONLY = "emergency_only"        # 仅应急时间
    WEEKEND_ONLY = "weekend_only"           # 仅周末
    WEEKDAY_ONLY = "weekday_only"           # 仅工作日


class PathfindingAlgorithm(str, Enum):
    """路径规划算法枚举"""
    SHORTEST_PATH = "shortest_path"          # 最短路径
    FASTEST_PATH = "fastest_path"           # 最快路径
    ACCESSIBLE_PATH = "accessible_path"      # 无障碍路径
    SECURE_PATH = "secure_path"             # 安全路径
    ENERGY_EFFICIENT = "energy_efficient"   # 节能路径
    EMERGENCY_EXIT = "emergency_exit"        # 应急疏散路径


class SpatialRelationType(str, Enum):
    """空间关系类型枚举"""
    PARENT_CHILD = "parent_child"           # 父子关系
    ADJACENT = "adjacent"                   # 相邻关系
    CONNECTED = "connected"                 # 连通关系
    OVERLAPPING = "overlapping"             # 重叠关系
    CONTAINED = "contained"                 # 包含关系
    ACCESSIBLE_FROM = "accessible_from"     # 可达关系


class EnvironmentalParameter(str, Enum):
    """环境参数枚举"""
    TEMPERATURE = "temperature"             # 温度
    HUMIDITY = "humidity"                   # 湿度
    AIR_QUALITY = "air_quality"            # 空气质量
    NOISE_LEVEL = "noise_level"            # 噪音等级
    LIGHTING_LEVEL = "lighting_level"      # 照明等级
    OCCUPANCY_COUNT = "occupancy_count"    # 占用人数
    CO2_LEVEL = "co2_level"                # 二氧化碳浓度
    PRESSURE = "pressure"                   # 气压


class CapacityType(str, Enum):
    """容量类型枚举"""
    PERSON_CAPACITY = "person_capacity"     # 人员容量
    VEHICLE_CAPACITY = "vehicle_capacity"   # 车辆容量
    EQUIPMENT_CAPACITY = "equipment_capacity"  # 设备容量
    STORAGE_CAPACITY = "storage_capacity"   # 存储容量
    POWER_CAPACITY = "power_capacity"       # 电力容量
    NETWORK_CAPACITY = "network_capacity"   # 网络容量


class SecurityLevel(str, Enum):
    """安全级别枚举"""
    PUBLIC = "public"                       # 公共级别
    INTERNAL = "internal"                   # 内部级别
    CONFIDENTIAL = "confidential"           # 机密级别
    SECRET = "secret"                       # 秘密级别
    TOP_SECRET = "top_secret"              # 绝密级别


class MaintenanceType(str, Enum):
    """维护类型枚举"""
    ROUTINE = "routine"                     # 常规维护
    PREVENTIVE = "preventive"               # 预防性维护
    CORRECTIVE = "corrective"               # 纠正性维护
    EMERGENCY = "emergency"                 # 应急维护
    UPGRADE = "upgrade"                     # 升级维护
    CLEANING = "cleaning"                   # 清洁维护 