
from fastapi import APIRouter, Depends

from app.data.models import User
from app.security.methods import get_current_active_user


router = APIRouter()


@router.get("/me", response_model=User)
async def get_users_me(current_user: User = Depends(get_current_active_user)):
    """ Side note:
    You can declare the same dependency at the router or decorator level and
    then declare it again in the path operation to get its value.

    It won't be evaluated twice, it doesn't add any extra computation, there's
    a dependency cache in place that stores the values of already solved
    dependencies for a given request (you can also disable the cache for a
    specific dependency, but that's not what you need here).

    So yeah, declare it at the top level to ensure everything in a router has
    the same security, and then at the path operation level again to get the
    solved value if you need it.
     ~ Tiangolo
    """
    return current_user


