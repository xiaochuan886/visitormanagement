"""
场景实例 API 路由
严格遵循 Clean Architecture 和 API 开发规范
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

# API依赖项
from ..dependencies.auth import get_current_user
from ..dependencies.tenant import get_current_tenant
from ..dependencies.permissions import (
    require_instance_view, require_instance_create,
    require_instance_edit, require_instance_delete,
    require_instance_activate, require_instance_clone
)
from ..dependencies.services import get_scenario_instance_service

# API响应模型
from ..models.base_response import (
    DataResponse, PaginatedResponse, OperationResponse,
    BatchOperationResponse, ErrorCodes
)

# DTO模型
from ...application.dto.scenario_dto import (
    ScenarioInstanceCreateDTO, ScenarioInstanceUpdateDTO,
    ScenarioInstanceResponseDTO, ScenarioInstanceQueryDTO,
    ScenarioInstanceStatus, ScenarioInstanceCloneDTO,
    ScenarioInstanceBatchUpdateDTO
)

# 应用服务
from ...application.services.scenario_service import ScenarioInstanceService

# 异常处理
from ...domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, ConfigurationValidationError,
    ConfigurationConflictError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/instances", tags=["场景实例"])


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


@router.post(
    "",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="创建场景实例",
    description="基于模板创建新的场景实例",
    responses={
        201: {"description": "场景实例创建成功"},
        400: {"description": "请求参数错误"},
        403: {"description": "权限不足"},
        404: {"description": "模板不存在"},
        409: {"description": "实例代码冲突"},
        422: {"description": "数据验证失败"}
    }
)
@handle_service_exceptions
async def create_scenario_instance(
    instance_data: ScenarioInstanceCreateDTO,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_create)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    创建场景实例
    
    - **权限要求**: scenario:instance:create
    - **租户隔离**: 是
    - **操作审计**: 是
    
    **请求示例**:
    ```json
    {
        "instance_name": "前台标准登记",
        "instance_code": "front_desk_standard",
        "template_id": "uuid-of-template",
        "priority_level": 8,
        "custom_configurations": {
            "business_hours": {"start": "08:00", "end": "18:00"}
        },
        "routing_rules": {
            "conditions": [{"field": "visitor_type", "operator": "eq", "value": "standard"}]
        },
        "applicable_sites": ["headquarters"],
        "applicable_departments": ["reception"]
    }
    ```
    """
    result = await instance_service.create_instance(
        instance_data,
        current_user["sub"],
        tenant_id
    )
    
    return DataResponse(
        data=result,
        message="场景实例创建成功"
    )


@router.get(
    "",
    response_model=PaginatedResponse[ScenarioInstanceResponseDTO],
    summary="获取场景实例列表",
    description="分页获取场景实例列表，支持筛选和搜索",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"}
    }
)
@handle_service_exceptions
async def list_scenario_instances(
    template_id: Optional[UUID] = Query(None, description="模板ID筛选"),
    instance_status: Optional[ScenarioInstanceStatus] = Query(None, description="实例状态筛选"),
    auto_routing_enabled: Optional[bool] = Query(None, description="是否启用自动路由"),
    search: Optional[str] = Query(None, description="搜索关键词（实例名称、代码）"),
    applicable_sites: Optional[List[str]] = Query(None, description="适用站点筛选"),
    applicable_departments: Optional[List[str]] = Query(None, description="适用部门筛选"),
    priority_min: Optional[int] = Query(None, description="最小优先级", ge=1, le=10),
    priority_max: Optional[int] = Query(None, description="最大优先级", ge=1, le=10),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_view)
) -> PaginatedResponse[ScenarioInstanceResponseDTO]:
    """
    获取场景实例列表
    
    - **权限要求**: scenario:instance:view
    - **支持分页**: 是，最大每页100条
    - **支持筛选**: 模板、状态、站点、部门、优先级
    - **支持搜索**: 实例名称、代码
    """
    query_dto = ScenarioInstanceQueryDTO(
        template_id=template_id,
        instance_status=instance_status,
        auto_routing_enabled=auto_routing_enabled,
        search=search,
        applicable_sites=applicable_sites,
        applicable_departments=applicable_departments,
        priority_min=priority_min,
        priority_max=priority_max
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
    "/{instance_id}",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="获取场景实例详情",
    description="根据ID获取场景实例的详细信息",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"},
        404: {"description": "实例不存在"}
    }
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
    "/{instance_id}",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="更新场景实例",
    description="更新指定的场景实例信息",
    responses={
        200: {"description": "更新成功"},
        403: {"description": "权限不足"},
        404: {"description": "实例不存在"},
        422: {"description": "数据验证失败"}
    }
)
@handle_service_exceptions
async def update_scenario_instance(
    instance_id: UUID,
    update_data: ScenarioInstanceUpdateDTO,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_edit)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    更新场景实例
    
    - **权限要求**: scenario:instance:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    - **注意**: 更新配置可能影响正在执行的场景
    """
    instance = await instance_service.update_instance(
        instance_id,
        update_data,
        current_user["sub"],
        tenant_id
    )
    
    return DataResponse(
        data=instance,
        message="场景实例更新成功"
    )


@router.delete(
    "/{instance_id}",
    response_model=OperationResponse,
    summary="删除场景实例",
    description="删除指定的场景实例（软删除）",
    responses={
        200: {"description": "删除成功"},
        403: {"description": "权限不足"},
        404: {"description": "实例不存在"},
        409: {"description": "实例正在使用中，无法删除"}
    }
)
@handle_service_exceptions
async def delete_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_delete)
) -> OperationResponse:
    """
    删除场景实例
    
    - **权限要求**: scenario:instance:delete
    - **删除方式**: 软删除
    - **操作审计**: 是
    - **限制**: 有执行记录的实例不能删除
    """
    await instance_service.delete_instance(
        instance_id,
        current_user["sub"],
        tenant_id
    )
    
    return OperationResponse(
        message="场景实例删除成功",
        affected_count=1
    )


@router.post(
    "/{instance_id}/activate",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="激活场景实例",
    description="激活指定的场景实例，使其可以被路由和执行",
    responses={
        200: {"description": "激活成功"},
        403: {"description": "权限不足"},
        404: {"description": "实例不存在"},
        409: {"description": "实例状态不允许激活"}
    }
)
@handle_service_exceptions
async def activate_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_activate)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    激活场景实例
    
    - **权限要求**: scenario:instance:activate
    - **租户隔离**: 是
    - **操作审计**: 是
    - **效果**: 实例状态变为active，可以被路由匹配
    """
    instance = await instance_service.activate_instance(
        instance_id,
        current_user["sub"],
        tenant_id
    )
    
    return DataResponse(
        data=instance,
        message="场景实例激活成功"
    )


