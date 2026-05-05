
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import jwt
from datetime import datetime, timedelta

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app import schemas, services

router = APIRouter()

def create_access_token(user_id: int, username: str) -> str:
    """生成JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user_id), "username": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

@router.post("/login")
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        user = services.user.login(db, user_login.username, user_login.password)
        if not user:
            raise HTTPException(status_code=400, detail="用户名或密码错误")
        access_token = create_access_token(user.id, user.username)
        return {
            "code": 0, 
            "message": "登录成功", 
            "data": {
                "id": user.id, 
                "username": user.username,
                "access_token": access_token,
                "token_type": "bearer"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败：{str(e)}")

@router.post("/register")
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # 检查用户名是否已存在
        existing_user = services.user.get_user_by_username(db, user_create.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user = services.user.create_user(db, user_create)
        access_token = create_access_token(user.id, user.username)
        return {
            "code": 0, 
            "message": "注册成功", 
            "data": {
                "id": user.id, 
                "username": user.username,
                "access_token": access_token,
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
