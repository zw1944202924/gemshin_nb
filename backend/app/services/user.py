
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.app.models import User
from backend.app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # bcrypt只支持前72字节，手动截断
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt只支持前72字节，手动截断
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

<<<<<<< HEAD
=======

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

>>>>>>> feature/backend-api-enhancement
def create_user(db: Session, user_create: UserCreate):
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def login(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
