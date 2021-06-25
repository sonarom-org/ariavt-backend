import http
import os
import imghdr

from fastapi import File, UploadFile, HTTPException, Form
from sqlalchemy.sql import select

from app.config import IMAGES_FOLDER
from app.data.models import UserInDB, User
from app.data.database import database, images, users
from app.data.io_files import save_file, delete_file


async def get_user(username: str) -> UserInDB:
    query = users.select().where(users.columns.username == username)
    user_dict = await database.fetch_one(query)
    # print(user_dict)
    if user_dict is not None:
        user = UserInDB(**user_dict)
    else:
        user = user_dict
    return user


async def add_image(
        file: UploadFile = File(...),
        user: User = None,
        title: str = '',
        text: str = '',
        ):
    relative_path = os.path.join(IMAGES_FOLDER, file.filename)
    print('Writing file {} to disk...'.format(file.filename))
    contents = await file.read()
    # Check if uploaded file is actually an image
    img_type = imghdr.what(None, contents)
    if img_type is None:
        raise HTTPException(status_code=422,
                            detail="Uploaded file is not an image")
    await save_file(relative_path, contents)
    query = images.insert().values(title=title,
                                   text=text,
                                   relative_path=relative_path,
                                   user_id=user.id)
    last_record_id = await database.execute(query)
    return last_record_id


async def remove_image(id_: int, relative_path: str, user: User) -> None:
    query = select([images.c.id, images.c.user_id]).where(images.c.id == id_)
    db_images = await database.fetch_one(query)
    # If a record is found
    if db_images is not None:
        # Do not perform the deletion of an image if the user who
        # intends to perform the deletion does not own the image
        if db_images['user_id'] != user.id:
            raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED,
                                detail="Operation not allowed")
        # Delete image file from file system
        await delete_file(relative_path)
        # Delete image record from images table
        query = images.delete().where(images.columns.id == id_)
        await database.execute(query)
