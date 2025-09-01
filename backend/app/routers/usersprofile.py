from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/api/users", tags=["users"])  # e.g. GET /api/users/


# --------------------------
# Dependency to get current user (creates a demo user if none exists)
# --------------------------
async def get_current_user(db: AsyncSession = Depends(get_db)) -> models.User:
    result = await db.execute(select(models.User).limit(1))
    user = result.scalars().first()
    if not user:
        user = models.User(full_name="Demo User", phone="00000000", email="demo@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


# --------------------------
# CREATE a new user
# --------------------------
@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: schemas.UserBase, db: AsyncSession = Depends(get_db)):
    # Pydantic v2 -> use model_dump(); if you're on v1, replace with .dict()
    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    user = models.User(**payload)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# --------------------------
# READ all users
# --------------------------
@router.get("/", response_model=List[schemas.UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users


# --------------------------
# READ current user's profile
# --------------------------
@router.get("/me", response_model=schemas.UserResponse)
async def get_me(user: models.User = Depends(get_current_user)):
    return user


@router.get("/me/profile", response_model=schemas.UserResponse)
async def get_profile(user: models.User = Depends(get_current_user)):
    return user


# --------------------------
# UPDATE current user's profile
# --------------------------
@router.put("/me/profile", response_model=schemas.UserResponse)
async def update_profile(
    data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    update_data = (
        data.model_dump(exclude_unset=True)
        if hasattr(data, "model_dump")
        else data.dict(exclude_unset=True)
    )
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


# --------------------------
# DELETE a user by ID
# --------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # AsyncSession.delete() is synchronous; commit is awaited
    db.delete(user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
