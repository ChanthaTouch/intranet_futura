from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models import Recruitment
from app.schemas import RecruitmentCreate, RecruitmentResponse
from typing import List

router = APIRouter(prefix="/recruitments", tags=["recruitments"])


# Create a recruitment
@router.post("/", response_model=RecruitmentResponse)
async def create_recruitment(recruitment: RecruitmentCreate, db: AsyncSession = Depends(get_db)):
    db_recruitment = Recruitment(
        name=recruitment.name,
        position=recruitment.position,
        project=recruitment.project,
        hiring_manager=recruitment.hiring_manager,
        request_date=recruitment.request_date,
        start_date=recruitment.start_date,
        status=recruitment.status
    )
    db.add(db_recruitment)
    await db.commit()
    await db.refresh(db_recruitment)
    return db_recruitment


# Get all recruitments
@router.get("/", response_model=List[RecruitmentResponse])
async def get_recruitments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recruitment))
    return result.scalars().all()


# Get recruitment by ID
@router.get("/{recruitment_id}", response_model=RecruitmentResponse)
async def get_recruitment(recruitment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recruitment).where(Recruitment.id == recruitment_id))
    db_recruitment = result.scalars().first()
    if not db_recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")
    return db_recruitment


# Update recruitment
@router.put("/{recruitment_id}", response_model=RecruitmentResponse)
async def update_recruitment(recruitment_id: int, recruitment: RecruitmentCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recruitment).where(Recruitment.id == recruitment_id))
    db_recruitment = result.scalars().first()
    if not db_recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")

    db_recruitment.name = recruitment.name
    db_recruitment.position = recruitment.position
    db_recruitment.project = recruitment.project
    db_recruitment.hiring_manager = recruitment.hiring_manager
    db_recruitment.request_date = recruitment.request_date
    db_recruitment.start_date = recruitment.start_date
    db_recruitment.status = recruitment.status

    await db.commit()
    await db.refresh(db_recruitment)
    return db_recruitment


# Delete recruitment
@router.delete("/{recruitment_id}")
async def delete_recruitment(recruitment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recruitment).where(Recruitment.id == recruitment_id))
    db_recruitment = result.scalars().first()
    if not db_recruitment:
        raise HTTPException(status_code=404, detail="Recruitment not found")
    await db.delete(db_recruitment)
    await db.commit()
    return {"message": "Recruitment deleted successfully"}
