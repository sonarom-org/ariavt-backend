import tempfile
import imghdr

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

service = FastAPI()


@service.post("/")
async def echo_image(
        file: UploadFile = File(...),
):
    """Simple echo service for testing purposes.
    It receives a file and returns it.
    """
    img_bytes = await file.read()
    img_type = imghdr.what(None, img_bytes)

    if img_type is None:
        raise HTTPException(
            status_code=422,
            detail='Invalid image returned from service'
        )

    with tempfile.NamedTemporaryFile(
        mode='w+b', suffix=f'.{img_type}', delete=False
    ) as F_OUT:
        F_OUT.write(img_bytes)
        return FileResponse(F_OUT.name, media_type=f'image/{img_type}')


@service.post("/json")
async def echo_random_result(
        file: UploadFile = File(...),
):
    """Simple echo service for testing purposes.
    It receives a file and returns a message in JSON format.
    """
    img_bytes = await file.read()
    img_type = imghdr.what(None, img_bytes)

    if img_type is None:
        raise HTTPException(
            status_code=422,
            detail='Invalid image returned from service'
        )

    return {'image': 'OK'}


@service.get("/ping")
async def echo_random_result():
    """Simple ping."""
    return {'ping': 'OK'}
