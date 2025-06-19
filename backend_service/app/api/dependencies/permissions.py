"""
权限管理依赖注入
"""
from typing import Dict, Any, List
from fastapi import Depends, HTTPException, status

from .auth import get_current_user
from .tenant import get_current_tenant


class ScenarioPermissions:
    """场景管理权限定义"""
    
    # 场景模板权限
    TEMPLATE_VIEW = "scenario:template:view"
    TEMPLATE_CREATE = "scenario:template:create"
    TEMPLATE_EDIT = "scenario:template:edit"
    TEMPLATE_DELETE = "scenario:template:delete"
    TEMPLATE_MANAGE_BUILTIN = "scenario:template:manage_builtin"
    
    # 场景实例权限
    INSTANCE_VIEW = "scenario:instance:view"
    INSTANCE_CREATE = "scenario:instance:create"
    INSTANCE_EDIT = "scenario:instance:edit"
    INSTANCE_DELETE = "scenario:instance:delete"
    INSTANCE_ACTIVATE = "scenario:instance:activate"
    INSTANCE_CLONE = "scenario:instance:clone"
    
    # 场景执行权限
    EXECUTION_VIEW = "scenario:execution:view"
    EXECUTION_CREATE = "scenario:execution:create"
    EXECUTION_MANAGE = "scenario:execution:manage"
    EXECUTION_CANCEL = "scenario:execution:cancel"
    
    # 路由规则权限
    ROUTING_VIEW = "scenario:routing:view"
    ROUTING_CREATE = "scenario:routing:create"
    ROUTING_EDIT = "scenario:routing:edit"
    ROUTING_DELETE = "scenario:routing:delete"
    
    # 分析权限
    ANALYTICS_VIEW = "scenario:analytics:view"
    ANALYTICS_EXPORT = "scenario:analytics:export"
    
    # 系统管理权限
    SYSTEM_ADMIN = "scenario:system:admin"
    SYSTEM_CONFIG = "scenario:system:config"


def require_permission(permission: str):
    """检查单个权限"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        user_roles = current_user.get("roles", [])
        
        # 超级管理员拥有所有权限
        if "super_admin" in user_roles or "system_admin" in user_roles:
            return current_user
        
        # 检查具体权限
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {permission}",
                headers={"X-Required-Permission": permission}
            )
        
        return current_user
    
    return permission_checker


def require_any_permission(permissions: List[str]):
    """检查多个权限中的任意一个"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        user_roles = current_user.get("roles", [])
        
        # 超级管理员拥有所有权限
        if "super_admin" in user_roles or "system_admin" in user_roles:
            return current_user
        
        # 检查是否有任意一个权限
        for permission in permissions:
            if permission in user_permissions:
                return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少以下任意权限: {', '.join(permissions)}",
            headers={"X-Required-Permissions": ','.join(permissions)}
        )
    
    return permission_checker


def require_all_permissions(permissions: List[str]):
    """检查多个权限的全部"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        user_roles = current_user.get("roles", [])
        
        # 超级管理员拥有所有权限
        if "super_admin" in user_roles or "system_admin" in user_roles:
            return current_user
        
        # 检查是否拥有所有权限
        missing_permissions = []
        for permission in permissions:
            if permission not in user_permissions:
                missing_permissions.append(permission)
        
        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {', '.join(missing_permissions)}",
                headers={"X-Missing-Permissions": ','.join(missing_permissions)}
            )
        
        return current_user
    
    return permission_checker


# 场景管理常用权限依赖
require_template_view = require_permission(ScenarioPermissions.TEMPLATE_VIEW)
require_template_create = require_permission(ScenarioPermissions.TEMPLATE_CREATE)
require_template_edit = require_permission(ScenarioPermissions.TEMPLATE_EDIT)
require_template_delete = require_permission(ScenarioPermissions.TEMPLATE_DELETE)
require_template_manage_builtin = require_permission(ScenarioPermissions.TEMPLATE_MANAGE_BUILTIN)

require_instance_view = require_permission(ScenarioPermissions.INSTANCE_VIEW)
require_instance_create = require_permission(ScenarioPermissions.INSTANCE_CREATE)
require_instance_edit = require_permission(ScenarioPermissions.INSTANCE_EDIT)
require_instance_delete = require_permission(ScenarioPermissions.INSTANCE_DELETE)
require_instance_activate = require_permission(ScenarioPermissions.INSTANCE_ACTIVATE)
require_instance_clone = require_permission(ScenarioPermissions.INSTANCE_CLONE)

require_execution_view = require_permission(ScenarioPermissions.EXECUTION_VIEW)
require_execution_create = require_permission(ScenarioPermissions.EXECUTION_CREATE)
require_execution_manage = require_permission(ScenarioPermissions.EXECUTION_MANAGE)
require_execution_cancel = require_permission(ScenarioPermissions.EXECUTION_CANCEL)

require_routing_view = require_permission(ScenarioPermissions.ROUTING_VIEW)
require_routing_create = require_permission(ScenarioPermissions.ROUTING_CREATE)
require_routing_edit = require_permission(ScenarioPermissions.ROUTING_EDIT)
require_routing_delete = require_permission(ScenarioPermissions.ROUTING_DELETE)

require_analytics_view = require_permission(ScenarioPermissions.ANALYTICS_VIEW)
require_analytics_export = require_permission(ScenarioPermissions.ANALYTICS_EXPORT)

require_system_admin = require_permission(ScenarioPermissions.SYSTEM_ADMIN)
require_system_config = require_permission(ScenarioPermissions.SYSTEM_CONFIG)


def check_resource_access(resource_type: str, resource_id: str = None):
    """检查资源访问权限"""
    def access_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
        tenant_id: str = Depends(get_current_tenant)
    ):
        # 这里可以添加更复杂的资源访问控制逻辑
        # 比如检查资源是否属于当前租户，用户是否有权访问特定资源等
        
        user_roles = current_user.get("roles", [])
        
        # 超级管理员可以访问所有资源
        if "super_admin" in user_roles:
            return current_user
        
        # 租户管理员可以访问本租户的所有资源
        if "tenant_admin" in user_roles:
            return current_user
        
        # 其他用户需要有具体的权限
        return current_user
    
    return access_checker 