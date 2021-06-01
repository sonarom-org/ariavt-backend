
import os
import stat

from fastapi import HTTPException
from fastapi.responses import FileResponse
import aiofiles.os as aio_os
import aiofiles as ai
from aiofiles.os import stat as aio_stat

from app.config import DATA_FOLDER, IMAGES_FOLDER


async def file_exists(path: str) -> bool:
    try:
        stat_result = await aio_stat(path)
    except FileNotFoundError:
        return False
    else:
        mode = stat_result.st_mode
        if not stat.S_ISREG(mode):
            return False
    return True


async def create_folders():
    if not os.path.exists(DATA_FOLDER):
        await aio_os.mkdir(DATA_FOLDER)


async def save_file(relative_path: str, contents: bytes):
    full_path = os.path.join(DATA_FOLDER, relative_path)
    async with ai.open(full_path, mode='wb+') as f:
        await f.write(contents)


async def get_file(filename: str):
    path = os.path.join(DATA_FOLDER, IMAGES_FOLDER, filename)
    exists = await file_exists(path)
    if exists:
        return FileResponse(path)
    else:
        raise HTTPException(status_code=404, detail="Item not found")
