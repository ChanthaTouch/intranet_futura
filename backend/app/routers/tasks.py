from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from ..db import SessionLocal
from ..models.models import Task, User
from ..security import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

async def get_db():
    async with SessionLocal() as session:
        yield session

class TaskIn(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "todo"
    color: Optional[str] = None
    order_index: Optional[int] = 0
    deadline: Optional[date] = None

def task_to_dict(t: Task):
    return {
        "id": t.id,
        "user_id": t.user_id,
        "title": t.title,
        "description": t.description,
        "status": t.status or "todo",
        "order_index": t.order_index or 0,
        "color": t.color,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }

@router.get("/my", operation_id="my_tasks")
async def my_tasks(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(Task).where(Task.user_id == u.id).order_by(Task.status, Task.order_index, Task.id))
    return [task_to_dict(t) for t in res.scalars().all()]

@router.post("", operation_id="create_task")
async def create_task(body: TaskIn, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    t = Task(user_id=u.id, **body.dict())
    db.add(t); await db.commit(); await db.refresh(t)
    return task_to_dict(t)

@router.put("/{task_id}", operation_id="update_task")
async def update_task(task_id: int, body: TaskIn, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(Task).where(Task.id==task_id, Task.user_id==u.id))
    t = res.scalar_one_or_none()
    if not t: raise HTTPException(status_code=404, detail="Not found")
    data = body.dict()
    for k,v in data.items():
        setattr(t, k, v)
    t.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(t)
    return task_to_dict(t)

@router.delete("/{task_id}", operation_id="delete_task")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == u.id))
    t = res.scalar_one_or_none()
    if not t: raise HTTPException(status_code=404, detail="Not found")
    await db.delete(t)
    await db.commit()
    return {"ok": True}
