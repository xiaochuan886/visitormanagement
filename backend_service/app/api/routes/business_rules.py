"""
业务规则管理API
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.services.business_rule_service import BusinessRuleService
from app.application.dto.business_rule_dto import (
    BusinessRuleCreateDTO,
    BusinessRuleUpdateDTO,
    BusinessRuleResponseDTO,
    BusinessRuleExecutionRequestDTO,
    BusinessRuleExecutionResultDTO,
    RuleExecutionLogResponseDTO
)
from app.api.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.core.exceptions import NotFoundError

router = APIRouter()

@router.post(
    "/",
    response_model=BusinessRuleResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建业务规则",
    description="创建新的业务规则，支持复杂的条件判断和动作执行"
)
async def create_business_rule(
    business_rule: BusinessRuleCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建业务规则"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.create_business_rule(
            tenant_id=current_user.tenant_id,
            business_rule=business_rule,
            created_by=current_user.username
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建业务规则失败: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[BusinessRuleResponseDTO],
    summary="获取业务规则列表",
    description="获取当前租户的所有业务规则列表，支持分页和筛选"
)
async def list_business_rules(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    rule_type: Optional[str] = Query(None, description="规则类型筛选"),
    rule_category: Optional[str] = Query(None, description="规则类别筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取业务规则列表"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.list_business_rules(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            rule_type=rule_type,
            rule_category=rule_category,
            is_active=is_active
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取业务规则列表失败: {str(e)}"
        )

@router.get(
    "/{rule_id}",
    response_model=BusinessRuleResponseDTO,
    summary="获取业务规则详情",
    description="根据规则ID获取业务规则的详细信息"
)
async def get_business_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取业务规则详情"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.get_business_rule(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="业务规则不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取业务规则失败: {str(e)}"
        )

@router.put(
    "/{rule_id}",
    response_model=BusinessRuleResponseDTO,
    summary="更新业务规则",
    description="更新指定的业务规则，支持部分字段更新"
)
async def update_business_rule(
    rule_id: UUID,
    business_rule: BusinessRuleUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新业务规则"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.update_business_rule(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id,
            business_rule=business_rule,
            updated_by=current_user.username
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="业务规则不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新业务规则失败: {str(e)}"
        )

@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除业务规则",
    description="软删除指定的业务规则（实际为停用）"
)
async def delete_business_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除业务规则"""
    service = BusinessRuleService(db)
    
    try:
        success = await service.delete_business_rule(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="业务规则不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除业务规则失败: {str(e)}"
        )

@router.post(
    "/{rule_id}/execute",
    response_model=BusinessRuleExecutionResultDTO,
    summary="执行业务规则",
    description="执行指定的业务规则，根据输入数据进行条件判断和动作执行"
)
async def execute_business_rule(
    rule_id: UUID,
    execution_request: BusinessRuleExecutionRequestDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """执行业务规则"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.execute_business_rule(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id,
            execution_request=execution_request,
            executed_by=current_user.username
        )
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="业务规则不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"执行业务规则失败: {str(e)}"
        )

@router.post(
    "/batch-execute",
    response_model=List[BusinessRuleExecutionResultDTO],
    summary="批量执行业务规则",
    description="根据指定条件批量执行多个业务规则"
)
async def batch_execute_business_rules(
    execution_request: BusinessRuleExecutionRequestDTO,
    rule_type: Optional[str] = Query(None, description="规则类型筛选"),
    rule_category: Optional[str] = Query(None, description="规则类别筛选"),
    rule_ids: Optional[str] = Query(None, description="指定规则ID列表，多个用逗号分隔"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量执行业务规则"""
    service = BusinessRuleService(db)
    
    try:
        # 解析规则ID列表
        rule_id_list = None
        if rule_ids:
            rule_id_list = [UUID(rid.strip()) for rid in rule_ids.split(",")]
        
        result = await service.batch_execute_business_rules(
            tenant_id=current_user.tenant_id,
            execution_request=execution_request,
            rule_type=rule_type,
            rule_category=rule_category,
            rule_ids=rule_id_list,
            executed_by=current_user.username
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"规则ID格式错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"批量执行业务规则失败: {str(e)}"
        )

@router.get(
    "/{rule_id}/executions",
    response_model=List[RuleExecutionLogResponseDTO],
    summary="获取规则执行历史",
    description="获取指定业务规则的执行历史记录"
)
async def get_rule_execution_history(
    rule_id: UUID,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    start_time: Optional[str] = Query(None, description="开始时间筛选 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间筛选 (ISO格式)"),
    execution_result: Optional[str] = Query(None, description="执行结果筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取规则执行历史"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.get_rule_execution_history(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id,
            skip=skip,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            execution_result=execution_result
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取规则执行历史失败: {str(e)}"
        )

@router.get(
    "/executions/{execution_id}",
    response_model=RuleExecutionLogResponseDTO,
    summary="获取规则执行详情",
    description="获取指定规则执行记录的详细信息"
)
async def get_rule_execution_detail(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取规则执行详情"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.get_rule_execution_detail(
            tenant_id=current_user.tenant_id,
            execution_id=execution_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="规则执行记录不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取规则执行详情失败: {str(e)}"
        )

@router.post(
    "/{rule_id}/validate",
    response_model=dict,
    summary="验证业务规则",
    description="验证业务规则的配置是否正确，包括条件语法和动作定义"
)
async def validate_business_rule(
    rule_id: UUID,
    test_data: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证业务规则"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.validate_business_rule(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id,
            test_data=test_data
        )
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="业务规则不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"验证业务规则失败: {str(e)}"
        )

@router.post(
    "/{rule_id}/activate",
    response_model=BusinessRuleResponseDTO,
    summary="激活业务规则",
    description="激活指定的业务规则，使其可用于规则执行"
)
async def activate_business_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """激活业务规则"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.activate_business_rule(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="业务规则不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"激活业务规则失败: {str(e)}"
        )

@router.post(
    "/{rule_id}/deactivate",
    response_model=BusinessRuleResponseDTO,
    summary="停用业务规则",
    description="停用指定的业务规则，阻止规则执行"
)
async def deactivate_business_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """停用业务规则"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.deactivate_business_rule(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="业务规则不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"停用业务规则失败: {str(e)}"
        )

@router.get(
    "/statistics/execution-summary",
    response_model=dict,
    summary="获取规则执行统计",
    description="获取业务规则的执行统计信息，包括成功率、平均执行时间等"
)
async def get_rule_execution_statistics(
    rule_id: Optional[UUID] = Query(None, description="指定规则ID，不指定则统计所有规则"),
    start_time: Optional[str] = Query(None, description="开始时间筛选 (ISO格式)"),
    end_time: Optional[str] = Query(None, description="结束时间筛选 (ISO格式)"),
    rule_type: Optional[str] = Query(None, description="规则类型筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取规则执行统计"""
    service = BusinessRuleService(db)
    
    try:
        result = await service.get_rule_execution_statistics(
            tenant_id=current_user.tenant_id,
            rule_id=rule_id,
            start_time=start_time,
            end_time=end_time,
            rule_type=rule_type
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取规则执行统计失败: {str(e)}"
        ) 