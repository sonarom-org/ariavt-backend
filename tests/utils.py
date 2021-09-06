from pathlib import Path
from typing import List

from httpx import AsyncClient, Response

from tests.models_test import TokenResponse


async def upload_single_image(
        client: AsyncClient,
        token_r: TokenResponse,
        image_name: str,
        title: str = 'text',
        text: str = 'text',
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
    response = await client.post('/images/',
                                 files=files,
                                 data={
                                     "text": text,
                                     "title": title,
                                 },
                                 headers=token_r.headers)
    return response


async def upload_images(
        client: AsyncClient,
        token_r: TokenResponse,
        image_names: List[str]
        ) -> Response:
    # >>> files = [('images', ('foo.png', open('foo.png', 'rb'), 'image/png')),
    #               ('images', ('bar.png', open('bar.png', 'rb'), 'image/png'))]
    # >>> r = httpx.post("https://httpbin.org/post", files=files)
    files = []
    for image_name in image_names:
        # Get the complete path of the image to be uploaded
        file_to_upload = Path('/app_wd/tests/_imgs', image_name)
        # Open file and build json to post
        files.append(('files', file_to_upload.open('rb')))
    # Add necessary 'multipart/form-data' header
    headers = token_r.headers.copy()
    headers['Content-Type'] = 'multipart/form-data'
    print('HEADERS', headers)
    # Post data
    response = await client.post('/images/batch-upload',
                                 files=files,
                                 headers=token_r.headers)
    return response


async def delete_images(
        client: AsyncClient,
        token_r: TokenResponse,
        ids: List[int]
        ) -> Response:
    headers = token_r.headers.copy()
    headers['Content-Type'] = 'application/json'
    print('HEADERS', headers)
    # Select images to delete
    response = await client.post('/images/selection', json=ids,
                                 headers=token_r.headers)
    selection = response.json()['selection']
    # Delete selected images
    response = await client.delete('/images/selection/{}'.format(selection),
                                   headers=token_r.headers)
    print(response)
    return response
