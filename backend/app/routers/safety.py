from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..security import get_db, get_current_user
from ..models.models import SafetyReport, EnvironmentReport, User

router = APIRouter(prefix="/api/safety", tags=["safety"])

@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    s_cnt = (await db.execute(select(func.count()).select_from(SafetyReport))).scalar() or 0
    e_cnt = (await db.execute(select(func.count()).select_from(EnvironmentReport))).scalar() or 0
    return {"safety_reports": int(s_cnt), "environment_reports": int(e_cnt)}
