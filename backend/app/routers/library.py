from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..security import get_db, get_current_user
from ..models.models import LibraryItem, LibraryCategory, User
from ..utils import save_upload

router = APIRouter(prefix="/api/library", tags=["library"])

@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    res = await db.execute(select(LibraryCategory))
    return [ {"id": c.id, "name": c.name} for c in res.scalars().all() ]

@router.post("/upload")
async def upload_library_file(category_id: int | None = None, file: UploadFile = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    stored_name, path, size, mime = await save_upload(file, subdir="library")
    item = LibraryItem(category_id=category_id, title=file.filename, path=path, uploaded_by=u.id)
    db.add(item); await db.commit()
    return {"ok": True, "id": item.id}
