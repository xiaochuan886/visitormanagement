"""
认证API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app.infrastructure.auth.jwt_handler import jwt_handler
from app.infrastructure.database.connection import get_db
from app.domain.entities.employee import Employee

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str  # 可以是email或用户名
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_info: dict


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


async def authenticate_employee(email: str, password: str, db: AsyncSession):
    """认证员工用户"""
    from sqlalchemy import text
    
    # 查询员工
    query = text("""
        SELECT e.*, array_agg(r.name) as roles, array_agg(r.permissions) as permissions
        FROM employees e
        LEFT JOIN employee_roles er ON e.id = er.employee_id
        LEFT JOIN user_roles r ON er.role_id = r.id
        WHERE e.email = :email 
        AND e.status = 'active' 
        AND (e.is_deleted IS NULL OR e.is_deleted = FALSE)
        GROUP BY e.id
    """)
    
    result = await db.execute(query, {"email": email})
    row = result.fetchone()
    
    if not row:
        return None
    
    # 检查密码
    if not row.password_hash:
        return None
    
    if not pwd_context.verify(password, row.password_hash):
        # 记录失败登录
        update_query = text("""
            UPDATE employees 
            SET login_attempts = COALESCE(login_attempts, 0) + 1,
                locked_until = CASE 
                    WHEN COALESCE(login_attempts, 0) + 1 >= 5 
                    THEN NOW() + INTERVAL '30 minutes'
                    ELSE locked_until
                END
            WHERE id = :employee_id
        """)
        await db.execute(update_query, {"employee_id": row.id})
        await db.commit()
        return None
    
    # 检查账户是否锁定
    if row.locked_until and datetime.now(timezone.utc) < row.locked_until:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"账户已被锁定，请在 {row.locked_until} 后重试"
        )
    
    # 登录成功，重置登录尝试
    update_query = text("""
        UPDATE employees 
        SET login_attempts = 0, 
            locked_until = NULL, 
            last_login_at = NOW()
        WHERE id = :employee_id
    """)
    await db.execute(update_query, {"employee_id": row.id})
    await db.commit()
    
    # 处理角色和权限
    roles = [r for r in row.roles if r] if row.roles else []
    permissions = []
    if row.permissions:
        for perm_list in row.permissions:
            if perm_list:
                import json
                try:
                    perms = json.loads(perm_list)
                    permissions.extend(perms)
                except:
                    pass
    
    return {
        "id": row.id,
        "name": row.name,
        "email": row.email,
        "employee_id": row.employee_id,
        "position": row.position,
        "tenant_id": row.tenant_id,
        "roles": roles,
        "permissions": list(set(permissions))  # 去重
    }


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    try:
        # 尝试员工认证
        user_info = await authenticate_employee(login_data.username, login_data.password, db)
        
        if not user_info:
            # 兼容旧的硬编码认证
            if login_data.username == "admin" and login_data.password == "admin123":
                user_info = {
                    "id": "1",
                    "name": "Admin User",
                    "email": "admin@system.com",
                    "employee_id": "ADMIN",
                    "position": "System Administrator",
                    "tenant_id": "default",
                    "roles": ["admin"],
                    "permissions": ["*"]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
        
        # 创建令牌
        tokens = jwt_handler.create_user_tokens(
            user_id=str(user_info["id"]),
            username=user_info["name"],
            tenant_id=user_info["tenant_id"],
            roles=user_info["roles"],
            permissions=user_info["permissions"]
        )
        
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=jwt_handler.access_token_expire_minutes * 60,
            user_info={
                "id": user_info["id"],
                "name": user_info["name"],
                "email": user_info["email"],
                "employee_id": user_info["employee_id"],
                "position": user_info["position"],
                "roles": user_info["roles"]
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/refresh", response_model=dict, summary="刷新访问令牌")
async def refresh_access_token(refresh_data: RefreshTokenRequest):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        payload = jwt_handler.verify_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id", "default")
        
        # 创建新的访问令牌
        token_data = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "roles": ["admin"],  # 实际项目中应从数据库获取
            "permissions": ["visitor:read", "visitor:write", "visitor:delete"]
        }
        
        access_token = jwt_handler.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": jwt_handler.access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期"
        )


@router.post("/logout", summary="用户登出")
async def logout():
    """用户登出"""
    # 在实际项目中，可能需要将令牌加入黑名单
    return {"message": "登出成功"}


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(current_user: dict = Depends(jwt_handler.verify_token)):
    """获取当前用户信息"""
    return {
        "user_id": current_user.get("sub"),
        "username": current_user.get("username"),
        "tenant_id": current_user.get("tenant_id"),
        "roles": current_user.get("roles", []),
        "permissions": current_user.get("permissions", [])
    } 