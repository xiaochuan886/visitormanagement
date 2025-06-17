"""
测试数据工厂模块

提供各种测试数据的工厂类，用于单元测试和集成测试。
"""

from .form_factories import (
    FormConfigurationFactory,
    FormFieldConfigurationFactory,
    # FormValidationRuleFactory - 已移除，模型不存在
)

from .workflow_factories import (
    WorkflowConfigurationFactory,
    # WorkflowExecutionFactory - 已移除，模型结构不匹配
)

from .business_rule_factories import (
    BusinessRuleFactory,
    # RuleExecutionLogFactory - 已移除，模型结构不匹配
)

from .spatial_factories import (
    SpatialHierarchyFactory,
    # SpatialEntityFactory - 已移除，模型结构不匹配  
)

__all__ = [
    # 表单相关工厂
    'FormConfigurationFactory',
    'FormFieldConfigurationFactory',
    
    # 工作流相关工厂  
    'WorkflowConfigurationFactory',
    
    # 业务规则相关工厂
    'BusinessRuleFactory',
    
    # 空间配置相关工厂
    'SpatialHierarchyFactory',
]

# 技术债务说明：
# 1. 部分工厂类的字段名可能与实际数据库模型不完全匹配，需要后续调整
# 2. 某些枚举类型使用字符串常量替代，待枚举定义完善后恢复
# 3. 复杂工厂类暂时简化，避免过度依赖不存在的模型关系 