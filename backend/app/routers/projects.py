from fastapi.responses import FileResponse
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..security import get_db, get_current_user
from ..config import config
from ..models.models import Contract, ContractAccess, ProjectMessage, ProjectFile, User

router = APIRouter(prefix="/api/projects", tags=["projects"])

async def _can_access(db: AsyncSession, user: User, project_id: int) -> bool:
    if user.role_id == 1:
        return True
    res = await db.execute(select(ContractAccess).where(ContractAccess.contract_id==project_id, ContractAccess.user_id==user.id))
    return bool(res.scalar_one_or_none())

@router.get("/active", operation_id="list_active_projects")
async def list_active(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if u.role_id == 1:
        res = await db.execute(select(Contract).where(Contract.status=='active').order_by(Contract.code.asc()))
    else:
        res = await db.execute(select(Contract).join(ContractAccess, ContractAccess.contract_id==Contract.id).where(Contract.status=='active', ContractAccess.user_id==u.id).order_by(Contract.code.asc()))
    rows = res.scalars().all()
    out = []
    # (Rest of the code remains the same)
    for c in rows:
        role = 'admin' if u.role_id==1 else None
        if role is None:
            r = await db.execute(select(ContractAccess).where(ContractAccess.contract_id == c.id, ContractAccess.user_id == u.id))
            r = r.scalar_one_or_none()
            if r:
                role = 'client' if r.can_read else 'none'
        out.append({"id": c.id, "code": c.code, "name": c.name, "role": role})
    return out

@router.get("/{project_id}", operation_id="get_project")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    res = await db.execute(select(Contract).where(Contract.id == project_id))
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Not found")
    return project

@router.get("/{project_id}/messages", operation_id="list_project_messages")
async def list_messages(project_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    res = await db.execute(select(ProjectMessage).where(ProjectMessage.contract_id == project_id).order_by(ProjectMessage.created_at.asc()))
    return res.scalars().all()

@router.post("/{project_id}/messages", operation_id="post_project_message")
async def post_message(project_id: int, message: str = Form(...), db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    pm = ProjectMessage(contract_id=project_id, user_id=u.id, message=message)
    db.add(pm)
    await db.commit()
    await db.refresh(pm)
    return pm

@router.put("/files/{file_id}", operation_id="update_file_project")
async def update_file(file_id: int, folder: int | None = Form(None), description: str | None = Form(None), db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(ProjectFile, ContractAccess).outerjoin(ContractAccess, (ContractAccess.contract_id==ProjectFile.contract_id) & (ContractAccess.user_id==u.id)).where(ProjectFile.id==file_id))
    row = res.first()
    if not row: raise HTTPException(status_code=404, detail='Not found')
    if not (u.role_id == 1 or row[1] is not None):
        raise HTTPException(status_code=403, detail='Not allowed')
    pf = row[0]
    if folder is not None: pf.folder = folder
    if description is not None: pf.description = description
    await db.commit()
    return {"ok": True}

@router.delete("/files/{file_id}", operation_id="delete_file_project")
async def delete_file(file_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(ProjectFile, ContractAccess).outerjoin(ContractAccess, (ContractAccess.contract_id==ProjectFile.contract_id) & (ContractAccess.user_id==u.id)).where(ProjectFile.id==file_id))
    row = res.first()
    if not row: raise HTTPException(status_code=404, detail='Not found')
    pf = row[0]
    # (Rest of the code remains the same)
    if not (u.role_id == 1 or row[1] is not None):
        raise HTTPException(status_code=403, detail='Not allowed')
    await db.delete(pf)
    await db.commit()
    return {"ok": True}
