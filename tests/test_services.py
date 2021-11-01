import pytest
from httpx import AsyncClient
from http import HTTPStatus as StC

from tests.models_test import AccessToken, TokenResponse


@pytest.mark.asyncio
async def test_service_methods(client: AsyncClient, token_r: TokenResponse):

    response = await client.get("/services/", headers=token_r.headers)
    print(response.json())
    assert response.status_code == StC.NOT_FOUND

    # -----------------------------------------------------------------

    service_1 = {
        "name": "service_1",
        "url": "http://localhost:8080",
        "full_name": "Service 1",
        "description": "Service 1 for image analysis",
    }

    service_2 = {
        "name": "service_2",
        "url": "http://localhost:8080",
        "full_name": "2nd Service",
        "description": "Second service for image analysis",
    }

    # -----------------------------------------------------------------

    # -> Add services

    response = await client.post(
        "/services/",
        data=service_1,
        headers=token_r.headers
    )

    assert response.status_code == StC.OK
    service_1_id = response.json()['id']

    response = await client.post(
        "/services/",
        data=service_2,
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['id']
    service_2_id = response.json()['id']

    # -> Get added services

    response = await client.get(
        "/services/{}".format(service_1_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    # Check if all service fields are present and match
    assert response.json()['id'] == service_1_id
    assert response.json()['name'] == service_1['name']
    assert response.json()['url'] == service_1['url']
    assert response.json()['full_name'] == service_1['full_name']
    assert response.json()['description'] == service_1['description']

    response = await client.get(
        "/services/{}".format(service_2_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    # Check if all service fields are present and match
    assert response.json()['id'] == service_2_id
    assert response.json()['name'] == service_2['name']
    assert response.json()['url'] == service_2['url']
    assert response.json()['full_name'] == service_2['full_name']
    assert response.json()['description'] == service_2['description']

    # -> Get all services

    response = await client.get("/services/", headers=token_r.headers)
    print(response.json())
    assert response.status_code == StC.OK
    assert len(response.json()) == 2

    # -----------------------------------------------------------------
    # => Update service

    # -> Update service as admin

    # - Update service

    service_1_updated = service_1.copy()
    del service_1_updated['name']
    service_1_updated['full_name'] = 'Service 1 Updated'
    response = await client.put(
        "/services/{}".format(service_1_id),
        data=service_1_updated,
        headers=token_r.headers
    )
    assert response.status_code == StC.OK

    # - Get updated service

    response = await client.get(
        "/services/{}".format(service_1_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['full_name'] == 'Service 1 Updated'

    # -> Update service as regular user

    user_tr = await AccessToken.get_certain_token(client, "user", "user")

    response = await client.put(
        "/services/{}".format(service_1_id),
        data=service_1,
        headers=user_tr.headers
    )
    if response.status_code != StC.OK:
        print(response.json())
    assert response.status_code == StC.UNAUTHORIZED

    # -----------------------------------------------------------------

    # -> Delete added services

    response = await client.delete(
        "/services/{}".format(service_1_id),
        headers=token_r.headers
    )
    assert response.status_code == StC.OK

    response = await client.delete(
        "/services/{}".format(service_2_id),
        headers=token_r.headers
    )

    print(response.json())
    assert response.status_code == StC.OK
    assert response.json()['removed']
    assert response.json()['removed'] == service_2_id

    # -> Get deleted services

    response = await client.get(
        "/services/{}".format(service_1_id),
        headers=token_r.headers
    )
    assert response.status_code == StC.NOT_FOUND

    response = await client.get(
        "/services/{}".format(service_2_id),
        headers=token_r.headers
    )
    assert response.status_code == StC.NOT_FOUND
