"""
场景管理 API 路由
严格遵循 Clean Architecture 和 API 开发规范
"""
import logging
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

# 基础设施依赖
from ...infrastructure.database.connection import get_db_session

# API依赖项
from ..dependencies.auth import get_current_user
from ..dependencies.tenant import get_current_tenant
from ..dependencies.permissions import (
    require_template_view, require_template_create, require_template_edit, require_template_delete,
    require_instance_view, require_instance_create, require_instance_edit, require_instance_delete,
    require_execution_view, require_execution_create, require_execution_manage,
    require_routing_view, require_routing_create, require_routing_edit,
    require_analytics_view, require_system_admin
)
from ..dependencies.services import (
    get_scenario_template_service, get_scenario_instance_service,
    get_scenario_routing_service, get_scenario_execution_service
)

# API响应模型
from ..models.base_response import (
    DataResponse, PaginatedResponse, OperationResponse, 
    BatchOperationResponse, ErrorResponse, StatusCodes, ErrorCodes
)

# DTO模型
from ...application.dto.scenario_dto import (
    # 场景模板 DTOs
    ScenarioTemplateCreateDTO, ScenarioTemplateUpdateDTO, ScenarioTemplateResponseDTO,
    ScenarioTemplateQueryDTO, ScenarioTemplateCategory,
    
    # 场景实例 DTOs
    ScenarioInstanceCreateDTO, ScenarioInstanceUpdateDTO, ScenarioInstanceResponseDTO,
    ScenarioInstanceQueryDTO, ScenarioInstanceStatus,
    
    # 场景执行 DTOs
    ScenarioExecutionCreateDTO, ScenarioExecutionResponseDTO, ScenarioExecutionQueryDTO,
    
    # 路由规则 DTOs
    ScenarioRoutingRuleCreateDTO, ScenarioRoutingRuleResponseDTO
)

# 应用服务
from ...application.services.scenario_service import ScenarioTemplateService, ScenarioInstanceService
from ...application.services.scenario_routing_service import ScenarioRoutingService
from ...application.services.scenario_execution_service import ScenarioExecutionService

# 异常处理
from ...domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, ConfigurationValidationError, ConfigurationConflictError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scenarios", tags=["场景管理"])


# ================== 错误处理器 ==================

