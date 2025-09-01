from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..security import get_db, get_current_user
from ..models.models import HelpdeskTicket, User
from ..schemas import TicketCreate

router = APIRouter(prefix="/api/helpdesk", tags=["helpdesk"])

@router.post("/tickets")
async def create_ticket(payload: TicketCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    t = HelpdeskTicket(created_by=u.id, title=payload.title, description=payload.description or "", priority=payload.priority, status="open")
    db.add(t); await db.commit(); return {"ok": True, "id": t.id}

@router.get("/tickets")
async def list_tickets(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(HelpdeskTicket).order_by(HelpdeskTicket.id.desc()))
    return [ {"id":t.id,"title":t.title,"priority":t.priority,"status":t.status,"created_at":str(t.created_at)} for t in res.scalars().all() ]
