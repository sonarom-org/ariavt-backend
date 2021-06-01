
from fastapi import APIRouter

from app.data.models import User


router = APIRouter()


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(current_user: User):
    return [{"item_id": "Foo", "owner": current_user.username}]