def handle_service_exceptions(func):
    """服务异常处理装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConfigurationNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
                headers={"X-Error-Code": ErrorCodes.RESOURCE_NOT_FOUND}
            )
        except ConfigurationValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
                headers={"X-Error-Code": ErrorCodes.VALIDATION_ERROR}
            )
        except ConfigurationConflictError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
                headers={"X-Error-Code": ErrorCodes.RESOURCE_CONFLICT}
            )
        except Exception as e:
            logger.error(f"API处理异常: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="内部服务器错误",
                headers={"X-Error-Code": "INTERNAL_SERVER_ERROR"}
            )
    return wrapper


# ================== 场景模板 API ==================

@router.post(
    "/templates",
    response_model=DataResponse[ScenarioTemplateResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="创建场景模板",
    description="创建新的场景模板，需要模板创建权限"
)
@handle_service_exceptions
async def create_scenario_template(
    template_data: ScenarioTemplateCreateDTO,
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_create)
) -> DataResponse[ScenarioTemplateResponseDTO]:
    """
    创建场景模板
    
    - **权限要求**: scenario:template:create
    - **租户隔离**: 是
    - **操作审计**: 是
    """
    result = await template_service.create_template(template_data, tenant_id)
    
    return DataResponse(
        data=result,
        message="场景模板创建成功"
    )


@router.get(
    "/templates",
    response_model=PaginatedResponse[ScenarioTemplateResponseDTO],
    summary="获取场景模板列表",
    description="分页获取场景模板列表，支持筛选和搜索"
)
@handle_service_exceptions
async def list_scenario_templates(
    template_category: Optional[ScenarioTemplateCategory] = Query(None, description="模板分类"),
    is_builtin: Optional[bool] = Query(None, description="是否为内置模板"),
    is_template_active: Optional[bool] = Query(None, description="是否激活"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    template_tags: Optional[List[str]] = Query(None, description="模板标签"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_view)
) -> PaginatedResponse[ScenarioTemplateResponseDTO]:
    """
    获取场景模板列表
    
    - **权限要求**: scenario:template:view
    - **支持分页**: 是
    - **支持筛选**: 是
    """
    query_dto = ScenarioTemplateQueryDTO(
        template_category=template_category,
        is_builtin=is_builtin,
        is_template_active=is_template_active,
        search=search,
        template_tags=template_tags
    )
    
    skip = (page - 1) * page_size
    templates, total = await template_service.list_templates(
        query_dto, tenant_id, skip, page_size
    )
    
    return PaginatedResponse.create(
        data=templates,
        total=total,
        page=page,
        page_size=page_size,
        message="获取场景模板列表成功"
    )


@router.get(
    "/templates/{template_id}",
    response_model=DataResponse[ScenarioTemplateResponseDTO],
    summary="获取场景模板详情",
    description="根据ID获取场景模板的详细信息"
)
@handle_service_exceptions
async def get_scenario_template(
    template_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_view)
) -> DataResponse[ScenarioTemplateResponseDTO]:
    """
    获取场景模板详情
    
    - **权限要求**: scenario:template:view
    - **租户隔离**: 是
    """
    template = await template_service.get_template(template_id, tenant_id)
    
    return DataResponse(
        data=template,
        message="获取场景模板详情成功"
    )


@router.put(
    "/templates/{template_id}",
    response_model=DataResponse[ScenarioTemplateResponseDTO],
    summary="更新场景模板",
    description="更新指定的场景模板信息"
)
@handle_service_exceptions
async def update_scenario_template(
    template_id: UUID,
    update_data: ScenarioTemplateUpdateDTO,
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_edit)
) -> DataResponse[ScenarioTemplateResponseDTO]:
    """
    更新场景模板
    
    - **权限要求**: scenario:template:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    """
    template = await template_service.update_template(template_id, update_data, tenant_id)
    
    return DataResponse(
        data=template,
        message="场景模板更新成功"
    )


@router.delete(
    "/templates/{template_id}",
    response_model=OperationResponse,
    summary="删除场景模板",
    description="删除指定的场景模板（软删除）"
)
@handle_service_exceptions
async def delete_scenario_template(
    template_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_delete)
) -> OperationResponse:
    """
    删除场景模板
    
    - **权限要求**: scenario:template:delete
    - **删除方式**: 软删除
    - **操作审计**: 是
    """
    await template_service.delete_template(template_id, tenant_id)
    
    return OperationResponse(
        message="场景模板删除成功",
        affected_count=1
    )


# ================== 场景实例 API ==================

@router.post(
    "/instances",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="创建场景实例",
    description="基于模板创建场景实例"
)
@handle_service_exceptions
async def create_scenario_instance(
    instance_data: ScenarioInstanceCreateDTO,
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_create)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    创建场景实例
    
    - **权限要求**: scenario:instance:create
    - **租户隔离**: 是
    - **操作审计**: 是
    """
    result = await instance_service.create_instance(instance_data, tenant_id)
    
    return DataResponse(
        data=result,
        message="场景实例创建成功"
    )


@router.get(
    "/instances",
    response_model=PaginatedResponse[ScenarioInstanceResponseDTO],
    summary="获取场景实例列表",
    description="分页获取场景实例列表"
)
@handle_service_exceptions
async def list_scenario_instances(
    template_id: Optional[UUID] = Query(None, description="模板ID"),
    instance_status: Optional[ScenarioInstanceStatus] = Query(None, description="实例状态"),
    auto_routing_enabled: Optional[bool] = Query(None, description="是否启用自动路由"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_view)
) -> PaginatedResponse[ScenarioInstanceResponseDTO]:
    """
    获取场景实例列表
    
    - **权限要求**: scenario:instance:view
    - **支持分页**: 是
    - **支持筛选**: 是
    """
    query_dto = ScenarioInstanceQueryDTO(
        template_id=template_id,
        instance_status=instance_status,
        auto_routing_enabled=auto_routing_enabled,
        search=search
    )
    
    skip = (page - 1) * page_size
    instances, total = await instance_service.list_instances(
        query_dto, tenant_id, skip, page_size
    )
    
    return PaginatedResponse.create(
        data=instances,
        total=total,
        page=page,
        page_size=page_size,
        message="获取场景实例列表成功"
    )


@router.get(
    "/instances/{instance_id}",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="获取场景实例详情",
    description="根据ID获取场景实例的详细信息"
)
@handle_service_exceptions
async def get_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_view)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    获取场景实例详情
    
    - **权限要求**: scenario:instance:view
    - **租户隔离**: 是
    """
    instance = await instance_service.get_instance(instance_id, tenant_id)
    
    return DataResponse(
        data=instance,
        message="获取场景实例详情成功"
    )


@router.put(
    "/instances/{instance_id}",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="更新场景实例",
    description="更新指定的场景实例信息"
)
@handle_service_exceptions
async def update_scenario_instance(
    instance_id: UUID,
    update_data: ScenarioInstanceUpdateDTO,
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_edit)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    更新场景实例
    
    - **权限要求**: scenario:instance:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    """
    instance = await instance_service.update_instance(instance_id, update_data, tenant_id)
    
    return DataResponse(
        data=instance,
        message="场景实例更新成功"
    )


