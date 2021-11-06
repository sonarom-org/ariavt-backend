import tempfile
from typing import List, Union, Optional

from fastapi import (
    APIRouter, HTTPException, Form, status, Depends,
)
from pydantic.class_validators import Any
from sqlalchemy.sql import select, and_
from httpx import AsyncClient
from starlette.responses import FileResponse

from app.data.io_files import get_file, get_json_from_file
from app.data.models import User, Service
from app.data.database import services, images, results
from app.data.operations import add_result_image, add_result_file
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
        current_user: User = Depends(get_current_active_user),
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
async def get_service(
        service_id: int,
        image_id: Optional[int] = None,
        force_analysis: Optional[bool] = False,
        current_user: User = Depends(get_current_active_user),
):

    query = select([services]).where(services.c.id == service_id)
    db_service = await database.fetch_one(query)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")

    # If image_id is None, then return the service.
    # Else, send the image to the service and return the result.
    if image_id is None:
        return db_service
    else:
        # To perform the update, the image must be owned by the user
        query = select([images]).where(images.c.id == image_id)
        db_image = await database.fetch_one(query)
        if db_image['user_id'] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user does not own the image.",
            )

        # Check if the result was already obtained.
        # If it was, and the analysis is not forced, return it from
        #   database.
        # Else, obtain the result from the service and store it in the
        #   database.
        if not force_analysis:
            query = select(
                [results]
            ).where(
                and_(
                    results.c.image_id == image_id,
                    results.c.service_id == service_id,

                )
            )
            db_result = await database.fetch_one(query)
            if db_result is not None:
                if db_service['result_type'] == 'measurement':
                    return await get_json_from_file(db_result['relative_path'])
                elif db_service['result_type'] == 'image':
                    return await get_file(db_result['relative_path'])
                else:
                    raise HTTPException(
                        status_code=403, detail='Unknown result type'
                    )

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
                img_bytes = response.content

                db_id, image_type = await add_result_image(
                    image_id, img_bytes, db_service['name'], db_service['id']
                )

                # Create temporary image file and return it
                with tempfile.NamedTemporaryFile(
                    mode='w+b', suffix=f'.{image_type}', delete=False
                ) as F_OUT:
                    F_OUT.write(img_bytes)
                    return FileResponse(
                        F_OUT.name, media_type=f'image/{image_type}'
                    )
            elif db_service['result_type'] == 'measurement':
                await add_result_file(
                    image_id, response.content, db_service['name'],
                    db_service['id']
                )
                # Returns the exact answer given by the service
                return response.json()
            else:
                raise HTTPException(
                    status_code=403, detail='Unknown result type'
                )


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

