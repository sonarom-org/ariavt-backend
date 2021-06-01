
import os
from typing import List
import imghdr

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.config import IMAGES_FOLDER
from app.data.models import ImageIn, Image
from app.data.database import database, images
from app.data.io_files import save_file, get_file


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


@router.get("/files/{filename}")
async def get_file_by_name(filename: str):
    return await get_file(filename)


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    relative_path = os.path.join(IMAGES_FOLDER, file.filename)
    print('Writing file {} to disk...'.format(file.filename))
    contents = await file.read()
    # Check if uploaded file is actually an image
    img_type = imghdr.what(None, contents)
    if img_type is None:
        raise HTTPException(status_code=422, detail="Uploaded file is not an image")
    await save_file(relative_path, contents)
    query = images.insert().values(text="Image",
                                   relative_path=relative_path)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}


@router.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}

