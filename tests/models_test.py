from typing import Any
from pydantic import BaseModel


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

    @staticmethod
    async def get_certain_token(client, username, password):
        login_data = {
            "username": username,
            "password": password,
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
