import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models.models import Ticket  # Adjust if path is different
from app.schemas import TicketResponse  # Assuming you have a schema

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

# ✅ Get all tickets
@router.get("/", response_model=list[TicketResponse])
async def get_tickets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ticket))
    tickets = result.scalars().all()
    return tickets


# ✅ Create ticket
@router.post("/", response_model=TicketResponse)
async def create_ticket(
    title: str = Form(...),
    description: str = Form(...),
    quantity: int = Form(...),
    deadline: str = Form(...),
    priority: str = Form("normal"),
    boq: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    filename = None
    if boq:
        filename = f"{int.from_bytes(os.urandom(4), 'big')}_{boq.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(boq.file, buffer)

    ticket = Ticket(
        title=title,
        description=description,
        quantity=quantity,
        deadline=deadline,
        priority=priority,
        boq=filename,
    )

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    return ticket


# ✅ Get ticket by ID
@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


# ✅ Delete ticket
@router.delete("/{ticket_id}")
async def delete_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await db.delete(ticket)
    await db.commit()
    return {"message": "Ticket deleted successfully"}
