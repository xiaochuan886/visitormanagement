"""
表单配置服务
提供表单配置管理的业务逻辑
"""
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.application.dto.form_config_dto import (
    FormConfigurationCreateDTO,
    FormConfigurationUpdateDTO,
    FormConfigurationResponseDTO,
    FormConfigurationQueryDTO,
    FormConfigurationListResponseDTO,
    FormValidationResultDTO,
    FormRenderDataDTO,
    FormSubmissionDTO,
    FormSubmissionResultDTO
)
from app.application.interfaces.repository import IFormConfigurationRepository, IFormFieldConfigurationRepository
from app.domain.enums.config_enums import ConfigurationStatus
from app.domain.exceptions.config_exceptions import (
    FormConfigurationException,
    FormValidationException,
    ConfigurationNotFoundException,
    DuplicateConfigurationException
)
# from app.domain.events.config_events import (
#     FormConfigurationCreated,
#     FormConfigurationUpdated,
#     FormConfigurationActivated,
#     FormConfigurationDeactivated
# )
from app.infrastructure.database.models import FormConfiguration, FormFieldConfiguration
from app.core.logging import LoggerMixin
from app.infrastructure.cache.redis_client import get_redis
# from app.core.events import EventPublisher


class FormConfigurationService(LoggerMixin):
    """表单配置服务"""
    
    def __init__(self, session):
        from app.infrastructure.repositories.form_config_repository import (
            FormConfigurationRepository, 
            FormFieldConfigurationRepository
        )
        self.session = session
        self.form_config_repo = FormConfigurationRepository(session)
        self.form_field_repo = FormFieldConfigurationRepository(session)
        # self.event_publisher = event_publisher  # 临时注释
        self.logger.info("表单配置服务初始化完成")
    
    async def create_form_configuration(
        self,
        tenant_id: str,
        form_config: FormConfigurationCreateDTO,
        created_by: str
    ) -> FormConfigurationResponseDTO:
        """创建表单配置"""
        try:
            self.logger.info(f"开始创建表单配置: {form_config.form_name}")
            
            # 检查名称重复
            existing_config = await self.form_config_repo.find_by_name(
                form_config.form_name, UUID(tenant_id)
            )
            if existing_config:
                raise DuplicateConfigurationException(
                    "表单配置", form_config.form_name, "name"
                )
            
            # 验证表单配置
            validation_result = await self._validate_form_configuration(form_config)
            if not validation_result.is_valid:
                raise FormValidationException(
                    "表单配置验证失败",
                    list(validation_result.field_errors.keys()),
                    validation_result.field_errors
                )
            
            # 获取最新版本号
            latest_version = await self.form_config_repo.get_latest_version(
                form_config.form_type.value, UUID(tenant_id)
            )
            
            # 如果设为默认，先取消其他默认配置
            if form_config.is_default:
                await self._unset_default_forms(form_config.form_type.value, tenant_id)
            
            # 创建表单配置
            form_configuration = FormConfiguration(
                form_name=form_config.form_name,
                form_type=form_config.form_type.value,
                form_version=latest_version + 1,
                description=form_config.description,
                form_schema=form_config.form_schema or {},
                ui_schema=form_config.ui_schema or {},
                validation_schema=form_config.validation_schema or {},
                is_active=True,
                is_default=form_config.is_default,
                tenant_id=tenant_id,
                created_by=created_by,
                updated_by=created_by
            )
            
            # 保存表单配置
            saved_config = await self.form_config_repo.create(form_configuration)
            
            # 创建表单字段
            for field_dto in form_config.form_fields:
                field_config = FormFieldConfiguration(
                    form_configuration_id=saved_config.id,
                    field_key=field_dto.field_key,
                    field_label=field_dto.field_label,
                    field_type=field_dto.field_type.value,
                    field_order=field_dto.field_order,
                    is_required=field_dto.is_required,
                    is_readonly=field_dto.is_readonly,
                    is_visible=field_dto.is_visible,
                    default_value=field_dto.default_value,
                    placeholder_text=field_dto.placeholder_text,
                    help_text=field_dto.help_text,
                    validation_rules=field_dto.validation_rules or {},
                    field_options=field_dto.field_options or {},
                    conditional_logic=field_dto.conditional_logic or {}
                )
                await self.form_field_repo.create(field_config)
            
            # 清除缓存
            await self._clear_form_cache(tenant_id, form_config.form_type.value)
            
            # 发布事件 (临时注释)
            # event = FormConfigurationCreated(
            #     aggregate_id=str(saved_config.id),
            #     tenant_id=tenant_id,
            #     user_id=user_id,
            #     form_type=create_dto.form_type.value,
            #     form_name=create_dto.form_name,
            #     field_count=len(create_dto.form_fields),
            #     has_validation_rules=bool(create_dto.validation_schema),
            #     has_conditional_logic=any(field.conditional_logic for field in create_dto.form_fields)
            # )
            # await self.event_publisher.publish(event)
            
            # 返回响应
            response = await self._build_form_response(saved_config)
            self.logger.info(f"表单配置创建成功: {response.id}")
            return response
            
        except Exception as e:
            self.logger.error(f"创建表单配置失败: {str(e)}")
            raise FormConfigurationException(f"创建表单配置失败: {str(e)}")
    
    async def update_form_configuration(
        self,
        config_id: UUID,
        update_dto: FormConfigurationUpdateDTO,
        tenant_id: str,
        user_id: str
    ) -> FormConfigurationResponseDTO:
        """更新表单配置"""
        try:
            self.logger.info(f"开始更新表单配置: {config_id}")
            
            # 获取现有配置
            existing_config = await self.form_config_repo.get_by_id(config_id)
            if not existing_config or existing_config.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("表单配置", str(config_id))
            
            # 记录变更前的数据
            changes = {}
            previous_version = existing_config.form_version
            
            # 更新字段
            if update_dto.form_name and update_dto.form_name != existing_config.form_name:
                # 检查名称重复
                name_exists = await self.form_config_repo.find_by_name(
                    update_dto.form_name, UUID(tenant_id)
                )
                if name_exists and name_exists.id != config_id:
                    raise DuplicateConfigurationException(
                        "表单配置", update_dto.form_name, "name"
                    )
                changes['form_name'] = {
                    'old': existing_config.form_name,
                    'new': update_dto.form_name
                }
                existing_config.form_name = update_dto.form_name
            
            if update_dto.description is not None:
                changes['description'] = {
                    'old': existing_config.description,
                    'new': update_dto.description
                }
                existing_config.description = update_dto.description
            
            if update_dto.form_schema is not None:
                changes['form_schema'] = {
                    'old': existing_config.form_schema,
                    'new': update_dto.form_schema
                }
                existing_config.form_schema = update_dto.form_schema
            
            if update_dto.ui_schema is not None:
                existing_config.ui_schema = update_dto.ui_schema
            
            if update_dto.validation_schema is not None:
                existing_config.validation_schema = update_dto.validation_schema
            
            if update_dto.is_active is not None:
                changes['is_active'] = {
                    'old': existing_config.is_active,
                    'new': update_dto.is_active
                }
                existing_config.is_active = update_dto.is_active
            
            if update_dto.is_default is not None and update_dto.is_default:
                await self._unset_default_forms(existing_config.form_type, tenant_id)
                existing_config.is_default = True
            
            # 更新字段配置
            field_changes = []
            if update_dto.form_fields is not None:
                # 删除现有字段
                await self.form_field_repo.delete_by_form_config(config_id)
                
                # 创建新字段
                for field_dto in update_dto.form_fields:
                    field_config = FormFieldConfiguration(
                        form_configuration_id=config_id,
                        field_key=field_dto.field_key,
                        field_label=field_dto.field_label,
                        field_type=field_dto.field_type.value,
                        field_order=field_dto.field_order,
                        is_required=field_dto.is_required,
                        is_readonly=field_dto.is_readonly,
                        is_visible=field_dto.is_visible,
                        default_value=field_dto.default_value,
                        placeholder_text=field_dto.placeholder_text,
                        help_text=field_dto.help_text,
                        validation_rules=field_dto.validation_rules or {},
                        field_options=field_dto.field_options or {},
                        conditional_logic=field_dto.conditional_logic or {}
                    )
                    await self.form_field_repo.create(field_config)
                    field_changes.append({
                        'action': 'updated',
                        'field_key': field_dto.field_key,
                        'field_type': field_dto.field_type.value
                    })
            
            # 增加版本号并保存
            existing_config.form_version += 1
            existing_config.updated_by = user_id
            existing_config.updated_at = datetime.utcnow()
            
            updated_config = await self.form_config_repo.update(existing_config)
            
            # 清除缓存
            await self._clear_form_cache(tenant_id, existing_config.form_type)
            
            # 发布事件
            event = FormConfigurationUpdated(
                aggregate_id=str(config_id),
                tenant_id=tenant_id,
                user_id=user_id,
                form_type=existing_config.form_type,
                form_name=existing_config.form_name,
                previous_version=previous_version,
                new_version=existing_config.form_version,
                changes=changes,
                field_changes=field_changes
            )
            # await self.event_publisher.publish(event)
            
            # 返回响应
            response = await self._build_form_response(updated_config)
            self.logger.info(f"表单配置更新成功: {config_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"更新表单配置失败: {str(e)}")
            if isinstance(e, (ConfigurationNotFoundException, DuplicateConfigurationException)):
                raise
            raise FormConfigurationException(f"更新表单配置失败: {str(e)}")
    
    async def get_form_configuration(
        self,
        config_id: UUID,
        tenant_id: str
    ) -> FormConfigurationResponseDTO:
        """获取表单配置详情"""
        try:
            self.logger.info(f"获取表单配置: {config_id}")
            
            # 先尝试从缓存获取
            cache_key = f"form_config:{tenant_id}:{config_id}"
            cache = await self._get_cache()
            cached_result = await cache.get(cache_key)
            if cached_result:
                return FormConfigurationResponseDTO.parse_raw(cached_result)
            
            # 从数据库获取
            config = await self.form_config_repo.get_by_id(config_id)
            if not config or config.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("表单配置", str(config_id))
            
            # 构建响应
            response = await self._build_form_response(config)
            
            # 缓存结果
            await cache.set(cache_key, response.json(), expire=3600)
            
            return response
            
        except Exception as e:
            self.logger.error(f"获取表单配置失败: {str(e)}")
            raise FormConfigurationException(f"获取表单配置失败: {str(e)}")
    
    async def list_form_configurations(
        self,
        query_dto: FormConfigurationQueryDTO,
        tenant_id: str
    ) -> FormConfigurationListResponseDTO:
        """查询表单配置列表"""
        try:
            filters = {"tenant_id": UUID(tenant_id)}
            
            if query_dto.form_type:
                filters["form_type"] = query_dto.form_type.value
            if query_dto.is_active is not None:
                filters["is_active"] = query_dto.is_active
            if query_dto.is_default is not None:
                filters["is_default"] = query_dto.is_default
            if query_dto.form_name:
                filters["form_name__icontains"] = query_dto.form_name
            
            # 计算分页
            skip = (query_dto.page - 1) * query_dto.page_size
            
            # 查询数据
            configs = await self.form_config_repo.find_by(filters)
            total = await self.form_config_repo.count(filters)
            
            # 分页处理
            paginated_configs = configs[skip:skip + query_dto.page_size]
            
            # 构建响应
            items = []
            for config in paginated_configs:
                response = await self._build_form_response(config)
                items.append(response)
            
            total_pages = (total + query_dto.page_size - 1) // query_dto.page_size
            
            return FormConfigurationListResponseDTO(
                items=items,
                total=total,
                page=query_dto.page,
                page_size=query_dto.page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            self.logger.error(f"查询表单配置列表失败: {str(e)}")
            raise FormConfigurationException(f"查询表单配置列表失败: {str(e)}")
    
    async def delete_form_configuration(
        self,
        config_id: UUID,
        tenant_id: str,
        user_id: str
    ) -> bool:
        """删除表单配置"""
        try:
            self.logger.info(f"开始删除表单配置: {config_id}")
            
            # 获取配置
            config = await self.form_config_repo.get_by_id(config_id)
            if not config or config.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("表单配置", str(config_id))
            
            # 删除字段配置
            await self.form_field_repo.delete_by_form_config(config_id)
            
            # 删除表单配置
            result = await self.form_config_repo.delete(config_id)
            
            if result:
                # 清除缓存
                await self._clear_form_cache(tenant_id, config.form_type)
                
                # 发布事件
                event = FormConfigurationDeactivated(
                    aggregate_id=str(config_id),
                    tenant_id=tenant_id,
                    user_id=user_id,
                    form_type=config.form_type,
                    form_name=config.form_name,
                    reason="用户删除"
                )
                # await self.event_publisher.publish(event)
                
                self.logger.info(f"表单配置删除成功: {config_id}")
            
            return result
            
        except ConfigurationNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"删除表单配置失败: {str(e)}")
            raise FormConfigurationException(f"删除表单配置失败: {str(e)}")
    
    async def get_form_render_data(
        self,
        form_type: str,
        tenant_id: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> FormRenderDataDTO:
        """获取表单渲染数据"""
        try:
            # 获取活跃的表单配置
            config = await self.form_config_repo.find_active_by_form_type(
                form_type, UUID(tenant_id)
            )
            if not config:
                raise ConfigurationNotFoundException("表单配置", form_type)
            
            # 获取字段配置
            fields = await self.form_field_repo.find_by_form_config(config.id)
            
            # 构建表单结构
            form_schema = config.form_schema or {}
            ui_schema = config.ui_schema or {}
            validation_rules = config.validation_schema or {}
            
            # 处理只读和隐藏字段
            readonly_fields = [f.field_key for f in fields if f.is_readonly]
            hidden_fields = [f.field_key for f in fields if not f.is_visible]
            
            return FormRenderDataDTO(
                form_config_id=config.id,
                form_schema=form_schema,
                ui_schema=ui_schema,
                initial_data=initial_data or {},
                readonly_fields=readonly_fields,
                hidden_fields=hidden_fields,
                validation_rules=validation_rules
            )
            
        except ConfigurationNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"获取表单渲染数据失败: {str(e)}")
            raise FormConfigurationException(f"获取表单渲染数据失败: {str(e)}")
    
    async def validate_form_data(
        self,
        form_config_id: UUID,
        form_data: Dict[str, Any],
        tenant_id: str
    ) -> FormValidationResultDTO:
        """验证表单数据"""
        try:
            start_time = datetime.utcnow()
            
            # 获取表单配置
            config = await self.form_config_repo.get_by_id(form_config_id)
            if not config or config.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("表单配置", str(form_config_id))
            
            # 获取字段配置
            fields = await self.form_field_repo.find_by_form_config(form_config_id)
            
            errors = []
            warnings = []
            field_errors = {}
            
            # 验证每个字段
            for field in fields:
                field_value = form_data.get(field.field_key)
                field_validation_errors = []
                
                # 必填验证
                if field.is_required and (field_value is None or field_value == ""):
                    field_validation_errors.append(f"{field.field_label} 是必填项")
                
                # 类型验证
                if field_value is not None:
                    validation_errors = await self._validate_field_value(
                        field, field_value
                    )
                    field_validation_errors.extend(validation_errors)
                
                if field_validation_errors:
                    field_errors[field.field_key] = field_validation_errors
                    errors.extend([{
                        "field": field.field_key,
                        "message": error
                    } for error in field_validation_errors])
            
            # 计算验证耗时
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return FormValidationResultDTO(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                field_errors=field_errors,
                validation_duration_ms=duration_ms
            )
            
        except ConfigurationNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"表单数据验证失败: {str(e)}")
            raise FormConfigurationException(f"表单数据验证失败: {str(e)}")
    
    # 私有辅助方法
    
    async def _validate_form_configuration(
        self,
        config_dto: FormConfigurationCreateDTO
    ) -> FormValidationResultDTO:
        """验证表单配置"""
        errors = []
        warnings = []
        field_errors = {}
        
        # 验证表单字段
        field_keys = set()
        field_orders = set()
        
        for field in config_dto.form_fields:
            # 检查字段键名重复
            if field.field_key in field_keys:
                field_errors.setdefault(field.field_key, []).append("字段键名重复")
            field_keys.add(field.field_key)
            
            # 检查字段顺序重复
            if field.field_order in field_orders:
                field_errors.setdefault(field.field_key, []).append("字段顺序重复")
            field_orders.add(field.field_order)
        
        return FormValidationResultDTO(
            is_valid=len(field_errors) == 0,
            errors=errors,
            warnings=warnings,
            field_errors=field_errors,
            validation_duration_ms=0
        )
    
    async def _validate_field_value(
        self,
        field_config: FormFieldConfiguration,
        value: Any
    ) -> List[str]:
        """验证字段值"""
        errors = []
        
        # 基于字段类型的验证
        if field_config.field_type == "email":
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(value)):
                errors.append(f"{field_config.field_label} 格式不正确")
        
        elif field_config.field_type == "phone":
            if not str(value).replace("+", "").replace("-", "").replace(" ", "").isdigit():
                errors.append(f"{field_config.field_label} 格式不正确")
        
        elif field_config.field_type == "number":
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"{field_config.field_label} 必须是数字")
        
        # 自定义验证规则
        validation_rules = field_config.validation_rules or {}
        for rule_name, rule_config in validation_rules.items():
            if rule_name == "min_length":
                if len(str(value)) < rule_config:
                    errors.append(f"{field_config.field_label} 长度不能少于 {rule_config} 个字符")
            elif rule_name == "max_length":
                if len(str(value)) > rule_config:
                    errors.append(f"{field_config.field_label} 长度不能超过 {rule_config} 个字符")
        
        return errors
    
    async def _build_form_response(
        self,
        config: FormConfiguration
    ) -> FormConfigurationResponseDTO:
        """构建表单配置响应"""
        # 获取字段配置
        fields = await self.form_field_repo.find_by_form_config(config.id)
        
        field_responses = []
        for field in fields:
            field_response = {
                "id": field.id,
                "field_key": field.field_key,
                "field_label": field.field_label,
                "field_type": field.field_type,
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
                "created_at": field.created_at
            }
            field_responses.append(field_response)
        
        # 按字段顺序排序
        field_responses.sort(key=lambda x: x["field_order"])
        
        return FormConfigurationResponseDTO(
            id=config.id,
            form_name=config.form_name,
            form_type=config.form_type,
            form_version=config.form_version,
            description=config.description,
            is_active=config.is_active,
            is_default=config.is_default,
            form_fields=field_responses,
            form_schema=config.form_schema,
            ui_schema=config.ui_schema,
            validation_schema=config.validation_schema,
            tenant_id=config.tenant_id,
            created_at=config.created_at,
            updated_at=config.updated_at,
            created_by=config.created_by,
            updated_by=config.updated_by
        )
    
    async def _unset_default_forms(self, form_type: str, tenant_id: str):
        """取消其他默认表单配置"""
        existing_defaults = await self.form_config_repo.find_by({
            "form_type": form_type,
            "tenant_id": UUID(tenant_id),
            "is_default": True
        })
        
        for config in existing_defaults:
            config.is_default = False
            await self.form_config_repo.update(config)
    
    async def _clear_form_cache(self, tenant_id: str, form_type: str):
        """清除表单缓存"""
        try:
            cache = await self._get_cache()
            # 清除相关缓存模式
            cache_patterns = [
                f"form_config:{tenant_id}:*",
                f"form_list:{tenant_id}:{form_type}:*",
                f"form_render:{tenant_id}:{form_type}"
            ]
            
            for pattern in cache_patterns:
                keys = await cache.keys(pattern)
                for key in keys:
                    await cache.delete(key)
        except Exception as e:
            self.logger.warning(f"清除缓存失败: {str(e)}")

    async def _get_cache(self):
        """获取Redis缓存客户端"""
        return await get_redis() 