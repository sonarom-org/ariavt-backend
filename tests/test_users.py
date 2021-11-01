import pytest
from http import HTTPStatus as StC
from httpx import AsyncClient

from tests.models_test import AccessToken, TokenResponse

from app.globals import USER_ROLE


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
        headers=token_r.headers
    )

    assert response.status_code == StC.OK
    user1_id = response.json()['id']

    response = await client.post(
        "/users/",
        data=user2,
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['id']
    user2_id = response.json()['id']

    # -> Get added users

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['id']
    assert response.json()['username']
    assert response.json()['full_name']
    assert response.json()['role']
    assert response.json()['email']
    assert response.json()['username'] == user1['username']

    response = await client.get(
        "/users/{}".format(user2_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['id']
    assert response.json()['username']
    assert response.json()['full_name']
    assert response.json()['role']
    assert response.json()['email']

    # -> Get all users

    response = await client.get("/users/", headers=token_r.headers)
    print(response.json())
    assert response.status_code == StC.OK
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
        headers=token_r.headers
    )
    assert response.status_code == StC.OK

    # - Get updated user

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
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
        headers=user_tr.headers
    )
    if response.status_code != StC.OK:
        print(response.json())
    assert response.status_code == StC.OK

    # - Get updated user

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['full_name'] == 'User 1 Updated (II)'

    # -----------------------------------------------------------------
    # => Try to perform admin operations with user account

    user_tr = await AccessToken.get_certain_token(
        client, "user1", "new_password")

    response = await client.post(
        "/users/",
        data=user3,
        headers=user_tr.headers
    )
    assert response.status_code == StC.UNAUTHORIZED

    response = await client.get(
        "/users/{}".format(user2_id),
        headers=user_tr.headers
    )
    assert response.status_code == StC.UNAUTHORIZED

    # - Delete added user
    response = await client.delete(
        "/users/{}".format(user2_id),
        headers=user_tr.headers)
    assert response.status_code == StC.UNAUTHORIZED

    # -----------------------------------------------------------------

    # -> Delete added users

    response = await client.delete(
        "/users/{}".format(user1_id),
        headers=token_r.headers
    )
    assert response.status_code == StC.OK

    response = await client.delete(
        "/users/{}".format(user2_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['removed']
    assert response.json()['removed'] == user2_id

    # -> Get deleted users

    response = await client.get(
        "/users/{}".format(user1_id),
        headers=token_r.headers
    )
    assert response.status_code == StC.NOT_FOUND

    response = await client.get(
        "/users/{}".format(user2_id),
        headers=token_r.headers
    )
    assert response.status_code == StC.NOT_FOUND
