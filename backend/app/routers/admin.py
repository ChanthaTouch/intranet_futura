
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..security import get_db, get_current_user, get_password_hash
from ..models.models import Holiday, User, Role, Contract, Client, ContractAccess
from ..schemas import UserCreate, UserUpdate, UserOut, ContractCreate, ContractUpdate, ClientCreate, ClientUpdate, RoleCreate, RoleUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])

def ensure_admin(u: User):
    if u.role_id != 1:
        raise HTTPException(status_code=403, detail="Admin only")

@router.get("/users", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    res = await db.execute(select(User).order_by(User.id.desc()))
    return list(res.scalars().all())

@router.post("/users", response_model=UserOut)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    exists = await db.execute(select(User).where((User.username==payload.username) | (User.email==payload.email)))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User exists")
    user = User(email=payload.email, username=payload.username, full_name=payload.full_name or payload.username, hashed_password=get_password_hash(payload.password), role_id=payload.role_id or 3)
    db.add(user); await db.commit(); await db.refresh(user)
    return user

@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    res = await db.execute(select(User).where(User.id==user_id))
    user = res.scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        data["hashed_password"] = get_password_hash(data.pop("password"))
    await db.execute(update(User).where(User.id==user_id).values(**{k:v for k,v in data.items() if k in User.__table__.columns.keys()}))
    await db.commit(); await db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(delete(User).where(User.id==user_id))
    await db.commit()
    return {"ok": True}

@router.get("/roles")
async def list_roles(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    res = await db.execute(select(Role).order_by(Role.id.asc()))
    return [{"id":r.id,"name":r.name,"description":r.description} for r in res.scalars().all()]

@router.post("/roles")
async def create_role(payload: RoleCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    r = Role(name=payload.name, description=payload.description)
    db.add(r); await db.commit(); return {"ok": True, "id": r.id}

@router.put("/roles/{role_id}")
async def update_role(role_id: int, payload: RoleUpdate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(update(Role).where(Role.id==role_id).values(**payload.model_dump(exclude_unset=True)))
    await db.commit(); return {"ok": True}

@router.delete("/roles/{role_id}")
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(delete(Role).where(Role.id==role_id)); await db.commit(); return {"ok": True}

@router.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    res = await db.execute(select(Contract).order_by(Contract.code.asc()))
    return [{"id":c.id,"code":c.code,"name":c.name,"client_type":c.client_type,"status":c.status} for c in res.scalars().all()]

@router.post("/projects")
async def create_project(payload: ContractCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    c = Contract(**payload.model_dump())
    db.add(c); await db.commit()
    try:
        exists = await db.execute(select(ContractAccess).where(ContractAccess.contract_id==c.id, ContractAccess.user_id==u.id))
        if not exists.scalar_one_or_none():
            db.add(ContractAccess(contract_id=c.id, user_id=u.id, role="pm"))
            await db.commit()
    except Exception:
        pass
    return {"ok": True, "id": c.id}

@router.put("/projects/{project_id}")
async def update_project(project_id: int, payload: ContractUpdate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(update(Contract).where(Contract.id==project_id).values(**payload.model_dump(exclude_unset=True)))
    await db.commit(); return {"ok": True}

@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(delete(Contract).where(Contract.id==project_id)); await db.commit(); return {"ok": True}

@router.get("/clients")
async def list_clients(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    res = await db.execute(select(Client).order_by(Client.name.asc()))
    return [{"id":c.id,"name":c.name,"email":c.email,"phone":c.phone} for c in res.scalars().all()]

@router.post("/clients")
async def create_client(payload: ClientCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    c = Client(**payload.model_dump())
    db.add(c); await db.commit(); return {"ok": True, "id": c.id}

@router.put("/clients/{client_id}")
async def update_client(client_id: int, payload: ClientUpdate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(update(Client).where(Client.id==client_id).values(**payload.model_dump(exclude_unset=True)))
    await db.commit(); return {"ok": True}

@router.delete("/clients/{client_id}")
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(delete(Client).where(Client.id==client_id)); await db.commit(); return {"ok": True}


@router.post("/projects/{project_id}/access/{user_id}")
async def grant_project_access(project_id: int, user_id: int, payload: dict | None = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    await ensure_admin_or_pm(db, u, project_id)
    role = (payload or {}).get("role") or "member"
    exists = await db.execute(select(ContractAccess).where(ContractAccess.contract_id==project_id, ContractAccess.user_id==user_id))
    if not exists.scalar_one_or_none():
        db.add(ContractAccess(contract_id=project_id, user_id=user_id, role=role))
    else:
        await db.execute(update(ContractAccess).where(ContractAccess.contract_id==project_id, ContractAccess.user_id==user_id).values(role=role))
    await db.commit(); return {"ok": True}

@router.delete("/projects/{project_id}/access/{user_id}")
async def revoke_project_access(project_id: int, user_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(delete(ContractAccess).where(ContractAccess.contract_id==project_id, ContractAccess.user_id==user_id))
    await db.commit(); return {"ok": True}


@router.get("/projects/{project_id}/members")
async def list_project_members(project_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    res = await db.execute(
        select(User.id, User.email, User.username, User.full_name, ContractAccess.role)
        .join(ContractAccess, ContractAccess.user_id == User.id)
        .where(ContractAccess.contract_id == project_id)
        .order_by(User.username.asc())
    )
    rows = res.fetchall()
    return [{"id":r.id, "email":r.email, "username":r.username, "full_name":r.full_name, "role":r.role} for r in rows]


# ---- Holidays ----
@router.get("/holidays")
async def list_holidays(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Holiday).order_by(Holiday.date.asc()))
    return [dict(id=h.id, date=str(h.date), name=h.name, country=h.country) for h in res.scalars().all()]

@router.post("/holidays")
async def create_holiday(payload: dict, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    from datetime import date as _date
    dt = _date.fromisoformat(payload.get("date"))
    # reject weekends
    if dt.weekday() in (5,6):
        raise HTTPException(status_code=422, detail="Public holidays cannot fall on Saturday or Sunday.")
    h = Holiday(date=dt, name=payload.get("name") or "Holiday", country=(payload.get("country") or None))
    db.add(h); await db.commit(); return {"ok": True, "id": h.id}

@router.put("/holidays/{hid}")
async def update_holiday(hid: int, payload: dict, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    await db.execute(update(Holiday).where(Holiday.id==hid).values(name=payload.get("name"), country=payload.get("country")))
    await db.commit(); return {"ok": True}

@router.delete("/holidays/{hid}")
async def delete_holiday(hid: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    ensure_admin(u)
    h = await db.get(Holiday, hid)
    if not h: raise HTTPException(status_code=404, detail="Not found")
    await db.delete(h); await db.commit(); return {"ok": True}


async def ensure_admin_or_pm(db: AsyncSession, u: User, project_id: int):
    if u.role_id == 1:
        return
    res = await db.execute(select(ContractAccess).where(ContractAccess.contract_id==project_id, ContractAccess.user_id==u.id, ContractAccess.role=='pm'))
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Managers only")

@router.put("/projects/{project_id}/access/{user_id}")
async def update_project_access(project_id: int, user_id: int, payload: dict, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    await ensure_admin_or_pm(db, u, project_id)
    role = (payload or {}).get("role")
    if role not in ("member","viewer","pm"):
        raise HTTPException(status_code=422, detail="Invalid role")
    await db.execute(update(ContractAccess).where(ContractAccess.contract_id==project_id, ContractAccess.user_id==user_id).values(role=role))
    await db.commit(); return {"ok": True}