@router.delete(
    "/instances/{instance_id}",
    response_model=OperationResponse,
    summary="删除场景实例",
    description="删除指定的场景实例（软删除）"
)
@handle_service_exceptions
async def delete_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_delete)
) -> OperationResponse:
    """
    删除场景实例
    
    - **权限要求**: scenario:instance:delete
    - **删除方式**: 软删除
    - **操作审计**: 是
    """
    await instance_service.delete_instance(instance_id, tenant_id)
    
    return OperationResponse(
        message="场景实例删除成功",
        affected_count=1
    )


@router.post(
    "/instances/{instance_id}/activate",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="激活场景实例",
    description="激活指定的场景实例"
)
@handle_service_exceptions
async def activate_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_edit)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    激活场景实例
    
    - **权限要求**: scenario:instance:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    """
    instance = await instance_service.activate_instance(instance_id, tenant_id)
    
    return DataResponse(
        data=instance,
        message="场景实例激活成功"
    )


@router.post(
    "/instances/{instance_id}/deactivate",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="停用场景实例",
    description="停用指定的场景实例"
)
@handle_service_exceptions
async def deactivate_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_edit)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    停用场景实例
    
    - **权限要求**: scenario:instance:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    """
    instance = await instance_service.deactivate_instance(instance_id, tenant_id)
    
    return DataResponse(
        data=instance,
        message="场景实例停用成功"
    )


# ================== 场景执行 API ==================

@router.post(
    "/executions",
    response_model=DataResponse[ScenarioExecutionResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="创建场景执行",
    description="创建新的场景执行任务"
)
@handle_service_exceptions
async def create_scenario_execution(
    execution_data: ScenarioExecutionCreateDTO,
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant),
    execution_service: ScenarioExecutionService = Depends(get_scenario_execution_service),
    _: Dict[str, Any] = Depends(require_execution_create)
) -> DataResponse[ScenarioExecutionResponseDTO]:
    """
    创建场景执行
    
    - **权限要求**: scenario:execution:create
    - **处理方式**: 异步处理
    - **租户隔离**: 是
    """
    execution = await execution_service.create_execution(execution_data, tenant_id)
    
    # 添加后台任务执行场景
    background_tasks.add_task(
        execution_service.execute_scenario_async,
        execution.id,
        tenant_id
    )
    
    return DataResponse(
        data=execution,
        message="场景执行任务创建成功"
    )


