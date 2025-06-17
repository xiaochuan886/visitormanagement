"""
测试数据工厂单元测试

测试所有工厂类的正确性。
"""

import pytest
from test.factories.form_factories import (
    FormConfigurationFactory,
    FormFieldConfigurationFactory,
    FormValidationRuleFactory
)
from test.factories.workflow_factories import (
    WorkflowConfigurationFactory,
    WorkflowStepFactory,
    WorkflowTransitionFactory
)
from test.factories.spatial_factories import (
    SpatialHierarchyFactory,
    SpatialEntityFactory
)
from test.factories.business_rule_factories import (
    BusinessRuleFactory,
    RuleConditionFactory,
    RuleActionFactory,
    RuleExecutionHistoryFactory
)


class TestFormFactories:
    """表单工厂测试"""
    
    @pytest.mark.unit
    def test_form_configuration_factory(self):
        """测试表单配置工厂"""
        # Arrange & Act
        form_config = FormConfigurationFactory()
        
        # Assert
        assert form_config.id is not None
        assert form_config.tenant_id == "test-tenant"
        assert form_config.name.startswith("测试表单_")
        assert form_config.version == "1.0.0"
        assert form_config.form_schema["type"] == "object"
    
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
        assert len(form_config.form_schema["required"]) == 3
    
    @pytest.mark.unit
    def test_complex_form_factory(self):
        """测试复杂表单工厂"""
        # Arrange & Act
        form_config = FormConfigurationFactory.create_complex_form()
        
        # Assert
        assert form_config.name == "complex_test_form"
        properties = form_config.form_schema["properties"]
        assert len(properties) == 9  # 9种不同类型的字段
        assert "text_field" in properties
        assert "nested_object" in properties
    
    @pytest.mark.unit
    def test_form_field_configuration_factory(self):
        """测试表单字段配置工厂"""
        # Arrange & Act
        field_config = FormFieldConfigurationFactory()
        
        # Assert
        assert field_config.id is not None
        assert field_config.tenant_id == "test-tenant"
        assert field_config.field_key.startswith("test_field_")
        assert field_config.field_config["placeholder"] == "请输入内容"
    
    @pytest.mark.unit
    def test_name_field_factory(self):
        """测试姓名字段工厂"""
        # Arrange & Act
        field_config = FormFieldConfigurationFactory.create_name_field("form-123")
        
        # Assert
        assert field_config.field_key == "visitor_name"
        assert field_config.field_label == "访客姓名"
        assert field_config.is_required is True
        assert field_config.validation_rules["pattern"] == "^[\\u4e00-\\u9fa5a-zA-Z\\s]{2,50}$"
    
    @pytest.mark.unit
    def test_phone_field_factory(self):
        """测试电话字段工厂"""
        # Arrange & Act
        field_config = FormFieldConfigurationFactory.create_phone_field("form-123")
        
        # Assert
        assert field_config.field_key == "visitor_phone"
        assert field_config.field_label == "联系电话"
        assert field_config.is_required is True
        assert field_config.validation_rules["pattern"] == "^1[3-9]\\d{9}$"
    
    @pytest.mark.unit
    def test_form_validation_rule_factory(self):
        """测试表单验证规则工厂"""
        # Arrange & Act
        rule = FormValidationRuleFactory()
        
        # Assert
        assert rule.id is not None
        assert rule.tenant_id == "test-tenant"
        assert rule.rule_definition["operator"] == "required"
        assert rule.is_active is True


class TestWorkflowFactories:
    """工作流工厂测试"""
    
    @pytest.mark.unit
    def test_workflow_configuration_factory(self):
        """测试工作流配置工厂"""
        # Arrange & Act
        workflow_config = WorkflowConfigurationFactory()
        
        # Assert
        assert workflow_config.id is not None
        assert workflow_config.tenant_id == "test-tenant"
        assert workflow_config.name.startswith("test_workflow_")
        assert workflow_config.workflow_schema["start_step"] == "start"
        assert "end" in workflow_config.workflow_schema["end_steps"]
    
    @pytest.mark.unit
    def test_visitor_approval_workflow_factory(self):
        """测试访客审批工作流工厂"""
        # Arrange & Act
        workflow_config = WorkflowConfigurationFactory.create_visitor_approval_workflow()
        
        # Assert
        assert workflow_config.name == "visitor_approval"
        assert workflow_config.title == "访客审批工作流"
        assert workflow_config.workflow_schema["start_step"] == "submit_application"
        assert "approved" in workflow_config.workflow_schema["end_steps"]
        assert "rejected" in workflow_config.workflow_schema["end_steps"]
    
    @pytest.mark.unit
    def test_workflow_step_factory(self):
        """测试工作流步骤工厂"""
        # Arrange & Act
        step = WorkflowStepFactory()
        
        # Assert
        assert step.id is not None
        assert step.tenant_id == "test-tenant"
        assert step.step_key.startswith("test_step_")
        assert step.step_config["timeout_minutes"] == 60
    
    @pytest.mark.unit
    def test_workflow_transition_factory(self):
        """测试工作流转换工厂"""
        # Arrange & Act
        transition = WorkflowTransitionFactory()
        
        # Assert
        assert transition.id is not None
        assert transition.tenant_id == "test-tenant"
        assert transition.transition_key.startswith("transition_")


