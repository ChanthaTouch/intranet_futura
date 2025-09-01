from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..security import get_db, get_current_user
from ..models.models import QAChecklist, User

router = APIRouter(prefix="/api/qa", tags=["quality"])

@router.get("/checklists")
async def list_checklists(contract_id: int | None = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    q = select(QAChecklist)
    if contract_id: q = q.where(QAChecklist.contract_id==contract_id)
    res = await db.execute(q.order_by(QAChecklist.id.desc()))
    return [ {"id":x.id,"title":x.title,"status":x.status} for x in res.scalars().all() ]
