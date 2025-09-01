from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..schemas import Token
from ..models.models import User
from ..security import get_db, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(payload: dict, db: AsyncSession = Depends(get_db)):
    username = payload.get("username", "")
    password = payload.get("password", "")
    q = await db.execute(select(User).where((User.username == username) | (User.email == username)))
    user = q.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
    )
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}