@router.post(
    "/{instance_id}/deactivate",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="停用场景实例",
    description="停用指定的场景实例，使其不再被路由匹配",
    responses={
        200: {"description": "停用成功"},
        403: {"description": "权限不足"},
        404: {"description": "实例不存在"}
    }
)
@handle_service_exceptions
async def deactivate_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_edit)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    停用场景实例
    
    - **权限要求**: scenario:instance:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    - **效果**: 实例状态变为inactive，不再被路由匹配
    """
    instance = await instance_service.deactivate_instance(
        instance_id,
        current_user["sub"],
        tenant_id
    )
    
    return DataResponse(
        data=instance,
        message="场景实例停用成功"
    )


@router.post(
    "/{instance_id}/clone",
    response_model=DataResponse[ScenarioInstanceResponseDTO],
    summary="克隆场景实例",
    description="基于现有实例创建一个新的实例副本",
    responses={
        201: {"description": "克隆成功"},
        403: {"description": "权限不足"},
        404: {"description": "原实例不存在"},
        409: {"description": "新实例代码冲突"}
    }
)
@handle_service_exceptions
async def clone_scenario_instance(
    instance_id: UUID,
    clone_data: ScenarioInstanceCloneDTO,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_clone)
) -> DataResponse[ScenarioInstanceResponseDTO]:
    """
    克隆场景实例
    
    - **权限要求**: scenario:instance:clone
    - **租户隔离**: 是
    - **操作审计**: 是
    - **用途**: 基于现有配置快速创建相似实例
    """
    cloned_instance = await instance_service.clone_instance(
        instance_id,
        clone_data,
        current_user["sub"],
        tenant_id
    )
    
    return DataResponse(
        data=cloned_instance,
        message="场景实例克隆成功"
    )


@router.post(
    "/batch/update-status",
    response_model=BatchOperationResponse,
    summary="批量更新实例状态",
    description="批量更新多个场景实例的状态",
    responses={
        200: {"description": "批量更新成功"},
        403: {"description": "权限不足"},
        422: {"description": "部分更新失败"}
    }
)
@handle_service_exceptions
async def batch_update_instance_status(
    batch_data: ScenarioInstanceBatchUpdateDTO,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_edit)
) -> BatchOperationResponse:
    """
    批量更新实例状态
    
    - **权限要求**: scenario:instance:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    - **限制**: 最多一次处理100个实例
    """
    result = await instance_service.batch_update_status(
        batch_data,
        current_user["sub"],
        tenant_id
    )
    
    return BatchOperationResponse(
        total_count=result.get("total", 0),
        success_count=result.get("success", 0),
        failed_count=result.get("failed", 0),
        errors=result.get("errors", []),
        message="批量更新实例状态完成"
    )


@router.get(
    "/{instance_id}/executions",
    response_model=PaginatedResponse[Dict[str, Any]],
    summary="获取实例执行记录",
    description="获取指定实例的所有执行记录",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"},
        404: {"description": "实例不存在"}
    }
)
@handle_service_exceptions
async def get_instance_executions(
    instance_id: UUID,
    execution_status: Optional[str] = Query(None, description="执行状态筛选"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_view)
) -> PaginatedResponse[Dict[str, Any]]:
    """
    获取实例执行记录
    
    - **权限要求**: scenario:instance:view
    - **租户隔离**: 是
    - **支持筛选**: 执行状态、时间范围
    """
    skip = (page - 1) * page_size
    executions, total = await instance_service.get_instance_executions(
        instance_id, tenant_id, execution_status, start_date, end_date, skip, page_size
    )
    
    return PaginatedResponse.create(
        data=executions,
        total=total,
        page=page,
        page_size=page_size,
        message="获取实例执行记录成功"
    )


@router.get(
    "/{instance_id}/statistics",
    response_model=DataResponse[Dict[str, Any]],
    summary="获取实例统计信息",
    description="获取实例的执行统计和性能数据",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"},
        404: {"description": "实例不存在"}
    }
)
@handle_service_exceptions
async def get_instance_statistics(
    instance_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    instance_service: ScenarioInstanceService = Depends(get_scenario_instance_service),
    _: Dict[str, Any] = Depends(require_instance_view)
) -> DataResponse[Dict[str, Any]]:
    """
    获取实例统计信息
    
    - **权限要求**: scenario:instance:view
    - **租户隔离**: 是
    - **统计信息**: 执行次数、成功率、平均执行时间等
    """
    statistics = await instance_service.get_instance_statistics(instance_id, tenant_id)
    
    return DataResponse(
        data=statistics,
        message="获取实例统计信息成功"
    ) 