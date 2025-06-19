"""
场景管理 API 路由
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database.connection import get_db_session
from ...api.dependencies.auth import get_current_user
from ...api.dependencies.tenant import get_tenant_id
from ...application.dto.scenario_dto import (
    # 场景模板 DTOs
    ScenarioTemplateCreateDTO, ScenarioTemplateUpdateDTO, ScenarioTemplateResponseDTO,
    ScenarioTemplateQueryDTO, ScenarioTemplateCategory,
    
    # 场景实例 DTOs
    ScenarioInstanceCreateDTO, ScenarioInstanceUpdateDTO, ScenarioInstanceResponseDTO,
    ScenarioInstanceQueryDTO, ScenarioInstanceStatus, ScenarioInstanceCloneDTO,
    ScenarioInstanceBatchUpdateDTO, ScenarioInstanceBatchActivateDTO,
    
    # 场景执行 DTOs
    ScenarioExecutionCreateDTO, ScenarioExecutionUpdateDTO, ScenarioExecutionResponseDTO,
    ScenarioExecutionQueryDTO, ScenarioExecutionStatus, ScenarioExecutionType,
    
    # 场景路由 DTOs
    ScenarioRoutingRuleCreateDTO, ScenarioRoutingRuleUpdateDTO, ScenarioRoutingRuleResponseDTO,
    
    # 分析 DTOs
    ScenarioAnalyticsResponseDTO,
    
    # 导入导出 DTOs
    ScenarioTemplateExportDTO, ScenarioTemplateImportDTO
)
from ...application.services.scenario_service import ScenarioTemplateService, ScenarioInstanceService
from ...application.services.scenario_routing_service import ScenarioRoutingService
from ...application.services.scenario_execution_service import ScenarioExecutionService
from ...domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, ConfigurationValidationError, ConfigurationConflictError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scenarios", tags=["场景管理"])


# ================== 场景模板 API ==================

@router.post("/templates", response_model=ScenarioTemplateResponseDTO, status_code=201)
async def create_scenario_template(
    template_data: ScenarioTemplateCreateDTO,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """创建场景模板"""
    try:
        service = ScenarioTemplateService(db)
        result = await service.create_template(
            template_data, 
            current_user["user_id"],
            tenant_id
        )
        return result
        
    except ConfigurationConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ConfigurationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"创建场景模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/templates", response_model=Dict[str, Any])
async def list_scenario_templates(
    template_category: Optional[ScenarioTemplateCategory] = None,
    is_builtin: Optional[bool] = None,
    is_template_active: Optional[bool] = None,
    search: Optional[str] = None,
    template_tags: Optional[List[str]] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """列出场景模板"""
    try:
        query = ScenarioTemplateQueryDTO(
            template_category=template_category,
            is_builtin=is_builtin,
            is_template_active=is_template_active,
            search=search,
            template_tags=template_tags
        )
        
        service = ScenarioTemplateService(db)
        templates, total = await service.list_templates(query, tenant_id, skip, limit)
        
        return {
            "items": templates,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
        
    except Exception as e:
        logger.error(f"列出场景模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/templates/{template_id}", response_model=ScenarioTemplateResponseDTO)
async def get_scenario_template(
    template_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """获取场景模板详情"""
    try:
        service = ScenarioTemplateService(db)
        return await service.get_template(template_id, tenant_id)
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取场景模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.put("/templates/{template_id}", response_model=ScenarioTemplateResponseDTO)
async def update_scenario_template(
    template_id: UUID,
    update_data: ScenarioTemplateUpdateDTO,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """更新场景模板"""
    try:
        service = ScenarioTemplateService(db)
        return await service.update_template(
            template_id,
            update_data,
            current_user["user_id"],
            tenant_id
        )
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConfigurationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"更新场景模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.delete("/templates/{template_id}")
async def delete_scenario_template(
    template_id: UUID,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """删除场景模板"""
    try:
        service = ScenarioTemplateService(db)
        await service.delete_template(template_id, current_user["user_id"], tenant_id)
        return {"message": "场景模板删除成功"}
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConfigurationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"删除场景模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


# ================== 场景实例 API ==================

@router.post("/instances", response_model=ScenarioInstanceResponseDTO, status_code=201)
async def create_scenario_instance(
    instance_data: ScenarioInstanceCreateDTO,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """创建场景实例"""
    try:
        service = ScenarioInstanceService(db)
        result = await service.create_instance(
            instance_data,
            current_user["user_id"],
            tenant_id
        )
        return result
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConfigurationConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ConfigurationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"创建场景实例失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/instances", response_model=Dict[str, Any])
async def list_scenario_instances(
    template_id: Optional[UUID] = None,
    instance_status: Optional[ScenarioInstanceStatus] = None,
    auto_routing_enabled: Optional[bool] = None,
    applicable_sites: Optional[List[str]] = Query(None),
    applicable_departments: Optional[List[str]] = Query(None),
    applicable_roles: Optional[List[str]] = Query(None),
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """列出场景实例"""
    try:
        query = ScenarioInstanceQueryDTO(
            template_id=template_id,
            instance_status=instance_status,
            auto_routing_enabled=auto_routing_enabled,
            applicable_sites=applicable_sites,
            applicable_departments=applicable_departments,
            applicable_roles=applicable_roles,
            search=search
        )
        
        service = ScenarioInstanceService(db)
        instances, total = await service.list_instances(query, tenant_id, skip, limit)
        
        return {
            "items": instances,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
        
    except Exception as e:
        logger.error(f"列出场景实例失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/instances/{instance_id}", response_model=ScenarioInstanceResponseDTO)
async def get_scenario_instance(
    instance_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """获取场景实例详情"""
    try:
        service = ScenarioInstanceService(db)
        return await service.get_instance(instance_id, tenant_id)
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取场景实例失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/instances/{instance_id}/clone", response_model=ScenarioInstanceResponseDTO)
async def clone_scenario_instance(
    instance_id: UUID,
    clone_data: ScenarioInstanceCloneDTO,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """克隆场景实例"""
    try:
        # 这里需要实现克隆逻辑
        # service = ScenarioInstanceService(db)
        # return await service.clone_instance(clone_data, current_user["user_id"], tenant_id)
        
        raise HTTPException(status_code=501, detail="克隆功能暂未实现")
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"克隆场景实例失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


# ================== 场景执行 API ==================

@router.post("/executions", response_model=ScenarioExecutionResponseDTO, status_code=201)
async def create_scenario_execution(
    execution_data: ScenarioExecutionCreateDTO,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """创建场景执行"""
    try:
        service = ScenarioExecutionService(db)
        result = await service.create_execution(
            execution_data,
            current_user["user_id"],
            tenant_id
        )
        return result
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConfigurationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"创建场景执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/executions", response_model=Dict[str, Any])
async def list_scenario_executions(
    scenario_instance_id: Optional[UUID] = None,
    execution_status: Optional[ScenarioExecutionStatus] = None,
    execution_type: Optional[ScenarioExecutionType] = None,
    target_entity_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """列出场景执行"""
    try:
        query = ScenarioExecutionQueryDTO(
            scenario_instance_id=scenario_instance_id,
            execution_status=execution_status,
            execution_type=execution_type,
            target_entity_type=target_entity_type
        )
        
        service = ScenarioExecutionService(db)
        executions, total = await service.list_executions(query, tenant_id, skip, limit)
        
        return {
            "items": executions,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
        
    except Exception as e:
        logger.error(f"列出场景执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/executions/{execution_id}", response_model=ScenarioExecutionResponseDTO)
async def get_scenario_execution(
    execution_id: UUID,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """获取场景执行详情"""
    try:
        service = ScenarioExecutionService(db)
        return await service.get_execution(execution_id, tenant_id)
        
    except ConfigurationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取场景执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


# ================== 智能路由 API ==================

@router.post("/route", response_model=Dict[str, Any])
async def route_scenario(
    context: Dict[str, Any],
    entity_type: str = Query(..., description="实体类型"),
    entity_id: str = Query(..., description="实体ID"),
    auto_execute: bool = Query(False, description="是否自动执行匹配的场景"),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """智能场景路由"""
    try:
        routing_service = ScenarioRoutingService(db)
        
        # 执行场景路由
        matched_scenarios = await routing_service.route_scenario(
            context=context,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=current_user["user_id"],
            tenant_id=tenant_id
        )
        
        result = {
            "matched_scenarios": matched_scenarios,
            "count": len(matched_scenarios),
            "auto_executed": False,
            "executions": []
        }
        
        # 如果启用自动执行
        if auto_execute and matched_scenarios:
            executions = await routing_service.execute_matched_scenarios(
                scenarios=matched_scenarios,
                context=context,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=current_user["user_id"],
                tenant_id=tenant_id
            )
            
            result["auto_executed"] = True
            result["executions"] = executions
        
        return result
        
    except Exception as e:
        logger.error(f"智能路由失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.post("/routing-rules", response_model=ScenarioRoutingRuleResponseDTO, status_code=201)
async def create_routing_rule(
    rule_data: ScenarioRoutingRuleCreateDTO,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """创建路由规则"""
    try:
        service = ScenarioRoutingService(db)
        result = await service.create_routing_rule(
            rule_data,
            current_user["user_id"],
            tenant_id
        )
        return result
        
    except ConfigurationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"创建路由规则失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


# ================== 预制场景模板初始化 API ==================

@router.post("/templates/initialize-builtin")
async def initialize_builtin_templates(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """初始化四大核心场景模板"""
    try:
        service = ScenarioTemplateService(db)
        
        # 四大核心场景模板定义
        builtin_templates = [
            {
                "template_name": "访客自主申请",
                "template_code": "visitor_self_register",
                "template_category": ScenarioTemplateCategory.VISITOR_MANAGEMENT,
                "template_description": "访客通过系统自主申请访问",
                "is_builtin": True,
                "scenario_features": {
                    "registration_type": "self_service",
                    "approval_required": True,
                    "auto_approval_rules": ["company_whitelist", "frequent_visitor"],
                    "supported_channels": ["web", "mobile", "wechat"]
                },
                "default_configurations": {
                    "form_config": {
                        "form_schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "title": "访客姓名"},
                                "phone": {"type": "string", "title": "手机号码"},
                                "company": {"type": "string", "title": "公司名称"},
                                "purpose": {"type": "string", "title": "访问目的"},
                                "expected_date": {"type": "string", "format": "date", "title": "预计访问日期"},
                                "expected_time": {"type": "string", "format": "time", "title": "预计访问时间"}
                            },
                            "required": ["name", "phone", "company", "purpose", "expected_date"]
                        },
                        "validation_schema": {
                            "required_fields": ["name", "phone", "company", "purpose"],
                            "field_rules": {
                                "phone": {"type": "string", "pattern": "^1[3-9]\\d{9}$"},
                                "name": {"type": "string", "min_length": 2, "max_length": 50}
                            }
                        }
                    },
                    "workflow_config": {
                        "workflow_steps": [
                            {"step_type": "validate_form", "config": {"critical": True}},
                            {"step_type": "check_blacklist", "config": {"critical": True}},
                            {"step_type": "auto_approve_check", "config": {"critical": False}},
                            {"step_type": "manual_review", "config": {"critical": True, "condition": "!auto_approved"}},
                            {"step_type": "notify_visitor", "config": {"critical": False}},
                            {"step_type": "generate_qr_code", "config": {"critical": False}}
                        ]
                    },
                    "business_rules": [
                        {
                            "rule_name": "公司白名单自动审批",
                            "rule_conditions": {
                                "conditions": [
                                    {"field": "visitor.company_name", "operator": "in", "value": ["阿里巴巴", "腾讯", "百度"]}
                                ]
                            },
                            "rule_actions": [
                                {"action_type": "update_status", "params": {"status": "auto_approved"}}
                            ],
                            "critical": False
                        }
                    ]
                },
                "supported_roles": ["visitor", "employee", "security"],
                "trigger_conditions": {
                    "conditions": [
                        {"field": "registration_type", "operator": "eq", "value": "self_service"},
                        {"field": "entity_type", "operator": "eq", "value": "visitor"}
                    ]
                },
                "template_tags": ["访客管理", "自主申请", "基础场景"]
            },
            {
                "template_name": "员工邀约已知访客",
                "template_code": "employee_invite_known",
                "template_category": ScenarioTemplateCategory.VISITOR_MANAGEMENT,
                "template_description": "员工邀约已知访客快速通道",
                "is_builtin": True,
                "scenario_features": {
                    "registration_type": "employee_invite",
                    "visitor_type": "known",
                    "approval_required": False,
                    "fast_track": True
                },
                "default_configurations": {
                    "form_config": {
                        "form_schema": {
                            "type": "object", 
                            "properties": {
                                "visitor_id": {"type": "string", "title": "访客ID"},
                                "visit_date": {"type": "string", "format": "date", "title": "访问日期"},
                                "visit_time": {"type": "string", "format": "time", "title": "访问时间"},
                                "purpose": {"type": "string", "title": "访问目的"}
                            },
                            "required": ["visitor_id", "visit_date", "purpose"]
                        }
                    },
                    "workflow_config": {
                        "workflow_steps": [
                            {"step_type": "validate_visitor", "config": {"critical": True}},
                            {"step_type": "check_employee_permission", "config": {"critical": True}},
                            {"step_type": "auto_approve", "config": {"critical": False}},
                            {"step_type": "notify_security", "config": {"critical": False}}
                        ]
                    }
                },
                "supported_roles": ["employee", "security"],
                "trigger_conditions": {
                    "conditions": [
                        {"field": "registration_type", "operator": "eq", "value": "employee_invite"},
                        {"field": "visitor_type", "operator": "eq", "value": "known"}
                    ]
                },
                "template_tags": ["员工邀约", "已知访客", "快速通道"]
            },
            {
                "template_name": "员工邀约未知访客",
                "template_code": "employee_invite_unknown",
                "template_category": ScenarioTemplateCategory.VISITOR_MANAGEMENT,
                "template_description": "员工邀约未知访客，需要填写详细信息",
                "is_builtin": True,
                "scenario_features": {
                    "registration_type": "employee_invite",
                    "visitor_type": "unknown",
                    "approval_required": True,
                    "detailed_form": True
                },
                "default_configurations": {
                    "form_config": {
                        "form_schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "title": "访客姓名"},
                                "phone": {"type": "string", "title": "手机号码"},
                                "company": {"type": "string", "title": "公司名称"},
                                "id_number": {"type": "string", "title": "身份证号"},
                                "purpose": {"type": "string", "title": "访问目的"},
                                "visit_date": {"type": "string", "format": "date", "title": "访问日期"},
                                "visit_time": {"type": "string", "format": "time", "title": "访问时间"},
                                "meeting_room": {"type": "string", "title": "会议室"}
                            },
                            "required": ["name", "phone", "company", "purpose", "visit_date"]
                        }
                    },
                    "workflow_config": {
                        "workflow_steps": [
                            {"step_type": "validate_form", "config": {"critical": True}},
                            {"step_type": "check_employee_permission", "config": {"critical": True}},
                            {"step_type": "manager_approval", "config": {"critical": True}},
                            {"step_type": "security_review", "config": {"critical": False}},
                            {"step_type": "notify_visitor", "config": {"critical": False}}
                        ]
                    }
                },
                "supported_roles": ["employee", "manager", "security"],
                "trigger_conditions": {
                    "conditions": [
                        {"field": "registration_type", "operator": "eq", "value": "employee_invite"},
                        {"field": "visitor_type", "operator": "eq", "value": "unknown"}
                    ]
                },
                "template_tags": ["员工邀约", "未知访客", "详细审核"]
            },
            {
                "template_name": "访客批量邀约",
                "template_code": "visitor_batch_invite",
                "template_category": ScenarioTemplateCategory.VISITOR_MANAGEMENT,
                "template_description": "批量邀约访客，支持Excel导入",
                "is_builtin": True,
                "scenario_features": {
                    "registration_type": "batch_invite",
                    "batch_processing": True,
                    "excel_import": True,
                    "approval_required": True
                },
                "default_configurations": {
                    "form_config": {
                        "form_schema": {
                            "type": "object",
                            "properties": {
                                "event_name": {"type": "string", "title": "活动名称"},
                                "event_date": {"type": "string", "format": "date", "title": "活动日期"},
                                "event_time": {"type": "string", "format": "time", "title": "活动时间"},
                                "location": {"type": "string", "title": "活动地点"},
                                "visitor_list": {"type": "array", "title": "访客列表"},
                                "batch_file": {"type": "string", "title": "批量导入文件"}
                            },
                            "required": ["event_name", "event_date", "location"]
                        }
                    },
                    "workflow_config": {
                        "workflow_steps": [
                            {"step_type": "validate_batch_data", "config": {"critical": True}},
                            {"step_type": "process_excel", "config": {"critical": True}},
                            {"step_type": "batch_validation", "config": {"critical": True}},
                            {"step_type": "manager_approval", "config": {"critical": True}},
                            {"step_type": "batch_notification", "config": {"critical": False}}
                        ]
                    }
                },
                "supported_roles": ["employee", "manager", "admin"],
                "trigger_conditions": {
                    "conditions": [
                        {"field": "registration_type", "operator": "eq", "value": "batch_invite"},
                        {"field": "entity_type", "operator": "eq", "value": "event"}
                    ]
                },
                "template_tags": ["批量邀约", "Excel导入", "活动管理"]
            }
        ]
        
        created_templates = []
        
        for template_config in builtin_templates:
            try:
                # 检查是否已存在
                existing = await service._get_template_by_code(
                    template_config["template_code"], tenant_id
                )
                
                if existing:
                    logger.info(f"内置模板已存在，跳过: {template_config['template_code']}")
                    continue
                
                # 创建模板
                template_dto = ScenarioTemplateCreateDTO(**template_config)
                template = await service.create_template(
                    template_dto,
                    current_user["user_id"],
                    tenant_id
                )
                created_templates.append(template)
                
                logger.info(f"创建内置模板成功: {template.template_name}")
                
            except Exception as e:
                logger.error(f"创建内置模板失败: {template_config['template_name']}, error: {str(e)}")
                continue
        
        return {
            "message": f"成功初始化 {len(created_templates)} 个内置场景模板",
            "created_templates": created_templates
        }
        
    except Exception as e:
        logger.error(f"初始化内置模板失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


# ================== 场景统计和分析 API ==================

@router.get("/analytics/summary")
async def get_scenario_analytics_summary(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db_session)
):
    """获取场景分析摘要"""
    try:
        # 这里可以实现场景使用统计和分析
        # 暂时返回简单的统计信息
        
        return {
            "total_templates": 0,
            "total_instances": 0,
            "total_executions": 0,
            "success_rate": 0.0,
            "avg_execution_time": 0.0,
            "top_scenarios": [],
            "recent_executions": []
        }
        
    except Exception as e:
        logger.error(f"获取场景分析摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误") 