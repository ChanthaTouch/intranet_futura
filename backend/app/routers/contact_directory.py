from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from typing import List

from app.schemas import ContactDirectoryCreate, ContactDirectoryResponse
from app.models import ContactDirectory

router = APIRouter(prefix="/contact-directory", tags=["contact-directory"])

# Create a contact directory entry
@router.post("/", response_model=ContactDirectoryResponse)
async def create_contact_directory(contact: ContactDirectoryCreate, db: AsyncSession = Depends(get_db)):
    db_contact = ContactDirectory(
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        position=contact.position,
        department=contact.department,
        office=contact.office
    )
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

# Get all contact directory entries
@router.get("/", response_model=List[ContactDirectoryResponse])
async def get_contact_directory(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContactDirectory))
    return result.scalars().all()
# Get contact directory entry by ID
@router.get("/{contact_id}", response_model=ContactDirectoryResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContactDirectory).where(ContactDirectory.id == contact_id))
    db_contact = result.scalars().first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
# Update contact directory entry

