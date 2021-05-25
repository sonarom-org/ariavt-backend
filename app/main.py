from typing import List
# from icecream import ic
from fastapi import FastAPI, File, UploadFile
import os
from config import data
# Development:
from fastapi.middleware.cors import CORSMiddleware


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

# TODO: check how to handle files list.
# TODO: allow uploading multiple files at a time.

# Received messages list
app.messages = []
app.files = {}


@app.get("/ping")
async def ping():
    return {"ping": "OK"}


@app.post("/files/")
async def upload_files_bytes(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}


@app.get("/files/{filename}")
async def get_file_by_name(filename: str):
    print(app.files)
    return app.files[filename]


@app.get("/files/")
async def get_files():
    print(app.files)
    return [{"name": file, "url": "url"} for file in app.files]


@app.post("/upload/")
async def upload_file_bytes(file: UploadFile = File(...)):
    app.files[file.filename] = {"file": file.file}
    path_to_save = os.path.join(data['folder'], file.filename)
    print('Writing file {} to disk...'.format(file.filename))
    with open(path_to_save, 'wb+') as f:
        f.write(file.file.read())
        f.close()
    return {"filename": file.filename}


@app.post("/uploadfiles/")
async def upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}
