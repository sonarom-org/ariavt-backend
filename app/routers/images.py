
from typing import List

from fastapi import APIRouter, File, UploadFile

from app.data.models import ImageIn, Image
from app.data.database import database, images
from app.data.io_files import get_file
from app.data.operations import add_image


router = APIRouter()


@router.get("/images/", response_model=List[Image])
async def read_images():
    query = images.select()
    return await database.fetch_all(query)


@router.post("/images/", response_model=Image)
async def create_image(image: ImageIn):
    query = images.insert().values(text=image.text,
                                   relative_path=image.relative_path)
    last_record_id = await database.execute(query)
    return {**image.dict(), "id": last_record_id}


@router.post("/files/")
async def upload_files_bytes(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


@router.get("/{filename}")
async def get_image_by_name(filename: str):
    return await get_file(filename)


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    last_record_id = await add_image(file)
    return {"id": last_record_id}


@router.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    ids = []
    for file in files:
        last_record_id = await add_image(file)
        ids.append(last_record_id)
    return {"ids": ids}

