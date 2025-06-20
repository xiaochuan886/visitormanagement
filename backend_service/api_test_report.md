
📊 访客管理系统API测试报告
==================================================

🎯 测试概览:
   • 总测试数: 10
   • 成功数: 9
   • 失败数: 1
   • 成功率: 90.0%

📋 详细结果:

✅ 系统健康检查
   方法: GET /health
   状态: HTTP 200 - success

❌ API文档
   方法: GET /docs
   状态: HTTP 200 - error
   错误: 0, message='Attempt to decode JSON with unexpected mimetype: text/html; charset=utf-8', url=URL('htt...

✅ 员工列表
   方法: GET /api/v1/employees/
   状态: HTTP 200 - success
   数据: 5 条记录

✅ 部门列表
   方法: GET /api/v1/departments/
   状态: HTTP 200 - success
   数据: 5 条记录

✅ 站点列表
   方法: GET /api/v1/sites/
   状态: HTTP 200 - success
   数据: 2 条记录

✅ 访客列表
   方法: GET /api/v1/visitors/
   状态: HTTP 200 - success
   数据: 2 条记录

✅ 员工详情
   方法: GET /api/v1/employees/1
   状态: HTTP 200 - success
   数据: 1 条记录

✅ 部门详情
   方法: GET /api/v1/departments/6
   状态: HTTP 200 - success
   数据: 1 条记录

✅ 站点详情
   方法: GET /api/v1/sites/5
   状态: HTTP 200 - success
   数据: 1 条记录

✅ 创建访客
   方法: POST /api/v1/visitors/
   状态: HTTP 200 - success
   数据: 1 条记录

⚠️  需要修复的问题:
   • API文档: 0, message='Attempt to decode JSON with unexpected mimetype: text/html; charset=utf-8', url=URL('htt...

🎉 可用于前端开发的API端点:
   • GET /health - 系统健康检查
   • GET /api/v1/employees/ - 员工列表
   • GET /api/v1/departments/ - 部门列表
   • GET /api/v1/sites/ - 站点列表
   • GET /api/v1/visitors/ - 访客列表
   • GET /api/v1/employees/1 - 员工详情
   • GET /api/v1/departments/6 - 部门详情
   • GET /api/v1/sites/5 - 站点详情
   • POST /api/v1/visitors/ - 创建访客

📖 前端开发指南:
   • 认证方式: Bearer Token
   • 基础URL: http://localhost:8000
   • 认证端点: POST /api/v1/auth/login
   • 数据格式: JSON
   • 响应格式: 统一响应结构

🔧 后续工作建议:
   1. 修复失败的API端点
   2. 完善API文档和示例
   3. 增加错误处理和验证
   4. 提供Postman集合或OpenAPI规范
   5. 创建前端集成指南
