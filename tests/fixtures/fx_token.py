import pytest
import requests


@pytest.fixture(scope="session")
def auth_token():
    # login endpoint untuk dapat token
    resp = requests.post(
        "http://127.0.0.1:8000/api/v1/user/login",
        data={"username": "Admin", "password": "admin@777999"},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]
