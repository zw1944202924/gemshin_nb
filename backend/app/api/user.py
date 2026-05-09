
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import jwt
from datetime import datetime, timedelta
from typing import Optional

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app import schemas, services

router = APIRouter()
security = HTTPBearer()


def create_access_token(user_id: int, username: str) -> str:
    """生成JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user_id), "username": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(user_id: int, username: str) -> str:
    """生成JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"sub": str(user_id), "username": username, "type": "refresh", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> dict:
    """验证JWT token并返回payload"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """获取当前用户（需要access token）"""
    token = credentials.credentials
    payload = verify_token(token)
    if payload.get("type") == "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请使用access token访问"
        )
    return payload


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """获取当前用户（可选，匿名用户返回None）"""
    if credentials is None:
        return None
    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None

@router.post("/login")
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        user = services.user.login(db, user_login.username, user_login.password)
        if not user:
            raise HTTPException(status_code=400, detail="用户名或密码错误")
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id, user.username)
        return {
            "code": 0,
            "message": "登录成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败：{str(e)}")

@router.post("/register")
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = services.user.get_user_by_username(db, user_create.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user = services.user.create_user(db, user_create)
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id, user.username)
        return {
            "code": 0,
            "message": "注册成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        }
    except IntegrityError as e:
        db.rollback()
        if "users.username" in str(e):
            raise HTTPException(status_code=400, detail="用户名已存在")
        if "users.email" in str(e):
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        raise HTTPException(status_code=400, detail="数据提交错误，请检查输入")
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败：{str(e)}")


@router.post("/refresh")
def refresh_token(refresh_request: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    """刷新access token"""
    try:
        payload = verify_token(refresh_request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的refresh token"
            )

        user_id = int(payload.get("sub"))
        username = payload.get("username")

        user = services.user.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已禁用"
            )

        access_token = create_access_token(user.id, user.username)
        new_refresh_token = create_refresh_token(user.id, user.username)

        return {
            "code": 0,
            "message": "Token刷新成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token刷新失败：{str(e)}")
