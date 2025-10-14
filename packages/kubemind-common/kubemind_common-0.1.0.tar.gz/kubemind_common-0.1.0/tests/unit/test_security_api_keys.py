import asyncio

import pytest
from starlette.requests import Request

from kubemind_common.security.api_keys import (
    APIKeyAuth,
    create_api_key_dependency,
    generate_api_key,
    hash_api_key,
    validate_api_key_format,
    get_api_key_from_header,
)


def make_request(headers: dict[str, str]) -> Request:
    scope = {"type": "http", "method": "GET", "path": "/", "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()]}
    return Request(scope)


def test_generate_and_validate_api_key_format():
    key = generate_api_key(prefix="km", length=4)
    assert key.startswith("km_")
    assert validate_api_key_format(key)
    assert not validate_api_key_format("invalid")


def test_hash_api_key_stable():
    h1 = hash_api_key("km_abc")
    h2 = hash_api_key("km_abc")
    assert h1 == h2


def test_get_api_key_from_header_ok_and_missing():
    async def flow():
        req = make_request({"X-API-Key": generate_api_key("km", length=2)})
        key = await get_api_key_from_header(req)
        assert key
        with pytest.raises(Exception):
            await get_api_key_from_header(make_request({}))

    asyncio.get_event_loop().run_until_complete(flow())


def test_api_key_dependency_validation():
    async def dummy_validator(api_key: str):
        return True

    dep = create_api_key_dependency(validator=dummy_validator)

    async def flow():
        good = make_request({"X-API-Key": generate_api_key("km", length=2)})
        assert await dep(good)
        with pytest.raises(Exception):
            await dep(make_request({"X-API-Key": "bad"}))

    asyncio.get_event_loop().run_until_complete(flow())


def test_api_key_auth_callable():
    auth = APIKeyAuth()

    async def flow():
        good = make_request({"X-API-Key": generate_api_key("km", length=2)})
        assert await auth(good)
        with pytest.raises(Exception):
            await auth(make_request({"X-API-Key": "bad"}))

    asyncio.get_event_loop().run_until_complete(flow())

