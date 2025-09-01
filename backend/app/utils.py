import os, uuid, aiofiles
from fastapi import UploadFile
from .config import config

async def save_upload(file: UploadFile, subdir: str = "") -> tuple[str, str, int, str]:
    os.makedirs(config.storage.files_dir, exist_ok=True)
    dir_path = os.path.join(config.storage.files_dir, subdir) if subdir else config.storage.files_dir
    os.makedirs(dir_path, exist_ok=True)
    suffix = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    path = os.path.join(dir_path, stored_name)
    size = 0
    async with aiofiles.open(path, "wb") as f:
        while True:
            chunk = await file.read(1024*1024)
            if not chunk:
                break
            size += len(chunk)
            await f.write(chunk)
    return stored_name, path, size, file.content_type or "application/octet-stream"
