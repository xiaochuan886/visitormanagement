"""
领域层基础实体定义
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class BaseEntity(BaseModel):
    """基础实体类"""
    id: Optional[int] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class AuditableEntity(BaseEntity):
    """可审计实体基类"""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None


class TenantEntity(AuditableEntity):
    """多租户实体基类"""
    tenant_id: str = Field(default="default", description="租户ID")


class DomainEvent(BaseModel):
    """领域事件基类"""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    aggregate_id: str
    aggregate_type: str
    event_data: dict
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1 