class TestSpatialFactories:
    """空间工厂测试"""
    
    @pytest.mark.unit
    def test_spatial_hierarchy_factory(self):
        """测试空间层级结构工厂"""
        # Arrange & Act
        hierarchy = SpatialHierarchyFactory()
        
        # Assert
        assert hierarchy.id is not None
        assert hierarchy.tenant_id == "test-tenant"
        assert hierarchy.hierarchy_name.startswith("test_hierarchy_")
        assert hierarchy.max_levels == 5
        assert len(hierarchy.level_config["levels"]) == 5
    
    @pytest.mark.unit
    def test_office_hierarchy_factory(self):
        """测试办公场所层级结构工厂"""
        # Arrange & Act
        hierarchy = SpatialHierarchyFactory.create_office_hierarchy()
        
        # Assert
        assert hierarchy.hierarchy_name == "office_space_hierarchy"
        assert hierarchy.hierarchy_code == "OFFICE_HIER"
        assert hierarchy.max_levels == 4
        assert len(hierarchy.level_config["levels"]) == 4
    
    @pytest.mark.unit
    def test_spatial_entity_factory(self):
        """测试空间实体工厂"""
        # Arrange & Act
        entity = SpatialEntityFactory()
        
        # Assert
        assert entity.id is not None
        assert entity.tenant_id == "test-tenant"
        assert entity.entity_name.startswith("test_entity_")
        assert entity.level == 1
        assert entity.spatial_config["capacity"] == 10


class TestBusinessRuleFactories:
    """业务规则工厂测试"""
    
    @pytest.mark.unit
    def test_business_rule_factory(self):
        """测试业务规则工厂"""
        # Arrange & Act
        rule = BusinessRuleFactory()
        
        # Assert
        assert rule.id is not None
        assert rule.tenant_id == "test-tenant"
        assert rule.rule_name.startswith("test_rule_")
        assert rule.priority == 100
        assert len(rule.rule_definition["conditions"]) == 1
    
    @pytest.mark.unit
    def test_visitor_validation_rule_factory(self):
        """测试访客验证规则工厂"""
        # Arrange & Act
        rule = BusinessRuleFactory.create_visitor_validation_rule()
        
        # Assert
        assert rule.rule_name == "visitor_phone_validation"
        assert rule.rule_code == "VISITOR_PHONE_VAL"
        assert len(rule.rule_definition["conditions"]) == 2
        assert rule.rule_definition["logical_operator"] == "and"
    
    @pytest.mark.unit
    def test_rule_condition_factory(self):
        """测试规则条件工厂"""
        # Arrange & Act
        condition = RuleConditionFactory()
        
        # Assert
        assert condition.id is not None
        assert condition.tenant_id == "test-tenant"
        assert condition.field_path == "test_field"
        assert condition.expected_value == "test_value"
    
    @pytest.mark.unit
    def test_rule_action_factory(self):
        """测试规则动作工厂"""
        # Arrange & Act
        action = RuleActionFactory()
        
        # Assert
        assert action.id is not None
        assert action.tenant_id == "test-tenant"
        assert action.action_params["message"] == "动作执行成功"
    
    @pytest.mark.unit
    def test_rule_execution_history_factory(self):
        """测试规则执行历史工厂"""
        # Arrange & Act
        history = RuleExecutionHistoryFactory()
        
        # Assert
        assert history.id is not None
        assert history.tenant_id == "test-tenant"
        assert history.duration_ms == 100
        assert history.execution_result["conditions_evaluated"] == 1 