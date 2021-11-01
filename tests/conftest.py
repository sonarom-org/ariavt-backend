import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from tests.models_test import AccessToken

from app.main import app


@pytest.fixture
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            yield ac


@pytest.fixture
async def token_r(client: AsyncClient):
    tr = await AccessToken.get_token(client)
    return tr
