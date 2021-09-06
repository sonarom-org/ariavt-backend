
from typing import List, Optional
import hashlib

from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Form,\
    status
from fastapi import Depends
from sqlalchemy.sql import select

from app.data.models import Image, User
from app.data.database import database, images
from app.data.io_files import get_file, get_file_base64
from app.data.operations import add_image, remove_image
from app.security.methods import get_current_active_user


router = APIRouter()

selection = {}


@router.get("/", response_model=List[Image])
async def read_images(
        ids: Optional[List[int]] = Query(None),
        user_id: Optional[int] = Query(None),
        current_user: User = Depends(get_current_active_user)
        ):
    if ids is not None:
        # https://stackoverflow.com/questions/8603088/
        query = select([images]).where(images.c.id.in_(ids))
        db_images = await database.fetch_all(query)
        if not db_images:
            raise HTTPException(status_code=404, detail="Item(s) not found")
        return db_images
    elif user_id is not None:
        query = select([images]).where(user_id == images.c.user_id)
        db_images = await database.fetch_all(query)
        return db_images
    else:
        # Return the images ids of the current user
        query = select([images]).where(current_user.id == images.c.user_id)
        db_images = await database.fetch_all(query)
        return db_images


@router.get("/{id_}")
async def get_image(id_: int):
    query = images.select().where(images.columns.id == id_)
    db_image = await database.fetch_one(query)
    if db_image is not None:
        return await get_file(db_image['relative_path'])
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/base64/{id_}")
async def get_image(id_: int):
    query = images.select().where(images.columns.id == id_)
    db_image = await database.fetch_one(query)
    if db_image is not None:
        return await get_file_base64(db_image['relative_path'])
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.post("/")
async def upload_image(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_active_user),
        title: str = Form(...),
        text: str = Form('')
        ):
    last_record_id = await add_image(file, current_user, title, text)
    return {"id": last_record_id}


@router.post("/batch-upload")
async def upload_images(
        files: List[UploadFile] = File(...),
        current_user: User = Depends(get_current_active_user)
        ):
    ids = []
    for file in files:
        last_record_id = await add_image(file, current_user)
        ids.append(last_record_id)
    return {"ids": ids}


@router.post("/selection", status_code=201)
async def select_images(ids: List[int]):
    selection_hash = hashlib.sha256(str(ids).encode("utf-8")).hexdigest()[:8]
    selection[selection_hash] = ids
    return {'selection': selection_hash}


@router.delete("/selection/{selection_hash}", status_code=200)
async def delete_images(
        selection_hash: str,
        current_user: User = Depends(get_current_active_user)
        ):
    # Get DB records for given ids
    query = select([images], images.c.id.in_(selection[selection_hash]))
    db_images = await database.fetch_all(query)
    # Remove all selected images
    for db_image in db_images:
        await remove_image(db_image['id'], db_image['relative_path'],
                           current_user)
    return {'removed': selection[selection_hash]}


@router.put("/{image_id}")
async def update_image(
        image_id: int,
        text: Optional[str] = Form(None),
        title: Optional[str] = Form(None),
        current_user: User = Depends(get_current_active_user)
):
    # To perform the update, the image must be owned by the user
    query = select([images]).where(images.c.id == image_id)
    db_image = await database.fetch_one(query)
    if db_image['user_id'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user does not own the image.",
        )

    # If the image is owned by the user, perform the update
    values = dict(title=title, text=text,)

    query = images.update().values(**values).where(images.c.id == image_id)
    # TODO: esto no devuelve nada con el update
    last_record_id = await database.execute(query)
    return {"id": last_record_id}
