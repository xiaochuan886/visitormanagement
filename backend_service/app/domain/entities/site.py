"""
站点实体定义
"""
from typing import Optional
from pydantic import Field

from .base import TenantEntity
from ..enums import SiteStatus


class Site(TenantEntity):
    """站点实体"""
    
    # 基本信息
    name: str = Field(..., description="站点名称")
    code: str = Field(..., description="站点编码")
    description: Optional[str] = Field(None, description="站点描述")
    
    # 地址信息
    address: Optional[str] = Field(None, description="详细地址")
    city: Optional[str] = Field(None, description="城市")
    province: Optional[str] = Field(None, description="省份")
    postal_code: Optional[str] = Field(None, description="邮政编码")
    country: Optional[str] = Field("中国", description="国家")
    
    # 联系信息
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="联系邮箱")
    website: Optional[str] = Field(None, description="网站地址")
    
    # 地理位置
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    
    # 状态信息
    status: SiteStatus = Field(SiteStatus.ACTIVE, description="站点状态")
    
    # 工作时间
    working_hours_start: Optional[str] = Field("09:00", description="工作开始时间")
    working_hours_end: Optional[str] = Field("18:00", description="工作结束时间")
    
    # 时区
    timezone: str = Field("Asia/Shanghai", description="时区")
    
    @property
    def is_active(self) -> bool:
        """是否为活跃状态"""
        return self.status == SiteStatus.ACTIVE
    
    @property
    def full_address(self) -> str:
        """完整地址"""
        parts = [self.country, self.province, self.city, self.address]
        return " ".join(filter(None, parts))
    
    def activate(self) -> None:
        """激活站点"""
        self.status = SiteStatus.ACTIVE
    
    def deactivate(self) -> None:
        """停用站点"""
        self.status = SiteStatus.INACTIVE
    
    def set_maintenance(self) -> None:
        """设置为维护状态"""
        self.status = SiteStatus.MAINTENANCE 