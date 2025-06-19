"""
场景管理服务 - 利用现有配置引擎实现动态场景管理
"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update, delete
from sqlalchemy.orm import selectinload, joinedload

from ..dto.scenario_dto import (
    ScenarioTemplateCreateDTO, ScenarioTemplateUpdateDTO, ScenarioTemplateResponseDTO,
    ScenarioInstanceCreateDTO, ScenarioInstanceUpdateDTO, ScenarioInstanceResponseDTO,
    ScenarioExecutionCreateDTO, ScenarioExecutionUpdateDTO, ScenarioExecutionResponseDTO,
    ScenarioRoutingRuleCreateDTO, ScenarioRoutingRuleUpdateDTO, ScenarioRoutingRuleResponseDTO,
    ScenarioTemplateQueryDTO, ScenarioInstanceQueryDTO, ScenarioExecutionQueryDTO,
    ScenarioInstanceCloneDTO, ScenarioTemplateCategory, ScenarioInstanceStatus
)
from ...infrastructure.database.models import (
    ScenarioTemplateModel, ScenarioInstanceModel, ScenarioExecutionModel, 
    ScenarioRoutingRuleModel, ScenarioAnalyticsModel
)
from ...domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, ConfigurationValidationError, ConfigurationConflictError
)

# 集成现有配置引擎服务
from .form_configuration_service import FormConfigurationService
from .workflow_configuration_service import WorkflowConfigurationService
from .business_rule_service import BusinessRuleService
from .spatial_configuration_service import SpatialConfigurationService

logger = logging.getLogger(__name__)


class ScenarioTemplateService:
    """场景模板服务 - 管理可复用的场景模板"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        # 注入配置引擎服务
        self.form_service = FormConfigurationService(db_session)
        self.workflow_service = WorkflowConfigurationService(db_session)
        self.business_rule_service = BusinessRuleService(db_session)
        self.spatial_service = SpatialConfigurationService(db_session)
    
    async def create_template(
        self, 
        template_data: ScenarioTemplateCreateDTO, 
        created_by: str,
        tenant_id: str
    ) -> ScenarioTemplateResponseDTO:
        """创建场景模板"""
        try:
            # 检查模板代码唯一性
            existing = await self._get_template_by_code(template_data.template_code, tenant_id)
            if existing:
                raise ConfigurationConflictError(f"模板代码 {template_data.template_code} 已存在")
            
            # 验证默认配置的有效性
            await self._validate_default_configurations(template_data.default_configurations)
            
            # 创建模板实例
            template = ScenarioTemplateModel(
                template_name=template_data.template_name,
                template_code=template_data.template_code,
                template_category=template_data.template_category.value,
                template_description=template_data.template_description,
                is_builtin=template_data.is_builtin,
                scenario_features=template_data.scenario_features,
                default_configurations=template_data.default_configurations,
                supported_roles=template_data.supported_roles,
                trigger_conditions=template_data.trigger_conditions,
                template_tags=template_data.template_tags,
                created_by=created_by,
                updated_by=created_by,
                tenant_id=tenant_id
            )
            
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)
            
            logger.info(f"创建场景模板成功: {template.template_name} (ID: {template.id})")
            return ScenarioTemplateResponseDTO.from_orm(template)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建场景模板失败: {str(e)}")
            raise
    
    async def _validate_default_configurations(self, configs: Dict[str, Any]) -> None:
        """验证默认配置的有效性"""
        try:
            # 验证表单配置
            if "form_config" in configs:
                form_config = configs["form_config"]
                if "form_schema" in form_config:
                    # 简单验证表单schema结构
                    if not isinstance(form_config["form_schema"], dict):
                        raise ConfigurationValidationError("表单配置schema必须是字典类型")
            
            # 验证工作流配置  
            if "workflow_config" in configs:
                workflow_config = configs["workflow_config"]
                if "workflow_steps" in workflow_config:
                    if not isinstance(workflow_config["workflow_steps"], list):
                        raise ConfigurationValidationError("工作流步骤必须是列表类型")
            
            # 验证业务规则配置
            if "business_rules" in configs:
                rules = configs["business_rules"]
                if not isinstance(rules, list):
                    raise ConfigurationValidationError("业务规则必须是列表类型")
                
                for rule in rules:
                    if "rule_conditions" not in rule or "rule_actions" not in rule:
                        raise ConfigurationValidationError("业务规则必须包含条件和动作")
            
            logger.debug("默认配置验证通过")
            
        except Exception as e:
            logger.error(f"配置验证失败: {str(e)}")
            raise ConfigurationValidationError(f"配置验证失败: {str(e)}")
    
    async def _get_template_by_code(self, code: str, tenant_id: str) -> Optional[ScenarioTemplateModel]:
        """根据代码获取模板"""
        stmt = select(ScenarioTemplateModel).where(
            and_(
                ScenarioTemplateModel.template_code == code,
                ScenarioTemplateModel.tenant_id == tenant_id,
                ScenarioTemplateModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_template(self, template_id: UUID, tenant_id: str) -> ScenarioTemplateResponseDTO:
        """获取场景模板"""
        stmt = select(ScenarioTemplateModel).where(
            and_(
                ScenarioTemplateModel.id == template_id,
                ScenarioTemplateModel.tenant_id == tenant_id,
                ScenarioTemplateModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()
        
        if not template:
            raise ConfigurationNotFoundError(f"场景模板 {template_id} 不存在")
        
        return ScenarioTemplateResponseDTO.from_orm(template)
    
    async def list_templates(
        self, 
        query: ScenarioTemplateQueryDTO,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ScenarioTemplateResponseDTO], int]:
        """列出场景模板"""
        # 构建查询条件
        conditions = [
            ScenarioTemplateModel.tenant_id == tenant_id,
            ScenarioTemplateModel.is_deleted == False
        ]
        
        if query.template_category:
            conditions.append(ScenarioTemplateModel.template_category == query.template_category.value)
        
        if query.is_builtin is not None:
            conditions.append(ScenarioTemplateModel.is_builtin == query.is_builtin)
        
        if query.is_template_active is not None:
            conditions.append(ScenarioTemplateModel.is_template_active == query.is_template_active)
        
        if query.search:
            search_pattern = f"%{query.search}%"
            conditions.append(
                or_(
                    ScenarioTemplateModel.template_name.ilike(search_pattern),
                    ScenarioTemplateModel.template_description.ilike(search_pattern),
                    ScenarioTemplateModel.template_code.ilike(search_pattern)
                )
            )
        
        if query.template_tags:
            # 使用JSONB包含操作符查询标签
            for tag in query.template_tags:
                conditions.append(
                    ScenarioTemplateModel.template_tags.op('@>')([tag])
                )
        
        # 执行查询
        stmt = select(ScenarioTemplateModel).where(and_(*conditions))
        count_stmt = select(func.count(ScenarioTemplateModel.id)).where(and_(*conditions))
        
        # 获取总数
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 获取分页数据
        stmt = stmt.offset(skip).limit(limit).order_by(ScenarioTemplateModel.created_at.desc())
        result = await self.db.execute(stmt)
        templates = result.scalars().all()
        
        return [ScenarioTemplateResponseDTO.from_orm(t) for t in templates], total
    
    async def update_template(
        self,
        template_id: UUID,
        update_data: ScenarioTemplateUpdateDTO,
        updated_by: str,
        tenant_id: str
    ) -> ScenarioTemplateResponseDTO:
        """更新场景模板"""
        template = await self._get_template_by_id(template_id, tenant_id)
        if not template:
            raise ConfigurationNotFoundError(f"场景模板 {template_id} 不存在")
        
        # 检查是否是内置模板
        if template.is_builtin:
            raise ConfigurationValidationError("内置模板不允许修改")
        
        try:
            # 更新字段
            update_dict = update_data.dict(exclude_unset=True)
            
            # 验证配置更新
            if "default_configurations" in update_dict:
                await self._validate_default_configurations(update_dict["default_configurations"])
            
            # 更新版本号
            if any(key in update_dict for key in ['scenario_features', 'default_configurations']):
                update_dict['template_version'] = template.template_version + 1
            
            update_dict['updated_by'] = updated_by
            update_dict['updated_at'] = datetime.utcnow()
            
            stmt = update(ScenarioTemplateModel).where(
                and_(
                    ScenarioTemplateModel.id == template_id,
                    ScenarioTemplateModel.tenant_id == tenant_id
                )
            ).values(**update_dict)
            
            await self.db.execute(stmt)
            await self.db.commit()
            
            # 重新获取更新后的模板
            updated_template = await self._get_template_by_id(template_id, tenant_id)
            logger.info(f"更新场景模板成功: {template_id}")
            
            return ScenarioTemplateResponseDTO.from_orm(updated_template)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新场景模板失败: {str(e)}")
            raise
    
    async def _get_template_by_id(self, template_id: UUID, tenant_id: str) -> Optional[ScenarioTemplateModel]:
        """根据ID获取模板"""
        stmt = select(ScenarioTemplateModel).where(
            and_(
                ScenarioTemplateModel.id == template_id,
                ScenarioTemplateModel.tenant_id == tenant_id,
                ScenarioTemplateModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_template(self, template_id: UUID, deleted_by: str, tenant_id: str) -> bool:
        """删除场景模板（软删除）"""
        template = await self._get_template_by_id(template_id, tenant_id)
        if not template:
            raise ConfigurationNotFoundError(f"场景模板 {template_id} 不存在")
        
        if template.is_builtin:
            raise ConfigurationValidationError("内置模板不允许删除")
        
        # 检查是否有关联的实例
        instances_count = await self._count_template_instances(template_id, tenant_id)
        if instances_count > 0:
            raise ConfigurationValidationError(f"模板有 {instances_count} 个关联实例，无法删除")
        
        try:
            stmt = update(ScenarioTemplateModel).where(
                and_(
                    ScenarioTemplateModel.id == template_id,
                    ScenarioTemplateModel.tenant_id == tenant_id
                )
            ).values(
                is_deleted=True,
                deleted_by=deleted_by,
                deleted_at=datetime.utcnow()
            )
            
            await self.db.execute(stmt)
            await self.db.commit()
            
            logger.info(f"删除场景模板成功: {template_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"删除场景模板失败: {str(e)}")
            raise
    
    async def _count_template_instances(self, template_id: UUID, tenant_id: str) -> int:
        """统计模板关联的实例数量"""
        stmt = select(func.count(ScenarioInstanceModel.id)).where(
            and_(
                ScenarioInstanceModel.template_id == template_id,
                ScenarioInstanceModel.tenant_id == tenant_id,
                ScenarioInstanceModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar()


class ScenarioInstanceService:
    """场景实例服务 - 管理基于模板创建的具体场景"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.template_service = ScenarioTemplateService(db_session)
        # 配置引擎服务集成
        self.form_service = FormConfigurationService(db_session)
        self.workflow_service = WorkflowConfigurationService(db_session)
        self.business_rule_service = BusinessRuleService(db_session)
        self.spatial_service = SpatialConfigurationService(db_session)
    
    async def create_instance(
        self,
        instance_data: ScenarioInstanceCreateDTO,
        created_by: str,
        tenant_id: str
    ) -> ScenarioInstanceResponseDTO:
        """创建场景实例"""
        try:
            # 验证模板存在
            template = await self.template_service._get_template_by_id(
                instance_data.template_id, tenant_id
            )
            if not template:
                raise ConfigurationNotFoundError(f"场景模板 {instance_data.template_id} 不存在")
            
            # 检查实例代码唯一性
            existing = await self._get_instance_by_code(instance_data.instance_code, tenant_id)
            if existing:
                raise ConfigurationConflictError(f"实例代码 {instance_data.instance_code} 已存在")
            
            # 合并模板默认配置和自定义配置
            merged_config = await self._merge_configurations(
                template.default_configurations,
                {
                    "custom": instance_data.custom_configurations,
                    "form_overrides": instance_data.form_config_overrides,
                    "workflow_overrides": instance_data.workflow_config_overrides,
                    "business_rule_overrides": instance_data.business_rule_overrides,
                    "spatial_overrides": instance_data.spatial_config_overrides
                }
            )
            
            # 验证合并后的配置
            await self._validate_instance_configuration(merged_config)
            
            # 创建实例
            instance = ScenarioInstanceModel(
                instance_name=instance_data.instance_name,
                instance_code=instance_data.instance_code,
                template_id=instance_data.template_id,
                priority_level=instance_data.priority_level,
                custom_configurations=instance_data.custom_configurations,
                form_config_overrides=instance_data.form_config_overrides,
                workflow_config_overrides=instance_data.workflow_config_overrides,
                business_rule_overrides=instance_data.business_rule_overrides,
                spatial_config_overrides=instance_data.spatial_config_overrides,
                routing_rules=instance_data.routing_rules,
                trigger_conditions=instance_data.trigger_conditions,
                auto_routing_enabled=instance_data.auto_routing_enabled,
                applicable_sites=instance_data.applicable_sites,
                applicable_departments=instance_data.applicable_departments,
                applicable_roles=instance_data.applicable_roles,
                effective_from=instance_data.effective_from,
                effective_until=instance_data.effective_until,
                created_by=created_by,
                updated_by=created_by,
                tenant_id=tenant_id
            )
            
            self.db.add(instance)
            await self.db.commit()
            await self.db.refresh(instance)
            
            # 如果启用自动路由，创建或更新路由规则
            if instance_data.auto_routing_enabled:
                await self._create_auto_routing_rules(instance)
            
            logger.info(f"创建场景实例成功: {instance.instance_name} (ID: {instance.id})")
            return await self._build_instance_response(instance)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建场景实例失败: {str(e)}")
            raise
    
    async def _merge_configurations(
        self, 
        template_config: Dict[str, Any], 
        overrides: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并模板配置和覆盖配置"""
        merged = template_config.copy()
        
        # 深度合并配置
        if overrides.get("custom"):
            merged.update(overrides["custom"])
        
        # 表单配置覆盖
        if overrides.get("form_overrides"):
            if "form_config" in merged:
                merged["form_config"].update(overrides["form_overrides"])
            else:
                merged["form_config"] = overrides["form_overrides"]
        
        # 工作流配置覆盖
        if overrides.get("workflow_overrides"):
            if "workflow_config" in merged:
                merged["workflow_config"].update(overrides["workflow_overrides"])
            else:
                merged["workflow_config"] = overrides["workflow_overrides"]
        
        # 业务规则覆盖
        if overrides.get("business_rule_overrides"):
            merged["business_rules"] = overrides["business_rule_overrides"]
        
        # 空间配置覆盖
        if overrides.get("spatial_overrides"):
            if "spatial_config" in merged:
                merged["spatial_config"].update(overrides["spatial_overrides"])
            else:
                merged["spatial_config"] = overrides["spatial_overrides"]
        
        return merged
    
    async def _validate_instance_configuration(self, config: Dict[str, Any]) -> None:
        """验证实例配置的完整性"""
        try:
            # 利用现有配置引擎进行验证
            
            # 验证表单配置
            if "form_config" in config:
                form_config = config["form_config"]
                # 调用表单配置服务验证
                # 这里可以扩展为调用实际的表单验证逻辑
                if not isinstance(form_config.get("form_schema", {}), dict):
                    raise ConfigurationValidationError("表单配置格式错误")
            
            # 验证工作流配置
            if "workflow_config" in config:
                workflow_config = config["workflow_config"]
                if "workflow_steps" in workflow_config:
                    steps = workflow_config["workflow_steps"]
                    if not isinstance(steps, list) or len(steps) == 0:
                        raise ConfigurationValidationError("工作流必须包含至少一个步骤")
            
            logger.debug("实例配置验证通过")
            
        except Exception as e:
            logger.error(f"实例配置验证失败: {str(e)}")
            raise ConfigurationValidationError(f"实例配置验证失败: {str(e)}")
    
    async def _get_instance_by_code(self, code: str, tenant_id: str) -> Optional[ScenarioInstanceModel]:
        """根据代码获取实例"""
        stmt = select(ScenarioInstanceModel).where(
            and_(
                ScenarioInstanceModel.instance_code == code,
                ScenarioInstanceModel.tenant_id == tenant_id,
                ScenarioInstanceModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _create_auto_routing_rules(self, instance: ScenarioInstanceModel) -> None:
        """为实例创建自动路由规则"""
        try:
            # 基于实例的触发条件创建路由规则
            routing_rule = ScenarioRoutingRuleModel(
                rule_name=f"auto_route_{instance.instance_code}",
                rule_description=f"自动路由规则 - {instance.instance_name}",
                rule_priority=instance.priority_level * 10,  # 基于优先级计算路由优先级
                rule_conditions=instance.trigger_conditions,
                target_scenario_ids=[str(instance.id)],
                condition_logic="AND",
                match_strategy="first_match",
                tenant_id=instance.tenant_id,
                created_by=instance.created_by,
                updated_by=instance.created_by
            )
            
            self.db.add(routing_rule)
            await self.db.flush()  # 不立即提交，等待主事务完成
            
            logger.debug(f"为实例 {instance.id} 创建自动路由规则")
            
        except Exception as e:
            logger.error(f"创建自动路由规则失败: {str(e)}")
            # 路由规则创建失败不影响实例创建
    
    async def _build_instance_response(self, instance: ScenarioInstanceModel) -> ScenarioInstanceResponseDTO:
        """构建实例响应DTO"""
        # 加载关联的模板信息
        await self.db.refresh(instance, ['scenario_template'])
        
        response = ScenarioInstanceResponseDTO.from_orm(instance)
        
        # 如果需要，加载模板信息
        if instance.scenario_template:
            response.template = ScenarioTemplateResponseDTO.from_orm(instance.scenario_template)
        
        return response
    
    async def get_instance(self, instance_id: UUID, tenant_id: str) -> ScenarioInstanceResponseDTO:
        """获取场景实例"""
        stmt = select(ScenarioInstanceModel).options(
            selectinload(ScenarioInstanceModel.scenario_template)
        ).where(
            and_(
                ScenarioInstanceModel.id == instance_id,
                ScenarioInstanceModel.tenant_id == tenant_id,
                ScenarioInstanceModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise ConfigurationNotFoundError(f"场景实例 {instance_id} 不存在")
        
        return await self._build_instance_response(instance)
    
    async def list_instances(
        self,
        query: ScenarioInstanceQueryDTO,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ScenarioInstanceResponseDTO], int]:
        """列出场景实例"""
        conditions = [
            ScenarioInstanceModel.tenant_id == tenant_id,
            ScenarioInstanceModel.is_deleted == False
        ]
        
        if query.template_id:
            conditions.append(ScenarioInstanceModel.template_id == query.template_id)
        
        if query.instance_status:
            conditions.append(ScenarioInstanceModel.instance_status == query.instance_status.value)
        
        if query.auto_routing_enabled is not None:
            conditions.append(ScenarioInstanceModel.auto_routing_enabled == query.auto_routing_enabled)
        
        if query.search:
            search_pattern = f"%{query.search}%"
            conditions.append(
                or_(
                    ScenarioInstanceModel.instance_name.ilike(search_pattern),
                    ScenarioInstanceModel.instance_code.ilike(search_pattern)
                )
            )
        
        # JSONB数组查询
        if query.applicable_sites:
            for site in query.applicable_sites:
                conditions.append(
                    ScenarioInstanceModel.applicable_sites.op('@>')([site])
                )
        
        if query.applicable_departments:
            for dept in query.applicable_departments:
                conditions.append(
                    ScenarioInstanceModel.applicable_departments.op('@>')([dept])
                )
        
        if query.applicable_roles:
            for role in query.applicable_roles:
                conditions.append(
                    ScenarioInstanceModel.applicable_roles.op('@>')([role])
                )
        
        # 执行查询
        stmt = select(ScenarioInstanceModel).options(
            selectinload(ScenarioInstanceModel.scenario_template)
        ).where(and_(*conditions))
        
        count_stmt = select(func.count(ScenarioInstanceModel.id)).where(and_(*conditions))
        
        # 获取总数
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 获取分页数据
        stmt = stmt.offset(skip).limit(limit).order_by(ScenarioInstanceModel.created_at.desc())
        result = await self.db.execute(stmt)
        instances = result.scalars().all()
        
        responses = []
        for instance in instances:
            responses.append(await self._build_instance_response(instance))
        
        return responses, total 