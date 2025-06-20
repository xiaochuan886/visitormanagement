"""
API路由模块
"""
from fastapi import APIRouter

from .visitors import router as visitors_router
from .employees import router as employees_router
from .departments import router as departments_router
from .sites import router as sites_router
from .auth import router as auth_router
# 恢复配置引擎路由
from .form_config import router as form_config_router
from .workflow_config import router as workflow_config_router
from .spatial_config import router as spatial_config_router
from .business_rules import router as business_rules_router
# 场景管理路由
from .scenarios import router as scenarios_router
from .scenario_templates import router as scenario_templates_router

# 门岗前台移动端路由
from .gate import router as gate_router
from .reception import router as reception_router
from .mobile import router as mobile_router
from .devices import router as devices_router
from .health import router as health_router

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

# 场景管理API路由
api_router.include_router(scenarios_router, prefix="/config/scenarios", tags=["场景管理"])
api_router.include_router(scenario_templates_router, prefix="/config/scenarios", tags=["场景模板"]) 

# 门岗前台移动端API路由
api_router.include_router(gate_router, prefix="/gate", tags=["门岗管理"])
api_router.include_router(reception_router, prefix="/reception", tags=["前台管理"])
api_router.include_router(mobile_router, prefix="/mobile", tags=["移动端"])
api_router.include_router(devices_router, prefix="/devices", tags=["设备管理"])
api_router.include_router(health_router, prefix="/health", tags=["系统健康检查"])