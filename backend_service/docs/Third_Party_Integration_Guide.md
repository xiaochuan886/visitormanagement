# 第三方系统集成指南

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **适用角色**: 系统集成工程师、API开发者

## 🎯 集成概述

访客管理系统支持与多种第三方系统集成，提供开放的API接口和标准化的集成方案，实现数据互通和业务协同。

### 支持的集成类型
- ✅ **企业微信集成**: 消息通知、用户同步
- ✅ **邮件系统集成**: SMTP邮件发送
- ✅ **智能设备集成**: 人脸识别、门禁系统
- ✅ **OA系统集成**: 员工信息同步
- ✅ **安防系统集成**: 访客信息推送
- ✅ **报表系统集成**: 数据导出和分析

## 🔗 企业微信集成

### 配置企业微信应用

#### 1. 创建企业微信应用
```python
# config/wechat_config.py
WECHAT_CONFIG = {
    "corp_id": "your_corp_id",
    "agent_id": 1000001,
    "secret": "your_app_secret",
    "api_base_url": "https://qyapi.weixin.qq.com/cgi-bin"
}
```

#### 2. 获取访问令牌
```python
# services/wechat_service.py
import requests
from typing import Optional

class WeChatService:
    def __init__(self, corp_id: str, secret: str):
        self.corp_id = corp_id
        self.secret = secret
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

    async def get_access_token(self) -> str:
        """获取企业微信访问令牌"""
        if self.access_token and self.token_expires_at > datetime.now():
            return self.access_token

        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            if data.get("errcode") == 0:
                self.access_token = data["access_token"]
                self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
                return self.access_token
            else:
                raise Exception(f"获取微信令牌失败: {data}")

    async def send_message(self, user_id: str, message: str) -> bool:
        """发送消息给指定用户"""
        token = await self.get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"

        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": WECHAT_CONFIG["agent_id"],
            "text": {
                "content": message
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            result = response.json()
            return result.get("errcode") == 0
```

### 访客通知集成
```python
# services/notification_service.py
class NotificationService:
    def __init__(self, wechat_service: WeChatService):
        self.wechat_service = wechat_service

    async def notify_visitor_approval(self, visitor: VisitorModel, employee: EmployeeModel):
        """通知员工访客审批"""
        message = f"""
📋 访客审批通知

访客信息：
👤 姓名：{visitor.name}
📱 电话：{visitor.phone_number}
🏢 公司：{visitor.company_name}
🎯 目的：{visitor.purpose}
⏰ 预约时间：{visitor.expected_date.strftime('%Y-%m-%d %H:%M')}

请及时处理访客审批！
        """

        await self.wechat_service.send_message(employee.wechat_user_id, message)

    async def notify_visitor_arrival(self, visitor: VisitorModel):
        """通知访客到达"""
        message = f"""
🚶 访客到达通知

{visitor.name} 已到达前台
📱 电话：{visitor.phone_number}
🎫 通行码：{visitor.pass_code}
⏰ 到达时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

请前往前台接待！
        """

        if visitor.employee and visitor.employee.wechat_user_id:
            await self.wechat_service.send_message(visitor.employee.wechat_user_id, message)
```

## 📧 邮件系统集成

### SMTP配置
```python
# config/email_config.py
EMAIL_CONFIG = {
    "smtp_server": "smtp.company.com",
    "smtp_port": 587,
    "use_tls": True,
    "username": "visitor-system@company.com",
    "password": "your_email_password",
    "from_name": "访客管理系统"
}
```

### 邮件服务实现
```python
# services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

class EmailService:
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG["smtp_server"]
        self.smtp_port = EMAIL_CONFIG["smtp_port"]
        self.username = EMAIL_CONFIG["username"]
        self.password = EMAIL_CONFIG["password"]

    async def send_visitor_confirmation(self, visitor: VisitorModel):
        """发送访客确认邮件"""
        if not visitor.email:
            return

        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>访客预约确认</title>
</head>
<body>
    <h2>访客预约确认</h2>
    <p>亲爱的 {{ visitor.name }}，</p>
    <p>您的访客预约已确认，详情如下：</p>
    
    <table border="1" cellpadding="5">
        <tr><td>姓名</td><td>{{ visitor.name }}</td></tr>
        <tr><td>通行码</td><td><strong>{{ visitor.pass_code }}</strong></td></tr>
        <tr><td>预约时间</td><td>{{ visitor.expected_date.strftime('%Y-%m-%d %H:%M') }}</td></tr>
        <tr><td>接待员工</td><td>{{ visitor.employee.name }}</td></tr>
        <tr><td>状态</td><td>{{ visitor.status }}</td></tr>
    </table>
    
    <p>请按时到达，并携带有效身份证件。</p>
    <p>如有疑问，请联系接待员工。</p>
    
    <hr>
    <p><small>此邮件由访客管理系统自动发送，请勿回复。</small></p>
</body>
</html>
        """)

        html_content = template.render(visitor=visitor)
        
        await self._send_email(
            to_email=visitor.email,
            subject="访客预约确认通知",
            html_content=html_content
        )

    async def _send_email(self, to_email: str, subject: str, html_content: str):
        """发送邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{EMAIL_CONFIG['from_name']} <{self.username}>"
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if EMAIL_CONFIG["use_tls"]:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"邮件已发送至: {to_email}")
        except Exception as e:
            print(f"邮件发送失败: {e}")
```

