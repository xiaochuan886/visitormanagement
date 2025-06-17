"""
表单配置相关DTO定义
定义表单配置系统中的数据传输对象
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from app.domain.enums.config_enums import FormType, FieldType, ValidationSeverity


class FormFieldConfigurationDTO(BaseModel):
    """表单字段配置DTO"""
    field_key: str = Field(..., description="字段键名", min_length=1, max_length=100)
    field_label: str = Field(..., description="字段标签", min_length=1, max_length=200)
    field_type: FieldType = Field(..., description="字段类型")
    field_order: int = Field(..., description="字段顺序", ge=0)
    is_required: bool = Field(False, description="是否必填")
    is_readonly: bool = Field(False, description="是否只读")
    is_visible: bool = Field(True, description="是否可见")
    default_value: Optional[str] = Field(None, description="默认值")
    placeholder_text: Optional[str] = Field(None, description="占位符文本", max_length=200)
    help_text: Optional[str] = Field(None, description="帮助文本")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="验证规则")
    field_options: Optional[Dict[str, Any]] = Field(None, description="字段选项")
    conditional_logic: Optional[Dict[str, Any]] = Field(None, description="条件显示逻辑")

    @validator('field_key')
    def validate_field_key(cls, v):
        """验证字段键名格式"""
        if not v.replace('_', '').isalnum():
            raise ValueError('字段键名只能包含字母、数字和下划线')
        return v

    @validator('field_options')
    def validate_field_options(cls, v, values):
        """验证字段选项"""
        if v is None:
            return v
        
        field_type = values.get('field_type')
        if field_type in [FieldType.SELECT, FieldType.MULTISELECT, FieldType.RADIO]:
            if 'options' not in v or not isinstance(v['options'], list):
                raise ValueError(f'{field_type.value} 类型字段必须提供options选项列表')
        
        return v


class FormConfigurationCreateDTO(BaseModel):
    """表单配置创建DTO"""
    form_name: str = Field(..., description="表单名称", min_length=2, max_length=100)
    form_type: FormType = Field(..., description="表单类型")
    description: Optional[str] = Field(None, description="表单描述")
    form_fields: List[FormFieldConfigurationDTO] = Field(..., description="表单字段列表", min_items=1)
    form_schema: Optional[Dict[str, Any]] = Field(None, description="完整表单结构")
    ui_schema: Optional[Dict[str, Any]] = Field(None, description="UI渲染配置")
    validation_schema: Optional[Dict[str, Any]] = Field(None, description="验证规则")
    is_default: bool = Field(False, description="是否设为默认表单")

    @validator('form_fields')
    def validate_form_fields(cls, v):
        """验证表单字段列表"""
        if not v:
            raise ValueError('表单至少需要包含一个字段')
        
        # 检查字段键名重复
        field_keys = [field.field_key for field in v]
        if len(field_keys) != len(set(field_keys)):
            raise ValueError('字段键名不能重复')
        
        # 检查字段顺序重复
        field_orders = [field.field_order for field in v]
        if len(field_orders) != len(set(field_orders)):
            raise ValueError('字段顺序不能重复')
        
        return v


class FormConfigurationUpdateDTO(BaseModel):
    """表单配置更新DTO"""
    form_name: Optional[str] = Field(None, description="表单名称", min_length=2, max_length=100)
    description: Optional[str] = Field(None, description="表单描述")
    form_fields: Optional[List[FormFieldConfigurationDTO]] = Field(None, description="表单字段列表")
    form_schema: Optional[Dict[str, Any]] = Field(None, description="完整表单结构")
    ui_schema: Optional[Dict[str, Any]] = Field(None, description="UI渲染配置")
    validation_schema: Optional[Dict[str, Any]] = Field(None, description="验证规则")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_default: Optional[bool] = Field(None, description="是否设为默认表单")

    @validator('form_fields')
    def validate_form_fields(cls, v):
        """验证表单字段列表"""
        if v is not None:
            if not v:
                raise ValueError('表单至少需要包含一个字段')
            
            # 检查字段键名重复
            field_keys = [field.field_key for field in v]
            if len(field_keys) != len(set(field_keys)):
                raise ValueError('字段键名不能重复')
        
        return v


class FormFieldResponseDTO(BaseModel):
    """表单字段响应DTO"""
    id: UUID = Field(..., description="字段ID")
    field_key: str = Field(..., description="字段键名")
    field_label: str = Field(..., description="字段标签")
    field_type: str = Field(..., description="字段类型")
    field_order: int = Field(..., description="字段顺序")
    is_required: bool = Field(..., description="是否必填")
    is_readonly: bool = Field(..., description="是否只读")
    is_visible: bool = Field(..., description="是否可见")
    default_value: Optional[str] = Field(None, description="默认值")
    placeholder_text: Optional[str] = Field(None, description="占位符文本")
    help_text: Optional[str] = Field(None, description="帮助文本")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="验证规则")
    field_options: Optional[Dict[str, Any]] = Field(None, description="字段选项")
    conditional_logic: Optional[Dict[str, Any]] = Field(None, description="条件显示逻辑")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class FormConfigurationResponseDTO(BaseModel):
    """表单配置响应DTO"""
    id: UUID = Field(..., description="配置ID")
    form_name: str = Field(..., description="表单名称")
    form_type: str = Field(..., description="表单类型")
    form_version: int = Field(..., description="表单版本")
    description: Optional[str] = Field(None, description="表单描述")
    is_active: bool = Field(..., description="是否激活")
    is_default: bool = Field(..., description="是否默认表单")
    form_fields: List[FormFieldResponseDTO] = Field(..., description="表单字段列表")
    form_schema: Optional[Dict[str, Any]] = Field(None, description="完整表单结构")
    ui_schema: Optional[Dict[str, Any]] = Field(None, description="UI渲染配置")
    validation_schema: Optional[Dict[str, Any]] = Field(None, description="验证规则")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")

    class Config:
        from_attributes = True


class FormConfigurationListResponseDTO(BaseModel):
    """表单配置列表响应DTO"""
    items: List[FormConfigurationResponseDTO] = Field(..., description="配置列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    total_pages: int = Field(..., description="总页数")


class FormConfigurationQueryDTO(BaseModel):
    """表单配置查询DTO"""
    form_type: Optional[FormType] = Field(None, description="表单类型")
    form_name: Optional[str] = Field(None, description="表单名称（模糊搜索）")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_default: Optional[bool] = Field(None, description="是否默认表单")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="页大小", ge=1, le=100)


class FormValidationResultDTO(BaseModel):
    """表单验证结果DTO"""
    is_valid: bool = Field(..., description="是否验证通过")
    errors: List[Dict[str, Any]] = Field(..., description="错误信息列表")
    warnings: List[Dict[str, Any]] = Field(..., description="警告信息列表")
    field_errors: Dict[str, List[str]] = Field(..., description="字段错误详情")
    validation_duration_ms: int = Field(..., description="验证耗时（毫秒）")


class FormRenderDataDTO(BaseModel):
    """表单渲染数据DTO"""
    form_config_id: UUID = Field(..., description="表单配置ID")
    form_schema: Dict[str, Any] = Field(..., description="表单结构")
    ui_schema: Dict[str, Any] = Field(..., description="UI配置")
    initial_data: Optional[Dict[str, Any]] = Field(None, description="初始数据")
    readonly_fields: List[str] = Field([], description="只读字段列表")
    hidden_fields: List[str] = Field([], description="隐藏字段列表")
    validation_rules: Dict[str, Any] = Field(..., description="验证规则")


class FormSubmissionDTO(BaseModel):
    """表单提交DTO"""
    form_config_id: UUID = Field(..., description="表单配置ID")
    form_data: Dict[str, Any] = Field(..., description="表单数据")
    submit_context: Optional[Dict[str, Any]] = Field(None, description="提交上下文")
    auto_validate: bool = Field(True, description="是否自动验证")


class FormSubmissionResultDTO(BaseModel):
    """表单提交结果DTO"""
    submission_id: UUID = Field(..., description="提交ID")
    is_valid: bool = Field(..., description="是否验证通过")
    processed_data: Dict[str, Any] = Field(..., description="处理后的数据")
    validation_result: FormValidationResultDTO = Field(..., description="验证结果")
    processing_duration_ms: int = Field(..., description="处理耗时（毫秒）")
    next_actions: List[str] = Field([], description="下一步动作建议")


class FormTemplateDTO(BaseModel):
    """表单模板DTO"""
    template_name: str = Field(..., description="模板名称")
    template_category: str = Field(..., description="模板分类")
    form_type: FormType = Field(..., description="表单类型")
    template_description: str = Field(..., description="模板描述")
    template_schema: Dict[str, Any] = Field(..., description="模板结构")
    is_system_template: bool = Field(False, description="是否系统模板")
    tags: List[str] = Field([], description="标签列表")


class FormFieldValidationRuleDTO(BaseModel):
    """表单字段验证规则DTO"""
    rule_type: str = Field(..., description="规则类型")
    rule_params: Dict[str, Any] = Field(..., description="规则参数")
    error_message: str = Field(..., description="错误提示信息")
    severity: ValidationSeverity = Field(ValidationSeverity.ERROR, description="严重级别")


class FormConditionalLogicDTO(BaseModel):
    """表单条件逻辑DTO"""
    condition_field: str = Field(..., description="条件字段")
    condition_operator: str = Field(..., description="条件操作符")
    condition_value: Any = Field(..., description="条件值")
    target_fields: List[str] = Field(..., description="目标字段列表")
    action_type: str = Field(..., description="动作类型（show/hide/require/optional）")


class FormConfigurationExportDTO(BaseModel):
    """表单配置导出DTO"""
    export_format: str = Field("json", description="导出格式")
    include_fields: bool = Field(True, description="是否包含字段配置")
    include_validation: bool = Field(True, description="是否包含验证规则")
    include_ui_schema: bool = Field(True, description="是否包含UI配置")
    compress_output: bool = Field(False, description="是否压缩输出") 