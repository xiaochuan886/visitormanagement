"""
场景模板 API 路由
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
    require_template_view, require_template_create, 
    require_template_edit, require_template_delete,
    require_system_admin
)
from ..dependencies.services import get_scenario_template_service

# API响应模型
from ..models.base_response import (
    DataResponse, PaginatedResponse, OperationResponse, 
    BatchOperationResponse, ErrorCodes
)

# DTO模型
from ...application.dto.scenario_dto import (
    ScenarioTemplateCreateDTO, ScenarioTemplateUpdateDTO, 
    ScenarioTemplateResponseDTO, ScenarioTemplateQueryDTO, 
    ScenarioTemplateCategory
)

# 应用服务
from ...application.services.scenario_service import ScenarioTemplateService

# 异常处理
from ...domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, ConfigurationValidationError, 
    ConfigurationConflictError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["场景模板"])


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
    response_model=DataResponse[ScenarioTemplateResponseDTO],
    status_code=status.HTTP_201_CREATED,
    summary="创建场景模板",
    description="创建新的场景模板，需要模板创建权限",
    responses={
        201: {"description": "场景模板创建成功"},
        400: {"description": "请求参数错误"},
        403: {"description": "权限不足"},
        409: {"description": "模板代码冲突"},
        422: {"description": "数据验证失败"}
    }
)
@handle_service_exceptions
async def create_scenario_template(
    template_data: ScenarioTemplateCreateDTO,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_create)
) -> DataResponse[ScenarioTemplateResponseDTO]:
    """
    创建场景模板
    
    - **权限要求**: scenario:template:create
    - **租户隔离**: 是
    - **操作审计**: 是
    
    **请求示例**:
    ```json
    {
        "template_name": "标准访客登记",
        "template_code": "visitor_checkin_standard",
        "template_category": "visitor_management",
        "template_description": "标准的访客登记流程",
        "scenario_features": {
            "form_steps": ["identity_verification", "information_input"],
            "required_fields": ["name", "phone", "company"]
        },
        "default_configurations": {
            "max_duration": 480,
            "notification_enabled": true
        }
    }
    ```
    """
    result = await template_service.create_template(
        template_data, 
        current_user["sub"],
        tenant_id
    )
    
    return DataResponse(
        data=result,
        message="场景模板创建成功"
    )


@router.get(
    "",
    response_model=PaginatedResponse[ScenarioTemplateResponseDTO],
    summary="获取场景模板列表",
    description="分页获取场景模板列表，支持筛选和搜索",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"}
    }
)
@handle_service_exceptions
async def list_scenario_templates(
    template_category: Optional[ScenarioTemplateCategory] = Query(
        None, description="模板分类筛选"
    ),
    is_builtin: Optional[bool] = Query(
        None, description="是否为内置模板"
    ),
    is_template_active: Optional[bool] = Query(
        None, description="是否激活"
    ),
    search: Optional[str] = Query(
        None, description="搜索关键词（模板名称、代码、描述）"
    ),
    template_tags: Optional[List[str]] = Query(
        None, description="模板标签筛选"
    ),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_view)
) -> PaginatedResponse[ScenarioTemplateResponseDTO]:
    """
    获取场景模板列表
    
    - **权限要求**: scenario:template:view
    - **支持分页**: 是，最大每页100条
    - **支持筛选**: 分类、状态、标签
    - **支持搜索**: 模板名称、代码、描述
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
    "/{template_id}",
    response_model=DataResponse[ScenarioTemplateResponseDTO],
    summary="获取场景模板详情",
    description="根据ID获取场景模板的详细信息",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"},
        404: {"description": "模板不存在"}
    }
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
    "/{template_id}",
    response_model=DataResponse[ScenarioTemplateResponseDTO],
    summary="更新场景模板",
    description="更新指定的场景模板信息",
    responses={
        200: {"description": "更新成功"},
        403: {"description": "权限不足"},
        404: {"description": "模板不存在"},
        422: {"description": "数据验证失败"}
    }
)
@handle_service_exceptions
async def update_scenario_template(
    template_id: UUID,
    update_data: ScenarioTemplateUpdateDTO,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_edit)
) -> DataResponse[ScenarioTemplateResponseDTO]:
    """
    更新场景模板
    
    - **权限要求**: scenario:template:edit
    - **租户隔离**: 是
    - **操作审计**: 是
    - **限制**: 内置模板不能修改核心属性
    """
    template = await template_service.update_template(
        template_id, 
        update_data, 
        current_user["sub"],
        tenant_id
    )
    
    return DataResponse(
        data=template,
        message="场景模板更新成功"
    )


