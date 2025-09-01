
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, text, insert, func, update
from pydantic import BaseModel, Field
from datetime import date, timedelta, datetime
from ..security import get_db, get_current_user
from ..models.models import User, LeaveRequest, Timesheet, Holiday, TimesheetStaff
from ..schemas import TimesheetCreate
from typing import List


ANNUAL_QUOTA = 18.0
MONTHLY_ACCRUAL = 1.5  # days per month

def _daterange(d1: date, d2: date):
    step = 1 if d2 >= d1 else -1
    cur = d1
    while True:
        yield cur
        if cur == d2: break
        cur = cur + timedelta(days=step)

async def _load_holidays(db: AsyncSession) -> set[date]:
    res = await db.execute(select(Holiday.date))
    return set([r[0] for r in res.all()])

def _is_weekend(d: date) -> bool:
    return d.weekday() in (5,6)

async def _working_days(start: date, end: date, db: AsyncSession) -> list[date]:
    hols = await _load_holidays(db)
    days = []
    for d in _daterange(start, end):
        if d in hols or _is_weekend(d): continue
        days.append(d)
    return days

async def _leave_days_total(start: date, end: date, db: AsyncSession, selected: list[date] | None, half_days: list[date] | None) -> tuple[list[date], float]:
    wdays = await _working_days(start, end, db)
    sset = set(selected) if selected else set(wdays)
    hset = set(half_days or [])
    chosen = [d for d in wdays if d in sset]
    total = 0.0
    for d in chosen:
        total += 0.5 if d in hset else 1.0
    # snap to 0.5 increments
    total = round(total*2)/2.0
    return chosen, total

async def _annual_balance(u: User, year: int, db: AsyncSession) -> dict:
    # months accrued in the given year considering join date
    today = date.today()
    # Determine months elapsed in the year as of today
    if today.year > year:
        months_elapsed = 12
    elif today.year == year:
        months_elapsed = today.month
    else:
        months_elapsed = 0
    # Adjust for join date
    if u.created_at and u.created_at.year == year:
        months_elapsed = max(0, months_elapsed - (u.created_at.month - 1))
    elif u.created_at and u.created_at.year > year:
        months_elapsed = 0
    accrued = min(ANNUAL_QUOTA, months_elapsed * MONTHLY_ACCRUAL)

    # Sum taken & pending for this year (annual/sick/emergency count, unpaid ignored)
    types = ('annual','sick','emergency')
    res = await db.execute(
        select(func.coalesce(func.sum(LeaveRequest.days), 0.0))
        .where(LeaveRequest.user_id==u.id)
        .where(func.extract('year', LeaveRequest.start_date)==year)
        .where(LeaveRequest.leave_type.in_(types))
    )
    taken_all = float(res.scalar() or 0.0)

    # Optionally separate approved vs pending
    res2 = await db.execute(
        select(func.coalesce(func.sum(LeaveRequest.days), 0.0))
        .where(LeaveRequest.user_id==u.id)
        .where(func.extract('year', LeaveRequest.start_date)==year)
        .where(LeaveRequest.leave_type.in_(types))
        .where(LeaveRequest.status=='approved')
    )
    taken_approved = float(res2.scalar() or 0.0)

    res3 = await db.execute(
        select(func.coalesce(func.sum(LeaveRequest.days), 0.0))
        .where(LeaveRequest.user_id==u.id)
        .where(func.extract('year', LeaveRequest.start_date)==year)
        .where(LeaveRequest.leave_type.in_(types))
        .where(LeaveRequest.status=='pending')
    )
    pending = float(res3.scalar() or 0.0)

    available = max(0.0, accrued - (approved := taken_approved) - pending)
    return dict(year=year, quota=ANNUAL_QUOTA, monthly_accrual=MONTHLY_ACCRUAL, accrued=round(accrued,2), approved=round(approved,2), pending=round(pending,2), available=round(available,2), as_of=str(today))
router = APIRouter(prefix="/api/hr", tags=["hr"])

