from pathlib import Path

import pytest
from httpx import AsyncClient, Response
from http import HTTPStatus as StC

from tests.models_test import AccessToken, TokenResponse
from tests.utils import upload_single_image


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


async def upload_single_image_to_service(
        client: AsyncClient,
        token_r: TokenResponse,
        image_name: str,
) -> Response:
    # Get the complete path of the image to be uploaded
    file_to_upload = Path('/app_wd/tests/_imgs', image_name)
    # Open file and build json to post
    files = {'file': file_to_upload.open('rb')}
    # Add necessary 'multipart/form-data' header
    # headers = token_r.headers.copy()
    # headers['Content-Type'] = 'multipart/form-data'
    # print('HEADERS', headers)
    # Post data
    response = await client.post(
        '/services/empty-service',
        files=files,
        headers=token_r.headers
    )
    return response


@pytest.mark.asyncio
async def test_service_image(client: AsyncClient, token_r: TokenResponse):

    # -> Upload single image
    image_name = 'c_im0236.png'
    response = await upload_single_image(client, token_r, image_name)
    print(response)
    assert response.status_code == StC.OK
    image_id = response.json()['id']

    # -> Add service
    service_1 = {
        "name": "service",
        "url": "http://127.0.0.1:8888/",
        "full_name": "Service",
        "description": "Service for image analysis",
    }

    response = await client.post(
        "/services/",
        data=service_1,
        headers=token_r.headers
    )

    assert response.status_code == StC.OK
    service_id = response.json()['id']

    response = await client.get(
        f"/services/{service_id}",
        params={'image_id': image_id},
        headers=token_r.headers,
    )

    assert response.status_code == StC.OK
    assert type(response.content) == bytes
