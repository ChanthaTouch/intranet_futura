from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
import traceback, sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .config import config
from .db import SessionLocal
from .models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_minutes: int | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or config.security.access_token_exp_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.security.jwt_secret, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, config.security.jwt_secret, algorithms=["HS256"])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except Exception:
        traceback.print_exc(file=sys.stdout)
        raise credentials_exception
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user