# ----- Schemas (local to keep things simple) -----
class LeaveCreate(BaseModel):
    start_date: date
    end_date: date
    leave_type: str = Field(..., max_length=50)  # annual, sick, emergency, unpaid
    reason: str | None = None
    selected_dates: list[date] | None = None   # optional: subset of working days between start/end
    half_days: list[date] | None = None        # optional: dates counted as 0.5 instead of 1.0
    require_manager_approval: bool = False
    days: float | None = None  # optional pre-computed total from client
    
# ----- Leave Requests -----

@router.get("/my/leave-balance")
async def my_leave_balance(year: int | None = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    year = year or date.today().year
    try:
        # Ensure 'days' column exists for aggregation
        await db.execute(text("ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS days FLOAT"))
    except Exception:
        pass
    return await _annual_balance(u, year, db)

@router.get("/my/leaves")
async def my_leaves(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    try:
        await db.execute(text("ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS days FLOAT"))
    except Exception:
        pass
    res = await db.execute(select(LeaveRequest).where(LeaveRequest.user_id==u.id).order_by(LeaveRequest.id.desc()))
    out = [dict(id=r.id, start_date=str(r.start_date), end_date=str(r.end_date), leave_type=r.leave_type, reason=r.reason, status=r.status, days=getattr(r,'days', None)) for r in res.scalars().all()]
    return out

@router.post("/my/leaves")
async def create_leave(payload: LeaveCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    # Cross-year not supported in this version
    if payload.end_date < payload.start_date:
        raise HTTPException(status_code=422, detail="End date must be after start date")
    if payload.start_date.year != payload.end_date.year:
        raise HTTPException(status_code=422, detail="Leave must be within a single calendar year")

    # Past-dated rules
    if payload.start_date < date.today() and payload.leave_type not in ("sick","emergency"):
        raise HTTPException(status_code=422, detail="Back-dated leave only allowed for sick or emergency types.")
    if payload.start_date < date.today() and (not payload.reason or not payload.reason.strip()):
        raise HTTPException(status_code=422, detail="Please provide a reason for back-dated leave.")

    # Build chosen days and total
    try:
        await db.execute(text("ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS days FLOAT"))
    except Exception:
        pass

    chosen, total = await _leave_days_total(payload.start_date, payload.end_date, db, payload.selected_dates, payload.half_days)
    if payload.days is not None:
        total = float(payload.days)
    if total < 0.5:
        raise HTTPException(status_code=422, detail="Minimum leave is 0.5 day.")
    if abs(total*2 - round(total*2)) > 1e-6:
        raise HTTPException(status_code=422, detail="Leave days must be in 0.5 increments.")

    # Balance check for annual types (annual/sick/emergency count toward balance, unpaid ignored)
    if payload.leave_type in ("annual","sick","emergency"):
        bal = await _annual_balance(u, payload.start_date.year, db)
        if total > bal["available"] + 1e-6 and not payload.require_manager_approval:
            raise HTTPException(status_code=422, detail=f"Insufficient balance. Available: {bal['available']} days.")
    # Insert request
    lr = LeaveRequest(user_id=u.id, start_date=payload.start_date, end_date=payload.end_date, leave_type=payload.leave_type, reason=payload.reason or "", status="pending")
    # Set the computed days value
    try:
        await db.execute(insert(LeaveRequest.__table__).values(user_id=u.id, start_date=payload.start_date, end_date=payload.end_date, leave_type=payload.leave_type, reason=(payload.reason or ""), status="pending", days=total))
        await db.commit()
        # Return id of last insert - reselect
        res = await db.execute(select(LeaveRequest).where(LeaveRequest.user_id==u.id).order_by(LeaveRequest.id.desc()).limit(1))
        lr = res.scalars().first()
        return {"ok": True, "id": lr.id if lr else None}
    except Exception:
        # If insert with 'days' fails due to DB lacking column type nuance, fallback to ORM add then update
        db.add(lr); await db.commit(); return {"ok": True, "id": lr.id}

# ----- Timesheets -----
@router.get("/my/timesheets")
async def my_timesheets(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(Timesheet).where(Timesheet.user_id==u.id).order_by(Timesheet.work_date.desc(), Timesheet.id.desc()))
    rows = [dict(id=r.id, work_date=str(r.work_date), hours_worked=float(r.hours_worked), contract_id=r.contract_id, description=r.description, status=r.status) for r in res.scalars().all()]
    return rows


@router.post("/my/timesheets")
async def create_timesheet(payload: TimesheetCreate, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    # Sunday block
    if payload.work_date.weekday() in (5,6):
        raise HTTPException(status_code=422, detail="Timesheets are not allowed on Saturday or Sunday.")
    # Holiday block
    h = await db.execute(select(Holiday).where(Holiday.date==payload.work_date))
    if h.scalar_one_or_none():
        raise HTTPException(status_code=422, detail="Timesheets are not allowed on public holidays.")
    # Per-day limit <= 10
    q = await db.execute(select(func.coalesce(func.sum(Timesheet.hours_worked), 0)).where(Timesheet.user_id==u.id, Timesheet.work_date==payload.work_date))
    used = float(q.scalar() or 0)
    if used + float(payload.hours_worked) > 10.0 + 1e-6:
        raise HTTPException(status_code=422, detail=f"Daily limit exceeded: you already logged {used}h for this date.")
    # Range enforcement handled by Pydantic, also snap to 0.5 increments
    if (payload.hours_worked*2) % 1 != 0:
        raise HTTPException(status_code=422, detail="Hours must be in 0.5 increments.")
    ts = Timesheet(user_id=u.id, work_date=payload.work_date, hours_worked=float(payload.hours_worked), contract_id=payload.contract_id, description=payload.description or "", status="pending")
    db.add(ts); await db.commit(); return {"ok": True, "id": ts.id}



@router.get("/team/timesheets")
async def team_timesheets(status: str = "pending", db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    # List timesheets from users who report to me
    subq = select(User.id).where(User.manager_id==u.id)
    res = await db.execute(select(Timesheet, User).join(User, User.id==Timesheet.user_id).where(Timesheet.user_id.in_(subq), Timesheet.status==status).order_by(Timesheet.work_date.desc(), Timesheet.id.desc()))
    out = []
    for ts, usr in res.all():
        out.append(dict(id=ts.id, user=usr.username, work_date=str(ts.work_date), hours_worked=float(ts.hours_worked), contract_id=ts.contract_id, description=ts.description, status=ts.status))
    return out

@router.put("/timesheets/{ts_id}/approve")
async def approve_timesheet(ts_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    # only manager of the user can approve
    res = await db.execute(select(Timesheet, User).join(User, User.id==Timesheet.user_id).where(Timesheet.id==ts_id))
    row = res.first()
    if not row: raise HTTPException(status_code=404, detail="Not found")
    ts, usr = row
    if usr.manager_id != u.id and u.role_id != 1:
        raise HTTPException(status_code=403, detail="Not allowed")
    await db.execute(update(Timesheet).where(Timesheet.id==ts_id).values(status="approved", approved_by=u.id, approved_at=datetime.utcnow()))
    await db.commit(); return {"ok": True}

@router.put("/timesheets/{ts_id}/reject")
async def reject_timesheet(ts_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(Timesheet, User).join(User, User.id==Timesheet.user_id).where(Timesheet.id==ts_id))
    row = res.first()
    if not row: raise HTTPException(status_code=404, detail="Not found")
    ts, usr = row
    if usr.manager_id != u.id and u.role_id != 1:
        raise HTTPException(status_code=403, detail="Not allowed")
    await db.execute(update(Timesheet).where(Timesheet.id==ts_id).values(status="rejected", approved_by=u.id, approved_at=datetime.utcnow()))
    await db.commit(); return {"ok": True}


@router.get("/my/timesheets/week")
async def my_ts_week(start: date, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    end = start + timedelta(days=6)
    res = await db.execute(select(Timesheet).where(Timesheet.user_id==u.id, Timesheet.work_date>=start, Timesheet.work_date<=end).order_by(Timesheet.work_date.asc()))
    return [dict(id=r.id, work_date=str(r.work_date), hours_worked=float(r.hours_worked), contract_id=r.contract_id, description=r.description, status=r.status, submitted=getattr(r,'submitted',0)) for r in res.scalars().all()]


class WeekBulkItem(BaseModel):
    work_date: date
    hours_worked: float
    contract_id: int | None = None
    description: str | None = None

@router.post("/my/timesheets/bulk")
async def my_ts_bulk(items: list[WeekBulkItem], submitted: bool = False, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    try:
        await db.execute(text("ALTER TABLE timesheets ADD COLUMN IF NOT EXISTS submitted TINYINT NOT NULL DEFAULT 0"))
    except Exception:
        pass
    # Holidays
    holidays=set()
    try:
        from ..models.models import Holiday
        hs=await db.execute(select(Holiday.date)); holidays={d for (d,) in hs.all()}
    except Exception: pass

    from collections import defaultdict
    add_map=defaultdict(float)
    for it in items:
        if it.work_date.weekday() in (5,6): raise HTTPException(status_code=422, detail="Timesheets are not allowed on Saturday or Sunday.")
        if it.work_date in holidays: raise HTTPException(status_code=422, detail="Timesheets are not allowed on public holidays.")
        if it.hours_worked<0.5 or it.hours_worked>10 or (it.hours_worked*2)%1!=0: raise HTTPException(status_code=422, detail="Hours must be in 0.5 steps between 0.5 and 10.")
        add_map[it.work_date]+=float(it.hours_worked)

    for d,add in add_map.items():
        q=await db.execute(select(func.coalesce(func.sum(Timesheet.hours_worked),0)).where(Timesheet.user_id==u.id, Timesheet.work_date==d))
        used=float(q.scalar() or 0.0)
        if used+add>10.0+1e-6: raise HTTPException(status_code=422, detail=f"Daily limit exceeded for {d}: already {used}h")

    for it in items:
        db.add(Timesheet(user_id=u.id, work_date=it.work_date, hours_worked=float(it.hours_worked), contract_id=it.contract_id, description=it.description or "", status="pending", submitted=1 if submitted else 0))
    await db.commit(); return {"ok":True}


@router.put("/my/timesheets/submit-week")
async def my_ts_submit_week(start: date, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    try:
        await db.execute(text("ALTER TABLE timesheets ADD COLUMN IF NOT EXISTS submitted TINYINT NOT NULL DEFAULT 0"))
    except Exception: pass
    end = start + timedelta(days=6)
    await db.execute(update(Timesheet).where(Timesheet.user_id==u.id, Timesheet.work_date>=start, Timesheet.work_date<=end).values(submitted=1))
    await db.commit(); return {"ok":True}

# -------Leave Requeste Staff ----------------


router = APIRouter(prefix="/leave_requests", tags=["Leave Requests"])

# ---------- CREATE ----------
@router.post("/", response_model=dict)
async def create_leave_request(
    user_id: int,
    start_date: date,
    end_date: date,
    leave_type: str,
    reason: str | None = None,
    approver_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    leave = LeaveRequest(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        leave_type=leave_type,
        reason=reason,
        approver_id=approver_id,
        days=(end_date - start_date).days + 1  # calculate days
    )
    db.add(leave)
    await db.commit()
    await db.refresh(leave)
    return {"message": "Leave request created", "leave_request": leave.id}


# ---------- READ ALL ----------
@router.get("/", response_model=List[dict])
async def get_leave_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LeaveRequest))
    leaves = result.scalars().all()
    return leaves


# ---------- READ SINGLE ----------
@router.get("/{leave_id}", response_model=dict)
async def get_leave_request(leave_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave


# ---------- UPDATE ----------
@router.put("/{leave_id}", response_model=dict)
async def update_leave_request(
    leave_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    leave_type: str | None = None,
    reason: str | None = None,
    status: str | None = None,
    approver_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    if start_date:
        leave.start_date = start_date
    if end_date:
        leave.end_date = end_date
    if start_date and end_date:
        leave.days = (end_date - start_date).days + 1
    if leave_type:
        leave.leave_type = leave_type
    if reason:
        leave.reason = reason
    if status:
        leave.status = status
    if approver_id is not None:
        leave.approver_id = approver_id

    db.add(leave)
    await db.commit()
    await db.refresh(leave)
    return {"message": "Leave request updated", "leave_request": leave.id}


# ---------- DELETE ----------
@router.delete("/{leave_id}", response_model=dict)
async def delete_leave_request(leave_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    await db.delete(leave)
    await db.commit()
    return {"message": "Leave request deleted"}


