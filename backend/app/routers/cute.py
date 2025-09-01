from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models import Cute
from app.schemas import CuterCreate, CuterResponse
from typing import List

router = APIRouter(prefix="/cuters", tags=["cuters"])

@router.post("/", response_model=CuterResponse)
async def create_cuter(cuter: CuterCreate, db: AsyncSession = Depends(get_db)):
    db_cuter = Cute(
        name=cuter.name,
        description=cuter.description
    )
    db.add(db_cuter)
    await db.commit()
    await db.refresh(db_cuter)
    return db_cuter

@router.get("/", response_model=List[CuterResponse])
async def get_cuters(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cute))
    return result.scalars().all()

@router.get("/{cuter_id}", response_model=CuterResponse)
async def get_cuter(cuter_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cute).where(Cute.id == cuter_id))
    db_cuter = result.scalars().first()
    if not db_cuter:
        raise HTTPException(status_code=404, detail="Cuter not found")
    return db_cuter
