from typing import List
# from icecream import ic
from fastapi import FastAPI, File, UploadFile
import os
from core.config import data
# Development:
from fastapi.middleware.cors import CORSMiddleware

from core.database import database, ImageIn, Image, images

app = FastAPI()

# < Development:
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# >

# TODO: allow uploading multiple files at a time.


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/images/", response_model=List[Image])
async def read_images():
    query = images.select()
    return await database.fetch_all(query)


@app.post("/images/", response_model=Image)
async def create_image(image: ImageIn):
    query = images.insert().values(text=image.text,
                                   relative_path=image.relative_path)
    last_record_id = await database.execute(query)
    return {**image.dict(), "id": last_record_id}


@app.get("/ping")
async def ping():
    return {"ping": "OK"}


@app.post("/files/")
async def upload_files_bytes(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


@app.get("/files/{filename}")
async def get_file_by_name(filename: str):
    raise NotImplemented
    # print(app.files)
    # return app.files[filename]


@app.post("/upload/")
async def upload_file_bytes(file: UploadFile = File(...)):
    path_to_save = os.path.join(data['folder'], file.filename)
    print('Writing file {} to disk...'.format(file.filename))
    contents = await file.read()
    with open(path_to_save, 'wb+') as f:
        f.write(contents)
        f.close()
    query = images.insert().values(text="Image",
                                   relative_path=path_to_save)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}


@app.post("/uploadfiles/")
async def upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}
