import base64
import imghdr
import os
import stat

from fastapi import HTTPException
from fastapi.responses import FileResponse
import aiofiles.os as aio_os
import aiofiles as aiof
import aiofiles.os as aiof_os
from aiofiles.os import stat as aiof_stat

from app.config import DATA_FOLDER, IMAGES_FOLDER


async def file_exists(path: str) -> bool:
    try:
        stat_result = await aiof_stat(path)
    except FileNotFoundError:
        return False
    else:
        mode = stat_result.st_mode
        if not stat.S_ISREG(mode):
            return False
    return True


async def create_folders() -> None:
    folders_to_create = [IMAGES_FOLDER]
    for folder in folders_to_create:
        full_path = os.path.join(DATA_FOLDER, folder)
        if not os.path.exists(full_path):
            await aio_os.mkdir(full_path)


async def save_file(relative_path: str, contents: bytes) -> None:
    full_path = os.path.join(DATA_FOLDER, relative_path)
    async with aiof.open(full_path, mode='wb+') as f:
        await f.write(contents)


async def get_file(filename: str) -> FileResponse:
    path = os.path.join(DATA_FOLDER, filename)
    exists = await file_exists(path)
    if exists:
        return FileResponse(path)
    else:
        raise HTTPException(status_code=404, detail="Item not found")


async def get_file_bytes(filename: str) -> bytes:
    path = os.path.join(DATA_FOLDER, filename)
    exists = await file_exists(path)
    if exists:
        async with aiof.open(path, mode='rb') as img:
            return await img.read()
    else:
        raise HTTPException(status_code=404, detail="Item not found")


async def get_file_base64(filename: str):
    path = os.path.join(DATA_FOLDER, filename)
    exists = await file_exists(path)
    if exists:
        with open(path, "rb") as image_file:
            contents = image_file.read()
            # Check if uploaded file is actually an image
            image_format = imghdr.what(None, contents)
            encoded_image_string = base64.b64encode(contents)
        return {"image": encoded_image_string, "format": image_format}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


async def delete_file(relative_path: str) -> None:
    full_path = os.path.join(DATA_FOLDER, relative_path)
    try:
        await aiof_os.remove(full_path)
    except FileNotFoundError:
        # If the file does not exist, pass
        pass
