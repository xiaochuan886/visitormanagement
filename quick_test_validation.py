#!/usr/bin/env python3
"""
门岗前台功能快速验证脚本
检查代码文件完整性、导入逻辑和基本语法
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

def check_file_exists(file_path: str, description: str) -> bool:
    """检查文件是否存在"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {description}: {file_path} ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description}: {file_path} - 文件不存在")
        return False

def check_python_syntax(file_path: str) -> bool:
    """检查Python文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"❌ 语法错误 {file_path}: {e}")
        return False
    except Exception as e:
        print(f"⚠️ 检查文件 {file_path} 时出错: {e}")
        return False

def check_imports_in_file(file_path: str) -> List[str]:
    """提取文件中的导入语句"""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception as e:
        print(f"⚠️ 分析导入失败 {file_path}: {e}")
    
    return imports

def validate_implementation():
    """验证门岗前台功能实施"""
    
    print("🚀 开始门岗前台功能验证...")
    print("=" * 60)
    
    # 检查项目根目录
    if not os.path.exists("backend_service"):
        print("❌ 错误: 请在项目根目录运行此脚本")
        return False
    
    validation_results = {
        "files_checked": 0,
        "files_passed": 0,
        "syntax_errors": 0,
        "missing_files": 0
    }
    
    # 1. 检查Schema文件
    print("\n📁 Phase 1: Schema数据传输对象验证")
    print("-" * 40)
    
    schema_files = [
        ("backend_service/app/api/models/gate_schemas.py", "门岗放行Schema"),
        ("backend_service/app/api/models/reception_schemas.py", "前台签到Schema"),
        ("backend_service/app/api/models/mobile_schemas.py", "移动端Schema"),
        ("backend_service/app/api/models/device_schemas.py", "设备管理Schema")
    ]
    
    for file_path, description in schema_files:
        validation_results["files_checked"] += 1
        if check_file_exists(file_path, description):
            if check_python_syntax(file_path):
                validation_results["files_passed"] += 1
            else:
                validation_results["syntax_errors"] += 1
        else:
            validation_results["missing_files"] += 1
    
    # 2. 检查服务层文件
    print("\n🔧 Phase 2: 服务层实现验证")
    print("-" * 40)
    
    service_files = [
        ("backend_service/app/application/services/device_service.py", "设备管理服务"),
        ("backend_service/app/application/services/gate_verification_service.py", "门岗验证服务"),
        ("backend_service/app/application/services/reception_service.py", "前台接待服务"),
        ("backend_service/app/application/services/mobile_sync_service.py", "移动端同步服务")
    ]
    
    for file_path, description in service_files:
        validation_results["files_checked"] += 1
        if check_file_exists(file_path, description):
            if check_python_syntax(file_path):
                validation_results["files_passed"] += 1
            else:
                validation_results["syntax_errors"] += 1
        else:
            validation_results["missing_files"] += 1
    
    # 3. 检查数据模型文件
    print("\n🗄️ Phase 3: 数据模型验证")
    print("-" * 40)
    
    model_files = [
        ("backend_service/app/infrastructure/database/models.py", "数据模型定义"),
        ("backend_service/app/infrastructure/database/migrations/003_add_gate_reception_models.py", "数据库迁移脚本")
    ]
    
    for file_path, description in model_files:
        validation_results["files_checked"] += 1
        if check_file_exists(file_path, description):
            if check_python_syntax(file_path):
                validation_results["files_passed"] += 1
            else:
                validation_results["syntax_errors"] += 1
        else:
            validation_results["missing_files"] += 1
    
    # 4. 检查API路由文件
    print("\n🌐 Phase 4: API路由验证")
    print("-" * 40)
    
    route_files = [
        ("backend_service/app/api/routes/gate.py", "门岗API路由"),
        ("backend_service/app/api/routes/reception.py", "前台API路由"),
        ("backend_service/app/api/routes/mobile.py", "移动端API路由"),
        ("backend_service/app/api/routes/devices.py", "设备管理API路由"),
        ("backend_service/app/api/routes/health.py", "健康检查API路由"),
        ("backend_service/app/api/routes/__init__.py", "主路由注册")
    ]
    
    for file_path, description in route_files:
        validation_results["files_checked"] += 1
        if check_file_exists(file_path, description):
            if check_python_syntax(file_path):
                validation_results["files_passed"] += 1
            else:
                validation_results["syntax_errors"] += 1
        else:
            validation_results["missing_files"] += 1
    
    # 5. 检查测试和部署文件
    print("\n🧪 Phase 5: 测试和部署文件验证")
    print("-" * 40)
    
    deployment_files = [
        ("backend_service/tests/test_gate_reception_integration.py", "集成测试脚本"),
        ("scripts/update_api_docs.py", "API文档生成脚本"),
        ("docker-compose.gate-reception.yml", "Docker部署配置"),
        ("GATE_RECEPTION_IMPLEMENTATION_SUMMARY.md", "实施总结文档"),
        ("TESTING_GUIDE.md", "测试指南")
    ]
    
    for file_path, description in deployment_files:
        validation_results["files_checked"] += 1
        if check_file_exists(file_path, description):
            if file_path.endswith('.py'):
                if check_python_syntax(file_path):
                    validation_results["files_passed"] += 1
                else:
                    validation_results["syntax_errors"] += 1
            else:
                validation_results["files_passed"] += 1
        else:
            validation_results["missing_files"] += 1
    
    # 6. 检查路由注册
    print("\n🔗 路由注册验证")
    print("-" * 40)
    
    try:
        init_file = "backend_service/app/api/routes/__init__.py"
        if os.path.exists(init_file):
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_imports = [
                "from .gate import router as gate_router",
                "from .reception import router as reception_router", 
                "from .mobile import router as mobile_router",
                "from .devices import router as devices_router",
                "from .health import router as health_router"
            ]
            
            required_registrations = [
                "api_router.include_router(gate_router",
                "api_router.include_router(reception_router",
                "api_router.include_router(mobile_router", 
                "api_router.include_router(devices_router",
                "api_router.include_router(health_router"
            ]
            
            import_passed = 0
            for imp in required_imports:
                if imp in content:
                    print(f"✅ 导入检查: {imp.split()[1]}")
                    import_passed += 1
                else:
                    print(f"❌ 缺少导入: {imp}")
            
            registration_passed = 0
            for reg in required_registrations:
                if reg in content:
                    print(f"✅ 注册检查: {reg.split('(')[1].split('_router')[0]}")
                    registration_passed += 1
                else:
                    print(f"❌ 缺少注册: {reg}")
            
            print(f"路由导入: {import_passed}/{len(required_imports)} 通过")
            print(f"路由注册: {registration_passed}/{len(required_registrations)} 通过")
            
    except Exception as e:
        print(f"❌ 路由注册检查失败: {e}")
    
    # 7. 统计报告
    print("\n📊 验证结果统计")
    print("=" * 60)
    
    total_files = validation_results["files_checked"]
    passed_files = validation_results["files_passed"]
    syntax_errors = validation_results["syntax_errors"]
    missing_files = validation_results["missing_files"]
    
    success_rate = (passed_files / total_files * 100) if total_files > 0 else 0
    
    print(f"📁 检查文件总数: {total_files}")
    print(f"✅ 通过验证文件: {passed_files}")
    print(f"❌ 语法错误文件: {syntax_errors}")
    print(f"🚫 缺失文件数量: {missing_files}")
    print(f"📈 验证通过率: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("\n🎉 验证结果: 优秀! 代码实施质量很高")
        status = "EXCELLENT"
    elif success_rate >= 85:
        print("\n✅ 验证结果: 良好! 大部分功能正常")
        status = "GOOD"
    elif success_rate >= 70:
        print("\n⚠️ 验证结果: 一般，需要修复部分问题")
        status = "NEEDS_WORK"
    else:
        print("\n❌ 验证结果: 需要大量修复工作")
        status = "MAJOR_ISSUES"
    
    # 8. 功能模块检查
    print("\n🔍 功能模块完整性检查")
    print("-" * 40)
    
    modules_status = {
        "门岗验证": check_module_completeness("gate"),
        "前台签到": check_module_completeness("reception"), 
        "移动端同步": check_module_completeness("mobile"),
        "设备管理": check_module_completeness("devices"),
        "系统监控": check_module_completeness("health")
    }
    
    for module, status_ok in modules_status.items():
        status_icon = "✅" if status_ok else "❌"
        print(f"{status_icon} {module}: {'完整' if status_ok else '缺失组件'}")
    
    complete_modules = sum(modules_status.values())
    total_modules = len(modules_status)
    
    print(f"\n模块完整度: {complete_modules}/{total_modules} ({complete_modules/total_modules*100:.1f}%)")
    
    # 9. 下一步建议
    print("\n💡 下一步建议")
    print("-" * 40)
    
    if status == "EXCELLENT":
        print("🚀 代码质量优秀，建议：")
        print("  1. 启动Docker环境进行功能测试")
        print("  2. 运行集成测试套件")
        print("  3. 进行性能基准测试")
        print("  4. 部署到测试环境")
    elif status == "GOOD":
        print("✅ 代码基本完整，建议：")
        print("  1. 修复发现的语法错误")
        print("  2. 补齐缺失的文件")
        print("  3. 进行基础功能测试")
    else:
        print("⚠️ 需要更多工作，建议：")
        print("  1. 优先修复语法错误")
        print("  2. 补齐关键缺失文件")
        print("  3. 重新验证代码结构")
    
    return status == "EXCELLENT" or status == "GOOD"

def check_module_completeness(module: str) -> bool:
    """检查模块完整性"""
    
    required_files = {
        "gate": [
            "backend_service/app/api/models/gate_schemas.py",
            "backend_service/app/application/services/gate_verification_service.py",
            "backend_service/app/api/routes/gate.py"
        ],
        "reception": [
            "backend_service/app/api/models/reception_schemas.py", 
            "backend_service/app/application/services/reception_service.py",
            "backend_service/app/api/routes/reception.py"
        ],
        "mobile": [
            "backend_service/app/api/models/mobile_schemas.py",
            "backend_service/app/application/services/mobile_sync_service.py", 
            "backend_service/app/api/routes/mobile.py"
        ],
        "devices": [
            "backend_service/app/api/models/device_schemas.py",
            "backend_service/app/application/services/device_service.py",
            "backend_service/app/api/routes/devices.py"
        ],
        "health": [
            "backend_service/app/api/routes/health.py"
        ]
    }
    
    if module not in required_files:
        return False
    
    for file_path in required_files[module]:
        if not os.path.exists(file_path):
            return False
    
    return True

if __name__ == "__main__":
    print("📋 访客管理系统门岗前台功能验证脚本")
    print("🔍 检查代码完整性、语法正确性和模块完整度")
    print("")
    
    try:
        success = validate_implementation()
        exit_code = 0 if success else 1
        print(f"\n🏁 验证完成，退出代码: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断验证")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 