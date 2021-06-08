from asgi_lifespan import LifespanManager
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            yield ac


@pytest.mark.asyncio
async def test_get_images_not_authenticated(client):
    response = await client.get("/images/images/")
    print(response)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_access_token(client):
    login_data = {
        "username": "admin",
        "password": "admin",
    }

    r = await client.post("/token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
    print(tokens)


@pytest.mark.asyncio
async def test_get_images_authenticated(client):
    login_data = {
        "username": "admin",
        "password": "admin",
    }

    r = await client.post("/token", data=login_data)
    tokens = r.json()
    print('Bearer '+tokens['access_token'])

    headers = {
        'Authorization': 'Bearer '+tokens['access_token'],
        'accept': 'application/json',
    }

    response = await client.get("/images/images/", headers=headers)
    print(response)
    assert r.status_code == 200
