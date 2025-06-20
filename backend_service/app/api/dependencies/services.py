"""
服务层依赖注入
"""
from typing import Dict, Any
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database.connection import get_db
from ...application.services.scenario_service import (
    ScenarioTemplateService, 
    ScenarioInstanceService
)
from ...application.services.scenario_routing_service import ScenarioRoutingService
from ...application.services.scenario_execution_service import ScenarioExecutionService
from .auth import get_current_user


# ================ 场景管理服务依赖 ================

async def get_scenario_template_service(
    db: AsyncSession = Depends(get_db)
) -> ScenarioTemplateService:
    """获取场景模板服务"""
    return ScenarioTemplateService(db)


async def get_scenario_instance_service(
    db: AsyncSession = Depends(get_db)
) -> ScenarioInstanceService:
    """获取场景实例服务"""
    return ScenarioInstanceService(db)


async def get_scenario_routing_service(
    db: AsyncSession = Depends(get_db)
) -> ScenarioRoutingService:
    """获取场景路由服务"""
    return ScenarioRoutingService(db)


async def get_scenario_execution_service(
    db: AsyncSession = Depends(get_db)
) -> ScenarioExecutionService:
    """获取场景执行服务"""
    return ScenarioExecutionService(db)


# ================ 验证用户上下文的服务依赖 ================

async def get_authenticated_template_service(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ScenarioTemplateService:
    """获取已认证的场景模板服务"""
    service = ScenarioTemplateService(db)
    service.set_user_context(current_user)
    return service


async def get_authenticated_instance_service(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ScenarioInstanceService:
    """获取已认证的场景实例服务"""
    service = ScenarioInstanceService(db)
    service.set_user_context(current_user)
    return service


async def get_authenticated_routing_service(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ScenarioRoutingService:
    """获取已认证的场景路由服务"""
    service = ScenarioRoutingService(db)
    service.set_user_context(current_user)
    return service


async def get_authenticated_execution_service(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ScenarioExecutionService:
    """获取已认证的场景执行服务"""
    service = ScenarioExecutionService(db)
    service.set_user_context(current_user)
    return service


# ================ 服务工厂类 ================

class ServiceFactory:
    """服务工厂类"""
    
    def __init__(self, db: AsyncSession, current_user: Dict[str, Any] = None):
        self.db = db
        self.current_user = current_user
    
    def get_template_service(self) -> ScenarioTemplateService:
        """获取场景模板服务"""
        service = ScenarioTemplateService(self.db)
        if self.current_user:
            service.set_user_context(self.current_user)
        return service
    
    def get_instance_service(self) -> ScenarioInstanceService:
        """获取场景实例服务"""
        service = ScenarioInstanceService(self.db)
        if self.current_user:
            service.set_user_context(self.current_user)
        return service
    
    def get_routing_service(self) -> ScenarioRoutingService:
        """获取场景路由服务"""
        service = ScenarioRoutingService(self.db)
        if self.current_user:
            service.set_user_context(self.current_user)
        return service
    
    def get_execution_service(self) -> ScenarioExecutionService:
        """获取场景执行服务"""
        service = ScenarioExecutionService(self.db)
        if self.current_user:
            service.set_user_context(self.current_user)
        return service


async def get_service_factory(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ServiceFactory:
    """获取服务工厂实例"""
    return ServiceFactory(db, current_user)


# ================ 只读服务依赖（无需认证） ================

async def get_readonly_template_service(
    db: AsyncSession = Depends(get_db)
) -> ScenarioTemplateService:
    """获取只读场景模板服务（用于公开接口）"""
    return ScenarioTemplateService(db)


async def get_readonly_instance_service(
    db: AsyncSession = Depends(get_db)
) -> ScenarioInstanceService:
    """获取只读场景实例服务（用于公开接口）"""
    return ScenarioInstanceService(db)


async def get_readonly_routing_service(
    db: AsyncSession = Depends(get_db)
) -> ScenarioRoutingService:
    """获取只读场景路由服务（用于公开接口）"""
    return ScenarioRoutingService(db) 