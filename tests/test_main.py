import pytest
from http import HTTPStatus as sc
from httpx import AsyncClient

from tests.models_test import AccessToken, TokenResponse
from tests.utils import upload_images, upload_single_image, delete_images

from app.globals import USER_ROLE

# =====================================================================


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


# =====================================================================

@pytest.mark.asyncio
async def test_get_images_not_authenticated(client: AsyncClient):
    response = await client.get("/images/")
    print(response)
    assert response.status_code == sc.UNAUTHORIZED


# =====================================================================

@pytest.mark.asyncio
async def test_get_access_token(token_r: TokenResponse):
    print(token_r.response)
    assert token_r.response.status_code == sc.OK
    assert "access_token" in token_r.tokens
    assert token_r.at


# =====================================================================

@pytest.mark.asyncio
async def test_verify_token(
        client: AsyncClient,
        token_r: TokenResponse):
    # -> OK
    response = await client.get("/verify-token", headers=token_r.headers)
    print(response.json())
    assert response.status_code == sc.OK
    # -> UNAUTHORIZED
    headers = token_r.headers.copy()
    headers['Authorization'] = 'Bearer ' + 'bad-token'
    response = await client.get("/verify-token", headers=headers)
    print(response.json())
    assert response.status_code == sc.UNAUTHORIZED


# =====================================================================

@pytest.mark.asyncio
async def test_get_images_authenticated(
        client: AsyncClient,
        token_r: TokenResponse):
    response = await client.get("/images/", headers=token_r.headers)
    print(response)
    print(response.json())
    assert response.status_code == sc.OK


# =====================================================================

@pytest.mark.asyncio
async def test_get_current_user_unauthorized(
        client: AsyncClient):
    response = await client.get("/users/me")
    print(response)
    assert response.status_code == sc.UNAUTHORIZED


# =====================================================================

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, token_r: TokenResponse):
    response = await client.get("/users/me", headers=token_r.headers)
    print(response)
    response_json = response.json()
    assert response.status_code == sc.OK
    assert 'username' in response_json
    assert response_json['username'] == 'admin'
    assert not response_json['disabled']


# =====================================================================

@pytest.mark.asyncio
async def test_upload_image(client: AsyncClient, token_r: TokenResponse):
    image_name = 'c_im0236.png'

    # -> Upload single image

    response = await upload_single_image(client, token_r, image_name)
    print(response)
    assert response.status_code == sc.OK
    id_ = response.json()['id']

    # -> Remove uploaded image

    response = await delete_images(client, token_r, ids=[id_])
    assert response.status_code == sc.OK
    assert 'removed' in response.json()


# =====================================================================

