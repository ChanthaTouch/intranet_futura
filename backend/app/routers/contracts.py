from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, insert, delete
from ..security import get_db, get_current_user
from ..models.models import Office, Contract, UserFavorite, ContractClientToken, User
import secrets

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

@router.get("/offices")
async def list_offices(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(Office).order_by(Office.name.asc()))
    return [ {"id":o.id,"name":o.name} for o in res.scalars().all() ]

def _base_filter(office_id: int | None):
    from sqlalchemy import true
    return (Contract.office_id == office_id) if office_id else true()

@router.get("/stats")
async def contract_stats(office_id: int | None = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    fav_count = (await db.execute(select(func.count()).select_from(UserFavorite).join(Contract, Contract.id==UserFavorite.contract_id).where(UserFavorite.user_id==u.id).where(_base_filter(office_id)))).scalar() or 0
    ext_count = (await db.execute(select(func.count()).select_from(Contract).where(Contract.client_type=="external").where(Contract.status!="archived").where(_base_filter(office_id)))).scalar() or 0
    int_count = (await db.execute(select(func.count()).select_from(Contract).where(Contract.client_type=="internal").where(Contract.status!="archived").where(_base_filter(office_id)))).scalar() or 0
    onhold = (await db.execute(select(func.count()).select_from(Contract).where(Contract.status=="on_hold").where(_base_filter(office_id)))).scalar() or 0
    liquid = (await db.execute(select(func.count()).select_from(Contract).where(Contract.status=="to_be_liquidated").where(_base_filter(office_id)))).scalar() or 0
    archived = (await db.execute(select(func.count()).select_from(Contract).where(Contract.status=="archived").where(_base_filter(office_id)))).scalar() or 0
    return {"favorites":fav_count,"external":ext_count,"internal":int_count,"on_hold":onhold,"to_be_liquidated":liquid,"archived":archived}

@router.get("/list")
async def list_contracts(group: str, office_id: int | None = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    q = select(Contract)
    if group == "favorites":
        q = q.join(UserFavorite, UserFavorite.contract_id==Contract.id).where(UserFavorite.user_id==u.id)
    elif group == "external":
        q = q.where(Contract.client_type=="external", Contract.status!="archived")
    elif group == "internal":
        q = q.where(Contract.client_type=="internal", Contract.status!="archived")
    elif group == "on_hold":
        q = q.where(Contract.status=="on_hold")
    elif group == "to_be_liquidated":
        q = q.where(Contract.status=="to_be_liquidated")
    elif group == "archived":
        q = q.where(Contract.status=="archived")
    if office_id:
        q = q.where(Contract.office_id==office_id)
    res = await db.execute(q.order_by(Contract.code.asc()))
    return [ {"id":c.id,"code":c.code,"name":c.name,"status":c.status,"client_type":c.client_type,"office_id":c.office_id} for c in res.scalars().all() ]

@router.post("/favorite/{contract_id}")
async def add_favorite(contract_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    await db.execute(insert(UserFavorite).values(user_id=u.id, contract_id=contract_id).prefix_with("IGNORE"))
    await db.commit(); return {"ok": True}

@router.delete("/favorite/{contract_id}")
async def remove_favorite(contract_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    await db.execute(delete(UserFavorite).where(UserFavorite.user_id==u.id, UserFavorite.contract_id==contract_id)); await db.commit(); return {"ok": True}

@router.post("/client-access/{contract_id}")
async def create_client_access(contract_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    token = secrets.token_urlsafe(24)
    db.add(ContractClientToken(contract_id=contract_id, token=token, is_enabled=True))
    await db.commit()
    return {"ok": True, "token": token}