## 🤖 智能设备集成

### 人脸识别设备集成
```python
# services/face_recognition_service.py
class FaceRecognitionService:
    def __init__(self, device_api_url: str, api_key: str):
        self.device_api_url = device_api_url
        self.api_key = api_key

    async def register_visitor_face(self, visitor: VisitorModel, face_image: bytes) -> bool:
        """注册访客人脸"""
        url = f"{self.device_api_url}/api/face/register"
        
        data = {
            "user_id": str(visitor.id),
            "user_name": visitor.name,
            "pass_code": visitor.pass_code,
            "valid_from": visitor.expected_date.isoformat(),
            "valid_until": (visitor.expected_date + timedelta(days=1)).isoformat()
        }

        files = {
            "face_image": ("face.jpg", face_image, "image/jpeg")
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, files=files, headers=headers)
            return response.status_code == 200

    async def delete_visitor_face(self, visitor_id: int) -> bool:
        """删除访客人脸"""
        url = f"{self.device_api_url}/api/face/delete/{visitor_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            return response.status_code == 200

    async def get_access_records(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """获取门禁记录"""
        url = f"{self.device_api_url}/api/access/records"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
            return []
```

### 门禁系统集成
```python
# services/access_control_service.py
class AccessControlService:
    def __init__(self, device_config: dict):
        self.device_config = device_config

    async def grant_access(self, visitor: VisitorModel) -> bool:
        """授权访客门禁权限"""
        access_data = {
            "card_no": visitor.pass_code,
            "user_name": visitor.name,
            "access_level": self._get_access_level(visitor.purpose),
            "time_from": visitor.expected_date.isoformat(),
            "time_to": (visitor.expected_date + timedelta(hours=8)).isoformat(),
            "doors": self._get_accessible_doors(visitor)
        }

        return await self._send_to_access_system(access_data)

    def _get_access_level(self, purpose: str) -> int:
        """根据访问目的确定门禁级别"""
        level_map = {
            "business_meeting": 2,
            "interview": 1,
            "site_visit": 1,
            "delivery": 0,
            "maintenance": 3
        }
        return level_map.get(purpose, 1)

    def _get_accessible_doors(self, visitor: VisitorModel) -> List[str]:
        """获取可访问的门禁点"""
        if visitor.employee and visitor.employee.department:
            # 根据部门确定可访问区域
            department_doors = {
                "产品部": ["main_entrance", "building_a_floor_3"],
                "技术部": ["main_entrance", "building_a_floor_2"],
                "行政部": ["main_entrance", "building_a_floor_1"]
            }
            return department_doors.get(visitor.employee.department.name, ["main_entrance"])
        return ["main_entrance"]
```

## 🏢 OA系统集成

### 员工信息同步
```python
# services/oa_integration_service.py
class OAIntegrationService:
    def __init__(self, oa_api_url: str, api_key: str):
        self.oa_api_url = oa_api_url
        self.api_key = api_key

    async def sync_employees(self) -> int:
        """同步员工信息"""
        url = f"{self.oa_api_url}/api/employees"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception("获取员工信息失败")

            oa_employees = response.json()
            synced_count = 0

            for oa_emp in oa_employees:
                await self._sync_single_employee(oa_emp)
                synced_count += 1

            return synced_count

    async def _sync_single_employee(self, oa_employee: dict):
        """同步单个员工"""
        # 查找或创建员工记录
        employee = await self.employee_repository.get_by_employee_id(
            oa_employee["employee_id"]
        )

        if employee:
            # 更新现有员工信息
            employee.name = oa_employee["name"]
            employee.email = oa_employee["email"]
            employee.phone_number = oa_employee["phone"]
            employee.position = oa_employee["position"]
            employee.status = oa_employee["status"]
            await self.employee_repository.update(employee)
        else:
            # 创建新员工记录
            new_employee = EmployeeModel(
                name=oa_employee["name"],
                employee_id=oa_employee["employee_id"],
                email=oa_employee["email"],
                phone_number=oa_employee["phone"],
                position=oa_employee["position"],
                department_id=await self._get_department_id(oa_employee["department"]),
                tenant_id="default_tenant",
                created_by="oa_sync"
            )
            await self.employee_repository.create(new_employee)
```

## 📊 数据导出集成

