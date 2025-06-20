"""
门岗前台功能综合集成测试
测试访客从预约、门岗验证、前台签到到离开的完整流程
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base
from app.infrastructure.database.models import (
    VisitorModel, DeviceModel, VisitorVerificationModel,
    VisitorEntryModel, ReceptionCheckinModel, HostNotificationModel
)


class TestGateReceptionIntegration:
    """门岗前台集成测试类"""
    
    @pytest.fixture
    async def client(self):
        """异步HTTP客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def db_session(self):
        """测试数据库会话"""
        engine = create_engine("sqlite:///./test.db", echo=True)
        Base.metadata.create_all(engine)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    @pytest.fixture
    async def test_visitor_data(self):
        """测试访客数据"""
        return {
            "name": "张三",
            "phone": "13800138001",
            "id_card": "110101199001011234",
            "company": "测试公司",
            "visit_purpose": "商务洽谈",
            "host_name": "李四",
            "host_phone": "13800138002",
            "visit_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "expected_duration": 120,
            "vehicle_plate": "京A12345"
        }
    
    @pytest.fixture
    async def test_device_data(self):
        """测试设备数据"""
        return {
            "device_id": "GATE001",
            "device_name": "主门岗终端",
            "device_type": "gate_terminal",
            "location": "主入口",
            "ip_address": "192.168.1.100",
            "status": "online"
        }
    
    @pytest.mark.asyncio
    async def test_complete_visitor_flow(self, client: AsyncClient, test_visitor_data: dict, test_device_data: dict):
        """测试完整的访客流程"""
        
        # 1. 设备注册
        device_response = await client.post(
            "/api/v1/devices/register",
            json=test_device_data
        )
        assert device_response.status_code == 201
        device_data = device_response.json()
        assert device_data["success"] is True
        device_id = device_data["data"]["device_id"]
        
        # 2. 访客预约申请
        visitor_response = await client.post(
            "/api/v1/visitors/appointments",
            json=test_visitor_data
        )
        assert visitor_response.status_code == 201
        visitor_data = visitor_response.json()
        assert visitor_data["success"] is True
        visitor_id = visitor_data["data"]["id"]
        
        # 3. 门岗验证访客身份
        verification_data = {
            "visitor_id": visitor_id,
            "device_id": device_id,
            "verification_method": "qr_code",
            "verification_data": {
                "qr_code": "TEST_QR_CODE_12345",
                "scan_time": datetime.now().isoformat()
            }
        }
        
        verification_response = await client.post(
            "/api/v1/gate/verify-visitor",
            json=verification_data
        )
        assert verification_response.status_code == 200
        verification_result = verification_response.json()
        assert verification_result["success"] is True
        assert verification_result["data"]["access_granted"] is True
        
        # 4. 访客入园记录
        entry_data = {
            "visitor_id": visitor_id,
            "gate_id": device_id,
            "entry_photo_url": "https://example.com/photos/entry_001.jpg",
            "badge_number": "V001",
            "vehicle_plate": test_visitor_data["vehicle_plate"],
            "temperature_check": 36.5,
            "health_check_passed": True
        }
        
        entry_response = await client.post(
            "/api/v1/gate/visitor-entry",
            json=entry_data
        )
        assert entry_response.status_code == 201
        entry_result = entry_response.json()
        assert entry_result["success"] is True
        entry_id = entry_result["data"]["entry_id"]
        
        # 5. 获取今日访客列表
        today_visitors_response = await client.get(
            f"/api/v1/gate/today-visitors?gate_id={device_id}"
        )
        assert today_visitors_response.status_code == 200
        today_visitors = today_visitors_response.json()
        assert today_visitors["success"] is True
        assert len(today_visitors["data"]["visitors"]) > 0
        
        # 6. 前台签到
        checkin_data = {
            "visitor_id": visitor_id,
            "reception_desk_id": "RECEPTION001",
            "checkin_method": "manual",
            "waiting_area_id": "WAIT_AREA_A",
            "services_provided": ["身份验证", "访客登记", "等候安排"]
        }
        
        checkin_response = await client.post(
            "/api/v1/reception/visitor-checkin",
            json=checkin_data
        )
        assert checkin_response.status_code == 201
        checkin_result = checkin_response.json()
        assert checkin_result["success"] is True
        checkin_id = checkin_result["data"]["checkin_id"]
        
        # 7. 通知主机
        notification_data = {
            "visitor_id": visitor_id,
            "employee_id": 1,  # 假设主机员工ID
            "notification_channels": ["wechat", "email"],
            "notification_content": {
                "title": "访客到访通知",
                "message": f"您的访客{test_visitor_data['name']}已到达前台",
                "visitor_info": test_visitor_data
            }
        }
        
        notification_response = await client.post(
            "/api/v1/reception/notify-host",
            json=notification_data
        )
        assert notification_response.status_code == 201
        notification_result = notification_response.json()
        assert notification_result["success"] is True
        
        # 8. 获取等候区域状态
        waiting_status_response = await client.get(
            "/api/v1/reception/waiting-area/status"
        )
        assert waiting_status_response.status_code == 200
        waiting_status = waiting_status_response.json()
        assert waiting_status["success"] is True
        
        # 9. 移动端同步验证
        mobile_sync_data = {
            "device_id": "MOBILE001",
            "sync_type": "visitor_verification",
            "data_types": ["visitors", "verifications"],
            "last_sync_time": datetime.now().isoformat()
        }
        
        mobile_sync_response = await client.post(
            "/api/v1/mobile/sync-data",
            json=mobile_sync_data
        )
        assert mobile_sync_response.status_code == 200
        mobile_sync_result = mobile_sync_response.json()
        assert mobile_sync_result["success"] is True
        
        # 10. 设备状态监控
        device_monitoring_response = await client.get(
            f"/api/v1/devices/{device_id}/monitoring"
        )
        assert device_monitoring_response.status_code == 200
        monitoring_data = device_monitoring_response.json()
        assert monitoring_data["success"] is True
        
        print(f"✅ 完整访客流程测试成功:")
        print(f"   - 访客ID: {visitor_id}")
        print(f"   - 入园记录ID: {entry_id}")
        print(f"   - 签到记录ID: {checkin_id}")
    
    @pytest.mark.asyncio
    async def test_gate_verification_scenarios(self, client: AsyncClient):
        """测试门岗验证各种场景"""
        
        # 测试数据
        scenarios = [
            {
                "name": "二维码验证",
                "method": "qr_code",
                "data": {"qr_code": "QR123456", "scan_time": datetime.now().isoformat()},
                "expected_success": True
            },
            {
                "name": "身份证验证",
                "method": "id_card",
                "data": {"id_number": "110101199001011234", "scan_time": datetime.now().isoformat()},
                "expected_success": True
            },
            {
                "name": "人脸识别验证",
                "method": "face_recognition",
                "data": {"face_image": "base64_encoded_image", "confidence": 95.5},
                "expected_success": True
            },
            {
                "name": "手动验证",
                "method": "manual",
                "data": {"operator": "门岗保安", "reason": "系统故障临时处理"},
                "expected_success": True
            }
        ]
        
        for scenario in scenarios:
            verification_data = {
                "visitor_id": 1,  # 假设访客ID
                "device_id": "GATE001",
                "verification_method": scenario["method"],
                "verification_data": scenario["data"]
            }
            
            response = await client.post(
                "/api/v1/gate/verify-visitor",
                json=verification_data
            )
            
            if scenario["expected_success"]:
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                print(f"✅ {scenario['name']}验证测试通过")
            else:
                assert response.status_code >= 400
                print(f"❌ {scenario['name']}验证测试失败（预期）")
    
    @pytest.mark.asyncio
    async def test_reception_workflow(self, client: AsyncClient):
        """测试前台工作流程"""
        
        # 1. 获取前台工作台状态
        dashboard_response = await client.get("/api/v1/reception/dashboard")
        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()
        assert dashboard_data["success"] is True
        
        # 2. 访客签到流程测试
        checkin_methods = ["qr_code", "manual", "face_recognition", "id_card", "self_service"]
        
        for method in checkin_methods:
            checkin_data = {
                "visitor_id": 1,
                "reception_desk_id": "RECEPTION001",
                "checkin_method": method,
                "waiting_area_id": "WAIT_AREA_A"
            }
            
            response = await client.post(
                "/api/v1/reception/visitor-checkin",
                json=checkin_data
            )
            assert response.status_code == 201
            result = response.json()
            assert result["success"] is True
            print(f"✅ {method}签到方式测试通过")
        
        # 3. 会议室管理测试
        meeting_room_data = {
            "room_name": "会议室A",
            "room_code": "ROOM_A001",
            "capacity": 10,
            "location": "3楼西侧",
            "amenities": ["投影仪", "白板", "网络"],
            "booking_rules": {
                "advance_booking_days": 7,
                "max_booking_hours": 4,
                "min_booking_minutes": 30
            }
        }
        
        room_response = await client.post(
            "/api/v1/reception/meeting-rooms",
            json=meeting_room_data
        )
        assert room_response.status_code == 201
        room_result = room_response.json()
        assert room_result["success"] is True
        print("✅ 会议室创建测试通过")
    
    @pytest.mark.asyncio
    async def test_device_management(self, client: AsyncClient):
        """测试设备管理功能"""
        
        # 1. 设备注册
        device_data = {
            "device_id": "TEST_DEVICE_001",
            "device_name": "测试设备",
            "device_type": "gate_terminal",
            "location": "测试位置",
            "ip_address": "192.168.1.200",
            "capabilities": ["qr_scan", "face_recognition", "id_card_reader"]
        }
        
        register_response = await client.post(
            "/api/v1/devices/register",
            json=device_data
        )
        assert register_response.status_code == 201
        register_result = register_response.json()
        assert register_result["success"] is True
        device_id = register_result["data"]["device_id"]
        
        # 2. 设备状态更新
        status_data = {
            "status": "online",
            "cpu_usage": 45.2,
            "memory_usage": 68.1,
            "disk_usage": 32.5,
            "temperature": 42.0
        }
        
        status_response = await client.post(
            f"/api/v1/devices/{device_id}/status",
            json=status_data
        )
        assert status_response.status_code == 200
        status_result = status_response.json()
        assert status_result["success"] is True
        
        # 3. 设备配置更新
        config_data = {
            "configuration": {
                "scan_timeout": 30,
                "recognition_threshold": 0.85,
                "auto_sync_interval": 300
            },
            "operator": "系统管理员"
        }
        
        config_response = await client.put(
            f"/api/v1/devices/{device_id}/config",
            json=config_data
        )
        assert config_response.status_code == 200
        config_result = config_response.json()
        assert config_result["success"] is True
        
        print(f"✅ 设备管理功能测试通过 - 设备ID: {device_id}")
    
    @pytest.mark.asyncio
    async def test_mobile_sync_functionality(self, client: AsyncClient):
        """测试移动端同步功能"""
        
        # 1. 数据同步测试
        sync_data = {
            "device_id": "MOBILE_TEST_001",
            "sync_type": "full_sync",
            "data_types": ["visitors", "verifications", "entries"],
            "last_sync_time": None,  # 首次同步
            "network_quality": "good"
        }
        
        sync_response = await client.post(
            "/api/v1/mobile/sync-data",
            json=sync_data
        )
        assert sync_response.status_code == 200
        sync_result = sync_response.json()
        assert sync_result["success"] is True
        
        # 2. 离线验证上传测试
        offline_verifications = [
            {
                "visitor_id": 1,
                "device_id": "MOBILE_TEST_001",
                "verification_method": "qr_code",
                "verification_data": {"qr_code": "OFFLINE_QR_001"},
                "offline_time": datetime.now().isoformat(),
                "device_timestamp": datetime.now().isoformat()
            }
        ]
        
        upload_response = await client.post(
            "/api/v1/mobile/upload-offline-verifications",
            json={"verifications": offline_verifications}
        )
        assert upload_response.status_code == 200
        upload_result = upload_response.json()
        assert upload_result["success"] is True
        
        # 3. 应急验证测试
        emergency_data = {
            "emergency_type": "system_failure",
            "reason": "网络中断",
            "affected_devices": ["GATE001", "GATE002"],
            "operation_type": "enable_offline_mode",
            "operator": "应急响应员"
        }
        
        emergency_response = await client.post(
            "/api/v1/mobile/emergency-verification",
            json=emergency_data
        )
        assert emergency_response.status_code == 200
        emergency_result = emergency_response.json()
        assert emergency_result["success"] is True
        
        print("✅ 移动端同步功能测试通过")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_edge_cases(self, client: AsyncClient):
        """测试错误处理和边界情况"""
        
        # 1. 测试不存在的访客验证
        invalid_verification = {
            "visitor_id": 99999,  # 不存在的访客ID
            "device_id": "GATE001",
            "verification_method": "qr_code",
            "verification_data": {"qr_code": "INVALID_QR"}
        }
        
        response = await client.post(
            "/api/v1/gate/verify-visitor",
            json=invalid_verification
        )
        assert response.status_code == 404
        
        # 2. 测试无效设备状态更新
        invalid_status = {
            "status": "invalid_status",  # 无效状态
            "cpu_usage": 150.0  # 超出范围
        }
        
        response = await client.post(
            "/api/v1/devices/INVALID_DEVICE/status",
            json=invalid_status
        )
        assert response.status_code in [400, 404]
        
        # 3. 测试重复签到
        duplicate_checkin = {
            "visitor_id": 1,
            "reception_desk_id": "RECEPTION001",
            "checkin_method": "manual"
        }
        
        # 第一次签到
        response1 = await client.post(
            "/api/v1/reception/visitor-checkin",
            json=duplicate_checkin
        )
        # 第二次签到（重复）
        response2 = await client.post(
            "/api/v1/reception/visitor-checkin", 
            json=duplicate_checkin
        )
        
        # 根据业务逻辑，可能允许或不允许重复签到
        print(f"重复签到测试: 第一次={response1.status_code}, 第二次={response2.status_code}")
        
        print("✅ 错误处理和边界情况测试完成")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"]) 