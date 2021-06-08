
from typing import List
import hashlib

from fastapi import APIRouter, File, UploadFile

from app.data.models import Image
from app.data.database import database, images
from app.data.io_files import get_file
from app.data.operations import add_image, remove_image


router = APIRouter()

selection = {}


@router.get("/", response_model=List[Image])
async def read_images():
    query = images.select()
    return await database.fetch_all(query)


@router.get("/{filename}")
async def get_image_by_name(filename: str):
    return await get_file(filename)


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    last_record_id = await add_image(file)
    return {"id": last_record_id}


@router.post("/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    ids = []
    for file in files:
        last_record_id = await add_image(file)
        ids.append(last_record_id)
    return {"ids": ids}


@router.post("/selection", status_code=201)
async def select_images(file_names: List[str]):
    selection_hash = hashlib.sha256(str(file_names).encode("utf-8")).hexdigest()[:8]
    selection[selection_hash] = file_names
    return {'selection': selection_hash}


@router.delete("/selection/{selection_hash}", status_code=200)
async def select_images(selection_hash: str):
    for file_name in selection[selection_hash]:
        await remove_image(file_name)
    return {'removed': selection[selection_hash]}