### 报表数据API
```python
# api/routes/export.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
import pandas as pd
from io import BytesIO

router = APIRouter()

@router.get("/visitors/export")
async def export_visitors(
    format: str = Query("excel", regex="^(excel|csv|json)$"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """导出访客数据"""
    
    # 构建查询条件
    filters = {}
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    if status:
        filters["status"] = status

    # 获取数据
    visitors = await visitor_service.get_visitors_for_export(filters)
    
    # 转换为DataFrame
    df = pd.DataFrame([
        {
            "访客ID": v.id,
            "姓名": v.name,
            "电话": v.phone_number,
            "公司": v.company_name,
            "访问目的": v.purpose,
            "状态": v.status,
            "预约时间": v.expected_date,
            "签到时间": v.checkin_date,
            "签出时间": v.checkout_date,
            "接待员工": v.employee.name if v.employee else "",
            "部门": v.employee.department.name if v.employee and v.employee.department else ""
        }
        for v in visitors
    ])

    # 根据格式返回数据
    if format == "excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='访客数据')
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=visitors.xlsx"}
        )
    
    elif format == "csv":
        output = StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=visitors.csv"}
        )
    
    else:  # json
        return df.to_dict(orient='records')
```

## 🔐 API安全集成

### API密钥管理
```python
# services/api_key_service.py
class APIKeyService:
    def __init__(self):
        self.active_keys = {}  # 内存缓存活跃密钥

    async def generate_api_key(self, client_name: str, permissions: List[str]) -> str:
        """生成API密钥"""
        api_key = secrets.token_urlsafe(32)
        
        # 保存到数据库
        api_key_record = APIKeyModel(
            key_hash=self._hash_key(api_key),
            client_name=client_name,
            permissions=permissions,
            expires_at=datetime.now() + timedelta(days=365),
            is_active=True
        )
        await self.api_key_repository.create(api_key_record)
        
        return api_key

    async def validate_api_key(self, api_key: str) -> Optional[APIKeyModel]:
        """验证API密钥"""
        key_hash = self._hash_key(api_key)
        
        # 先从缓存查找
        if key_hash in self.active_keys:
            return self.active_keys[key_hash]
        
        # 从数据库查找
        key_record = await self.api_key_repository.get_by_hash(key_hash)
        if key_record and key_record.is_active and key_record.expires_at > datetime.now():
            self.active_keys[key_hash] = key_record
            return key_record
        
        return None

    def _hash_key(self, api_key: str) -> str:
        """对API密钥进行哈希"""
        return hashlib.sha256(api_key.encode()).hexdigest()
```

### Webhook集成
```python
# api/routes/webhooks.py
@router.post("/webhook/visitor-status")
async def visitor_status_webhook(
    visitor_id: int,
    new_status: str,
    webhook_secret: str = Header(..., alias="X-Webhook-Secret")
):
    """访客状态变更Webhook"""
    
    # 验证webhook密钥
    if not verify_webhook_secret(webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    
    # 更新访客状态
    visitor = await visitor_service.update_status(visitor_id, new_status)
    
    # 触发相关通知
    await notification_service.notify_status_change(visitor)
    
    return {"success": True, "visitor_id": visitor_id, "new_status": new_status}

def verify_webhook_secret(secret: str) -> bool:
    """验证webhook密钥"""
    expected_secret = os.getenv("WEBHOOK_SECRET")
    return hmac.compare_digest(secret, expected_secret)
```

## 📋 集成测试

### 集成测试套件
```python
# test/integration/test_third_party_integration.py
import pytest
from unittest.mock import AsyncMock, patch

class TestThirdPartyIntegration:
    
    @pytest.mark.asyncio
    async def test_wechat_message_sending(self):
        """测试企业微信消息发送"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value.json.return_value = {"errcode": 0}
            
            wechat_service = WeChatService("corp_id", "secret")
            result = await wechat_service.send_message("user123", "测试消息")
            
            assert result == True
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_email_sending(self):
        """测试邮件发送"""
        email_service = EmailService()
        visitor = VisitorModel(
            name="张三",
            email="test@example.com",
            pass_code="V123456"
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            await email_service.send_visitor_confirmation(visitor)
            mock_smtp.assert_called_once()

    @pytest.mark.asyncio
    async def test_face_recognition_integration(self):
        """测试人脸识别设备集成"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value.status_code = 200
            
            face_service = FaceRecognitionService("http://device-api", "api-key")
            result = await face_service.register_visitor_face(visitor, b"face_image_data")
            
            assert result == True
```

---

## 📞 技术支持

### 集成支持
- **负责人**: 系统集成团队
- **技术栈**: RESTful API、Webhook、SMTP
- **问题反馈**: 通过集成支持平台提交

### 相关文档
- [后端API完整参考手册](./Backend_API_Reference.md)
- [后端系统架构概览](./Backend_System_Architecture.md)
- [前端对接指南](./Frontend_Integration_Guide.md)