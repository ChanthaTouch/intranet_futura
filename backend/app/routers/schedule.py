from __future__ import annotations

from datetime import date
from typing import Optional, List, Set

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func, case, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..security import get_current_user, get_db
from ..models.models import User
from ..models.models_schedule import ProjectScheduleItem

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

# ---------- Schemas ----------
class ItemOut(BaseModel):
    id: int
    contract_id: int
    parent_id: Optional[int] = None
    title: str
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    progress: int = 0
    sort_index: int = 0

    class Config:
        from_attributes = True


class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    parent_id: Optional[int] = None


class ItemPatch(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    progress: Optional[int] = None
    parent_id: Optional[int] = None
    sort_index: Optional[int] = None


class ReorderPayload(BaseModel):
    contract_id: int
    parent_id: Optional[int] = None
    item_ids_in_order: List[int]


# ---------- Helpers ----------

async def _heal_cycles_for_contract(db: AsyncSession, contract_id: int) -> int:
    """     Auto-heal bad parent chains:
        - Break self-parenting `parent_id = id`
        - Break cycles (A->B->C->A) by setting the starting node's parent to NULL
        - Break dangling parents (pointing to non-existent id)
        Returns number of items modified.
    """
    # Load all ids and parents for this contract
    res = await db.execute(select(ProjectScheduleItem.id, ProjectScheduleItem.parent_id).where(ProjectScheduleItem.contract_id == contract_id))
    rows = res.all()
    id_to_parent = {int(r[0]): (None if r[1] is None else int(r[1])) for r in rows}
    modified = 0
    to_nullify = {} # item_id -> old_parent
    def mark_null(i):
        nonlocal modified
        if i in id_to_parent and id_to_parent[i] is not None:
            to_nullify[i] = id_to_parent[i]
            id_to_parent[i] = None
            modified += 1
    # Self-parenting
    for i, p in list(id_to_parent.items()):
        if p == i:
            mark_null(i)
    # Dangling parents
    for i, p in list(id_to_parent.items()):
        if p is not None and p not in id_to_parent:
            mark_null(i)
    # Cycles
    for i in list(id_to_parent.keys()):
        seen = set()
        current = i
        while current is not None:
            if current in seen:
                mark_null(i)
                break
            seen.add(current)
            current = id_to_parent.get(current)
    if modified > 0:
        for i, p in to_nullify.items():
            db.add(ProjectScheduleItem(id=i, parent_id=None, __is_modified__=True))
    await db.commit()
    return modified

async def _recalc_parent_chain(db: AsyncSession, parent_id: Optional[int]):
    """Walk up parent chain and update progress based on children."""
    current_id = parent_id
    while current_id is not None:
        children_res = await db.execute(select(func.sum(ProjectScheduleItem.progress)).where(ProjectScheduleItem.parent_id == current_id))
        total_progress = children_res.scalar_one_or_none() or 0
        item = await db.get(ProjectScheduleItem, current_id)
        if item:
            item.progress = total_progress
            await db.flush()
        current_id = item.parent_id if item else None

async def _collect_descendants(db: AsyncSession, item_id: int) -> Set[int]:
    """Recursively collect all descendant item IDs."""
    ids = {item_id}
    q = [item_id]
    while q:
        parent_id = q.pop(0)
        res = await db.execute(select(ProjectScheduleItem.id).where(ProjectScheduleItem.parent_id == parent_id))
        children = res.scalars().all()
        for child_id in children:
            if child_id not in ids:
                ids.add(child_id)
                q.append(child_id)
    return ids

async def _would_create_cycle(db: AsyncSession, item_id: int, new_parent_id: Optional[int]) -> bool:
    """Check if setting new_parent_id would create a cycle."""
    if new_parent_id is None:
        return False
    # Walk up the parent chain from the new parent. If we encounter the item itself, it's a cycle.
    current_id = new_parent_id
    while current_id is not None:
        if current_id == item_id:
            return True
        item = await db.get(ProjectScheduleItem, current_id)
        if not item:
            return False # Parent not found, not a cycle.
        current_id = item.parent_id
    return False

@router.get("/projects/{contract_id}/items", operation_id="list_schedule_items")
async def list_items(contract_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ProjectScheduleItem).where(ProjectScheduleItem.contract_id == contract_id).order_by(ProjectScheduleItem.sort_index))
    return res.scalars().all()

@router.post("/projects/{contract_id}/items", operation_id="create_schedule_item")
async def create_item(contract_id: int, payload: ItemCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    item = ProjectScheduleItem(contract_id=contract_id, **payload.dict())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.patch("/items/{item_id}", operation_id="update_schedule_item")
async def update_item(item_id: int, payload: ItemPatch, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    item = await db.get(ProjectScheduleItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    await _recalc_parent_chain(db, item.parent_id)
    return item

@router.post("/items/reorder", operation_id="reorder_schedule_items")
async def reorder_items(payload: ReorderPayload, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    step = 10
    for idx, item_id in enumerate(payload.item_ids_in_order):
        item = await db.get(ProjectScheduleItem, item_id)
        if not item or item.contract_id != payload.contract_id:
            continue
        # Validate cycle
        if await _would_create_cycle(db, item.id, payload.parent_id):
            continue
        item.parent_id = payload.parent_id
        item.sort_index = (idx + 1) * step
        await db.flush()
    await db.commit()
    await _recalc_parent_chain(db, payload.parent_id)
    return {"ok": True}

@router.delete("/items/{item_id}", operation_id="delete_schedule_item")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    item = await db.get(ProjectScheduleItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    parent = item.parent_id
    ids = await _collect_descendants(db, item_id)
    # delete children first to satisfy any FK constraints
    for iid in sorted(ids, reverse=True):
        obj = await db.get(ProjectScheduleItem, iid)
        if obj:
            await db.delete(obj)
    await db.commit()
    await _recalc_parent_chain(db, parent)
    return {"ok": True}

@router.post("/maintenance/{contract_id}/heal", operation_id="maintenance_heal_schedule")
async def maintenance_heal(contract_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    """A helper endpoint for fixing bad parent chains/cycles."""
    modified_count = await _heal_cycles_for_contract(db, contract_id)
    return {"modified_count": modified_count}
