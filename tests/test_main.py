from asgi_lifespan import LifespanManager
import pytest
from httpx import AsyncClient

from tests.utils import AccessToken

from app.main import app


@pytest.fixture
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            yield ac


@pytest.fixture
async def token_r(client):
    tr = await AccessToken.get_token(client)
    return tr


@pytest.mark.asyncio
async def test_get_images_not_authenticated(client):
    response = await client.get("/images/")
    print(response)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_access_token(token_r):
    assert token_r.response.status_code == 200
    assert "access_token" in token_r.tokens
    assert token_r.at


@pytest.mark.asyncio
async def test_get_images_authenticated(client, token_r):
    response = await client.get("/images/", headers=token_r.headers)
    print(response)
    assert response.status_code == 200
