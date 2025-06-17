"""
API路由模块
"""
from fastapi import APIRouter

from .visitors import router as visitors_router
from .employees import router as employees_router
from .departments import router as departments_router
from .sites import router as sites_router
from .auth import router as auth_router
from .form_config import router as form_config_router
from .workflow_config import router as workflow_config_router
from .spatial_config import router as spatial_config_router
from .business_rules import router as business_rules_router

# 创建主API路由器
api_router = APIRouter()

# 注册各模块路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(visitors_router, prefix="/visitors", tags=["访客管理"])
api_router.include_router(employees_router, prefix="/employees", tags=["员工管理"])
api_router.include_router(departments_router, prefix="/departments", tags=["部门管理"])
api_router.include_router(sites_router, prefix="/sites", tags=["站点管理"])

# 配置引擎API路由
api_router.include_router(form_config_router, prefix="/config/forms", tags=["表单配置"])
api_router.include_router(workflow_config_router, prefix="/config/workflows", tags=["工作流配置"])
api_router.include_router(spatial_config_router, prefix="/config/spatial", tags=["空间配置"])
api_router.include_router(business_rules_router, prefix="/config/rules", tags=["业务规则"]) 