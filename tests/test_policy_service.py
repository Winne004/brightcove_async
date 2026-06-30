from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from brightcove_async.schemas.policy_model import (
    CreatePolicyKeyBody,
    PolicyGeo,
    PolicyKey,
    PolicyKeyData,
)
from brightcove_async.services.policy import Policy

BASE_URL = "https://policy.api.brightcove.com/v1"


class DummyOAuth:
    async def get_access_token(self):
        return "test_token"

    @property
    async def headers(self):
        return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_session():
    return AsyncMock(spec=aiohttp.ClientSession)


@pytest.fixture
def dummy_oauth():
    return DummyOAuth()


@pytest.fixture
def policy_service(mock_session, dummy_oauth):
    return Policy(
        session=mock_session,
        oauth=dummy_oauth,
        base_url=BASE_URL,
        limit=10,
    )


def test_policy_initialization(policy_service):
    assert policy_service._limit == 10
    assert policy_service.base_url == BASE_URL


@pytest.mark.asyncio
async def test_create_policy_key(policy_service):
    with patch.object(
        policy_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = PolicyKey(
            key_string="BCpkADawqM1",
            key_data=PolicyKeyData(account_id="account123"),
        )

        key_data = PolicyKeyData(
            account_id="account123",
            apis=["search"],
            allowed_domains=["https://example.com"],
        )
        await policy_service.create_policy_key("account123", key_data)

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args.kwargs["method"] == "POST"
        assert call_args.kwargs["model"] == PolicyKey
        assert "account123/policy_keys" in call_args.kwargs["endpoint"]
        payload = call_args.kwargs["payload"]
        assert isinstance(payload, CreatePolicyKeyBody)
        assert payload.key_data is key_data


@pytest.mark.asyncio
async def test_create_policy_key_rejects_account_id_mismatch(policy_service):
    with patch.object(
        policy_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        key_data = PolicyKeyData(account_id="other")

        with pytest.raises(ValueError, match="must match the account_id"):
            await policy_service.create_policy_key("account123", key_data)

        mock_fetch.assert_not_called()


@pytest.mark.asyncio
async def test_get_policy_key(policy_service):
    with patch.object(
        policy_service, "fetch_data", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = PolicyKey(
            key_string="BCpkADawqM1",
            key_data=PolicyKeyData(account_id="account123"),
        )

        await policy_service.get_policy_key("account123", "BCpkADawqM1")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args.kwargs["model"] == PolicyKey
        assert "account123/policy_keys/BCpkADawqM1" in call_args.kwargs["endpoint"]


def test_create_policy_key_body_serializes_with_hyphenated_aliases():
    """The request body must use the hyphenated keys the API expects."""
    body = CreatePolicyKeyBody(
        key_data=PolicyKeyData(
            account_id="account123",
            apis=["search"],
            allowed_domains=["https://example.com"],
            require_ad_config=True,
            geo=PolicyGeo(countries=["us"], exclude_countries=False),
        )
    )

    dumped = body.model_dump(
        mode="json", by_alias=True, exclude_none=True, exclude_unset=True
    )

    assert dumped == {
        "key-data": {
            "account-id": "account123",
            "apis": ["search"],
            "allowed-domains": ["https://example.com"],
            "require-ad-config": True,
            "geo": {"countries": ["us"], "exclude_countries": False},
        }
    }


def test_policy_key_parses_hyphenated_response():
    """The response model accepts the hyphenated keys returned by the API."""
    payload = {
        "key-string": "BCpkADawqM1",
        "key-data": {
            "account-id": "2728142649001",
            "apis": ["search"],
            "allowed-domains": ["https://54.210.55.162"],
        },
    }

    key = PolicyKey.model_validate(payload)

    assert key.key_string == "BCpkADawqM1"
    assert key.key_data.account_id == "2728142649001"
    assert key.key_data.apis == ["search"]
    assert key.key_data.allowed_domains == ["https://54.210.55.162"]


def test_policy_key_parses_underscore_key_string():
    """The response model also accepts the schema's ``key_string`` spelling."""
    payload = {
        "key_string": "BCpkADawqM1",
        "key-data": {"account-id": "2728142649001"},
    }

    key = PolicyKey.model_validate(payload)

    assert key.key_string == "BCpkADawqM1"
