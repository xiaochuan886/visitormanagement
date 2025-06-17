"""
表单配置模块单元测试

测试表单配置服务、字段配置、验证规则等功能。
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.application.config_engine.form_configuration_service import FormConfigurationService
from app.domain.enums.config_enums import FormStatus, FieldType, ValidationRuleType
from app.infrastructure.exceptions.config_exceptions import FormConfigurationNotFoundError
from test.factories.form_factories import (
    FormConfigurationFactory,
    FormFieldConfigurationFactory,
    FormValidationRuleFactory
)


class TestFormConfigurationService:
    """表单配置服务测试"""
    
    @pytest.fixture
    def mock_repository(self):
        """模拟仓储"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """表单配置服务实例"""
        return FormConfigurationService(mock_repository)
    
    @pytest.mark.unit
    async def test_create_form_configuration_success(self, service, mock_repository):
        """测试创建表单配置成功"""
        # Arrange
        form_config = FormConfigurationFactory()
        mock_repository.create.return_value = form_config
        
        create_data = {
            "name": "test_form",
            "title": "测试表单",
            "description": "测试表单描述",
            "form_schema": {"type": "object"},
            "ui_schema": {"ui:widget": "form"}
        }
        
        # Act
        result = await service.create_form_configuration(
            create_data,
            "test-tenant",
            "test-user"
        )
        
        # Assert
        assert result.name == "test_form"
        assert result.title == "测试表单"
        assert result.status == FormStatus.ACTIVE
        mock_repository.create.assert_called_once()
    
    @pytest.mark.unit
    async def test_get_form_configuration_success(self, service, mock_repository):
        """测试获取表单配置成功"""
        # Arrange
        form_config = FormConfigurationFactory()
        mock_repository.get_by_id.return_value = form_config
        
        # Act
        result = await service.get_form_configuration(
            form_config.id,
            "test-tenant"
        )
        
        # Assert
        assert result.id == form_config.id
        mock_repository.get_by_id.assert_called_once_with(form_config.id, "test-tenant")
    
    @pytest.mark.unit
    async def test_get_form_configuration_not_found(self, service, mock_repository):
        """测试获取不存在的表单配置"""
        # Arrange
        mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(FormConfigurationNotFoundError):
            await service.get_form_configuration("non-existent-id", "test-tenant")
    
    @pytest.mark.unit
    async def test_update_form_configuration_success(self, service, mock_repository):
        """测试更新表单配置成功"""
        # Arrange
        form_config = FormConfigurationFactory()
        mock_repository.get_by_id.return_value = form_config
        mock_repository.update.return_value = form_config
        
        update_data = {
            "title": "更新后的标题",
            "description": "更新后的描述"
        }
        
        # Act
        result = await service.update_form_configuration(
            form_config.id,
            update_data,
            "test-tenant",
            "test-user"
        )
        
        # Assert
        assert result is not None
        mock_repository.update.assert_called_once()
    
    @pytest.mark.unit
    async def test_delete_form_configuration_success(self, service, mock_repository):
        """测试删除表单配置成功"""
        # Arrange
        form_config = FormConfigurationFactory()
        mock_repository.get_by_id.return_value = form_config
        mock_repository.delete.return_value = True
        
        # Act
        result = await service.delete_form_configuration(
            form_config.id,
            "test-tenant"
        )
        
        # Assert
        assert result is True
        mock_repository.delete.assert_called_once_with(form_config.id, "test-tenant")
    
    @pytest.mark.unit
    async def test_list_form_configurations(self, service, mock_repository):
        """测试获取表单配置列表"""
        # Arrange
        form_configs = [FormConfigurationFactory() for _ in range(3)]
        mock_repository.get_all.return_value = form_configs
        
        # Act
        result = await service.list_form_configurations("test-tenant")
        
        # Assert
        assert len(result) == 3
        mock_repository.get_all.assert_called_once_with("test-tenant")
    
    @pytest.mark.unit
    async def test_validate_form_data_success(self, service, mock_repository):
        """测试表单数据验证成功"""
        # Arrange
        form_config = FormConfigurationFactory.create_visitor_registration_form()
        mock_repository.get_by_id.return_value = form_config
        
        form_data = {
            "visitor_name": "张三",
            "visitor_phone": "13812345678",
            "visit_purpose": "商务洽谈"
        }
        
        # Act
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.return_value = None  # 验证成功
            result = await service.validate_form_data(
                form_config.id,
                form_data,
                "test-tenant"
            )
        
        # Assert
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.unit
    async def test_validate_form_data_with_errors(self, service, mock_repository):
        """测试表单数据验证失败"""
        # Arrange
        form_config = FormConfigurationFactory.create_visitor_registration_form()
        mock_repository.get_by_id.return_value = form_config
        
        form_data = {
            "visitor_name": "",  # 空名称
            "visitor_phone": "invalid_phone",  # 无效电话
            # 缺少 visit_purpose
        }
        
        # Act
        from jsonschema import ValidationError
        with patch('jsonschema.validate') as mock_validate:
            mock_validate.side_effect = ValidationError("Required property missing")
            result = await service.validate_form_data(
                form_config.id,
                form_data,
                "test-tenant"
            )
        
        # Assert
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
    
    @pytest.mark.unit
    async def test_generate_form_render_data(self, service, mock_repository):
        """测试生成表单渲染数据"""
        # Arrange
        form_config = FormConfigurationFactory.create_visitor_registration_form()
        mock_repository.get_by_id.return_value = form_config
        
        # Act
        result = await service.generate_form_render_data(
            form_config.id,
            "test-tenant"
        )
        
        # Assert
        assert "schema" in result
        assert "uiSchema" in result
        assert "formData" in result
        assert result["schema"]["type"] == "object"
    
    @pytest.mark.unit
    async def test_activate_form_configuration(self, service, mock_repository):
        """测试激活表单配置"""
        # Arrange
        form_config = FormConfigurationFactory(status=FormStatus.INACTIVE)
        mock_repository.get_by_id.return_value = form_config
        mock_repository.update.return_value = form_config
        
        # Act
        result = await service.activate_form_configuration(
            form_config.id,
            "test-tenant",
            "test-user"
        )
        
        # Assert
        assert result.status == FormStatus.ACTIVE
        mock_repository.update.assert_called_once()
    
    @pytest.mark.unit
    async def test_deactivate_form_configuration(self, service, mock_repository):
        """测试停用表单配置"""
        # Arrange
        form_config = FormConfigurationFactory(status=FormStatus.ACTIVE)
        mock_repository.get_by_id.return_value = form_config
        mock_repository.update.return_value = form_config
        
        # Act
        result = await service.deactivate_form_configuration(
            form_config.id,
            "test-tenant",
            "test-user"
        )
        
        # Assert
        assert result.status == FormStatus.INACTIVE
        mock_repository.update.assert_called_once()


class TestFormFieldConfiguration:
    """表单字段配置测试"""
    
    @pytest.mark.unit
    def test_form_field_configuration_creation(self):
        """测试表单字段配置创建"""
        # Arrange & Act
        field_config = FormFieldConfigurationFactory.create_name_field(
            form_id="test-form-id",
            tenant_id="test-tenant"
        )
        
        # Assert
        assert field_config.field_key == "visitor_name"
        assert field_config.field_label == "访客姓名"
        assert field_config.field_type == FieldType.TEXT
        assert field_config.is_required is True
    
    @pytest.mark.unit
    def test_phone_field_configuration(self):
        """测试电话字段配置"""
        # Arrange & Act
        field_config = FormFieldConfigurationFactory.create_phone_field(
            form_id="test-form-id",
            tenant_id="test-tenant"
        )
        
        # Assert
        assert field_config.field_key == "visitor_phone"
        assert field_config.field_type == FieldType.TEXT
        assert field_config.validation_rules["pattern"] == "^1[3-9]\\d{9}$"
    
    @pytest.mark.unit
    def test_email_field_configuration(self):
        """测试邮箱字段配置"""
        # Arrange & Act
        field_config = FormFieldConfigurationFactory.create_email_field(
            form_id="test-form-id",
            tenant_id="test-tenant"
        )
        
        # Assert
        assert field_config.field_key == "visitor_email"
        assert field_config.field_type == FieldType.EMAIL
        assert field_config.is_required is False


class TestFormValidationRule:
    """表单验证规则测试"""
    
    @pytest.mark.unit
    def test_required_validation_rule(self):
        """测试必填验证规则"""
        # Arrange & Act
        rule = FormValidationRuleFactory.create_required_rule(
            form_id="test-form-id",
            field_key="visitor_name",
            tenant_id="test-tenant"
        )
        
        # Assert
        assert rule.rule_type == ValidationRuleType.FIELD_VALIDATION
        assert rule.rule_definition["operator"] == "required"
        assert rule.rule_definition["value"] is True
    
    @pytest.mark.unit
    def test_length_validation_rule(self):
        """测试长度验证规则"""
        # Arrange & Act
        rule = FormValidationRuleFactory.create_length_rule(
            form_id="test-form-id",
            field_key="visitor_name",
            min_length=2,
            max_length=50,
            tenant_id="test-tenant"
        )
        
        # Assert
        assert rule.rule_type == ValidationRuleType.FIELD_VALIDATION
        assert "minLength" in rule.rule_definition["operator"] or "maxLength" in rule.rule_definition["operator"]
    
    @pytest.mark.unit
    def test_pattern_validation_rule(self):
        """测试正则验证规则"""
        # Arrange & Act
        pattern = "^1[3-9]\\d{9}$"
        rule = FormValidationRuleFactory.create_pattern_rule(
            form_id="test-form-id",
            field_key="visitor_phone",
            pattern=pattern,
            message="手机号码格式不正确",
            tenant_id="test-tenant"
        )
        
        # Assert
        assert rule.rule_type == ValidationRuleType.FIELD_VALIDATION
        assert rule.rule_definition["operator"] == "pattern"
        assert rule.rule_definition["value"] == pattern
    
    @pytest.mark.unit
    def test_cross_field_validation_rule(self):
        """测试跨字段验证规则"""
        # Arrange & Act
        rule = FormValidationRuleFactory.create_cross_field_rule(
            form_id="test-form-id",
            field1="start_date",
            field2="end_date",
            operator="less_than",
            tenant_id="test-tenant"
        )
        
        # Assert
        assert rule.rule_type == ValidationRuleType.CROSS_FIELD_VALIDATION
        assert "start_date" in rule.rule_name
        assert "end_date" in rule.rule_name


class TestFormConfigurationFactory:
    """表单配置工厂测试"""
    
    @pytest.mark.unit
    def test_basic_form_configuration_factory(self):
        """测试基础表单配置工厂"""
        # Arrange & Act
        form_config = FormConfigurationFactory()
        
        # Assert
        assert form_config.id is not None
        assert form_config.tenant_id == "test-tenant"
        assert form_config.status == FormStatus.ACTIVE
        assert form_config.version == "1.0.0"
        assert form_config.is_system_form is False
    
    @pytest.mark.unit
    def test_visitor_registration_form_factory(self):
        """测试访客登记表单工厂"""
        # Arrange & Act
        form_config = FormConfigurationFactory.create_visitor_registration_form()
        
        # Assert
        assert form_config.name == "visitor_registration"
        assert form_config.title == "访客登记表单"
        assert "visitor_name" in form_config.form_schema["properties"]
        assert "visitor_phone" in form_config.form_schema["properties"]
        assert "visit_purpose" in form_config.form_schema["properties"]
    
    @pytest.mark.unit
    def test_complex_form_factory(self):
        """测试复杂表单工厂"""
        # Arrange & Act
        form_config = FormConfigurationFactory.create_complex_form()
        
        # Assert
        assert form_config.name == "complex_test_form"
        properties = form_config.form_schema["properties"]
        assert "text_field" in properties
        assert "number_field" in properties
        assert "email_field" in properties
        assert "date_field" in properties
        assert "select_field" in properties
        assert "multi_select" in properties
        assert "boolean_field" in properties
        assert "file_field" in properties
        assert "nested_object" in properties 