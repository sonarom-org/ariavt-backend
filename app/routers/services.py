import imghdr
import tempfile
from typing import List, Union, Optional
import json

from fastapi import (
    APIRouter, HTTPException, Form, status, Depends,
)
from pydantic.class_validators import Any
from sqlalchemy.sql import select
from httpx import AsyncClient
from starlette.responses import FileResponse

from app.data.models import User, Service
from app.data.database import services
from app.security.methods import get_current_active_user
from app.globals import ADMIN_ROLE
from app.data.database import database
from app.routers.images import get_image_bytes


router = APIRouter()


@router.post("/")
async def add_service(
        name: str = Form(...),
        url: str = Form(...),
        result_type: str = Form(...),
        full_name: str = Form(...),
        description: str = Form(...),
        current_user: User = Depends(get_current_active_user)
):
    # Operation only available for admin users
    if current_user.role == ADMIN_ROLE:
        query = services.insert().values(
            name=name,
            url=url,
            result_type=result_type,
            full_name=full_name,
            description=description,
        )
        last_record_id = await database.execute(query)
        return {"id": last_record_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )


@router.get("/{service_id}", response_model=Union[Service, Any])
async def get_service(service_id: int, image_id: Optional[int] = None):
    query = select([services]).where(services.c.id == service_id)
    db_service = await database.fetch_one(query)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    # If image_id is not None, then send the image to the service and
    #   return the result.
    #   Else, return the service.
    if image_id is not None:
        image = await get_image_bytes(image_id)

        async with AsyncClient() as ac:
            # Build json to post
            files = {'file': image}
            # Add necessary 'multipart/form-data' header
            # headers = token_r.headers.copy()
            headers = {'accept': 'application/json'}
            # print('HEADERS', headers)
            # Post data
            response = await ac.post(
                db_service['url'],
                files=files,
                headers=headers
            )

            if db_service['result_type'] == 'image':
                # Create temporary image file and return it
                img_bytes = response.content
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
                    return FileResponse(
                        F_OUT.name, media_type=f'image/{img_type}'
                    )
            elif db_service['result_type'] == 'measurement':
                # Returns the exact answer given by the service
                return response.json()
            else:
                raise HTTPException(
                    status_code=403, detail='Unknown result type'
                )
    else:
        return db_service


@router.delete("/{service_id}")
async def delete_service(
        service_id: int,
        current_user: User = Depends(get_current_active_user)
):
    # Operation only available for admin users
    if current_user.role == ADMIN_ROLE:
        query = select([services]).where(services.c.id == service_id)
        db_service = await database.fetch_one(query)
        if not db_service:
            raise HTTPException(status_code=404, detail="Service not found")
        else:
            query = services.delete().where(services.columns.id == service_id)
            await database.execute(query)
            return {'removed': service_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )


@router.put("/{service_id}")
async def add_service(
        service_id: int,
        name: Optional[str] = Form(None),
        url: Optional[str] = Form(None),
        result_type: Optional[str] = Form(None),
        full_name: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        current_user: User = Depends(get_current_active_user)
):
    values = dict()
    if name:
        values['name'] = name
    if url:
        values['url'] = url
    if result_type:
        values['result_type'] = result_type
    if full_name:
        values['full_name'] = full_name
    if description:
        values['description'] = description

    # Operation only available for admin users
    if current_user.role == ADMIN_ROLE:
        query = services.update().values(
            **values
        ).where(services.c.id == service_id)
        last_record_id = await database.execute(query)
        return {"id": last_record_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )


@router.get("/", response_model=List[Service])
async def get_all_services():
    query = select([services])
    db_services = await database.fetch_all(query)
    if not db_services:
        raise HTTPException(status_code=404, detail="No service found")
    return db_services

