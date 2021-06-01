
from app.data.models import UserInDB
from app.data.database import users, database


async def get_user(username: str):
    query = users.select().where(users.columns.username == username)
    user_dict = await database.fetch_one(query)
    # print(user_dict)
    if user_dict is not None:
        user = UserInDB(**user_dict)
    else:
        user = user_dict
    return user