@router.delete(
    "/{template_id}",
    response_model=OperationResponse,
    summary="删除场景模板",
    description="删除指定的场景模板（软删除）",
    responses={
        200: {"description": "删除成功"},
        403: {"description": "权限不足"},
        404: {"description": "模板不存在"},
        409: {"description": "模板正在使用中，无法删除"}
    }
)
@handle_service_exceptions
async def delete_scenario_template(
    template_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_delete)
) -> OperationResponse:
    """
    删除场景模板
    
    - **权限要求**: scenario:template:delete
    - **删除方式**: 软删除
    - **操作审计**: 是
    - **限制**: 内置模板不能删除，有实例引用的模板不能删除
    """
    await template_service.delete_template(
        template_id, 
        current_user["sub"],
        tenant_id
    )
    
    return OperationResponse(
        message="场景模板删除成功",
        affected_count=1
    )


@router.post(
    "/initialize-builtin",
    response_model=BatchOperationResponse,
    summary="初始化内置模板",
    description="初始化系统预制的场景模板",
    responses={
        200: {"description": "初始化成功"},
        403: {"description": "权限不足"}
    }
)
@handle_service_exceptions
async def initialize_builtin_templates(
    tenant_id: str = Depends(get_current_tenant),
    current_user: Dict[str, Any] = Depends(get_current_user),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_system_admin)
) -> BatchOperationResponse:
    """
    初始化内置模板
    
    - **权限要求**: scenario:system:admin
    - **操作类型**: 批量操作
    - **租户隔离**: 是
    - **幂等性**: 已存在的模板不会重复创建
    """
    result = await template_service.initialize_builtin_templates(
        current_user["sub"],
        tenant_id
    )
    
    return BatchOperationResponse(
        total_count=result.get("total", 0),
        success_count=result.get("success", 0),
        failed_count=result.get("failed", 0),
        errors=result.get("errors", []),
        message="内置模板初始化完成"
    )


@router.get(
    "/{template_id}/instances",
    response_model=PaginatedResponse[Dict[str, Any]],
    summary="获取模板关联的实例",
    description="获取基于该模板创建的所有场景实例",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"},
        404: {"description": "模板不存在"}
    }
)
@handle_service_exceptions
async def get_template_instances(
    template_id: UUID,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_view)
) -> PaginatedResponse[Dict[str, Any]]:
    """
    获取模板关联的实例
    
    - **权限要求**: scenario:template:view
    - **租户隔离**: 是
    - **用途**: 查看模板使用情况
    """
    skip = (page - 1) * page_size
    instances, total = await template_service.get_template_instances(
        template_id, tenant_id, skip, page_size
    )
    
    return PaginatedResponse.create(
        data=instances,
        total=total,
        page=page,
        page_size=page_size,
        message="获取模板实例列表成功"
    )


@router.get(
    "/{template_id}/usage-stats",
    response_model=DataResponse[Dict[str, Any]],
    summary="获取模板使用统计",
    description="获取模板的使用统计信息",
    responses={
        200: {"description": "获取成功"},
        403: {"description": "权限不足"},
        404: {"description": "模板不存在"}
    }
)
@handle_service_exceptions
async def get_template_usage_stats(
    template_id: UUID,
    tenant_id: str = Depends(get_current_tenant),
    template_service: ScenarioTemplateService = Depends(get_scenario_template_service),
    _: Dict[str, Any] = Depends(require_template_view)
) -> DataResponse[Dict[str, Any]]:
    """
    获取模板使用统计
    
    - **权限要求**: scenario:template:view
    - **租户隔离**: 是
    - **统计信息**: 使用次数、实例数量、最近使用时间等
    """
    stats = await template_service.get_template_usage_stats(template_id, tenant_id)
    
    return DataResponse(
        data=stats,
        message="获取模板使用统计成功"
    ) 