@pytest.mark.asyncio
async def test_upload_and_get_image(client: AsyncClient, token_r: TokenResponse):
    image_name = 'c_im0236.png'

    # -> Upload image

    response = await upload_single_image(client, token_r, image_name)
    print(response)
    assert response.status_code == sc.OK
    assert response.json()['id']
    id_ = response.json()['id']

    # -> Get uploaded image

    response = await client.get("/images/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes

    # -> Get uploaded image base64

    response = await client.get("/images/base64/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes

    # -> Remove the file

    response = await delete_images(client, token_r, ids=[id_])
    assert response.status_code == sc.OK
    assert 'removed' in response.json()

    # -> Try fetching the removed file

    response = await client.get("/images/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.NOT_FOUND


# =====================================================================

@pytest.mark.asyncio
async def test_upload_and_get_images(client: AsyncClient, token_r: TokenResponse):
    image_names = ['c_im0236.png', 'c_im0237.png', 'c_im0238.png']

    # -> Upload image

    response = await upload_images(client, token_r, image_names)
    print(response)
    assert response.status_code == sc.OK
    assert response.json()['ids']
    ids = response.json()['ids']

    # -> Get uploaded image

    params = {'ids': ids}
    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes

    # -> Remove the file

    response = await delete_images(client, token_r, ids=ids)
    assert response.status_code == sc.OK
    assert 'removed' in response.json()
    print(response.json())

    # -> Try fetching the removed file

    print('PARAMS', params)
    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response.json())
    assert response.status_code == sc.NOT_FOUND


# =====================================================================

@pytest.mark.asyncio
async def test_get_user_images(client: AsyncClient, token_r: TokenResponse):
    image_names = ['c_im0236.png', 'c_im0237.png']

    # -> Upload image

    response = await upload_images(client, token_r, image_names)
    print(response)
    assert response.status_code == sc.OK
    assert response.json()['ids']
    ids = response.json()['ids']

    # -> Get uploaded images

    images_ids = {'ids': ids}
    # Get user id
    response = await client.get("/users/me", headers=token_r.headers)
    user = response.json()
    print("USER", user)
    # Get images given the user id
    params = {'user_id': user['id']}
    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    print(response.json())
    received_ids = {"ids": [image['id'] for image in response.json()]}
    assert images_ids == received_ids

    # -> Remove images

    response = await delete_images(client, token_r, ids=ids)
    assert response.status_code == sc.OK
    assert 'removed' in response.json()
    print(response.json())
    # Check if there are no images
    response = await client.get("/images/", headers=token_r.headers)
    assert response.json() == []


# =====================================================================

@pytest.mark.asyncio
async def test_user_methods(client: AsyncClient, token_r: TokenResponse):

    user1 = {
        "username": "user1",
        "full_name": "User One",
        "email": "user1@mail.com",
        "role": USER_ROLE,
        "password": "user1"
    }

    user2 = {
        "username": "user2",
        "full_name": "User One",
        "email": "user2@mail.com",
        "role": USER_ROLE,
        "password": "user2"
    }

    user3 = {
        "username": "user3",
        "full_name": "User One",
        "email": "user3@mail.com",
        "role": USER_ROLE,
        "password": "user3"
    }

    # -----------------------------------------------------------------

    # -> Add users

    response = await client.post(
        "/users/",
        data=user1,
        headers=token_r.headers)

    assert response.status_code == sc.OK
    user1_id = response.json()['id']

    response = await client.post(
        "/users/",
        data=user2,
        headers=token_r.headers)

    print(response.json())
    assert response.status_code == sc.OK
    assert response.json()['id']
    user2_id = response.json()['id']

    # -> Get added users

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers)

    print(response.json())
    assert response.status_code == sc.OK
    assert response.json()['id']
    assert response.json()['username']
    assert response.json()['full_name']
    assert response.json()['role']
    assert response.json()['email']
    assert response.json()['username'] == user1['username']

    response = await client.get(
        "/users/{}".format(user2_id),
        headers=token_r.headers)

    print(response.json())
    assert response.status_code == sc.OK
    assert response.json()['id']
    assert response.json()['username']
    assert response.json()['full_name']
    assert response.json()['role']
    assert response.json()['email']

    # -> Get all users

    response = await client.get("/users/", headers=token_r.headers)
    print(response.json())
    assert response.status_code == sc.OK
    # 4: 2 default users (admin, user) + 2 added users
    assert len(response.json()) == 4

    # -----------------------------------------------------------------
    # => Update user

    # -> Update user as admin

    # - Update user

    user1_updated = user1.copy()
    del user1_updated['username']
    user1_updated['full_name'] = 'User 1 Updated'
    response = await client.put(
        "/users/{}".format(user1_id),
        data=user1_updated,
        headers=token_r.headers)
    assert response.status_code == sc.OK

    # - Get updated user

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers)

    print(response.json())
    assert response.status_code == sc.OK
    assert response.json()['full_name'] == 'User 1 Updated'

    # -> Update user as user

    user_tr = await AccessToken.get_certain_token(client, "user1", "user1")

    # - Update user

    user1_updated = user1.copy()
    del user1_updated['username']
    user1_updated['full_name'] = 'User 1 Updated (II)'
    user1_updated['old_password'] = user1['password']
    user1_updated['password'] = 'new_password'
    print('user1_updated', user1_updated)

    response = await client.put(
        "/users/{}".format(user1_id),
        data=user1_updated,
        headers=user_tr.headers)
    if response.status_code != sc.OK:
        print(response.json())
    assert response.status_code == sc.OK

    # - Get updated user

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers)

    print(response.json())
    assert response.status_code == sc.OK
    assert response.json()['full_name'] == 'User 1 Updated (II)'

    # -----------------------------------------------------------------
    # => Try to perform admin operations with user account

    user_tr = await AccessToken.get_certain_token(
        client, "user1", "new_password")

    response = await client.post(
        "/users/",
        data=user3,
        headers=user_tr.headers)
    assert response.status_code == sc.UNAUTHORIZED

    response = await client.get(
        "/users/{}".format(user2_id),
        headers=user_tr.headers)
    assert response.status_code == sc.UNAUTHORIZED

    # - Delete added user
    response = await client.delete(
        "/users/{}".format(user2_id),
        headers=user_tr.headers)
    assert response.status_code == sc.UNAUTHORIZED

    # -----------------------------------------------------------------

    # -> Delete added users

    response = await client.delete(
        "/users/{}".format(user1_id),
        headers=token_r.headers)
    assert response.status_code == sc.OK

    response = await client.delete(
        "/users/{}".format(user2_id),
        headers=token_r.headers)

    print(response.json())
    assert response.status_code == sc.OK
    assert response.json()['removed']
    assert response.json()['removed'] == user2_id

    # -> Get deleted users

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers)
    assert response.status_code == sc.NOT_FOUND

    response = await client.get(
        "/users/{}".format(user2_id),
        headers=token_r.headers)
    assert response.status_code == sc.NOT_FOUND


# =====================================================================

@pytest.mark.asyncio
async def test_update_image(client: AsyncClient, token_r: TokenResponse):
    image_name = 'c_im0236.png'

    # -> Upload image

    response = await upload_single_image(client, token_r, image_name)
    print(response)
    assert response.status_code == sc.OK
    assert response.json()['id']
    id_ = response.json()['id']

    # -> Get uploaded image

    params = {'ids': id_}
    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes
    assert response.json()[0]["title"] == 'text'

    # -> Update image

    response = await client.put(
        "/images/{}".format(id_),
        data={
            'title': 'new title',
            'text': 'new text'
        },
        headers=token_r.headers
    )
    print(response)
    assert response.status_code == sc.OK

    response = await client.get("/images/", params=params, headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes
    assert response.json()[0]["title"] == 'new title'

    # -> Get uploaded image base64

    response = await client.get("/images/base64/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.OK
    assert type(response.content) == bytes

    # -> Remove the file

    response = await delete_images(client, token_r, ids=[id_])
    assert response.status_code == sc.OK
    assert 'removed' in response.json()

    # -> Try fetching the removed file

    response = await client.get("/images/{}".format(id_), headers=token_r.headers)
    print(response)
    assert response.status_code == sc.NOT_FOUND