
import os, uuid, shutil
from datetime import datetime
from typing import Optional, List, Tuple

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from sqlalchemy import select, func, update, text

from ..security import get_db, get_current_user
from ..config import config
from ..models.models import ProjectFile, ContractAccess, User
from ..models.models_schedule import ProjectFolder
from ..models.models_files import ProjectFileVersion, ProjectFolderPermission

router = APIRouter(prefix="/api/files", tags=["files"])

# --------- helpers ---------

async def _permissions_enabled(db: AsyncSession, contract_id: int) -> bool:
    res = await db.execute(select(func.count(ProjectFolderPermission.id)).where(ProjectFolderPermission.contract_id == contract_id))
    return (res.scalar_one() or 0) > 0

async def _folder_id_from_path(db: AsyncSession, contract_id: int, path: str | None) -> int | None:
    if not path:
        return None
    res = await db.execute(select(ProjectFolder.id).where(ProjectFolder.contract_id == contract_id, ProjectFolder.path == path))
    row = res.first()
    return row[0] if row else None

async def _effective_perm(db: AsyncSession, contract_id: int, user: User, folder_id: int | None) -> tuple[bool, bool]:
    """
        Return (can_read, can_write) for user on folder (inherit up the tree). Admin bypasses.
        If the project has no permission rows, default to (True, True) for project members.
    """
    # Admin role bypass
    if getattr(user, "role_id", None) == 1:
        return True, True
    # If no permissions configured, allow
    if not await _permissions_enabled(db, contract_id):
        return True, True
    # Build ancestor chain including None/root
    chain = []
    current = folder_id
    visited = set()
    while current is not None and current not in visited:
        chain.append(current)
        visited.add(current)
        par = await db.get(ProjectFolder, current)
        if not par:
            break
        current = par.parent_id
    chain.append(None)  # root fallback
    # Walk downwards from most specific to least
    for fid in chain:
        q = select(ProjectFolderPermission).where(ProjectFolderPermission.contract_id == contract_id, ProjectFolderPermission.user_id == user.id)
        if fid is None:
            q = q.where(ProjectFolderPermission.folder_id.is_(None))
        else:
            q = q.where(ProjectFolderPermission.folder_id == fid)
        res = await db.execute(q)
        p = res.scalar_one_or_none()
        if p:
            return (bool(p.can_read), bool(p.can_write))
    # no explicit entry => deny
    return False, False

def _proj_dir(contract_id: int) -> str:
    base = getattr(config.storage, "files_dir", "./var/files")
    p = os.path.join(base, str(contract_id))
    os.makedirs(p, exist_ok=True)
    return p

async def _can_access(db: AsyncSession, user: User, project_id: int) -> bool:
    if getattr(user, "role_id", None) == 1:
        return True
    res = await db.execute(select(ContractAccess).where(ContractAccess.contract_id == project_id, ContractAccess.user_id == user.id))
    return res.scalar_one_or_none() is not None

async def _folder_path(db: AsyncSession, folder_id: Optional[int]) -> Optional[str]:
    if not folder_id:
        return None
    f = await db.get(ProjectFolder, folder_id)
    if not f:
        return None
    return f.path

async def _ensure_unique_folder(db: AsyncSession, contract_id: int, parent_id: Optional[int], name: str) -> Tuple[str, Optional[str]]:
    """Return (path, err)."""
    base_path = ""
    if parent_id:
        p = await db.get(ProjectFolder, parent_id)
        if not p or p.contract_id != contract_id:
            return "", "Parent not found"
        base_path = p.path
    path = name if not base_path else f"{base_path}/{name}"
    # check duplicate
    res = await db.execute(select(ProjectFolder).where(ProjectFolder.contract_id == contract_id, ProjectFolder.path == path))
    if res.scalar_one_or_none():
        return "", "Folder already exists"
    return path, None

