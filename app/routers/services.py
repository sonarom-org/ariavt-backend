from typing import List, Union, Optional

from fastapi import APIRouter, HTTPException, Form, status
from fastapi import Depends
from sqlalchemy.sql import select

from app.data.models import User, Service
from app.data.database import services
from app.security.methods import get_current_active_user
from app.globals import ADMIN_ROLE
from app.data.database import database
from app.routers.images import get_image


router = APIRouter()


@router.post("/")
async def add_service(
        name: str = Form(...),
        url: str = Form(...),
        full_name: str = Form(...),
        description: str = Form(...),
        current_user: User = Depends(get_current_active_user)
):
    # Operation only available for admin users
    if current_user.role == ADMIN_ROLE:
        query = services.insert().values(
            name=name,
            url=url,
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


@router.get("/{service_id}", response_model=Service)  # Union[Service, None]
async def get_service(service_id: int):  #, image_id: Optional[int] = None):
    query = select([services]).where(services.c.id == service_id)
    db_service = await database.fetch_one(query)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    # If image_id is not None, then send the image to the service and
    #   return the result.
    #   Else, return the service.
    # if image_id is not None:
    #     # TODO: send image to the service and return the result.
    #     image = await get_image(image_id)
    #     return image
    # else:
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
        full_name: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        current_user: User = Depends(get_current_active_user)
):
    values = dict()
    if name:
        values['name'] = name
    if url:
        values['url'] = url
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

