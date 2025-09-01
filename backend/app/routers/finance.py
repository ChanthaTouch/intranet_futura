from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..security import get_db, get_current_user
from ..models.models import Budget, Invoice, User
from ..schemas import ContractUpdate, InvoiceCreate

router = APIRouter(prefix="/api/finance", tags=["finance"])

@router.post("/budgets")
async def create_budget(payload: ContractUpdate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    b = Budget(**payload.model_dump()); db.add(b); await db.commit(); return {"ok": True, "id": b.id}

@router.post("/invoices")
async def create_invoice(payload: InvoiceCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    inv = Invoice(**payload.model_dump()); db.add(inv); await db.commit(); return {"ok": True, "id": inv.id}

@router.get("/stats")
async def finance_stats(contract_id: int | None = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    q = select(func.sum(Budget.amount), func.count(Budget.id))
    if contract_id: q = q.where(Budget.contract_id==contract_id)
    bsum, bcount = (await db.execute(q)).one()
    paid = (await db.execute(select(func.sum(Invoice.amount)).where(Invoice.status=="paid"))).scalar()
    overdue = (await db.execute(select(func.count()).select_from(Invoice).where(Invoice.status=="overdue"))).scalar()
    return {"budget_total": float(bsum or 0), "budget_count": int(bcount or 0), "paid_total": float(paid or 0), "overdue_count": int(overdue or 0)}
