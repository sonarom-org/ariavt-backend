from typing import Any
from asgi_lifespan import LifespanManager
import pytest
from httpx import AsyncClient
from pydantic import BaseModel

from app.main import app


class TokenResponse(BaseModel):
    response: Any
    tokens: dict
    at: str
    headers: dict


class AccessToken:

    at = None

    @staticmethod
    async def get_token(client):
        if AccessToken.at is not None:
            return AccessToken.at
        else:
            login_data = {
                "username": "admin",
                "password": "admin",
            }

            response = await client.post("/token", data=login_data)
            response = response
            tokens = response.json()
            headers = {
                'Authorization': 'Bearer ' + tokens["access_token"],
                'accept': 'application/json',
            }
            tr = TokenResponse(response=response,
                               tokens=tokens,
                               at=tokens["access_token"],
                               headers=headers)
            return tr


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
