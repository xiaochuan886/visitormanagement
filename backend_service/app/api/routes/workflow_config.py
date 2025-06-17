"""
工作流配置管理API
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.services.workflow_configuration_service import WorkflowConfigurationService
from app.application.dto.workflow_config_dto import (
    WorkflowConfigurationCreateDTO,
    WorkflowConfigurationUpdateDTO,
    WorkflowConfigurationResponseDTO,
    WorkflowExecutionCreateDTO,
    WorkflowExecutionResponseDTO,
    WorkflowStepExecutionDTO
)
from app.api.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.core.exceptions import NotFoundError

router = APIRouter()

@router.post(
    "/",
    response_model=WorkflowConfigurationResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建工作流配置",
    description="创建新的工作流配置，支持多步骤审批流程定义"
)
async def create_workflow_configuration(
    workflow_config: WorkflowConfigurationCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建工作流配置"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.create_workflow_configuration(
            tenant_id=current_user.tenant_id,
            workflow_config=workflow_config,
            created_by=current_user.username
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建工作流配置失败: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[WorkflowConfigurationResponseDTO],
    summary="获取工作流配置列表",
    description="获取当前租户的所有工作流配置列表，支持分页和筛选"
)
async def list_workflow_configurations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    workflow_type: Optional[str] = Query(None, description="工作流类型筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流配置列表"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.list_workflow_configurations(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            workflow_type=workflow_type,
            is_active=is_active
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作流配置列表失败: {str(e)}"
        )

@router.get(
    "/{workflow_id}",
    response_model=WorkflowConfigurationResponseDTO,
    summary="获取工作流配置详情",
    description="根据工作流ID获取工作流配置的详细信息"
)
async def get_workflow_configuration(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流配置详情"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.get_workflow_configuration(
            tenant_id=current_user.tenant_id,
            workflow_id=workflow_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作流配置失败: {str(e)}"
        )

@router.put(
    "/{workflow_id}",
    response_model=WorkflowConfigurationResponseDTO,
    summary="更新工作流配置",
    description="更新指定的工作流配置，支持部分字段更新"
)
async def update_workflow_configuration(
    workflow_id: UUID,
    workflow_config: WorkflowConfigurationUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新工作流配置"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.update_workflow_configuration(
            tenant_id=current_user.tenant_id,
            workflow_id=workflow_id,
            workflow_config=workflow_config,
            updated_by=current_user.username
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新工作流配置失败: {str(e)}"
        )

@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除工作流配置",
    description="软删除指定的工作流配置（实际为停用）"
)
async def delete_workflow_configuration(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除工作流配置"""
    service = WorkflowConfigurationService(db)
    
    try:
        success = await service.delete_workflow_configuration(
            tenant_id=current_user.tenant_id,
            workflow_id=workflow_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流配置不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除工作流配置失败: {str(e)}"
        )

@router.post(
    "/{workflow_id}/execute",
    response_model=WorkflowExecutionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="启动工作流执行",
    description="基于指定的工作流配置启动一个新的工作流执行实例"
)
async def start_workflow_execution(
    workflow_id: UUID,
    execution_request: WorkflowExecutionCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """启动工作流执行"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.start_workflow_execution(
            tenant_id=current_user.tenant_id,
            workflow_id=workflow_id,
            execution_request=execution_request,
            initiated_by=current_user.username
        )
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工作流配置不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"启动工作流执行失败: {str(e)}"
        )

@router.get(
    "/{workflow_id}/executions",
    response_model=List[WorkflowExecutionResponseDTO],
    summary="获取工作流执行历史",
    description="获取指定工作流配置的所有执行历史记录"
)
async def list_workflow_executions(
    workflow_id: UUID,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    status: Optional[str] = Query(None, description="执行状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流执行历史"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.list_workflow_executions(
            tenant_id=current_user.tenant_id,
            workflow_id=workflow_id,
            skip=skip,
            limit=limit,
            status=status
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作流执行历史失败: {str(e)}"
        )

@router.get(
    "/executions/{execution_id}",
    response_model=WorkflowExecutionResponseDTO,
    summary="获取工作流执行详情",
    description="获取指定工作流执行实例的详细信息和当前状态"
)
async def get_workflow_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取工作流执行详情"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.get_workflow_execution(
            tenant_id=current_user.tenant_id,
            execution_id=execution_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流执行实例不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取工作流执行详情失败: {str(e)}"
        )

@router.post(
    "/executions/{execution_id}/step",
    response_model=WorkflowExecutionResponseDTO,
    summary="执行工作流步骤",
    description="执行工作流实例的下一个步骤，支持审批、自动处理等操作"
)
async def execute_workflow_step(
    execution_id: UUID,
    step_execution: WorkflowStepExecutionDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """执行工作流步骤"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.execute_workflow_step(
            tenant_id=current_user.tenant_id,
            execution_id=execution_id,
            step_execution=step_execution,
            executed_by=current_user.username
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流执行实例不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"执行工作流步骤失败: {str(e)}"
        )

@router.post(
    "/executions/{execution_id}/cancel",
    response_model=WorkflowExecutionResponseDTO,
    summary="取消工作流执行",
    description="取消正在进行的工作流执行实例"
)
async def cancel_workflow_execution(
    execution_id: UUID,
    reason: Optional[str] = Query(None, description="取消原因"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消工作流执行"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.cancel_workflow_execution(
            tenant_id=current_user.tenant_id,
            execution_id=execution_id,
            cancelled_by=current_user.username,
            cancel_reason=reason
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流执行实例不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"取消工作流执行失败: {str(e)}"
        )

@router.post(
    "/{workflow_id}/activate",
    response_model=WorkflowConfigurationResponseDTO,
    summary="激活工作流配置",
    description="激活指定的工作流配置，使其可用于工作流执行"
)
async def activate_workflow_configuration(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """激活工作流配置"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.activate_workflow_configuration(
            tenant_id=current_user.tenant_id,
            workflow_id=workflow_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"激活工作流配置失败: {str(e)}"
        )

@router.post(
    "/{workflow_id}/deactivate",
    response_model=WorkflowConfigurationResponseDTO,
    summary="停用工作流配置",
    description="停用指定的工作流配置，阻止新的工作流执行"
)
async def deactivate_workflow_configuration(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """停用工作流配置"""
    service = WorkflowConfigurationService(db)
    
    try:
        result = await service.deactivate_workflow_configuration(
            tenant_id=current_user.tenant_id,
            workflow_id=workflow_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"停用工作流配置失败: {str(e)}"
        ) 