# --------- Folders ----------
@router.get("/projects/{project_id}/folders")
async def list_folders(project_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    res = await db.execute(select(ProjectFolder).where(ProjectFolder.contract_id == project_id).order_by(ProjectFolder.path.asc()))
    rows = res.scalars().all()
    out = []
    for f in rows:
        can_read, _ = await _effective_perm(db, project_id, u, f.id)
        if can_read:
            out.append({"id": f.id, "name": f.name, "path": f.path, "parent_id": f.parent_id})
    return [{"id": f.id, "name": f.name, "path": f.path, "parent_id": f.parent_id} for f in rows]

@router.post("/projects/{project_id}/folders")
async def create_folder(project_id: int,
                        name: str = Form(...),
                        parent_id: Optional[int] = Form(None),
                        db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    name = name.strip().strip("/")
    if not name:
        raise HTTPException(400, "Invalid name")
    path, err = await _ensure_unique_folder(db, project_id, parent_id, name)
    if err:
        raise HTTPException(400, err)
    folder = ProjectFolder(contract_id=project_id, parent_id=parent_id, name=name, path=path)
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return {"id": folder.id, "name": folder.name, "path": folder.path, "parent_id": folder.parent_id}

@router.patch("/folders/{folder_id}")
async def rename_or_move_folder(folder_id: int,
                                name: Optional[str] = Form(None),
                                parent_id: Optional[int] = Form(None),
                                db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    folder = await db.get(ProjectFolder, folder_id)
    if not folder:
        raise HTTPException(404, "Folder not found")
    if not await _can_access(db, u, folder.contract_id):
        raise HTTPException(403, "Not allowed")
    # compute new path
    new_name = folder.name if name is None else name.strip().strip("/")
    new_parent = folder.parent_id if parent_id is None else parent_id
    base_path = ""
    if new_parent:
        p = await db.get(ProjectFolder, new_parent)
        if not p or p.contract_id != folder.contract_id:
            raise HTTPException(400, "Parent not found")
        # prevent making a folder its own descendant
        if p.path.startswith(folder.path + "/") or p.id == folder.id:
            raise HTTPException(400, "Invalid parent (cycle)")
        base_path = p.path
    new_path = new_name if not base_path else f"{base_path}/{new_name}"
    # update folder and its descendants' path
    # permission checks
    can_read, can_write_here = await _effective_perm(db, folder.contract_id, u, folder.id)
    if not can_write_here: raise HTTPException(403, "No write access on this folder")
    old_path = folder.path
    folder.name = new_name
    folder.parent_id = new_parent
    folder.path = new_path
    await db.flush()
    # rename descendants
    res = await db.execute(select(ProjectFolder).where(ProjectFolder.contract_id == folder.contract_id, ProjectFolder.path.like(old_path + "/%")))
    for child in res.scalars().all():
        child.path = child.path.replace(old_path + "/", new_path + "/", 1)
    # move files under this subtree by matching path prefix in ProjectFile.folder (string path)
    await db.execute(text("UPDATE project_files SET folder = REPLACE(folder, :oldp, :newp) WHERE folder LIKE :oldpref").bindparams(oldp=old_path + "/", newp=new_path + "/", oldpref=old_path + "/%"))
    await db.commit()
    return {"ok": True, "path": new_path}

# ---------- Files ----------
@router.get("/projects/{project_id}/items")
async def list_file_items(project_id: int, folder: Optional[str] = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    # permission check on folder
    fid = await _folder_id_from_path(db, project_id, folder)
    can_read, _ = await _effective_perm(db, project_id, u, fid)
    if not can_read:
        raise HTTPException(403, "No read access to this folder")
    # list files living exactly in this folder path (or NULL/'' for root)
    if folder in (None, "", "null", "NULL"):
        res = await db.execute(select(ProjectFile).where(ProjectFile.contract_id == project_id).where((ProjectFile.folder.is_(None)) | (ProjectFile.folder == "")).where(ProjectFile.deleted_at.is_(None)).order_by(ProjectFile.original_name.asc()))
    else:
        res = await db.execute(select(ProjectFile).where(ProjectFile.contract_id == project_id, ProjectFile.folder == folder, ProjectFile.deleted_at.is_(None)).order_by(ProjectFile.original_name.asc()))
    files = [f for f in (res.scalars().all()) if getattr(f, 'deleted_at', None) is None]
    out = []
    for f in files:
        # revision number = count of versions for this file
        vres = await db.execute(select(func.coalesce(func.max(ProjectFileVersion.revision_no), 0)).where(ProjectFileVersion.file_id == f.id))
        maxrev = vres.scalar_one() or 0
        # The ProjectFile row itself represents the latest revision too; if we never stored rev 1, set to maxrev or 1
        latest_rev = maxrev if maxrev > 0 else 1
        out.append({
            "id": f.id, "name": f.original_name, "size_bytes": f.size_bytes, "content_type": f.content_type,
            "folder": f.folder or "", "uploaded_at": getattr(f, "uploaded_at", None), "revision_no": latest_rev
        })
    return out

@router.patch("/items/{file_id}")
async def update_file(file_id: int,
                      folder: Optional[str] = Form(None),
                      name: Optional[str] = Form(None),
                      db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    f = await db.get(ProjectFile, file_id)
    if not f:
        raise HTTPException(404, "File not found")
    if not await _can_access(db, u, f.contract_id):
        raise HTTPException(403, "Not allowed")
    # permission checks for move/rename
    src_fid = await _folder_id_from_path(db, f.contract_id, f.folder or None)
    _, can_write_src = await _effective_perm(db, f.contract_id, u, src_fid)
    if not can_write_src: raise HTTPException(403, "No write access (source)")
    if folder is not None:
        dst_fid = await _folder_id_from_path(db, f.contract_id, folder or None)
        _, can_write_dst = await _effective_perm(db, f.contract_id, u, dst_fid)
        if not can_write_dst: raise HTTPException(403, "No write access (destination)")
        f.folder = folder or None
    if name is not None and name.strip():
        f.original_name = name.strip()
    await db.commit()
    return {"ok": True}

@router.post("/items/reorder")
async def reorder_items(project_id: int = Form(...),
                        folder: Optional[str] = Form(None),
                        ids: List[int] = Form(...),
                        db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    # ProjectFile lacks sort_index; we keep alphabetical order for now
    return {"ok": True}

# Upload / replace (revision)
@router.post("/projects/{project_id}/upload")
async def upload_file(project_id: int,
                      file: UploadFile = File(...),
                      folder: Optional[str] = Form(None),
                      replace_file_id: Optional[int] = Form(None),
                      db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    # write permission on target
    fid = await _folder_id_from_path(db, project_id, folder)
    _, can_write = await _effective_perm(db, project_id, u, fid)
    if not can_write:
        raise HTTPException(403, "No write access to this folder")

    os.makedirs(_proj_dir(project_id), exist_ok=True)

    # Sanitize filename
    orig = os.path.basename(file.filename or "upload.bin")
    safe_name = orig.replace("\\", "_").replace("/", "_")
    content_type = file.content_type or "application/octet-stream"

    if replace_file_id:
        # Replace: create a new version row for the uploaded file and set ProjectFile to the new blob.
        pf = await db.get(ProjectFile, replace_file_id)
        if not pf or pf.contract_id != project_id:
            raise HTTPException(404, "File to replace not found")
        # First, store the current file as a version row if it's not already recorded as latest rev
        res = await db.execute(select(func.coalesce(func.max(ProjectFileVersion.revision_no), 0)).where(ProjectFileVersion.file_id == pf.id))
        curr_max = res.scalar_one() or 0
        if curr_max == 0:
            # persist current state as revision 1
            v = ProjectFileVersion(file_id=pf.id, revision_no=1, stored_path=pf.stored_path, content_type=pf.content_type, size_bytes=pf.size_bytes, uploaded_by=getattr(u, "id", None))
            db.add(v)
            await db.flush()
            next_rev = 2
        else:
            next_rev = curr_max + 1

        # Save new blob
        new_basename = f"{uuid.uuid4().hex}-{safe_name}"
        dest = os.path.join(_proj_dir(project_id), new_basename)
        with open(dest, "wb") as out:
            shutil.copyfileobj(file.file, out)
        size = os.path.getsize(dest)

        # Update ProjectFile to point to new blob
        pf.original_name = safe_name
        pf.stored_path = dest
        pf.content_type = content_type
        pf.size_bytes = size
        await db.flush()

        # Record uploaded revision as next_rev in versions table
        v2 = ProjectFileVersion(file_id=pf.id, revision_no=next_rev, stored_path=dest, content_type=content_type, size_bytes=size, uploaded_by=getattr(u, "id", None))
        db.add(v2)
        await db.commit()
        return {"id": pf.id, "revision_no": next_rev, "name": pf.original_name, "size_bytes": pf.size_bytes, "folder": pf.folder or ""}

    # New upload
    new_basename = f"{uuid.uuid4().hex}-{safe_name}"
    dest = os.path.join(_proj_dir(project_id), new_basename)
    with open(dest, "wb") as out:
        shutil.copyfileobj(file.file, out)
    size = os.path.getsize(dest)

    pf = ProjectFile(contract_id=project_id, original_name=safe_name, stored_path=dest, content_type=content_type, size_bytes=size, folder=(folder or None))
    db.add(pf)
    await db.flush()
    # initial version 1
    v = ProjectFileVersion(file_id=pf.id, revision_no=1, stored_path=dest, content_type=content_type, size_bytes=size, uploaded_by=getattr(u, "id", None))
    db.add(v)
    await db.commit()
    await db.refresh(pf)
    return {"id": pf.id, "name": pf.original_name, "size_bytes": pf.size_bytes, "folder": pf.folder or "", "revision_no": 1}

@router.get("/items/{file_id}/versions")
async def get_versions(file_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    pf = await db.get(ProjectFile, file_id)
    if not pf:
        raise HTTPException(404, "Not found")
    if not await _can_access(db, u, pf.contract_id):
        raise HTTPException(403, "Not allowed")
    res = await db.execute(select(ProjectFileVersion).where(ProjectFileVersion.file_id == file_id).order_by(ProjectFileVersion.revision_no.asc()))
    out = [{"revision_no": v.revision_no, "size_bytes": v.size_bytes, "uploaded_at": v.uploaded_at} for v in res.scalars().all()]
    return out

@router.get("/items/{file_id}/download")
async def download_latest(file_id: int, version: Optional[int] = None, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    pf = await db.get(ProjectFile, file_id)
    if not pf:
        raise HTTPException(404, "Not found")
    if not await _can_access(db, u, pf.contract_id):
        raise HTTPException(403, "Not allowed")
    path = pf.stored_path
    if version is not None:
        res = await db.execute(select(ProjectFileVersion).where(ProjectFileVersion.file_id == file_id, ProjectFileVersion.revision_no == version))
        v = res.scalar_one_or_none()
        if not v:
            raise HTTPException(404, "Version not found")
        path = v.stored_path
    if not os.path.exists(path):
        raise HTTPException(404, "File missing on disk")
    fname = os.path.basename(path)
    return FileResponse(path, media_type=pf.content_type or "application/octet-stream", filename=fname)



@router.post("/items/{file_id}/restore")
async def restore(file_id: int, version: int = Form(...), db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    pf = await db.get(ProjectFile, file_id)
    if not pf:
        raise HTTPException(404, "Not found")
    if not await _can_access(db, u, pf.contract_id):
        raise HTTPException(403, "Not allowed")
    # find target version
    res = await db.execute(select(ProjectFileVersion).where(ProjectFileVersion.file_id == file_id, ProjectFileVersion.revision_no == version))
    v = res.scalar_one_or_none()
    if not v:
        raise HTTPException(404, "Version not found")

    # next revision number
    res2 = await db.execute(select(func.coalesce(func.max(ProjectFileVersion.revision_no), 0)).where(ProjectFileVersion.file_id == file_id))
    next_rev = (res2.scalar_one() or 0) + 1

    # logically "restore" by pointing the latest to the chosen blob and recording a new revision
    pf.stored_path = v.stored_path
    pf.content_type = v.content_type
    pf.size_bytes = v.size_bytes
    await db.flush()

    db.add(ProjectFileVersion(file_id=pf.id, revision_no=next_rev, stored_path=v.stored_path, content_type=v.content_type, size_bytes=v.size_bytes, uploaded_by=getattr(u, "id", None)))
    await db.commit()
    return {"ok": True, "revision_no": next_rev}


@router.get("/projects/{project_id}/members")
async def list_members(project_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    if not await _can_access(db, u, project_id):
        raise HTTPException(403, "Not allowed")
    res = await db.execute(select(ContractAccess.user_id).where(ContractAccess.contract_id == project_id))
    user_ids = [row[0] for row in res.all()]
    if not user_ids:
        return []
    res2 = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = res2.scalars().all()
    return [{"id": uu.id, "name": uu.name, "email": uu.email} for uu in users]

@router.get("/folders/{folder_id}/permissions")
async def get_permissions(folder_id: int, db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    folder = await db.get(ProjectFolder, folder_id)
    if not folder: raise HTTPException(404, "Folder not found")
    if not await _can_access(db, u, folder.contract_id):
        raise HTTPException(403, "Not allowed")
    # list members and explicit perms (inherit handled on access check, but we return explicit entries here)
    res = await db.execute(select(ContractAccess.user_id).where(ContractAccess.contract_id == folder.contract_id))
    user_ids = [row[0] for row in res.all()]
    if user_ids:
        resu = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = resu.scalars().all()
    else:
        users = []
    resp = await db.execute(select(ProjectFolderPermission).where(ProjectFolderPermission.contract_id == folder.contract_id, ProjectFolderPermission.folder_id == folder_id))
    pmap = { (p.user_id): p for p in resp.scalars().all() }
    out = []
    for uu in users:
        p = pmap.get(uu.id)
        out.append({"user_id": uu.id, "name": uu.name, "email": uu.email, "can_read": bool(getattr(p, "can_read", 0)), "can_write": bool(getattr(p, "can_write", 0))})
    return out

@router.post("/folders/{folder_id}/permissions")
async def set_permission(folder_id: int, user_id: int = Form(...), can_read: int = Form(1), can_write: int = Form(0), db: AsyncSession = Depends(get_db), u: User = Depends(get_current_user)):
    folder = await db.get(ProjectFolder, folder_id)
    if not folder: raise HTTPException(404, "Folder not found")
    if not await _can_access(db, u, folder.contract_id):
        raise HTTPException(403, "Not allowed")
    # upsert
    res = await db.execute(select(ProjectFolderPermission).where(ProjectFolderPermission.contract_id == folder.contract_id, ProjectFolderPermission.folder_id == folder_id, ProjectFolderPermission.user_id == user_id))
    row = res.scalar_one_or_none()
    if (not can_read) and (not can_write):
        if row:
            await db.delete(row)
            await db.commit()
        return {"ok": True, "deleted": True}
    if row:
        row.can_read = 1 if can_read else 0
        row.can_write = 1 if can_write else 0
        await db.commit()
        return {"ok": True, "updated": True}
    else:
        newp = ProjectFolderPermission(contract_id=folder.contract_id, folder_id=folder_id, user_id=user_id, can_read=1 if can_read else 0, can_write=1 if can_write else 0)
        db.add(newp); await db.commit()
        return {"ok": True, "created": True}