@router.get(
    "/executions",
    response_model=PaginatedResponse[ScenarioExecutionResponseDTO],
    summary="获取场景执行列表",
    description="分页获取场景执行记录"
)
@handle_service_exceptions
async def list_scenario_executions(
    scenario_instance_id: Optional[UUID] = Query(None, description="场景实例ID"),
    execution_status: Optional[str] = Query(None, description="执行状态"),
    execution_type: Optional[str] = Query(None, description="执行类型"),
    target_entity_type: Optional[str] = Query(None, description="目标实体类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tenant_id: str = Depends(get_current_tenant),
    execution_service: ScenarioExecutionService = Depends(get_scenario_execution_service),
    _: Dict[str, Any] = Depends(require_execution_view)
) -> PaginatedResponse[ScenarioExecutionResponseDTO]:
    """
    获取场景执行列表
    
    - **权限要求**: scenario:execution:view
    - **支持分页**: 是
    - **支持筛选**: 是
    """
    query_dto = ScenarioExecutionQueryDTO(
        scenario_instance_id=scenario_instance_id,
        execution_status=execution_status,
        execution_type=execution_type,
        target_entity_type=target_entity_type
    )
    
    skip = (page - 1) * page_size
    executions, total = await execution_service.list_executions(
        query_dto, tenant_id, skip, page_size
    )
    
    return PaginatedResponse.create(
        data=executions,
        total=total,
        page=page,
        page_size=page_size,
        message="获取场景执行列表成功"
    )


@router.get(
    "/executions/{execution_id}",
    response_model=DataResponse[ScenarioExecutionResponseDTO],
    summary="获取场景执行详情",
    description="根据ID获取场景执行的详细信息"
)
@handle_service_exceptions
async def get_scenario_execution(
    execution_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    execution_service: ScenarioExecutionService = Depends(get_scenario_execution_service),
    _: Dict[str, Any] = Depends(require_execution_view)
) -> DataResponse[ScenarioExecutionResponseDTO]:
    """
    获取场景执行详情
    
    - **权限要求**: scenario:execution:view
    - **租户隔离**: 是
    """
    execution = await execution_service.get_execution(execution_id, tenant_id)
    
    return DataResponse(
        data=execution,
        message="获取场景执行详情成功"
    )


@router.post(
    "/executions/{execution_id}/cancel",
    response_model=DataResponse[ScenarioExecutionResponseDTO],
    summary="取消场景执行",
    description="取消正在执行的场景任务"
)
@handle_service_exceptions
async def cancel_scenario_execution(
    execution_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    execution_service: ScenarioExecutionService = Depends(get_scenario_execution_service),
    _: Dict[str, Any] = Depends(require_execution_manage)
) -> DataResponse[ScenarioExecutionResponseDTO]:
    """
    取消场景执行
    
    - **权限要求**: scenario:execution:manage
    - **租户隔离**: 是
    """
    execution = await execution_service.cancel_execution(execution_id, tenant_id)
    
    return DataResponse(
        data=execution,
        message="场景执行取消成功"
    )


# ================== 场景路由 API ==================

@router.post(
    "/route",
    response_model=DataResponse[Dict[str, Any]],
    summary="路由场景",
    description="根据条件自动路由到匹配的场景"
)
@handle_service_exceptions
async def route_scenario(
    context: Dict[str, Any],
    entity_type: str = Query(..., description="实体类型"),
    entity_id: str = Query(..., description="实体ID"),
    auto_execute: bool = Query(False, description="是否自动执行"),
    tenant_id: str = Depends(get_current_tenant),
    routing_service: ScenarioRoutingService = Depends(get_scenario_routing_service),
    _: Dict[str, Any] = Depends(require_routing_view)
) -> DataResponse[Dict[str, Any]]:
    """
    路由场景
    
    - **权限要求**: scenario:routing:view
    - **租户隔离**: 是
    - **支持自动执行**: 是
    """
    result = await routing_service.route_scenario(
        context, entity_type, entity_id, auto_execute, tenant_id
    )
    
    return DataResponse(
        data=result,
        message="场景路由成功"
    )


@router.post(
    "/routing-rules",
    response_model=DataResponse[ScenarioRoutingRuleResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="创建路由规则",
    description="创建新的场景路由规则"
)
@handle_service_exceptions
async def create_routing_rule(
    rule_data: ScenarioRoutingRuleCreateDTO,
    tenant_id: str = Depends(get_current_tenant),
    routing_service: ScenarioRoutingService = Depends(get_scenario_routing_service),
    _: Dict[str, Any] = Depends(require_routing_create)
) -> DataResponse[ScenarioRoutingRuleResponseDTO]:
    """
    创建路由规则
    
    - **权限要求**: scenario:routing:create
    - **租户隔离**: 是
    - **操作审计**: 是
    """
    rule = await routing_service.create_routing_rule(rule_data, tenant_id)
    
    return DataResponse(
        data=rule,
        message="路由规则创建成功"
    )


# ================== 系统管理 API ==================

@router.post(
    "/templates/initialize-builtin",
    response_model=BatchOperationResponse,
    summary="初始化内置模板",
    description="初始化系统预制的场景模板"
)
@handle_service_exceptions
async def initialize_builtin_templates(
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_system_admin)
) -> BatchOperationResponse:
    """
    初始化内置模板
    
    - **权限要求**: scenario:system:admin
    - **操作类型**: 批量操作
    - **租户隔离**: 是
    """
    result = await template_service.initialize_builtin_templates(tenant_id)
    
    return BatchOperationResponse(
        total_count=result.get("total", 0),
        success_count=result.get("success", 0),
        failed_count=result.get("failed", 0),
        errors=result.get("errors", []),
        message="内置模板初始化完成"
    )


@router.get(
    "/analytics/summary",
    response_model=DataResponse[Dict[str, Any]],
    summary="获取场景分析摘要",
    description="获取场景执行的统计分析数据"
)
@handle_service_exceptions
async def get_scenario_analytics_summary(
    period: str = Query("daily", description="统计周期"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    tenant_id: str = Depends(get_current_tenant),
    execution_service: ScenarioExecutionService = Depends(get_scenario_execution_service),
    _: Dict[str, Any] = Depends(require_analytics_view)
) -> DataResponse[Dict[str, Any]]:
    """
    获取场景分析摘要
    
    - **权限要求**: scenario:analytics:view
    - **租户隔离**: 是
    - **支持时间范围**: 是
    """
    analytics = await execution_service.get_analytics_summary(
        tenant_id, period, start_date, end_date
    )
    
    return DataResponse(
        data=analytics,
        message="获取场景分析摘要成功"
    ) 