from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..security import get_db
from ..models.models import TimesheetStaff
from ..schemas import TimesheetCreate, TimesheetUpdate, TimesheetOut
from typing import List

router = APIRouter()

# CREATE
@router.post("/timesheets", response_model=TimesheetOut)
async def create_timesheet(payload: TimesheetCreate, db: AsyncSession = Depends(get_db)):
    ts = TimesheetStaff(**payload.dict())
    db.add(ts)
    await db.commit()
    await db.refresh(ts)
    return ts


# READ all
@router.get("/timesheets", response_model=List[TimesheetOut])
async def get_timesheets(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(TimesheetStaff))
    return res.scalars().all()


# READ one
@router.get("/timesheets/{ts_id}", response_model=TimesheetOut)
async def get_timesheet(ts_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(TimesheetStaff).where(TimesheetStaff.id == ts_id))
    ts = res.scalar_one_or_none()
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return ts


# UPDATE
@router.put("/timesheets/{ts_id}", response_model=TimesheetOut)
async def update_timesheet(ts_id: int, payload: TimesheetUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(TimesheetStaff).where(TimesheetStaff.id == ts_id))
    ts = res.scalar_one_or_none()
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")

    for k, v in payload.dict(exclude_unset=True).items():
        setattr(ts, k, v)

    db.add(ts)
    await db.commit()
    await db.refresh(ts)
    return ts


# DELETE
@router.delete("/timesheets/{ts_id}")
async def delete_timesheet(ts_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(TimesheetStaff).where(TimesheetStaff.id == ts_id))
    ts = res.scalar_one_or_none()
    if not ts:
        raise HTTPException(status_code=404, detail="Timesheet not found")

    await db.delete(ts)
    await db.commit()
    return {"ok": True, "message": f"Timesheet {ts_id} deleted"}
