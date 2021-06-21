
from asgi_lifespan import LifespanManager
import pytest
from http import HTTPStatus as sc
from httpx import AsyncClient

from tests.test_models import AccessToken, TokenResponse
from tests.utils import upload_images, upload_single_image, delete_images

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


@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_delete_all_images(
        client: AsyncClient,
        token_r: TokenResponse):
    response = await client.get("/images/", headers=token_r.headers)
    assert response.status_code == sc.OK
    print(response)
    print(response.json())
    images = response.json()
    images_ids = []
    for image in images:
        images_ids.append(image['id'])
    print("IMAGES_IDS", images_ids)
    response = await delete_images(client, token_r, ids=images_ids)
    assert response.status_code == sc.OK
    assert 'removed' in response.json()


@pytest.mark.asyncio
async def test_get_images_not_authenticated(client: AsyncClient):
    response = await client.get("/images/")
    print(response)
    assert response.status_code == sc.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_access_token(token_r: TokenResponse):
    print(token_r.response)
    assert token_r.response.status_code == sc.OK
    assert "access_token" in token_r.tokens
    assert token_r.at


@pytest.mark.asyncio
async def test_verify_token(
        client: AsyncClient,
        token_r: TokenResponse):
    # OK
    response = await client.get("/verify-token", headers=token_r.headers)
    print(response.json())
    assert response.status_code == sc.OK
    # UNAUTHORIZED
    headers = token_r.headers.copy()
    headers['Authorization'] = 'Bearer ' + 'bad-token'
    response = await client.get("/verify-token", headers=headers)
    print(response.json())
    assert response.status_code == sc.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_images_authenticated(
        client: AsyncClient,
        token_r: TokenResponse):
    response = await client.get("/images/", headers=token_r.headers)
    print(response)
    print(response.json())
    assert response.status_code == sc.OK


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(
        client: AsyncClient):
    response = await client.get("/users/me")
    print(response)
    assert response.status_code == sc.UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, token_r: TokenResponse):
    response = await client.get("/users/me", headers=token_r.headers)
    print(response)
    response_json = response.json()
    assert response.status_code == sc.OK
    assert 'username' in response_json
    assert response_json['username'] == 'admin'
    assert not response_json['disabled']


@pytest.mark.asyncio
async def test_upload_image(client: AsyncClient, token_r: TokenResponse):
    image_name = 'c_im0236.png'
    # Upload single image
    response = await upload_single_image(client, token_r, image_name)
    print(response)
    assert response.status_code == sc.OK
    id_ = response.json()['id']
    # Remove uploaded image
    response = await delete_images(client, token_r, ids=[id_])
    assert response.status_code == sc.OK
    assert 'removed' in response.json()


@pytest.mark.asyncio
async def test_upload_and_get_image(client: AsyncClient, token_r: TokenResponse):
    image_name = 'c_im0236.png'
    # Upload image
    response = await upload_single_image(client, token_r, image_name)
    print(response)
    assert response.status_code == sc.OK
    assert response.json()['id']
    id_ = response.json()['id']
    # Get uploaded image
    response = await client.get("/images/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes
    # Get uploaded image base64
    response = await client.get("/images/base64/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes
    # Remove the file
    response = await delete_images(client, token_r, ids=[id_])
    assert response.status_code == sc.OK
    assert 'removed' in response.json()
    # Try fetching the removed file
    response = await client.get("/images/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.NOT_FOUND


@pytest.mark.asyncio
async def test_upload_and_get_images(client: AsyncClient, token_r: TokenResponse):
    image_names = ['c_im0236.png', 'c_im0237.png', 'c_im0238.png']
    # Upload image
    response = await upload_images(client, token_r, image_names)
    print(response)
    assert response.status_code == sc.OK
    assert response.json()['ids']
    ids = response.json()['ids']
    # Get uploaded image
    params = {'ids': ids}
    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes
    # Remove the file
    response = await delete_images(client, token_r, ids=ids)
    assert response.status_code == sc.OK
    assert 'removed' in response.json()
    print(response.json())
    # Try fetching the removed file
    print('PARAMS', params)
    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response.json())
    assert response.status_code == sc.NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_images(client: AsyncClient, token_r: TokenResponse):
    image_names = ['c_im0236.png', 'c_im0237.png']
    # Upload image
    response = await upload_images(client, token_r, image_names)
    print(response)
    assert response.status_code == sc.OK
    assert response.json()['ids']
    ids = response.json()['ids']
    # Get uploaded image
    images_ids = {'ids': ids}
    response = await client.get("/users/me", headers=token_r.headers)
    user = response.json()
    print("USER", user)
    params = {'user_id': user['id']}
    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    print(response.json())
    assert images_ids == response.json()
    # Remove images
    response = await delete_images(client, token_r, ids=ids)
    assert response.status_code == sc.OK
    assert 'removed' in response.json()
    print(response.json())
