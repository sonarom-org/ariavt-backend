from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.sql import select

from app.data.models import User
from app.security.methods import (
    get_current_active_user, get_password_hash, verify_password
)
from app.globals import ADMIN_ROLE
from app.data.database import database, users


router = APIRouter()


@router.get("/me", response_model=User)
async def get_users_me(current_user: User = Depends(get_current_active_user)):
    """ Side note:
    You can declare the same dependency at the router or decorator
    level and then declare it again in the path operation to get its
    value.

    It won't be evaluated twice, it doesn't add any extra computation,
    there's a dependency cache in place that stores the values of
    already solved dependencies for a given request (you can also
    disable the cache for a specific dependency, but that's not what
    you need here).

    So yeah, declare it at the top level to ensure everything in a
    router has the same security, and then at the path operation level
    again to get the solved value if you need it.
     ~ Tiangolo
    """
    return current_user


@router.post("/")
async def add_user(
        username: str = Form(...),
        full_name: str = Form(...),
        email: str = Form(...),
        role: str = Form(...),
        password: str = Form(...),
        current_user: User = Depends(get_current_active_user)
):
    if current_user.role == ADMIN_ROLE:
        hashed_password = get_password_hash(password)

        query = users.insert().values(
            username=username,
            full_name=full_name,
            email=email,
            disabled=False,
            role=role,
            hashed_password=hashed_password
        )
        last_record_id = await database.execute(query)
        return {"id": last_record_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )


@router.put("/{user_id}")
async def update_user(
        user_id: int,
        full_name: str = Form(...),
        email: str = Form(...),
        role: str = Form(...),
        old_password: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        current_user: User = Depends(get_current_active_user)
):
    # To perform the update, the user/data must meet the following conditions:
    #  new_id = current_id AND role = current_role
    #  OR new_id != current_id AND current_role = admin
    if ((user_id == current_user.id and role == current_user.role)
            or (user_id != current_user.id
                and current_user.role == ADMIN_ROLE)):

        values = dict(
            full_name=full_name,
            email=email,
            disabled=False,
            role=role
        )

        if password is not None:
            hashed_password = get_password_hash(password)
            if current_user.role == ADMIN_ROLE:
                values.update(hashed_password=hashed_password)
            else:
                # If user is not ADMIN, check if previous password is
                # correct to approve the change request
                if old_password is not None:
                    query = select([users]).where(users.c.id == user_id)
                    db_user = await database.fetch_one(query)
                    if not db_user:
                        raise HTTPException(
                            status_code=404, detail="User not found")

                    if verify_password(old_password, db_user['hashed_password']):
                        values.update(hashed_password=hashed_password)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=(
                                "Unable to change user password: incorrect "
                                "old password"
                            ),
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=(
                            "Unable to change user password: old password not "
                            "provided"
                        ),
                    )

        query = users.update().values(
            **values
        ).where(users.c.id == user_id)
        last_record_id = await database.execute(query)
        return {"id": last_record_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
        user_id: int,
        current_user: User = Depends(get_current_active_user)
):
    if current_user.role == ADMIN_ROLE:
        query = select([users]).where(users.c.id == user_id)
        db_user = await database.fetch_one(query)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_active_user)
):
    if current_user.role == ADMIN_ROLE and user_id != current_user.id:
        query = select([users]).where(users.c.id == user_id)
        db_user = await database.fetch_one(query)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            query = users.delete().where(users.columns.id == user_id)
            await database.execute(query)
            return {'removed': user_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )


@router.get("/", response_model=List[User])
async def get_all_users(
        current_user: User = Depends(get_current_active_user)
):
    if current_user.role == ADMIN_ROLE:
        query = select([users])
        db_users = await database.fetch_all(query)
        if not db_users:
            raise HTTPException(status_code=404, detail="No user found")
        return db_users
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Operation not permitted",
        )
