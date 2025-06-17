"""
简化版配置引擎服务
临时解决方案，直接使用数据库会话，简化依赖关系
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.logging import LoggerMixin


class SimpleFormConfigurationService(LoggerMixin):
    """简化的表单配置服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger.info("简化表单配置服务初始化完成")
    
    async def list_form_configurations(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 10,
        form_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """获取表单配置列表"""
        try:
            from app.infrastructure.database.models import FormConfigurationModel, FormFieldConfigurationModel
            
            stmt = select(FormConfigurationModel).where(
                FormConfigurationModel.tenant_id == tenant_id
            )
            
            if form_type:
                stmt = stmt.where(FormConfigurationModel.form_type == form_type)
            if is_active is not None:
                stmt = stmt.where(FormConfigurationModel.is_active == is_active)
            
            stmt = stmt.offset(skip).limit(limit).order_by(FormConfigurationModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            configs = result.scalars().all()
            
            items = []
            for config in configs:
                # 获取表单字段
                fields_stmt = select(FormFieldConfigurationModel).where(
                    FormFieldConfigurationModel.form_config_id == config.id
                ).order_by(FormFieldConfigurationModel.field_order)
                
                fields_result = await self.session.execute(fields_stmt)
                fields = fields_result.scalars().all()
                
                form_fields = []
                for field in fields:
                    form_fields.append({
                        "id": str(field.id),
                        "field_key": field.field_key,
                        "field_label": field.field_label,
                        "field_type": str(field.field_type),
                        "field_order": field.field_order,
                        "is_required": field.is_required,
                        "is_readonly": field.is_readonly,
                        "is_visible": field.is_visible,
                        "default_value": field.default_value,
                        "placeholder_text": field.placeholder_text,
                        "help_text": field.help_text,
                        "validation_rules": field.validation_rules,
                        "field_options": field.field_options,
                        "conditional_logic": field.conditional_logic,
                        "created_at": field.created_at.isoformat()
                    })
                
                items.append({
                    "id": str(config.id),
                    "form_name": config.form_name,
                    "form_type": str(config.form_type),
                    "form_version": config.form_version,
                    "description": config.description,
                    "is_active": config.is_active,
                    "is_default": config.is_default,
                    "form_fields": form_fields,
                    "form_schema": config.form_schema,
                    "ui_schema": config.ui_schema,
                    "validation_schema": config.validation_schema,
                    "tenant_id": config.tenant_id,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                    "created_by": config.created_by,
                    "updated_by": config.updated_by
                })
            
            return items
            
        except Exception as e:
            self.logger.error(f"获取表单配置列表失败: {str(e)}")
            return []
    
    async def create_form_configuration(
        self,
        tenant_id: str,
        form_config: Dict[str, Any],
        created_by: str
    ) -> Dict[str, Any]:
        """创建表单配置"""
        try:
            from app.infrastructure.database.models import FormConfigurationModel, FormFieldConfigurationModel
            
            # 计算下一个可用的版本号
            max_version_stmt = select(func.max(FormConfigurationModel.form_version)).where(
                and_(
                    FormConfigurationModel.tenant_id == tenant_id,
                    FormConfigurationModel.form_type == form_config["form_type"]
                )
            )
            result = await self.session.execute(max_version_stmt)
            max_version = result.scalar()
            next_version = (max_version or 0) + 1
            
            # 创建表单配置 - 只设置存在的字段
            config = FormConfigurationModel(
                tenant_id=tenant_id,
                form_name=form_config["form_name"],
                form_type=form_config["form_type"],
                form_version=next_version,
                description=form_config.get("description"),
                form_schema=form_config.get("form_schema", {}),
                ui_schema=form_config.get("ui_schema", {}),
                validation_schema=form_config.get("validation_schema", {}),
                is_active=True,
                is_default=form_config.get("is_default", False),
                created_by=created_by,
                updated_by=created_by
            )
            
            self.session.add(config)
            await self.session.flush()  # 获取ID
            
            # 创建字段配置
            form_fields = []
            if "form_fields" in form_config:
                for field_data in form_config["form_fields"]:
                    field = FormFieldConfigurationModel(
                        form_config_id=config.id,
                        field_key=field_data["field_key"],
                        field_label=field_data["field_label"],
                        field_type=field_data["field_type"],
                        field_order=field_data.get("field_order", 1),
                        is_required=field_data.get("is_required", False),
                        is_readonly=field_data.get("is_readonly", False),
                        is_visible=field_data.get("is_visible", True),
                        default_value=field_data.get("default_value"),
                        placeholder_text=field_data.get("placeholder_text"),
                        help_text=field_data.get("help_text"),
                        validation_rules=field_data.get("validation_rules", {}),
                        field_options=field_data.get("field_options", {}),
                        conditional_logic=field_data.get("conditional_logic", {})
                    )
                    self.session.add(field)
                    await self.session.flush()  # 获取字段ID
                    
                    # 构建字段响应数据
                    form_fields.append({
                        "id": str(field.id),
                        "field_key": field.field_key,
                        "field_label": field.field_label,
                        "field_type": str(field.field_type),
                        "field_order": field.field_order,
                        "is_required": field.is_required,
                        "is_readonly": field.is_readonly,
                        "is_visible": field.is_visible,
                        "default_value": field.default_value,
                        "placeholder_text": field.placeholder_text,
                        "help_text": field.help_text,
                        "validation_rules": field.validation_rules,
                        "field_options": field.field_options,
                        "conditional_logic": field.conditional_logic,
                        "created_at": field.created_at.isoformat()
                    })
            
            await self.session.commit()
            
            # 返回完整的配置数据，包含所有必需字段
            return {
                "id": str(config.id),
                "form_name": config.form_name,
                "form_type": str(config.form_type),
                "form_version": config.form_version,
                "description": config.description,
                "is_active": config.is_active,
                "is_default": config.is_default,
                "form_fields": form_fields,
                "form_schema": config.form_schema,
                "ui_schema": config.ui_schema,
                "validation_schema": config.validation_schema,
                "tenant_id": config.tenant_id,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat(),
                "created_by": config.created_by,
                "updated_by": config.updated_by
            }
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"创建表单配置失败: {str(e)}")
            raise Exception(f"创建表单配置失败: {str(e)}")


class SimpleWorkflowConfigurationService(LoggerMixin):
    """简化的工作流配置服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger.info("简化工作流配置服务初始化完成")
    
    async def list_workflow_configurations(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 10,
        workflow_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """获取工作流配置列表"""
        try:
            from app.infrastructure.database.models import WorkflowConfigurationModel
            
            stmt = select(WorkflowConfigurationModel).where(
                WorkflowConfigurationModel.tenant_id == tenant_id
            )
            
            if workflow_type:
                stmt = stmt.where(WorkflowConfigurationModel.workflow_type == workflow_type)
            if is_active is not None:
                stmt = stmt.where(WorkflowConfigurationModel.is_active == is_active)
            
            stmt = stmt.offset(skip).limit(limit).order_by(WorkflowConfigurationModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            configs = result.scalars().all()
            
            items = []
            for config in configs:
                items.append({
                    "id": str(config.id),
                    "workflow_name": config.workflow_name,
                    "workflow_type": config.workflow_type,
                    "description": config.description,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat()
                })
            
            return items
            
        except Exception as e:
            self.logger.error(f"获取工作流配置列表失败: {str(e)}")
            return []


class SimpleSpatialConfigurationService(LoggerMixin):
    """简化的空间配置服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger.info("简化空间配置服务初始化完成")
    
    async def list_spatial_configurations(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """获取空间配置列表"""
        try:
            from app.infrastructure.database.models import SpatialConfigurationModel
            
            stmt = select(SpatialConfigurationModel).where(
                SpatialConfigurationModel.tenant_id == tenant_id
            )
            
            if is_active is not None:
                stmt = stmt.where(SpatialConfigurationModel.is_active == is_active)
            
            stmt = stmt.offset(skip).limit(limit).order_by(SpatialConfigurationModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            configs = result.scalars().all()
            
            items = []
            for config in configs:
                items.append({
                    "id": str(config.id),
                    "config_name": config.config_name,
                    "description": config.description,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat()
                })
            
            return items
            
        except Exception as e:
            self.logger.error(f"获取空间配置列表失败: {str(e)}")
            return []


class SimpleBusinessRuleService(LoggerMixin):
    """简化的业务规则服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger.info("简化业务规则服务初始化完成")
    
    async def list_business_rules(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 10,
        rule_category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """获取业务规则列表"""
        try:
            from app.infrastructure.database.models import BusinessRuleModel
            
            stmt = select(BusinessRuleModel).where(
                BusinessRuleModel.tenant_id == tenant_id
            )
            
            if rule_category:
                stmt = stmt.where(BusinessRuleModel.rule_category == rule_category)
            if is_active is not None:
                stmt = stmt.where(BusinessRuleModel.is_active == is_active)
            
            stmt = stmt.offset(skip).limit(limit).order_by(BusinessRuleModel.created_at.desc())
            
            result = await self.session.execute(stmt)
            rules = result.scalars().all()
            
            items = []
            for rule in rules:
                items.append({
                    "id": str(rule.id),
                    "rule_name": rule.rule_name,
                    "rule_category": rule.rule_category,
                    "description": rule.description,
                    "is_active": rule.is_active,
                    "created_at": rule.created_at.isoformat()
                })
            
            return items
            
        except Exception as e:
            self.logger.error(f"获取业务规则列表失败: {str(e)}")
            return [] 