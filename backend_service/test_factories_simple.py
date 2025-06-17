#!/usr/bin/env python3
"""
简单的工厂类验证脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 测试表单工厂
    print("🧪 测试表单工厂...")
    from test.factories.form_factories import FormConfigurationFactory
    
    form = FormConfigurationFactory()
    print(f"✅ 表单ID: {form.id[:8]}...")
    print(f"✅ 表单名称: {form.name}")
    print(f"✅ 表单版本: {form.version}")
    print(f"✅ Schema类型: {form.form_schema['type']}")
    
    # 测试访客登记表单
    visitor_form = FormConfigurationFactory.create_visitor_registration_form()
    print(f"✅ 访客表单: {visitor_form.name}")
    print(f"✅ 字段数量: {len(visitor_form.form_schema['properties'])}")
    
    # 测试工作流工厂
    print("\n🔄 测试工作流工厂...")
    from test.factories.workflow_factories import WorkflowConfigurationFactory
    
    workflow = WorkflowConfigurationFactory()
    print(f"✅ 工作流ID: {workflow.id[:8]}...")
    print(f"✅ 工作流名称: {workflow.name}")
    print(f"✅ 开始步骤: {workflow.workflow_schema['start_step']}")
    
    # 测试空间工厂
    print("\n🏢 测试空间工厂...")
    from test.factories.spatial_factories import SpatialHierarchyFactory
    
    hierarchy = SpatialHierarchyFactory()
    print(f"✅ 层级ID: {hierarchy.id[:8]}...")
    print(f"✅ 层级名称: {hierarchy.hierarchy_name}")
    print(f"✅ 最大层级: {hierarchy.max_levels}")
    
    # 测试业务规则工厂
    print("\n📋 测试业务规则工厂...")
    from test.factories.business_rule_factories import BusinessRuleFactory
    
    rule = BusinessRuleFactory()
    print(f"✅ 规则ID: {rule.id[:8]}...")
    print(f"✅ 规则名称: {rule.rule_name}")
    print(f"✅ 规则优先级: {rule.priority}")
    
    print("\n🎉 所有工厂测试通过！配置引擎数据工厂正常工作。")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试失败: {e}")
    sys.exit(1) 