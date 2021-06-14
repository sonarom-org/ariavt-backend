
import os
import imghdr

from fastapi import File, UploadFile, HTTPException

from app.config import IMAGES_FOLDER
from app.data.models import UserInDB
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


async def add_image(file: UploadFile = File(...), user: UserInDB = None):
    relative_path = os.path.join(IMAGES_FOLDER, file.filename)
    print('Writing file {} to disk...'.format(file.filename))
    contents = await file.read()
    # Check if uploaded file is actually an image
    img_type = imghdr.what(None, contents)
    if img_type is None:
        raise HTTPException(status_code=422, detail="Uploaded file is not an image")
    await save_file(relative_path, contents)
    query = images.insert().values(text="Image",
                                   relative_path=relative_path,
                                   user_id=user.id)
    last_record_id = await database.execute(query)
    return last_record_id


async def remove_image(id_: int, relative_path: str) -> None:
    # Delete image file from file system
    await delete_file(relative_path)
    # Delete image record from images table
    query = images.delete().where(images.columns.id == id_)
    await database.execute(query)
