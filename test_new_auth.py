import requests
import json

def test_new_authentication():
    """测试新的认证系统"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== 测试新认证系统 ===\n")
    
    # 测试1: 使用数据库中的管理员账户登录
    print("1. 测试数据库管理员登录 (admin@company.com)")
    login_data = {
        "username": "admin@company.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录成功!")
            print(f"用户信息: {json.dumps(data['user_info'], indent=2, ensure_ascii=False)}")
            print(f"令牌类型: {data['token_type']}")
            print(f"过期时间: {data['expires_in']}秒")
            
            # 保存令牌用于后续测试
            token = data['access_token']
            
            # 测试获取当前用户信息
            print("\n2. 测试获取当前用户信息")
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
            
            if me_response.status_code == 200:
                print("✅ 获取用户信息成功!")
                print(f"当前用户: {json.dumps(me_response.json(), indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ 获取用户信息失败: {me_response.text}")
        else:
            print(f"❌ 登录失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试2: 使用旧的硬编码认证（兼容性测试）
    print("\n3. 测试兼容旧认证 (admin)")
    login_data_old = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data_old,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ 兼容性登录成功!")
            print(f"用户信息: {json.dumps(data['user_info'], indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 兼容性登录失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试3: 错误密码
    print("\n4. 测试错误密码")
    login_data_wrong = {
        "username": "admin@company.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data_wrong,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 401:
            print("✅ 正确拒绝了错误密码")
        else:
            print(f"❌ 意外结果: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_new_authentication() 